"""Check fictional arithmetic and its explicit teaching limitations."""

from decimal import Decimal
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "equity_perpetuals_lab", ROOT / "scripts/equity_perpetuals_lab.py"
)
LAB = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAB)


class ArithmeticTests(unittest.TestCase):
    def test_long_and_short_are_symmetric_before_costs(self):
        self.assertEqual(LAB.linear_pnl(10, 100, 105), Decimal(50))
        self.assertEqual(LAB.linear_pnl(-10, 100, 105), Decimal(-50))
        self.assertEqual(LAB.linear_pnl("0.1", "0.2", "0.3"), Decimal("0.01"))
        self.assertEqual(LAB.linear_pnl(10, 100, 100), 0)

    def test_funding_signs_and_reference_notional(self):
        self.assertEqual(LAB.funding_cashflow(100, 100, "0.00001"), Decimal("-0.1"))
        self.assertEqual(LAB.funding_cashflow(-100, 100, "0.00001"), Decimal("0.1"))
        self.assertEqual(LAB.funding_cashflow(100, 100, "-0.00001"), Decimal("0.1"))
        self.assertEqual(LAB.funding_cashflow(100, 100, 0), 0)
        self.assertEqual(LAB.funding_cashflow(100, 200, "0.00001"), Decimal("-0.2"))

    def test_funding_is_a_transfer_before_other_costs(self):
        for rate in ("0.003", "-0.002", "0"):
            self.assertEqual(
                LAB.funding_cashflow(7, 123, rate)
                + LAB.funding_cashflow(-7, 123, rate), 0
            )

    def test_maintenance_changes_with_mark_not_only_initial_margin(self):
        state = LAB.margin_status(1000, 100, 100, 93, "0.025")
        self.assertEqual(state["equity"], 300)
        self.assertEqual(state["maintenance"], Decimal("232.500"))
        self.assertEqual(state["status"], "AT_OR_ABOVE_MAINTENANCE")
        self.assertEqual(
            LAB.margin_status(1000, 100, 100, 92, "0.025")["status"],
            "BELOW_MAINTENANCE",
        )

    def test_funding_and_fees_can_cross_threshold_without_new_mark(self):
        for kwargs in ({"cumulative_funding": -100}, {"fees": 100}):
            state = LAB.margin_status(1000, 100, 100, 93, "0.025", **kwargs)
            self.assertEqual(state["equity"], 200)
            self.assertEqual(state["status"], "BELOW_MAINTENANCE")

    def test_equal_threshold_and_short_position(self):
        boundary = LAB.margin_status(100, 10, 100, 100, "0.1")
        self.assertEqual(boundary["status"], "AT_OR_ABOVE_MAINTENANCE")
        short = LAB.margin_status(1000, -100, 100, 108, "0.025")
        self.assertEqual(short["equity"], 200)
        self.assertEqual(short["maintenance"], 270)
        self.assertEqual(short["status"], "BELOW_MAINTENANCE")

    def test_basis_compression_not_stock_direction_drives_combined_pnl(self):
        for exit_price in (50, 100, 105, 200):
            with self.subTest(exit_price=exit_price):
                self.assertEqual(
                    LAB.basis_hedge(10, 100, 102, exit_price, exit_price)["net_pnl"], 20
                )
        self.assertEqual(LAB.basis_hedge(10, 100, 102, 100, 110)["net_pnl"], -80)
        self.assertEqual(LAB.basis_hedge(10, 100, 102, 105, 105, costs=25)["net_pnl"], -5)

    def test_dividend_example_is_not_perp_entitlement(self):
        self.assertEqual(LAB.stock_total_pnl(10, 100, 98, 2), 0)
        self.assertEqual(LAB.linear_pnl(10, 100, 98), -20)

    def test_simple_annualization_is_not_compounding(self):
        self.assertEqual(LAB.simple_annual_rate("0.00001", 1), Decimal("0.08760"))
        self.assertEqual(LAB.simple_annual_rate("0.00008", 8), Decimal("0.08760"))
        self.assertEqual(LAB.simple_annual_rate("-0.00001", 1), Decimal("-0.08760"))

    def test_fixture_documents_its_scope(self):
        data = LAB.examples()
        self.assertIn("NOT_A_TRADING_ENGINE", data["boundary"])
        self.assertEqual(
            data["B_10000_notional_0_001_percent_per_hour"]["constant_rate_cost_24_hours"],
            Decimal("2.4"),
        )


class InputTests(unittest.TestCase):
    def test_nonfinite_invalid_and_boolean_inputs_are_rejected(self):
        for value in (True, False, None, "abc", "NaN", "Infinity", float("-inf")):
            with self.subTest(value=value), self.assertRaises(ValueError):
                LAB.number(value, "input")

    def test_positive_inputs_and_nonzero_position_are_required(self):
        for call in (
            lambda: LAB.linear_pnl(0, 100, 105),
            lambda: LAB.linear_pnl(1, 0, 105),
            lambda: LAB.linear_pnl(1, 100, -1),
            lambda: LAB.funding_cashflow(1, 0, "0.01"),
            lambda: LAB.basis_hedge(-1, 100, 102, 105, 105),
            lambda: LAB.simple_annual_rate("0.01", 0),
            lambda: LAB.margin_status(0, 1, 100, 100, "0.1"),
        ):
            with self.subTest(call=call), self.assertRaises(ValueError):
                call()

    def test_negative_costs_and_impossible_maintenance_are_rejected(self):
        for call in (
            lambda: LAB.basis_hedge(1, 100, 102, 105, 105, costs=-1),
            lambda: LAB.stock_total_pnl(1, 100, 98, dividend_per_share=-1),
            lambda: LAB.margin_status(100, 1, 100, 100, "-0.1"),
            lambda: LAB.margin_status(100, 1, 100, 100, 1),
            lambda: LAB.margin_status(100, 1, 100, 100, "0.1", fees=-1),
        ):
            with self.subTest(call=call), self.assertRaises(ValueError):
                call()


if __name__ == "__main__":
    unittest.main()
