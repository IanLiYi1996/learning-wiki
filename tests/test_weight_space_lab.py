import importlib.util
import math
from pathlib import Path
import random
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("weight_space_lab", ROOT / "scripts/weight_space_lab.py")
LAB = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = LAB
SPEC.loader.exec_module(LAB)


class WeightSpaceLabTests(unittest.TestCase):
    def test_affine_uses_output_by_input_matrix_convention(self):
        self.assertEqual(LAB.affine(((1, 2), (3, 4)), (5, 6), (7, 8)), (24, 47))

    def test_dimensions_rectangularity_and_nonfinite_values_are_rejected(self):
        for weights, inputs, bias in (
            (((1, 2),), (1,), (0,)),
            (((1, 2),), (1, 2), (0, 0)),
            (((1, 2), (3,)), (1, 2), (0, 0)),
            (((math.nan,),), (1,), (0,)),
            (((1,),), (math.inf,), (0,)),
            (((1,),), (1,), (math.nan,)),
        ):
            with self.subTest(weights=weights), self.assertRaises(ValueError):
                LAB.affine(weights, inputs, bias)
        with self.assertRaises(ValueError):
            LAB.Network(((1,),), (0,), ((1, 2),), (0,))

    def test_controller_has_fifteen_parameters_and_exact_logits(self):
        network = LAB.controller()
        self.assertEqual(network.parameter_count, 15)
        self.assertEqual(network.forward((0.0, 1.0)), (-1.0, 0.0, 1.0))
        self.assertEqual(network.forward((1.0, 0.0)), (1.0, 0.0, -1.0))

    def test_fix_restores_all_grid_decisions_without_training(self):
        self.assertEqual(LAB.grid_score(LAB.controller(bugged=True)), (11, 121))
        self.assertEqual(LAB.grid_score(LAB.controller()), (121, 121))

    def test_argmax_tie_prefers_stay_and_invalid_logits_are_rejected(self):
        self.assertEqual(LAB.action((0.0, 0.0, 0.0)), 1)
        for logits in ((0, 1), (0, math.inf, 1)):
            with self.assertRaises(ValueError):
                LAB.action(logits)

    def test_hidden_permutation_preserves_outputs_over_random_real_inputs(self):
        original = LAB.controller()
        renamed = LAB.permute_hidden(original, (1, 0))
        generator = random.Random(73)
        for _ in range(100):
            inputs = (generator.uniform(-2, 2), generator.uniform(-2, 2))
            self.assertEqual(original.forward(inputs), renamed.forward(inputs))
        for order in ((0, 0), (0,), (1, 2)):
            with self.assertRaises(ValueError):
                LAB.permute_hidden(original, order)

    def test_blind_average_can_destroy_identical_functions(self):
        original = LAB.Network(((1.0,), (-1.0,)), (0.0, 0.0), ((1.0, 0.0),), (0.0,))
        renamed = LAB.permute_hidden(original, (1, 0))
        for value in (-1.0, 0.0, 1.0):
            self.assertEqual(original.forward((value,)), renamed.forward((value,)))
        self.assertEqual(original.forward((1.0,)), (1.0,))
        self.assertEqual(LAB.average_networks(original, renamed).forward((1.0,)), (0.0,))
        aligned = LAB.permute_hidden(renamed, (1, 0))
        self.assertEqual(LAB.average_networks(original, aligned).forward((1.0,)), (1.0,))
        with self.assertRaises(ValueError):
            LAB.average_networks(original, LAB.controller())

    def test_partial_projection_does_not_remove_direction_everywhere(self):
        weights = ((2.0, 3.0), (4.0, 5.0))
        self.assertEqual(LAB.project_columns(weights, (1.0, 0.0), (0,)),
                         ((0.0, 3.0), (4.0, 5.0)))
        self.assertEqual(LAB.project_columns(weights, (1.0, 0.0), (0, 1)),
                         ((0.0, 0.0), (4.0, 5.0)))

    def test_projection_normalizes_direction_and_preserves_orthogonal_component(self):
        weights = ((2.0, 3.0), (4.0, 5.0))
        direction = (3.0, 4.0)
        result = LAB.project_columns(weights, direction, (0, 1))
        for column in range(2):
            self.assertAlmostEqual(sum(direction[row] * result[row][column]
                                       for row in range(2)), 0.0)
            self.assertLessEqual(sum(result[row][column] ** 2 for row in range(2)),
                                 sum(weights[row][column] ** 2 for row in range(2)))

    def test_invalid_projection_inputs_are_rejected(self):
        for direction, columns in (
            ((0, 0), (0,)), ((1,), (0,)), ((math.inf, 0), (0,)),
            ((1, 0), (-1,)), ((1, 0), (2,)), ((1, 0), (0, 0)),
        ):
            with self.subTest(direction=direction, columns=columns), self.assertRaises(ValueError):
                LAB.project_columns(((1, 2), (3, 4)), direction, columns)

    def test_demo_output_matches_documented_teaching_results(self):
        result = LAB.run_exercises()
        self.assertEqual(result["controller_parameters"], 15)
        self.assertEqual(result["fixed_grid"], (121, 121))
        self.assertEqual(result["hidden_permutation_max_error"], 0)
        self.assertEqual(result["blind_average_at_one"], 0)
        self.assertEqual(result["untouched_column_direction_component"], 3)


if __name__ == "__main__":
    unittest.main()
