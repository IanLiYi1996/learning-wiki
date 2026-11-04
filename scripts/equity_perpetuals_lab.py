"""Offline arithmetic for the equity-perpetuals learning topic.

Fictional inputs only. No network, account, order, price forecast, or replication
of a venue's complete margin engine. Decimal values keep money examples exact.
"""

from decimal import Decimal, InvalidOperation
import json


def number(value, name):
    """Accept finite decimal-like values, rejecting booleans and missing values."""
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{name} must be a finite number")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not result.is_finite():
        raise ValueError(f"{name} must be a finite number")
    return result


def positive(value, name):
    result = number(value, name)
    if result <= 0:
        raise ValueError(f"{name} must be positive")
    return result


def nonnegative(value, name):
    result = number(value, name)
    if result < 0:
        raise ValueError(f"{name} must be nonnegative")
    return result


def position(value):
    result = number(value, "quantity")
    if result == 0:
        raise ValueError("quantity must be nonzero (positive long, negative short)")
    return result


def linear_pnl(quantity, entry_price, exit_price):
    """Cash difference for a signed position, before fees and funding."""
    return position(quantity) * (
        positive(exit_price, "exit_price") - positive(entry_price, "entry_price")
    )


def funding_cashflow(quantity, oracle_price, period_rate):
    """Signed account cashflow; positive funding rate means longs pay shorts."""
    return -position(quantity) * positive(oracle_price, "oracle_price") * number(
        period_rate, "period_rate"
    )


def margin_status(
    initial_margin, quantity, entry_price, mark_price, maintenance_ratio,
    cumulative_funding=0, fees=0,
):
    """One isolated-position teaching model, not a real liquidation estimator."""
    ratio = nonnegative(maintenance_ratio, "maintenance_ratio")
    if ratio >= 1:
        raise ValueError("maintenance_ratio must be less than one")
    quantity = position(quantity)
    mark = positive(mark_price, "mark_price")
    equity = (
        positive(initial_margin, "initial_margin")
        + linear_pnl(quantity, entry_price, mark)
        + number(cumulative_funding, "cumulative_funding")
        - nonnegative(fees, "fees")
    )
    requirement = abs(quantity) * mark * ratio
    return {
        "equity": equity,
        "maintenance": requirement,
        "status": (
            "BELOW_MAINTENANCE" if equity < requirement
            else "AT_OR_ABOVE_MAINTENANCE"
        ),
    }


def basis_hedge(quantity, spot_entry, perp_entry, spot_exit, perp_exit, costs=0):
    """Long actual shares plus short equal equity units of a linear perpetual."""
    quantity = positive(quantity, "quantity")
    spot_pnl = linear_pnl(quantity, spot_entry, spot_exit)
    perp_pnl = linear_pnl(-quantity, perp_entry, perp_exit)
    return {
        "stock_pnl": spot_pnl,
        "perp_pnl": perp_pnl,
        "net_pnl": spot_pnl + perp_pnl - nonnegative(costs, "costs"),
    }


def stock_total_pnl(quantity, entry_price, exit_price, dividend_per_share=0):
    """Fictional cash stock return; no dividend tax or corporate-action engine."""
    quantity = positive(quantity, "quantity")
    return linear_pnl(quantity, entry_price, exit_price) + quantity * nonnegative(
        dividend_per_share, "dividend_per_share"
    )


def simple_annual_rate(period_rate, interval_hours):
    """Constant-rate, 365-day arithmetic. Not a yield forecast or compounded APY."""
    return number(period_rate, "period_rate") * Decimal(8760) / positive(
        interval_hours, "interval_hours"
    )


def examples():
    return {
        "boundary": "FICTIONAL_OFFLINE_ARITHMETIC_NOT_A_TRADING_ENGINE",
        "A_10_units_100_to_105": {
            "long_pnl": linear_pnl(10, 100, 105),
            "short_pnl": linear_pnl(-10, 100, 105),
        },
        "B_10000_notional_0_001_percent_per_hour": {
            "long_cashflow_per_hour": funding_cashflow(100, 100, "0.00001"),
            "short_cashflow_per_hour": funding_cashflow(-100, 100, "0.00001"),
            "constant_rate_cost_24_hours": -funding_cashflow(
                100, 100, "0.00001"
            ) * 24,
            "simple_annual_rate": simple_annual_rate("0.00001", 1),
        },
        "C_1000_margin_100_units": {
            "mark_100": margin_status(1000, 100, 100, 100, "0.025"),
            "mark_93": margin_status(1000, 100, 100, 93, "0.025"),
            "mark_92": margin_status(1000, 100, 100, 92, "0.025"),
            "mark_93_after_100_funding_cost": margin_status(
                1000, 100, 100, 93, "0.025", cumulative_funding=-100
            ),
        },
        "D_basis_2_to_0_and_2_to_10": {
            "both_exit_at_105": basis_hedge(10, 100, 102, 105, 105),
            "stock_100_perp_110": basis_hedge(10, 100, 102, 100, 110),
        },
        "E_fictional_ex_dividend_100_to_98": {
            "stock_including_2_dividend": stock_total_pnl(10, 100, 98, 2),
            "unadjusted_perp_price_pnl": linear_pnl(10, 100, 98),
        },
    }


if __name__ == "__main__":
    print(json.dumps(examples(), ensure_ascii=False, indent=2, default=str))
