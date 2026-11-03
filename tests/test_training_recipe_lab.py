import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest


PATH = Path(__file__).resolve().parents[1] / "scripts/training_recipe_lab.py"
SPEC = importlib.util.spec_from_file_location("training_recipe_lab", PATH)
lab = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = lab
SPEC.loader.exec_module(lab)


class CountsAndSampling(unittest.TestCase):
    def test_updates_do_not_multiply_generated_responses(self):
        self.assertEqual(lab.rollout_counts(256, 16, 2),
                         {"generated_responses": 4096, "valid_responses": 4096,
                          "optimizer_updates": 2})
        self.assertEqual(lab.rollout_counts(100, 4, 2, 20)["valid_responses"], 380)
        self.assertEqual(lab.rollout_counts(1, 1, 1, 1)["valid_responses"], 0)

    def test_invalid_counts(self):
        for args in ((0, 4, 2), (1, True, 1), (1, 1, 1, 2), (1, 1, 1, -1)):
            with self.assertRaises(ValueError):
                lab.rollout_counts(*args)

    def test_zero_observed_success_does_not_prove_impossibility(self):
        self.assertAlmostEqual(lab.zero_success_probability(.05, 16), .95 ** 16)
        self.assertAlmostEqual(lab.zero_success_probability(.1, 4), .6561)
        self.assertGreater(lab.zero_success_probability(.05, 16), .4)

    def test_probability_endpoints_and_large_counts(self):
        self.assertEqual(lab.zero_success_probability(0, 16), 1)
        self.assertEqual(lab.zero_success_probability(1, 16), 0)
        self.assertEqual(lab.zero_success_probability(.1, 10 ** 400), 0)

    def test_large_integer_conversion_does_not_imply_probability_underflow(self):
        self.assertAlmostEqual(lab.zero_success_probability(1e-310, 10 ** 310),
                               .36787944117144344, places=12)
        self.assertAlmostEqual(lab.zero_success_probability(1e-310, 10 ** 309),
                               math.exp(-.1), places=12)

    def test_invalid_probability_or_sample_selector(self):
        for probability, draws in ((math.nan, 4), (1.1, 4), (-.1, 4), (True, 4),
                                   (.1, 0), (.1, "16")):
            with self.assertRaises(ValueError):
                lab.zero_success_probability(probability, draws)


class MasksAndReplay(unittest.TestCase):
    def fixture(self):
        return ([11, 12, 13, 14], [11, 12, 13, 14], [False, True, False, True],
                [False, True, False, True], [None, -.2, None, -.8])

    def test_masked_and_unmasked_loss_are_different_targets(self):
        self.assertEqual(lab.masked_nll([-.1, -2, -.2, -3],
                                       [False, True, False, True]), 2.5)
        self.assertAlmostEqual(lab.masked_nll([-.1, -2, -.2, -3], [True] * 4), 1.325)

    def test_empty_loss_and_invalid_selector_are_not_silent(self):
        for logps, masks in (([], []), ([-1], [False]), ([-1], ["False"]),
                             ([1], [True]), ([math.nan], [True]), ([-1], [])):
            with self.assertRaises(ValueError):
                lab.masked_nll(logps, masks)

    def test_large_finite_loss_mean_does_not_overflow(self):
        self.assertEqual(lab.masked_nll([-1e308, -1e308], [True, True]), 1e308)

    def test_exact_token_replay(self):
        self.assertTrue(lab.replay_contract(*self.fixture()))
        args = self.fixture()
        args[1][2] = 99
        self.assertFalse(lab.replay_contract(*args))

    def test_different_length_is_not_identical_even_with_same_text_claim(self):
        args = self.fixture()
        args[1].pop()
        self.assertFalse(lab.replay_contract(*args))

    def test_environment_positions_cannot_be_training_actions(self):
        args = self.fixture()
        args[3][0] = True
        with self.assertRaises(ValueError):
            lab.replay_contract(*args)

    def test_model_action_can_be_masked_without_deleting_context(self):
        args = self.fixture()
        args[3][1] = False
        self.assertTrue(lab.replay_contract(*args))
        self.assertEqual(len(args[0]), 4)

    def test_context_placeholders_are_not_probabilities(self):
        args = self.fixture()
        args[4][0] = 0
        self.assertTrue(lab.replay_contract(*args))
        args[4][0] = -.2
        with self.assertRaises(ValueError):
            lab.replay_contract(*args)

    def test_missing_probability_invalid_token_or_alignment_is_rejected(self):
        for change in ("logprob", "token", "length", "selector"):
            args = self.fixture()
            if change == "logprob":
                args[4][1] = math.inf
            elif change == "token":
                args[0][1] = True
            elif change == "length":
                args[2].pop()
            else:
                args[2][1] = "True"
            with self.assertRaises(ValueError):
                lab.replay_contract(*args)


class FailureResourcesAndEvaluation(unittest.TestCase):
    def test_infrastructure_abort_is_not_zero_reward(self):
        self.assertEqual(lab.termination_contract("task_failed"),
                         {"valid_reward": True, "reward": 0})
        self.assertEqual(lab.termination_contract("infra_aborted"),
                         {"valid_reward": False, "reward": None})
        with self.assertRaises(ValueError):
            lab.termination_contract("timeout")

    def test_resource_units(self):
        self.assertEqual(lab.resource_days(64, 13), {"node_days": 832, "gpu_days": 6656})
        self.assertEqual(lab.resource_days(1, .5, 4), {"node_days": .5, "gpu_days": 2})

    def test_resource_invalid_inputs_and_overflow(self):
        for args in ((True, 13), (64, -1), (64, math.inf), (64, 13, 0), (64, 1e308)):
            with self.assertRaises(ValueError):
                lab.resource_days(*args)

    def test_large_counts_with_tiny_duration_can_have_finite_products(self):
        result = lab.resource_days(10 ** 309, 1e-309)
        self.assertAlmostEqual(result["node_days"], 1, places=12)
        self.assertAlmostEqual(result["gpu_days"], 8, places=12)
        result = lab.resource_days(1, 1e-309, 10 ** 309)
        self.assertAlmostEqual(result["gpu_days"], 1, places=12)

    def test_protocol_changes_are_named_not_attributed_to_weights(self):
        arguments = dict(task_version="v1", tools="fixed", simulator="A", judge="J",
                         decoding="temp=.7", budget="1K", samples=4,
                         aggregation="mean", context_management="full",
                         failure_policy="typed", evaluation_window="window-A",
                         search_locale="locale-A", leakage_filter="filter-v1")
        a = lab.EvalContract(**arguments)
        b = lab.EvalContract(**{**arguments, "simulator": "B", "aggregation": "any"})
        self.assertEqual(lab.protocol_differences(a, a), ())
        self.assertEqual(lab.protocol_differences(a, b), ("simulator", "aggregation"))
        c = lab.EvalContract(**{**arguments, "samples": 32})
        self.assertEqual(lab.protocol_differences(a, c), ("samples",))

    def test_web_window_and_error_scoring_belong_to_the_contract(self):
        arguments = dict(task_version="v1", tools="fixed", simulator="A", judge="J",
                         decoding="temp=.7", budget="1K", samples=4,
                         aggregation="mean", context_management="full",
                         failure_policy="retry-service-errors", evaluation_window="window-A",
                         search_locale="locale-A", leakage_filter="filter-v1")
        a = lab.EvalContract(**arguments)
        b = lab.EvalContract(**{**arguments, "failure_policy": "count-service-errors",
                               "evaluation_window": "window-B"})
        self.assertEqual(lab.protocol_differences(a, b),
                         ("failure_policy", "evaluation_window"))

    def test_incomplete_protocol_or_boolean_sample_count_is_rejected(self):
        arguments = dict(task_version="v1", tools="fixed", simulator="A", judge="J",
                         decoding="temp=.7", budget="1K", samples=4,
                         aggregation="mean", context_management="full",
                         failure_policy="typed", evaluation_window="window-A",
                         search_locale="locale-A", leakage_filter="filter-v1")
        for changed in ({"judge": ""}, {"samples": True}, {"samples": 0}):
            with self.assertRaises(ValueError):
                lab.EvalContract(**{**arguments, **changed})
        with self.assertRaises(ValueError):
            lab.protocol_differences({}, {})

    def test_cli_example_can_be_serialized_without_nonfinite_values(self):
        result = json.loads(json.dumps(lab.examples(), allow_nan=False))
        self.assertTrue(result["drift_rejected"])
        self.assertEqual(result["assistant_only_nll"], 2.5)
        self.assertEqual(result["protocol_differences"], ["simulator", "aggregation"])


if __name__ == "__main__":
    unittest.main()
