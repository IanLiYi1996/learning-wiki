"""Offline teaching models, not transaction encoding, signing, or production code."""

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import unittest

EXPECTED_SECONDS = 2016 * 600


def difficulty_after(old, actual_seconds):
    """Idealized difficulty, ignoring compact target rounding and powLimit."""
    if old <= 0 or actual_seconds <= 0:
        raise ValueError("Positive difficulty and elapsed time required")
    clamped = max(EXPECTED_SECONDS // 4, min(actual_seconds, EXPECTED_SECONDS * 4))
    return Fraction(old) * Fraction(EXPECTED_SECONDS, clamped)


def virtual_size(stripped_size, total_size):
    if not 0 <= stripped_size <= total_size:
        raise ValueError("Invalid serialized sizes")
    weight = stripped_size * 3 + total_size
    return (weight + 3) // 4


def to_units(text, decimals):
    if (
        not isinstance(text, str) or len(text) > 1000
        or not isinstance(decimals, int) or not 0 <= decimals <= 30
    ):
        raise ValueError("Use a decimal string and bounded integer decimals")
    try:
        value = Decimal(text)
    except InvalidOperation as error:
        raise ValueError("Invalid amount") from error
    if not value.is_finite() or value < 0:
        raise ValueError("Nonnegative finite amount required")
    # Exact tuple arithmetic avoids Decimal context rounding for large amounts.
    _, digits, exponent = value.as_tuple()
    if abs(exponent) > 1000:
        raise ValueError("Teaching model exponent is too large")
    coefficient = int("".join(map(str, digits)) or "0")
    shift = exponent + decimals
    if shift >= 0:
        if len(digits) + shift > 1000:
            raise ValueError("Teaching model amount is too large")
        return coefficient * 10 ** shift
    divisor = 10 ** (-shift)
    units, remainder = divmod(coefficient, divisor)
    if remainder:
        raise ValueError("Amount exceeds asset precision")
    return units


def execution_fee(gas_used, base_fee, priority_cap, max_fee):
    if min(gas_used, base_fee, priority_cap, max_fee) < 0 or max_fee < base_fee:
        raise ValueError("Ineligible fee parameters")
    return gas_used * min(max_fee, base_fee + priority_cap)


@dataclass
class NonceReservations:
    """Single-thread in-memory model; production needs atomic durable storage."""
    next_nonce: int
    request_nonce: dict = field(default_factory=dict)
    attempts: dict = field(default_factory=dict)

    def reserve(self, request):
        if request not in self.request_nonce:
            self.request_nonce[request] = self.next_nonce
            self.next_nonce += 1
        return self.request_nonce[request]

    def add_attempt(self, request, tx_hash):
        nonce = self.reserve(request)
        self.attempts.setdefault(request, set()).add(tx_hash)
        return nonce


@dataclass
class UtxoReservations:
    owners: dict = field(default_factory=dict)

    def reserve(self, outpoint, request):
        existing = self.owners.get(outpoint)
        if existing is not None and existing != request:
            raise ValueError("Outpoint already reserved")
        self.owners[outpoint] = request


@dataclass
class CreditBook:
    """Canonical-branch credits with an append-only teaching audit trail."""
    events: dict = field(default_factory=dict)
    journal: list = field(default_factory=list)

    @property
    def balance(self):
        return sum(item["amount"] for item in self.events.values() if item["active"])

    def observe(self, event_key, block_hash, amount):
        if amount < 0:
            raise ValueError("Negative credit")
        old = self.events.get(event_key)
        if old is not None and old["active"]:
            if old["block_hash"] != block_hash or old["amount"] != amount:
                raise ValueError("Conflicting canonical observation")
            return
        self.events[event_key] = {
            "block_hash": block_hash, "amount": amount, "active": True
        }
        self.journal.append(("credit", event_key, block_hash, amount))

    def rollback(self, orphaned_blocks):
        for key, item in self.events.items():
            if item["active"] and item["block_hash"] in orphaned_blocks:
                item["active"] = False
                self.journal.append(("reverse", key, item["block_hash"], -item["amount"]))


@dataclass
class Withdrawal:
    request_id: str
    raw_transaction: bytes
    transaction_id: str
    state: str = "SIGNED"

    def broadcast_timed_out(self):
        self.state = "BROADCAST_UNKNOWN"

    def retry_payload(self):
        if self.state not in {"SIGNED", "BROADCAST_UNKNOWN", "SUBMITTED"}:
            raise ValueError("Cannot rebroadcast in this state")
        return self.raw_transaction


class WorkbookTests(unittest.TestCase):
    def test_difficulty_faster(self):
        self.assertEqual(difficulty_after(100, EXPECTED_SECONDS // 2), 200)

    def test_difficulty_slower(self):
        self.assertEqual(difficulty_after(100, EXPECTED_SECONDS * 2), 50)

    def test_difficulty_clamp(self):
        self.assertEqual(difficulty_after(100, 1), 400)
        self.assertEqual(difficulty_after(100, EXPECTED_SECONDS * 10), 25)

    def test_difficulty_invalid(self):
        with self.assertRaises(ValueError):
            difficulty_after(100, 0)

    def test_vsize_and_rounding(self):
        self.assertEqual(virtual_size(100, 200), 125)
        self.assertEqual(virtual_size(100, 201), 126)

    def test_vsize_invalid(self):
        with self.assertRaises(ValueError):
            virtual_size(200, 100)

    def test_exact_token_units(self):
        self.assertEqual(to_units("12.345678", 6), 12_345_678)
        self.assertEqual(to_units("1.0000000", 6), 1_000_000)
        self.assertEqual(to_units("123456789012345678901234567890", 0),
                         123456789012345678901234567890)

    def test_excess_token_precision(self):
        with self.assertRaises(ValueError):
            to_units("0.0000001", 6)

    def test_invalid_token_amounts(self):
        for value in ("-1", "NaN", "Infinity", "oops", 0.1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                to_units(value, 6)

    def test_eip1559_effective_fee(self):
        gwei = 10 ** 9
        self.assertEqual(execution_fee(21000, 20 * gwei, 2 * gwei, 30 * gwei),
                         462_000 * gwei)
        self.assertEqual(execution_fee(21000, 20 * gwei, 2 * gwei, 21 * gwei),
                         441_000 * gwei)

    def test_fee_too_low(self):
        with self.assertRaises(ValueError):
            execution_fee(21000, 20, 2, 19)

    def test_nonce_idempotency_and_replacement(self):
        pool = NonceReservations(5)
        self.assertEqual(pool.reserve("request-a"), 5)
        self.assertEqual(pool.reserve("request-a"), 5)
        self.assertEqual(pool.reserve("request-b"), 6)
        self.assertEqual(pool.add_attempt("request-a", "tx1"), 5)
        self.assertEqual(pool.add_attempt("request-a", "tx2"), 5)
        self.assertEqual(pool.next_nonce, 7)

    def test_utxo_exclusivity(self):
        pool = UtxoReservations()
        pool.reserve(("teaching-network", "tx", 0), "request-a")
        pool.reserve(("teaching-network", "tx", 0), "request-a")
        with self.assertRaises(ValueError):
            pool.reserve(("teaching-network", "tx", 0), "request-b")

    def test_deposit_idempotency(self):
        book = CreditBook()
        key = ("teaching-network", "tx", 0)
        for _ in range(100):
            book.observe(key, "block-a", 100)
        self.assertEqual(book.balance, 100)
        self.assertEqual(len(book.journal), 1)

    def test_reorg_reversal_and_reinclusion(self):
        book = CreditBook()
        key = ("teaching-network", "tx", 0)
        book.observe(key, "old-branch", 100)
        book.rollback({"old-branch"})
        book.rollback({"old-branch"})
        self.assertEqual(book.balance, 0)
        book.observe(key, "new-branch", 100)
        book.observe(key, "new-branch", 100)
        self.assertEqual(book.balance, 100)
        self.assertEqual([entry[0] for entry in book.journal],
                         ["credit", "reverse", "credit"])

    def test_conflicting_event_rejected(self):
        book = CreditBook()
        key = ("teaching-network", "tx", 0)
        book.observe(key, "block-a", 100)
        with self.assertRaises(ValueError):
            book.observe(key, "block-b", 100)

    def test_uncertain_broadcast_reuses_payload(self):
        # Intentionally not a real encoded transaction.
        withdrawal = Withdrawal("request-a", b"teaching-bytes-only", "teaching-id")
        withdrawal.broadcast_timed_out()
        self.assertEqual(withdrawal.state, "BROADCAST_UNKNOWN")
        for _ in range(3):
            self.assertEqual(withdrawal.retry_payload(), b"teaching-bytes-only")
        self.assertEqual(withdrawal.transaction_id, "teaching-id")


if __name__ == "__main__":
    unittest.main(verbosity=2)
