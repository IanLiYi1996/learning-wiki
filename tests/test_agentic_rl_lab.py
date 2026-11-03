import importlib.util
import json
import math
from pathlib import Path
import unittest


PATH = Path(__file__).resolve().parents[1] / "scripts/agentic_rl_lab.py"
SPEC = importlib.util.spec_from_file_location("agentic_rl_lab", PATH)
lab = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lab)


class Advantages(unittest.TestCase):
    def test_centered_demo(self):
        self.assertEqual(lab.group_advantages([1, 1, 0, 0]), (.5, .5, -.5, -.5))

    def test_sample_std_not_population_std(self):
        result = lab.group_advantages([1, 1, 0, 0], standardize=True)
        self.assertAlmostEqual(result[0], math.sqrt(3) / 2, places=7)
        self.assertAlmostEqual(sum(result), 0)

    def test_degenerate_and_singleton(self):
        for rewards in ([1] * 4, [0] * 4, [-1] * 4, [1]):
            self.assertEqual(lab.group_advantages(rewards, standardize=True),
                             (0.0,) * len(rewards))

    def test_rewards_and_controls_are_validated(self):
        for rewards in ([], [True], [math.nan], [math.inf], ["1"]):
            with self.assertRaises(ValueError):
                lab.group_advantages(rewards)
        for controls in ({"epsilon": 0}, {"epsilon": True}, {"standardize": "yes"}):
            with self.assertRaises(ValueError):
                lab.group_advantages([0, 1], **controls)


class Objectives(unittest.TestCase):
    def test_positive_upper_plateau(self):
        result = lab.clipped_signal(math.log(1.4), 1)
        self.assertAlmostEqual(result["loss"], -1.2)
        self.assertEqual(result["gradient"], 0)

    def test_negative_upper_still_learns(self):
        result = lab.clipped_signal(math.log(1.4), -1)
        self.assertAlmostEqual(result["loss"], 1.4)
        self.assertAlmostEqual(result["gradient"], 1.4)

    def test_negative_lower_plateau(self):
        result = lab.clipped_signal(math.log(.6), -1)
        self.assertAlmostEqual(result["loss"], .8)
        self.assertEqual(result["gradient"], 0)

    def test_positive_lower_still_learns(self):
        result = lab.clipped_signal(math.log(.6), 1)
        self.assertAlmostEqual(result["loss"], -.6)
        self.assertAlmostEqual(result["gradient"], -.6)

    def test_is_and_cispo_have_distinct_gradients(self):
        self.assertAlmostEqual(lab.clipped_signal(math.log(1.4), 1, method="is")["gradient"], -1.4)
        self.assertAlmostEqual(lab.clipped_signal(math.log(1.4), 1, method="cispo")["gradient"], -1.2)
        self.assertAlmostEqual(lab.clipped_signal(math.log(.6), 1, method="cispo")["gradient"], -.8)

    def test_zero_advantage(self):
        for method in ("is", "ppo", "cispo"):
            result = lab.clipped_signal(math.log(1.4), 0, method=method)
            self.assertEqual(result["gradient"], 0)
            self.assertEqual(result["loss"], 0)

    def test_finite_difference_ppo_away_from_boundaries(self):
        step = 1e-6
        for ratio in (.6, 1, 1.4):
            for advantage in (-1, 1):
                x = math.log(ratio)
                derivative = (lab.clipped_signal(x + step, advantage)["loss"] -
                              lab.clipped_signal(x - step, advantage)["loss"]) / (2 * step)
                self.assertAlmostEqual(derivative, lab.clipped_signal(x, advantage)["gradient"], places=7)

    def test_cispo_finite_difference_holds_detached_weight_fixed(self):
        x, weight, step = math.log(1.4), 1.2, 1e-6
        derivative = (-weight * (x + step) + weight * (x - step)) / (2 * step)
        self.assertAlmostEqual(derivative, lab.clipped_signal(x, 1, method="cispo")["gradient"])

    def test_invalid_parameters_and_overflow(self):
        for params in ({"low": 0}, {"low": 1.1}, {"high": .9},
                       {"method": "dpo"}, {"low": True}):
            with self.assertRaises(ValueError):
                lab.clipped_signal(0, 1, **params)
        for x, advantage in ((math.nan, 1), (0, True), (1000, 1), (700, 1e308)):
            with self.assertRaises(ValueError):
                lab.clipped_signal(x, advantage)


class ReductionAndSequenceRatio(unittest.TestCase):
    def test_different_means_same_predictions(self):
        self.assertEqual(lab.reductions([[2], [0, 0, 0]]),
                         {"sample_mean": 1, "token_mean": .5})

    def test_equal_lengths_and_single_sequence(self):
        self.assertEqual(lab.reductions([[1, 3], [3, 5]]),
                         {"sample_mean": 3, "token_mean": 3})
        self.assertEqual(lab.reductions([[2]]), {"sample_mean": 2, "token_mean": 2})

    def test_empty_and_nonfinite_means_rejected(self):
        for values in ([], [[]], [[1], []], [[math.nan]], [[True]]):
            with self.assertRaises(ValueError):
                lab.reductions(values)

    def test_geometric_not_product_or_arithmetic(self):
        ratio = lab.gspo_ratio([-2 + math.log(1.2), -2 + math.log(.8)], [-2, -2])
        self.assertAlmostEqual(ratio, math.sqrt(.96))
        self.assertNotAlmostEqual(ratio, .96)
        self.assertNotAlmostEqual(ratio, 1)

    def test_identical_policy_and_repeating_tokens(self):
        self.assertEqual(lab.gspo_ratio([-2, -3], [-2, -3]), 1)
        self.assertAlmostEqual(lab.gspo_ratio([-2, -2], [-3, -3]),
                               lab.gspo_ratio([-2], [-3]))

    def test_ratio_alignment_invalid_logps_and_overflow(self):
        for current, old in (([], []), ([-1], [-1, -2]), ([.1], [-1]),
                             ([-1], [math.nan]), ([False], [-1]), ([-1], [-1001])):
            with self.assertRaises(ValueError):
                lab.gspo_ratio(current, old)

    def test_zero_objectives_keep_original_denominator(self):
        self.assertEqual(lab.sequence_loss([1, -1, 1], normalization_sequences=8), -.125)
        self.assertEqual(lab.sequence_loss([1, -1, 1, 0, 0, 0, 0, 0],
                                          normalization_sequences=8), -.125)
        self.assertAlmostEqual(lab.sequence_loss([1, -1, 1], normalization_sequences=3), -1/3)
        self.assertEqual(lab.sequence_loss([], normalization_sequences=8), 0)

    def test_invalid_denominator(self):
        for size in (0, -1, True, 2.0, 1):
            with self.assertRaises(ValueError):
                lab.sequence_loss([1, 2], normalization_sequences=size)


class SamplingAndLength(unittest.TestCase):
    def test_budget_returns_partial_batch(self):
        self.assertEqual(lab.dynamic_selection([[True, True], [False, False],
                         [True, False], [True, True]], requested=2, candidate_budget=4),
                         {"candidate_groups": 4, "effective_groups": 1,
                          "update_possible": True, "full_batch": False})

    def test_full_batch_stops_consumption(self):
        self.assertEqual(lab.dynamic_selection([[True, False], [False, True], ["invalid"]],
                         requested=2, candidate_budget=4)["candidate_groups"], 2)

    def test_no_signal_no_update(self):
        result = lab.dynamic_selection([[True, True], [False, False]],
                                       requested=2, candidate_budget=2)
        self.assertFalse(result["update_possible"])
        self.assertFalse(result["full_batch"])

    def test_budget_and_complete_boolean_groups(self):
        for groups in ([[True]], [[]], [[0, 1]], [["true", False]]):
            with self.assertRaises(ValueError):
                lab.dynamic_selection(groups, requested=1, candidate_budget=2)
        for requested, budget in ((0, 1), (True, 2), (2, 1), (1, 2.0)):
            with self.assertRaises(ValueError):
                lab.dynamic_selection([], requested=requested, candidate_budget=budget)

    def test_overlong_boundaries(self):
        self.assertEqual([lab.overlong_penalty(n, max_tokens=100, cache=20)
                          for n in (0, 80, 90, 100, 110)], [0, 0, -.5, -1, -1])

    def test_overlong_invalid_units(self):
        for n, maximum, cache in ((True, 100, 20), (-1, 100, 20), (1, 0, 1),
                                   (1, 100, 101), (1, 100, 0), (1, 100.0, 20)):
            with self.assertRaises(ValueError):
                lab.overlong_penalty(n, max_tokens=maximum, cache=cache)

    def test_cli_example_finite_and_scope(self):
        result = json.loads(json.dumps(lab.examples(), allow_nan=False))
        self.assertEqual(result["reductions"]["sample_mean"], 1)
        self.assertEqual(result["partial_dynamic_batch"]["effective_groups"], 1)
        source = PATH.read_text()
        self.assertNotRegex(source, r"import (torch|pytrio|requests|httpx|datasets)")


if __name__ == "__main__":
    unittest.main()
