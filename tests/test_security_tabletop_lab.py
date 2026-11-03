"""Pure standard-library tests; no real target, identity or cloud actions."""
import ast
from dataclasses import replace
from decimal import Decimal
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/security_tabletop_lab.py"
spec = importlib.util.spec_from_file_location("security_tabletop", PATH)
lab = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = lab
spec.loader.exec_module(lab)


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.clean = lab.Evidence("demo-v2", "demo-v2", True, True, "completed",
                                  "in_scope", True, 0, ())

    def test_ready_is_human_review_not_permission(self):
        result = lab.review_evidence(self.clean)
        self.assertEqual(result.decision, "RELEASE_REVIEW")
        self.assertIn("not_security_proof", result.reasons[0])

    def test_all_independent_blockers(self):
        for update, reason in [
            ({"authorized": False}, "authorization_missing"),
            ({"deployed_version": "demo-v1"}, "wrong_deployed_version"),
            ({"authentication_verified": False}, "authentication_unverified"),
            ({"run_state": "failed"}, "run_not_completed"),
            ({"run_state": "cancelled"}, "run_not_completed"),
            ({"run_state": "incomplete"}, "run_not_completed"),
            ({"scope": "scope_conflict"}, "scope_conflict"),
            ({"severities": ("HIGH",)}, "finding_at_threshold"),
            ({"severities": ("CRITICAL",)}, "finding_at_threshold"),
        ]:
            with self.subTest(update=update):
                result = lab.review_evidence(replace(self.clean, **update))
                self.assertEqual(result.decision, "BLOCK")
                self.assertIn(reason, result.reasons)

    def test_manual_paths_are_not_dynamic_security_proof(self):
        for update, reason in [
            ({"scope": "scoped_out"}, "no_dynamic_test_performed"),
            ({"coverage_recorded": False}, "coverage_not_recorded"),
            ({"unverified_count": 1}, "unverified_findings_pending"),
        ]:
            result = lab.review_evidence(replace(self.clean, **update))
            self.assertEqual(result.decision, "MANUAL_REVIEW")
            self.assertIn(reason, result.reasons)

    def test_blocks_do_not_get_downgraded_by_manual_item(self):
        result = lab.review_evidence(replace(self.clean, authorized=False, unverified_count=2))
        self.assertEqual(result.decision, "BLOCK")

    def test_medium_threshold_is_separate_from_human_risk_acceptance(self):
        evidence = replace(self.clean, severities=("MEDIUM",))
        self.assertEqual(lab.review_evidence(evidence).decision, "RELEASE_REVIEW")
        self.assertEqual(lab.review_evidence(evidence, "MEDIUM").decision, "BLOCK")

    def test_rejects_bad_status_type_and_counts(self):
        for update in [
            {"scope": "anything"}, {"run_state": "Succeeded"}, {"expected_version": ""},
            {"severities": ("UNKNOWN",)}, {"unverified_count": -1},
            {"unverified_count": True}, {"authorized": "false"},
            {"authentication_verified": 1}, {"coverage_recorded": None},
        ]:
            with self.subTest(update=update), self.assertRaises(ValueError):
                lab.review_evidence(replace(self.clean, **update))
        with self.assertRaises(ValueError):
            lab.review_evidence(self.clean, "NONE")

    def test_collects_multiple_reasons(self):
        result = lab.review_evidence(replace(self.clean, authorized=False,
                                            authentication_verified=False, run_state="failed"))
        self.assertEqual(len(result.reasons), 3)


class ToyCostTests(unittest.TestCase):
    def test_cumulative_parallel_work(self):
        self.assertEqual(lab.pentest_toy_fee([900, 900]), Decimal("25"))
        self.assertNotEqual(lab.pentest_toy_fee([900, 900]), Decimal("12.5"))

    def test_seconds_and_custom_rate(self):
        self.assertEqual(lab.pentest_toy_fee([1], "36"), Decimal(".01"))
        self.assertEqual(lab.pentest_toy_fee([]), Decimal(0))

    def test_code_first_tier_and_boundary(self):
        self.assertEqual(lab.code_toy_fee(1_500_000, 18), Decimal(480))
        self.assertEqual(lab.code_toy_fee(10_000_000, 0), Decimal(2000))
        self.assertEqual(lab.code_toy_fee(0, 0), Decimal(0))
        with self.assertRaises(ValueError):
            lab.code_toy_fee(10_000_001, 0)

    def test_rejects_negative_nonfinite_and_boolean_amounts(self):
        for value in [-1, "NaN", "Infinity", "-Infinity", True]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    lab.pentest_toy_fee([value])
                with self.assertRaises(ValueError):
                    lab.pentest_toy_fee([1], value)
                with self.assertRaises(ValueError):
                    lab.code_toy_fee(value, 1)
                with self.assertRaises(ValueError):
                    lab.code_toy_fee(1, value)

    def test_demo_output_is_offline_and_deterministic(self):
        import json
        output = subprocess.check_output([sys.executable, "-B", str(PATH)], text=True, cwd=ROOT)
        result = json.loads(output)
        self.assertIn("offline", result["notice"])
        self.assertEqual(result["ordinary_pentest_service_fee_usd"], "25.0")
        self.assertEqual(result["code_service_fee_usd"], "480.0")
        self.assertEqual(result["cases"]["green_but_failed"]["decision"], "BLOCK")

    def test_imports_have_no_sdk_network_or_shell_executor(self):
        imports = set()
        for node in ast.walk(ast.parse(PATH.read_text())):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module)
        self.assertEqual(imports, {"dataclasses", "decimal", "json"})


if __name__ == "__main__":
    unittest.main()
