"""Offline teaching only: paper evidence checks and toy service fee arithmetic.

No AWS API, credentials, network, target requests, IAM evaluation or deployment.
This is deliberately stricter than a product gate and is not its implementation.
"""

from dataclasses import dataclass
from decimal import Decimal
import json


@dataclass(frozen=True)
class Evidence:
    expected_version: str
    deployed_version: str
    authorized: bool
    authentication_verified: bool
    run_state: str
    scope: str
    coverage_recorded: bool
    unverified_count: int
    severities: tuple[str, ...]


@dataclass(frozen=True)
class Verdict:
    decision: str
    reasons: tuple[str, ...]


SEVERITIES = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


def review_evidence(evidence: Evidence, threshold: str = "HIGH") -> Verdict:
    """Classify fictional records; RELEASE_REVIEW is not permission to release."""
    if threshold not in SEVERITIES:
        raise ValueError("unknown threshold")
    if evidence.run_state not in {"completed", "failed", "cancelled", "incomplete"}:
        raise ValueError("unknown run_state")
    if evidence.scope not in {"in_scope", "scoped_out", "scope_conflict"}:
        raise ValueError("unknown scope")
    if not evidence.expected_version or not evidence.deployed_version:
        raise ValueError("version identifiers are required")
    if type(evidence.unverified_count) is not int or evidence.unverified_count < 0:
        raise ValueError("unverified_count must be a nonnegative integer")
    for field in ("authorized", "authentication_verified", "coverage_recorded"):
        if type(getattr(evidence, field)) is not bool:
            raise ValueError(f"{field} must be a boolean")
    if any(value not in SEVERITIES for value in evidence.severities):
        raise ValueError("unknown severity")
    blocked = []
    if not evidence.authorized:
        blocked.append("authorization_missing")
    if evidence.expected_version != evidence.deployed_version:
        blocked.append("wrong_deployed_version")
    if not evidence.authentication_verified:
        blocked.append("authentication_unverified")
    if evidence.run_state != "completed":
        blocked.append("run_not_completed")
    if evidence.scope == "scope_conflict":
        blocked.append("scope_conflict")
    if any(SEVERITIES[value] >= SEVERITIES[threshold] for value in evidence.severities):
        blocked.append("finding_at_threshold")
    if blocked:
        return Verdict("BLOCK", tuple(blocked))
    pending = []
    if evidence.scope == "scoped_out":
        pending.append("no_dynamic_test_performed")
    if not evidence.coverage_recorded:
        pending.append("coverage_not_recorded")
    if evidence.unverified_count:
        pending.append("unverified_findings_pending")
    if pending:
        return Verdict("MANUAL_REVIEW", tuple(pending))
    return Verdict("RELEASE_REVIEW", ("evidence_ready_for_human_review_not_security_proof",))


def _decimal(value) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("boolean is not an amount")
    number = Decimal(str(value))
    if not number.is_finite() or number < 0:
        raise ValueError("amount must be finite and nonnegative")
    return number


def pentest_toy_fee(task_seconds, hourly_rate="50") -> Decimal:
    """No trial/discount/taxes/resources; cumulative task work, not wall clock."""
    total = sum((_decimal(value) for value in task_seconds), Decimal(0))
    return total / Decimal(3600) * _decimal(hourly_rate)


def code_toy_fee(protected_loc, ciu) -> Decimal:
    """Only the first <=10 million LOC tier; input is assumed billed usage."""
    lines, units = _decimal(protected_loc), _decimal(ciu)
    if lines > Decimal(10_000_000):
        raise ValueError("higher tiers are outside this toy")
    return lines / Decimal(1_000_000) * Decimal(200) + units * Decimal(10)


def main():
    clean = Evidence("demo-v2", "demo-v2", True, True, "completed",
                     "in_scope", True, 0, ())
    from dataclasses import replace
    cases = {
        "complete_record": clean,
        "green_but_failed": replace(clean, run_state="failed"),
        "scoped_out": replace(clean, scope="scoped_out"),
        "wrong_version": replace(clean, deployed_version="demo-v1"),
        "hidden_unverified": replace(clean, unverified_count=1),
    }
    results = {name: {"decision": verdict.decision, "reasons": verdict.reasons}
               for name, evidence in cases.items()
               for verdict in (review_evidence(evidence),)}
    print(json.dumps({
        "notice": "offline fictional evidence; no tests or release actions performed",
        "cases": results,
        "ordinary_pentest_service_fee_usd": str(pentest_toy_fee([900, 900])),
        "code_service_fee_usd": str(code_toy_fee(1_500_000, 18)),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
