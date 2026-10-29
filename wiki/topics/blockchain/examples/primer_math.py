"""Offline checks for the illustrated primer's invented numbers.

No prices, RPC, wallets, signatures, credentials, or network requests.
These small arithmetic models are not exchange, lending, or wallet implementations.
"""

from decimal import Decimal
import unittest

D = Decimal


def fill_cost(asks, quantity):
    """Cost against a fixed, hypothetical order book, without fees."""
    if quantity <= 0:
        raise ValueError("Quantity must be positive")
    remaining, cost = quantity, D(0)
    for price, available in asks:
        if price <= 0 or available < 0:
            raise ValueError("Invalid hypothetical quote")
        taken = min(remaining, available)
        cost += taken * price
        remaining -= taken
        if remaining == 0:
            return cost
    raise ValueError("The fixed teaching book has insufficient depth")


def amm_out(a_reserve, u_reserve, sold_a):
    """Constant-product example with no fees and no rounding at execution."""
    if min(a_reserve, u_reserve, sold_a) <= 0:
        raise ValueError("Reserves and input must be positive")
    return u_reserve - a_reserve * u_reserve / (a_reserve + sold_a)


def health_factor(collateral, threshold, debt):
    """Single-collateral, fixed-threshold teaching model only."""
    if collateral < 0 or not D(0) < threshold <= D(1) or debt <= 0:
        raise ValueError("Invalid teaching inputs")
    return collateral * threshold / debt


class PrimerMathTests(unittest.TestCase):
    def test_utxo_amounts_and_fee(self):
        self.assertEqual(D("0.1000") - D("0.0300") - D("0.0699"), D("0.0001"))

    def test_toy_targets_include_the_boundary(self):
        self.assertEqual(sum(value <= 9 for value in range(10000)), 10)
        self.assertEqual(sum(value <= 19 for value in range(10000)), 20)
        self.assertEqual(D(10) / D(10000), D("0.001"))

    def test_reward_sources(self):
        self.assertEqual(D("3.125") + D("0.20"), D("3.325"))

    def test_gas_example(self):
        self.assertEqual(D(21000) * D(9) / D(10) ** 9, D("0.000189"))

    def test_fixed_orderbook_cost_and_average(self):
        asks = [(D(101), D(2)), (D(102), D(3)), (D(105), D(10))]
        cost = fill_cost(asks, D(4))
        self.assertEqual(cost, D(406))
        self.assertEqual(cost / D(4), D("101.5"))
        self.assertEqual(D(2) * D(101) - D(2) * D(99), D(4))

    def test_fixed_book_does_not_invent_liquidity(self):
        with self.assertRaises(ValueError):
            fill_cost([(D(101), D(2))], D(3))
        with self.assertRaises(ValueError):
            fill_cost([(D(101), D(2))], D(0))

    def test_valuation_is_price_times_a_named_supply(self):
        self.assertEqual(D(2) * D(1000000), D(2000000))
        self.assertEqual(D(2) * D(5000000), D(10000000))
        self.assertEqual(D(2) * D(10000000), D(20000000))
        self.assertEqual(D(3) * D(1000000) - D(2) * D(1000000), D(1000000))

    def test_amm_reserves_and_average(self):
        output = amm_out(D(100), D(10000), D(10))
        self.assertEqual(output.quantize(D("0.01")), D("909.09"))
        self.assertEqual((output / D(10)).quantize(D("0.01")), D("90.91"))
        new_u = D(10000) - output
        self.assertAlmostEqual(D(110) * new_u, D(1000000), places=20)
        self.assertGreater(amm_out(D(100), D(10000), D(1)), output / D(10))

    def test_amm_rejects_invalid_teaching_inputs(self):
        for inputs in [(D(0), D(100), D(10)), (D(100), D(-1), D(10)),
                       (D(100), D(100), D(0))]:
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                amm_out(*inputs)

    def test_health_factor_crosses_one(self):
        self.assertGreater(health_factor(D(1000), D("0.8"), D(600)), D(1))
        self.assertLess(health_factor(D(700), D("0.8"), D(600)), D(1))
        self.assertEqual(health_factor(D(750), D("0.8"), D(600)), D(1))

    def test_health_factor_rejects_invalid_inputs(self):
        for inputs in [(D(-1), D("0.8"), D(600)), (D(1000), D("1.1"), D(600)),
                       (D(1000), D("0.8"), D(0))]:
            with self.subTest(inputs=inputs), self.assertRaises(ValueError):
                health_factor(*inputs)

    def test_vault_share_conversion_without_fees(self):
        self.assertEqual(D(1100) / D(1000) * D(100), D(110))
        self.assertEqual(D(800) / D(1000) * D(100), D(80))

    def test_compounding_and_currency_result(self):
        value = D(1000) * D("1.01") ** 12
        self.assertEqual(value.quantize(D("0.01")), D("1126.83"))
        self.assertEqual((D(110) * D(8) / D(1000) - D(1)), D("-0.12"))
        self.assertEqual((D("0.005") * D(365) / D(7)).quantize(D("0.0001")),
                         D("0.2607"))

    def test_leverage_and_funding_examples(self):
        self.assertEqual(D(100) + D(10) * (D(96) - D(100)), D(60))
        self.assertEqual(D(100) + D(10) * (D(95) - D(100)), D(50))
        self.assertEqual(D(1000) * D("0.0001"), D("0.10"))

    def test_lightning_split_is_a_model_not_a_real_channel(self):
        before_a, before_b, payment = D("0.10"), D(0), D("0.03")
        after_a, after_b = before_a - payment, before_b + payment
        self.assertEqual(after_a, D("0.07"))
        self.assertEqual(after_b, D("0.03"))
        self.assertEqual(after_a + after_b, before_a + before_b)


if __name__ == "__main__":
    unittest.main(verbosity=2)
