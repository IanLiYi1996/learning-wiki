"""Test toy contracts without executing real security or cloud operations."""
import ast
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts/security_foundations_lab.py"
spec = importlib.util.spec_from_file_location("security_foundations", PATH)
lab = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = lab
spec.loader.exec_module(lab)


class AuthorizationToyTests(unittest.TestCase):
    def test_owner_and_tenant_are_independent_checks(self):
        self.assertTrue(lab.same_owner_read("a", "x", "a", "x"))
        self.assertFalse(lab.same_owner_read("a", "x", "b", "x"))
        self.assertFalse(lab.same_owner_read("a", "x", "a", "y"))
        self.assertFalse(lab.same_owner_read("a", "x", "b", "y"))

    def test_missing_noncanonical_or_wrong_type_identifiers(self):
        for value in ("", " a", "a ", None, 1, True):
            for position in range(4):
                args = ["a", "x", "a", "x"]
                args[position] = value
                with self.subTest(value=value, position=position), self.assertRaises(ValueError):
                    lab.same_owner_read(*args)


class PaperApprovalTests(unittest.TestCase):
    def setUp(self):
        self.action = lab.Action("tenant-a", "export_summary", "order-demo", "v1", "archive-a")
        self.approval = lab.PaperApproval(lab.action_fingerprint(self.action), 10, 20)

    def test_match_is_for_review_not_execution(self):
        self.assertEqual(lab.compare_paper_approval(self.action, self.approval, 15),
                         "MATCH_FOR_REVIEW")

    def test_every_field_is_bound_and_change_requires_review(self):
        for field, value in [("tenant", "tenant-b"), ("verb", "update_order"),
                             ("object_id", "order-other"), ("version", "v2"),
                             ("destination", "archive-b")]:
            with self.subTest(field=field):
                changed = replace(self.action, **{field: value})
                self.assertNotEqual(lab.action_fingerprint(changed), self.approval.fingerprint)
                self.assertEqual(lab.compare_paper_approval(changed, self.approval, 15), "REAPPROVE")

    def test_start_inclusive_expiry_exclusive_and_future_approval(self):
        self.assertEqual(lab.compare_paper_approval(self.action, self.approval, 10), "MATCH_FOR_REVIEW")
        self.assertEqual(lab.compare_paper_approval(self.action, self.approval, 9), "REAPPROVE")
        self.assertEqual(lab.compare_paper_approval(self.action, self.approval, 20), "REAPPROVE")

    def test_bad_action_and_fingerprint(self):
        for action in (replace(self.action, verb="shell"), replace(self.action, tenant="")):
            with self.assertRaises(ValueError):
                lab.action_fingerprint(action)
        for fingerprint in ("", "a" * 63, "z" * 64, None):
            with self.assertRaises(ValueError):
                lab.compare_paper_approval(self.action, replace(self.approval, fingerprint=fingerprint), 15)

    def test_invalid_window_and_nonfinite_time(self):
        for approval in (replace(self.approval, expires_at=10),
                         replace(self.approval, issued_at=21)):
            with self.assertRaises(ValueError):
                lab.compare_paper_approval(self.action, approval, 15)
        for value in (-1, True, float("nan"), float("inf"), "15"):
            with self.assertRaises(ValueError):
                lab.compare_paper_approval(self.action, self.approval, value)


class RecoveryAndCoverageTests(unittest.TestCase):
    def test_recovery_goals_are_not_restore_job_success(self):
        record = lab.observed_recovery(120, 90, 190, 15, 60)
        self.assertEqual(record["data_window"], 30)
        self.assertEqual(record["recovery_delay"], 70)
        self.assertFalse(record["rpo_goal_met"])
        self.assertFalse(record["rto_goal_met"])

    def test_goal_equality_and_zero_window(self):
        self.assertTrue(lab.observed_recovery(120, 105, 180, 15, 60)["rpo_goal_met"])
        self.assertTrue(lab.observed_recovery(120, 105, 180, 15, 60)["rto_goal_met"])
        record = lab.observed_recovery(0, 0, 0, 0, 0)
        self.assertTrue(record["rpo_goal_met"])
        self.assertTrue(record["rto_goal_met"])

    def test_impossible_recovery_or_invalid_units(self):
        for args in ((120, 121, 190, 15, 60), (120, 90, 119, 15, 60)):
            with self.assertRaises(ValueError):
                lab.observed_recovery(*args)
        for value in (-1, float("nan"), float("inf"), True, "120"):
            for index in range(5):
                args = [120, 90, 190, 15, 60]
                args[index] = value
                with self.assertRaises(ValueError):
                    lab.observed_recovery(*args)

    def test_coverage_denominator_and_deduplication(self):
        result = lab.coverage(["a", "b", "c", "d", "a"], ["a", "b", "c"], ["a", "b"])
        self.assertEqual(result, {"eligible": 4, "collected": 3, "verified": 2,
                                  "verified_ratio": .5})
        self.assertIsNone(lab.coverage([], [], [])["verified_ratio"])

    def test_impossible_coverage_and_invalid_ids(self):
        for groups in ((["a"], ["b"], []), (["a"], [], ["a"]), ([""], [], [])):
            with self.assertRaises(ValueError):
                lab.coverage(*groups)

    def test_repeatable_demo_and_no_side_effect_imports(self):
        output = json.loads(subprocess.check_output([sys.executable, "-B", str(PATH)], text=True))
        self.assertIn("offline", output["notice"])
        self.assertEqual(output["paper_same"], "MATCH_FOR_REVIEW")
        self.assertFalse(output["owner_other_tenant"])
        self.assertEqual(output["coverage"]["verified_ratio"], .5)
        imports = set()
        for node in ast.walk(ast.parse(PATH.read_text())):
            if isinstance(node, ast.Import):
                imports.update(item.name for item in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module)
        self.assertEqual(imports, {"dataclasses", "hashlib", "hmac", "json", "math"})


if __name__ == "__main__":
    unittest.main()
