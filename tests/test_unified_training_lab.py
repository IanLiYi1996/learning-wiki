import copy
import importlib.util
import json
import math
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location(
    "unified_training_lab", Path(__file__).resolve().parents[1] / "scripts/unified_training_lab.py")
LAB = importlib.util.module_from_spec(spec)
spec.loader.exec_module(LAB)


class TargetsAndWeights(unittest.TestCase):
    def test_condition_on_success_and_normalize(self):
        result = LAB.success_target([0.6, 0.2, 0.2], [1, 0, 1])
        self.assertAlmostEqual(result["success_mass"], 0.8)
        self.assertEqual(result["target"][1], 0)
        self.assertAlmostEqual(result["target"][0], 0.75)
        self.assertAlmostEqual(result["target"][2], 0.25)

    def test_changing_generator_changes_target(self):
        result = LAB.success_target([1/3] * 3, [1, 0, 1])
        self.assertEqual(result["target"], [0.5, 0, 0.5])

    def test_no_success_target_is_not_fabricated(self):
        with self.assertRaises(ValueError):
            LAB.success_target([0, 1], [1, 0])

    def test_probability_and_reward_contracts(self):
        for probabilities, rewards in (([], []), ([0.2, 0.2], [1, 0]),
                                        ([1.1, -0.1], [1, 0]), ([True, 0], [1, 0]),
                                        ([math.nan, 0], [1, 0]), ([1], [1, 0]),
                                        ([1], [True]), ([1], [0.5])):
            with self.subTest(probabilities=probabilities), self.assertRaises(ValueError):
                LAB.success_target(probabilities, rewards)

    def test_maxrl_weights_and_all_wrong(self):
        self.assertEqual(LAB.response_weights([1, 0, 0, 0]), [4, 0, 0, 0])
        self.assertEqual(LAB.response_weights([1] * 4), [1] * 4)
        self.assertEqual(LAB.response_weights([0] * 4), [0] * 4)
        self.assertAlmostEqual(sum(LAB.response_weights([1, 1, 1, 0])), 4)

    def test_finite_sampling_does_not_remove_difficulty_bias(self):
        self.assertEqual(LAB.finite_prompt_mass(0.25, 4), 0.68359375)
        self.assertEqual(LAB.finite_prompt_mass(0.75, 4), 0.99609375)
        self.assertEqual(LAB.finite_prompt_mass(0.25, 1), 0.25)
        self.assertEqual(LAB.finite_prompt_mass(0, 1000), 0)
        self.assertEqual(LAB.finite_prompt_mass(1, 1), 1)

    def test_finite_probability_small_values_are_stable(self):
        self.assertGreater(LAB.finite_prompt_mass(1e-20, 16), 0)
        for p, samples in ((-0.1, 1), (1.1, 1), (math.inf, 2),
                           (False, 1), (0.5, 0), (0.5, True), (0.5, 1.5)):
            with self.subTest(p=p), self.assertRaises(ValueError):
                LAB.finite_prompt_mass(p, samples)

    def test_pass_at_k_is_not_pass_at_one(self):
        self.assertEqual(LAB.pass_at_k(4, 1, 1), 0.25)
        self.assertEqual(LAB.pass_at_k(4, 1, 2), 0.5)
        self.assertEqual(LAB.pass_at_k(4, 1, 4), 1)
        self.assertEqual(LAB.pass_at_k(16, 0, 16), 0)
        self.assertEqual(LAB.pass_at_k(16, 16, 1), 1)

    def test_invalid_pass_at_k_counts(self):
        for args in ((0, 0, 1), (4, 5, 1), (4, 1, 5), (4, 1, 0),
                     (True, 0, 1), (4, 1.0, 1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                LAB.pass_at_k(*args)


class LossAndMixing(unittest.TestCase):
    def test_zero_weight_responses_count_but_prompts_do_not(self):
        result = LAB.loss_stats([99, 2, 2, 3, 3, 3], [0, 4, 4, 0, 0, 0],
                                [False, True, True, True, True, True])
        self.assertEqual(result, {"numerator": 16, "denominator": 5, "mean": 3.2})
        self.assertEqual(LAB.loss_stats([2, 2], [4, 4], [True, True])["mean"], 8)

    def test_all_wrong_and_all_prompt_are_distinct(self):
        self.assertEqual(LAB.loss_stats([2, 2], [0, 0], [True, True])["mean"], 0)
        self.assertIsNone(LAB.loss_stats([2, 2], [0, 0], [False, False])["mean"])
        self.assertIsNone(LAB.loss_stats([], [], [])["mean"])

    def test_invalid_nll_weights_masks_and_shapes(self):
        for args in (([1], [], [True]), ([1], [1], [False]), ([1], [1], [1]),
                     ([math.nan], [0], [False]), ([-1], [1], [True]),
                     ([1], [-1], [True]), ([1], [True], [True])):
            with self.subTest(args=args), self.assertRaises(ValueError):
                LAB.loss_stats(*args)

    def test_microbatch_means_require_denominator_weighting(self):
        self.assertEqual(LAB.pooled_mean([(16, 2), (0, 3)]), 3.2)
        self.assertNotEqual(LAB.pooled_mean([(16, 2), (0, 3)]), (8 + 0) / 2)
        self.assertIsNone(LAB.pooled_mean([]))
        self.assertIsNone(LAB.pooled_mean([(0, 0)]))
        with self.assertRaises(ValueError):
            LAB.pooled_mean([(1, 0)])

    def test_token_fraction_to_row_fraction(self):
        rates = LAB.source_probabilities([0.5, 0.5], [2, 8])
        self.assertEqual(rates, [0.8, 0.2])
        self.assertAlmostEqual(rates[0] * 2, rates[1] * 8)
        self.assertEqual(LAB.source_probabilities([0, 1], [2, 8]), [0, 1])

    def test_invalid_mixture_contracts(self):
        for fractions, lengths in (([0.5, 0.5], [0, 2]), ([1], [1, 2]),
                                   ([0.2, 0.2], [1, 2]), ([1], [math.inf]),
                                   ([1], [True])):
            with self.subTest(fractions=fractions), self.assertRaises(ValueError):
                LAB.source_probabilities(fractions, lengths)

    def test_schedule_endpoints_and_common_integral(self):
        self.assertEqual(LAB.schedule("half", 0), 0.02)
        self.assertEqual(LAB.schedule("half", 0.5), 0)
        self.assertEqual(LAB.schedule("growth", 1), 0.01)
        bins = 1000
        for name in ("constant", "decay", "growth", "half"):
            # Midpoint quadrature is exact for these piecewise linear functions
            # because the even number of bins includes their half-time breakpoint.
            mean = math.fsum(LAB.schedule(name, (i + 0.5) / bins) for i in range(bins)) / bins
            self.assertAlmostEqual(mean, 0.005)
        for args in (("other", 0), ("decay", -0.1), ("half", 1.1),
                     ("constant", True), ("constant", 0.5, 1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                LAB.schedule(*args)

    def test_dense_compute_includes_generation_and_shared_pretrain(self):
        self.assertEqual(LAB.dense_compute(1000, 100, 20, 30, 10),
                         {"estimated_total_flops": 1020000, "beyond_shared_pretrain_flops": 420000})
        for args in ((0, 0, 0, 0, 0), (True, 0, 0, 0, 0), (1, -1, 0, 0, 0),
                     (1, 0, 0, 1.5, 0)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                LAB.dense_compute(*args)

    def test_pure_serializable_demo(self):
        before = copy.deepcopy(LAB.demo())
        self.assertEqual(LAB.demo(), before)
        self.assertEqual(json.loads(json.dumps(before, allow_nan=False))["token_loss"]["mean"], 3.2)


if __name__ == "__main__":
    unittest.main()
