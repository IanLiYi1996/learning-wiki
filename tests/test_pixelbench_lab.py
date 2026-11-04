import copy
import importlib.util
import math
from pathlib import Path
import unittest


spec = importlib.util.spec_from_file_location(
    "pixelbench_lab", Path(__file__).resolve().parents[1] / "scripts/pixelbench_lab.py")
LAB = importlib.util.module_from_spec(spec)
spec.loader.exec_module(LAB)


class GridTests(unittest.TestCase):
    def setUp(self):
        self.output = {"palette": ["#FFFFFF", "#000000"],
                       "pixels": ["0000", "0110", "0110", "0000"]}

    def test_rgb_lookup_and_nonflat(self):
        rgb = LAB.render_rgb(self.output, 4)
        self.assertEqual(rgb[1][1], (0, 0, 0))
        self.assertEqual(rgb[0][0], (255, 255, 255))
        self.assertFalse(LAB.flat_rgb(self.output, 4))

    def test_list_rows_and_input_are_not_mutated(self):
        before = copy.deepcopy(self.output)
        _, grid = LAB.validate_grid(self.output, 4)
        listed = {**self.output, "pixels": [list(row) for row in grid]}
        self.assertEqual(LAB.render_rgb(self.output, 4), LAB.render_rgb(listed, 4))
        self.assertEqual(self.output, before)

    def test_duplicate_palette_is_flat_after_rendering(self):
        self.assertTrue(LAB.flat_rgb(
            {"palette": ["#FFFFFF", "#ffffff"], "pixels": ["01", "10"]}, 2))

    def test_equivalent_palette_permutation(self):
        other = {"palette": ["#000000", "#FFFFFF"],
                 "pixels": ["1111", "1001", "1001", "1111"]}
        self.assertEqual(LAB.render_rgb(self.output, 4), LAB.render_rgb(other, 4))

    def test_invalid_inputs_are_not_repaired(self):
        cases = [
            None, [], {},
            {**self.output, "palette": ["#fff", "#000000"]},
            {**self.output, "palette": ["#FFFFFF"]},
            {**self.output, "palette": ["#FFFFFF"] * 9},
            {**self.output, "palette": [True, "#000000"]},
            {**self.output, "pixels": ["0000"] * 3},
            {**self.output, "pixels": ["0000"] * 5},
            {**self.output, "pixels": ["000"] * 4},
            {**self.output, "pixels": ["00000"] * 4},
            {**self.output, "pixels": ["2222"] * 4},
            {**self.output, "pixels": ["8888"] * 4},
            {**self.output, "pixels": [" 000"] * 4},
            {**self.output, "pixels": [[True] * 4] * 4},
            {**self.output, "pixels": [[0.0] * 4] * 4},
            {**self.output, "pixels": [[-1] * 4] * 4},
        ]
        for value in cases:
            with self.subTest(value=value), self.assertRaises(ValueError):
                LAB.render_rgb(value, 4)

    def test_dimensions_must_be_positive_integers(self):
        for size in (True, 0, -1, 4.0, math.nan):
            with self.subTest(size=size), self.assertRaises(ValueError):
                LAB.validate_grid(self.output, size)


class ScoringTests(unittest.TestCase):
    def test_failure_denominators_are_different(self):
        result = LAB.denominator_summary([1, 0.5, None, None])
        self.assertEqual(result["all_expected_mean"], 0.375)
        self.assertEqual(result["valid_only_mean"], 0.75)
        self.assertEqual(result["coverage"], 0.5)

    def test_valid_zero_is_not_invalid(self):
        result = LAB.denominator_summary([0, None])
        self.assertEqual(result["valid"], 1)
        self.assertEqual(result["valid_only_mean"], 0)

    def test_no_valid_or_no_expected_does_not_divide_by_zero(self):
        all_bad = LAB.denominator_summary([None, None])
        self.assertEqual(all_bad["all_expected_mean"], 0)
        self.assertIsNone(all_bad["valid_only_mean"])
        empty = LAB.denominator_summary([])
        self.assertIsNone(empty["coverage"])
        self.assertIsNone(empty["all_expected_mean"])

    def test_invalid_numeric_scores(self):
        for score in (True, "1", math.nan, math.inf, -0.1, 1.1):
            with self.subTest(score=score), self.assertRaises(ValueError):
                LAB.denominator_summary([score])

    def test_comparison_set_changes_score_not_raw_metric(self):
        methods = {"A": [0.2] * 3, "B": [0.4] * 3, "C": [0.6] * 3}
        self.assertAlmostEqual(LAB.relative_aggregate(methods)["B"], 50)
        self.assertAlmostEqual(LAB.relative_aggregate({**methods, "D": [1] * 3})["B"], 25)
        self.assertEqual(methods["B"], [0.4] * 3)

    def test_aggregate_rejects_constant_columns_and_bad_shape(self):
        for methods in ({}, {"A": [0.2] * 3},
                        {"A": [0, 0, 1], "B": [1, 1, 1]},
                        {"A": [0, 0], "B": [1, 1, 1]},
                        {"A": [0, 0, math.nan], "B": [1, 1, 1]},
                        {"A": [0, False, 0], "B": [1, 1, 1]}):
            with self.subTest(methods=methods), self.assertRaises(ValueError):
                LAB.relative_aggregate(methods)

    def test_aggregate_accepts_finite_negative_cosines(self):
        scores = LAB.relative_aggregate({"A": [0, -0.5, -0.8], "B": [1, 0.5, 0.8]})
        self.assertEqual(scores, {"A": 0, "B": 100})

    def test_official_unit_vs_benchmark_weight(self):
        result = LAB.averages([[1] * 9, [0]])
        self.assertEqual(result["official_unit_weighted"], 0.9)
        self.assertEqual(result["benchmark_equal_weighted"], 0.5)

    def test_empty_invalid_benchmarks_rejected(self):
        for rows in ([], [[]], [[True]], [[1.5]], [[math.inf]]):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                LAB.averages(rows)

    def test_grouped_unit_requires_all_boolean_members(self):
        self.assertTrue(LAB.grouped_success([True, True]))
        self.assertFalse(LAB.grouped_success([True, False]))
        for row in ([], [1], [True, "yes"]):
            with self.subTest(row=row), self.assertRaises(ValueError):
                LAB.grouped_success(row)

    def test_resolution_positions_are_not_tokens(self):
        self.assertEqual(LAB.positions(64), {"size": 64, "positions": 4096, "relative": 16})
        self.assertEqual(LAB.positions(128)["relative"], 64)
        for size in (True, 0, -1, 1.5):
            with self.subTest(size=size), self.assertRaises(ValueError):
                LAB.positions(size)

    def test_demo_is_pure_and_deterministic(self):
        self.assertEqual(LAB.demo(), LAB.demo())
        self.assertEqual(LAB.demo()["paired_unit"], False)


if __name__ == "__main__":
    unittest.main()
