"""Regression tests for the offline toy lab, not real diffusion experiments."""

import importlib.util
import math
from pathlib import Path
import sys
import unittest


PATH = Path(__file__).resolve().parents[1] / "scripts/diffusion_lab.py"
SPEC = importlib.util.spec_from_file_location("diffusion_lab", PATH)
lab = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = lab
SPEC.loader.exec_module(lab)


class PreferenceTests(unittest.TestCase):
    def test_equal_reference_is_half_probability(self):
        probability, loss = lab.dpo_pair(3, 3)
        self.assertEqual(probability, .5)
        self.assertAlmostEqual(loss, math.log(2))

    def test_sign_and_monotonicity(self):
        outcomes = [lab.dpo_pair(gap) for gap in (-2, 0, 2)]
        self.assertTrue(outcomes[0][0] < outcomes[1][0] < outcomes[2][0])
        self.assertTrue(outcomes[0][1] > outcomes[1][1] > outcomes[2][1])

    def test_beta_rescales_logit(self):
        self.assertEqual(lab.dpo_pair(2, 1, 3), lab.dpo_pair(3))

    def test_extreme_logits_are_finite(self):
        for gap in (-1000, 1000):
            probability, loss = lab.dpo_pair(gap)
            self.assertTrue(0 <= probability <= 1)
            self.assertTrue(math.isfinite(loss))
        self.assertEqual(lab.dpo_pair(-1000)[1], 1000)

    def test_invalid_preference_inputs(self):
        for values in ((math.nan, 0, 1), (0, math.inf, 1), (0, 0, 0), (0, 0, -1)):
            with self.assertRaises(ValueError):
                lab.dpo_pair(*values)


class RewardTests(unittest.TestCase):
    def test_population_std_and_zero_variance(self):
        self.assertEqual(lab.normalized([5, 5, 5]), (0, 0, 0))
        result = lab.normalized([0, 1, 2])
        self.assertAlmostEqual(result[0], -math.sqrt(1.5), places=6)
        self.assertAlmostEqual(sum(result), 0)

    def test_constant_large_fractional_rewards_have_no_false_advantage(self):
        for value in (100000000.1, 1e308, -1e308):
            self.assertEqual(lab.normalized([value] * 3), (0, 0, 0))

    def test_small_and_large_finite_rewards_do_not_underflow_or_overflow_std(self):
        self.assertEqual(lab.normalized([0, 1e-200], epsilon=1e-300), (-1, 1))
        self.assertEqual(lab.normalized([-1e308, 1e308]), (-1, 1))

    def test_scale_dominance_vs_channel_normalization(self):
        channels = [[0, 100, 200], [2, 1, 0]]
        raw = lab.combined_advantages(channels, [1, 1], per_channel=False)
        separate = lab.combined_advantages(channels, [1, 1])
        self.assertTrue(raw[-1] > 1)
        self.assertTrue(all(abs(value) < 1e-6 for value in separate))

    def test_positive_scale_invariance_up_to_epsilon(self):
        a = lab.normalized([0, 1, 2])
        b = lab.normalized([0, 100, 200])
        for left, right in zip(a, b):
            self.assertAlmostEqual(left, right, places=6)

    def test_gating_masks_without_renormalization(self):
        result = lab.combined_advantages([[0, 1, 2]], [1], gates=[True, True, False])
        self.assertLess(result[0], 0)
        self.assertEqual(result[2], 0)
        self.assertLess(sum(result), 0)

    def test_conflict_is_coordinate_specific_dot_product(self):
        self.assertTrue(lab.conflicting([1, 0], [-1, 0]))
        self.assertFalse(lab.conflicting([1, 0], [0, 1]))
        self.assertFalse(lab.conflicting([1, 1], [2, 2]))

    def test_reward_shapes_and_finiteness(self):
        for channels, weights in (([], []), ([[1], [2, 3]], [1, 1]),
                                  ([[math.nan]], [1]), ([[1]], [0])):
            with self.assertRaises(ValueError):
                lab.combined_advantages(channels, weights)
        with self.assertRaises(ValueError):
            lab.combined_advantages([[1, 2]], [1], gates=[True])
        with self.assertRaises(ValueError):
            lab.normalized([])

    def test_combined_intermediate_overflow_is_rejected(self):
        for channels, weights in (([[0, 1, 2]], [1.7e308]),
                                  ([[0, 1], [0, 1]], [1.7e308, 1.7e308])):
            with self.assertRaises(ValueError):
                lab.combined_advantages(channels, weights)

    def test_formula_selector_requires_an_actual_boolean(self):
        for selector in ("False", "True", 0, 1, None):
            with self.assertRaises(ValueError):
                lab.combined_advantages([[0, 1, 2]], [1], per_channel=selector)


class EstimationTests(unittest.TestCase):
    def test_roofline_units_and_bottlenecks(self):
        a = lab.roofline(10e12, 1e12, 100e12, 1e12)
        b = lab.roofline(10e12, .01e12, 100e12, 1e12)
        self.assertEqual((a.lower_bound_seconds, a.bottleneck), (1, "memory"))
        self.assertEqual((b.lower_bound_seconds, b.bottleneck), (.1, "compute"))
        self.assertEqual(a.arithmetic_intensity, 10)

    def test_peak_does_not_fix_memory_bound_example(self):
        self.assertEqual(lab.roofline(10e12, 1e12, 200e12, 1e12).lower_bound_seconds, 1)
        self.assertEqual(lab.roofline(10e12, .5e12, 100e12, 1e12).lower_bound_seconds, .5)

    def test_video_policies_are_explicit(self):
        self.assertEqual(lab.video_tokens(1280, 720, 16), (40, 22, 4, 3520))
        self.assertEqual(lab.video_tokens(1280, 720, 16, spatial_policy="ceil"),
                         (40, 23, 4, 3680))
        self.assertEqual(lab.video_tokens(1280, 720, 16, spatial_policy="ceil",
                                         time_policy="ceil"), (40, 23, 5, 4600))
        self.assertEqual(lab.video_tokens(32, 32, 1), (1, 1, 1, 1))

    def test_sparsity_only_reduces_connection_term(self):
        self.assertEqual(lab.attention_flops(100, 10), 480000)
        self.assertEqual(lab.attention_flops(100, 10, 4), 180000)
        self.assertEqual(lab.attention_flops(100, 10) / 4, 120000)

    def test_steps_cfg_and_layers_multiply_work_not_measured_time(self):
        base = lab.dit_flops(100, 10, 40, 1, 1)
        self.assertEqual(lab.dit_flops(100, 10, 40, 3, 4, cfg_branches=2), base * 24)
        # Sparse attention leaves FFN work intact.
        self.assertEqual(lab.dit_flops(100, 10, 40, 1, 1, sparsity=4), 340000)

    def test_GB_and_GiB_are_not_interchangeable(self):
        result = lab.weight_memory(14_000_000_000)
        self.assertEqual(result["GB"], 28)
        self.assertAlmostEqual(result["GiB"], 26.07703209)

    def test_invalid_estimator_settings(self):
        calls = (lambda: lab.roofline(1, 1, 0, 1),
                 lambda: lab.video_tokens(1, 1, 16),
                 lambda: lab.video_tokens(32, 32, 1, spatial_policy="round"),
                 lambda: lab.video_tokens(32.0, 32, 1),
                 lambda: lab.attention_flops(100, 10, .5),
                 lambda: lab.dit_flops(100, 10, 40, 1, 0),
                 lambda: lab.weight_memory(1, -2))
        for call in calls:
            with self.assertRaises(ValueError):
                call()

    def test_derived_nonfinite_capacity_or_runtime_is_rejected(self):
        for call in (lambda: lab.weight_memory(2, 1e308),
                     lambda: lab.roofline(1e308, 1, 1e-308, 1),
                     lambda: lab.dit_flops(100, 10, 40, 10 ** 308, 1)):
            with self.assertRaises(ValueError):
                call()


class OracleTests(unittest.TestCase):
    def test_correctness_gate_rejects_bad_fast_candidates(self):
        for result in ([.2, math.nan], [.2, math.inf], [.2], [.2, .8]):
            self.assertFalse(lab.oracle_accepts([.2, .4], result))
        self.assertTrue(lab.oracle_accepts([.2, .4], [.2, .4000001]))
        self.assertFalse(lab.oracle_accepts([], []))
        self.assertFalse(lab.oracle_accepts([math.nan], [math.nan]))

    def test_tolerance_boundary_and_reference_relative_error(self):
        self.assertTrue(lab.oracle_accepts([0], [1e-6], atol=1e-6, rtol=0))
        self.assertFalse(lab.oracle_accepts([0], [2e-6], atol=1e-6, rtol=0))
        with self.assertRaises(ValueError):
            lab.oracle_accepts([1], [1], atol=math.nan)

    def test_large_finite_values_cannot_bypass_oracle_via_overflow(self):
        self.assertFalse(lab.oracle_accepts([1e308], [-1e308], atol=0, rtol=1.8))
        self.assertFalse(lab.oracle_accepts([1e308], [-1e308], atol=1e308, rtol=.8))
        self.assertTrue(lab.oracle_accepts([1e308], [-1e308], atol=0, rtol=2))

    def test_example_output_is_finite_and_serializable(self):
        import json
        result = json.loads(json.dumps(lab.examples(), allow_nan=False))
        self.assertTrue(result["oracle_NaN_rejected"])
        self.assertEqual(result["video_floor"][-1], 3520)


if __name__ == "__main__":
    unittest.main()
