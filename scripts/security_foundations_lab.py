"""Fictional, offline security teaching; no IAM engine or real approval system.

Nothing reads credentials, calls networks, restores resources or executes tools.
SHA-256 below binds a paper record, not a signer identity or trusted approval.
"""
from dataclasses import asdict, dataclass, replace
import hashlib
import hmac
import json
import math


def identifier(value):
    if not isinstance(value, str) or not value or value != value.strip():
        raise ValueError("a nonempty canonical identifier is required")
    return value


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) \
            or not math.isfinite(value) or value < 0:
        raise ValueError("a finite nonnegative time is required")
    return value


def same_owner_read(user, tenant, stored_owner, stored_tenant):
    """Toy rule: metadata is assumed trusted/server-side; not an IAM policy."""
    for value in (user, tenant, stored_owner, stored_tenant):
        identifier(value)
    return user == stored_owner and tenant == stored_tenant


@dataclass(frozen=True)
class Action:
    tenant: str
    verb: str
    object_id: str
    version: str
    destination: str


@dataclass(frozen=True)
class PaperApproval:
    fingerprint: str
    issued_at: float
    expires_at: float


def action_fingerprint(action):
    for value in asdict(action).values():
        identifier(value)
    if action.verb not in {"export_summary", "update_order"}:
        raise ValueError("unknown toy action")
    payload = json.dumps(asdict(action), sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()


def compare_paper_approval(action, approval, now):
    """MATCH_FOR_REVIEW is never an approval to execute. No actor/signature check."""
    requested = action_fingerprint(action)
    number(now)
    issued, expires = number(approval.issued_at), number(approval.expires_at)
    if expires <= issued:
        raise ValueError("approval must have a positive validity window")
    if not isinstance(approval.fingerprint, str) or len(approval.fingerprint) != 64 \
            or any(char not in "0123456789abcdef" for char in approval.fingerprint):
        raise ValueError("invalid teaching fingerprint")
    if now < issued or now >= expires:
        return "REAPPROVE"
    if not hmac.compare_digest(requested, approval.fingerprint):
        return "REAPPROVE"
    return "MATCH_FOR_REVIEW"


def observed_recovery(incident, usable_point, business_validated, rpo_goal, rto_goal):
    """All values use one clock/unit; usable_point is a human-validated assumption."""
    for value in (incident, usable_point, business_validated, rpo_goal, rto_goal):
        number(value)
    if usable_point > incident or business_validated < incident:
        raise ValueError("impossible event ordering")
    data_window, recovery_delay = incident - usable_point, business_validated - incident
    return {"data_window": data_window, "recovery_delay": recovery_delay,
            "rpo_goal_met": data_window <= rpo_goal,
            "rto_goal_met": recovery_delay <= rto_goal}


def coverage(eligible, collected, rule_verified):
    """Asset-id sets, not alarm counts. An incomplete denominator invalidates use."""
    sets = [set(group) for group in (eligible, collected, rule_verified)]
    for group in sets:
        for asset in group:
            identifier(asset)
    eligible_set, collected_set, verified_set = sets
    if not collected_set <= eligible_set or not verified_set <= collected_set:
        raise ValueError("coverage sets must follow eligible -> collected -> verified")
    return {"eligible": len(eligible_set), "collected": len(collected_set),
            "verified": len(verified_set),
            "verified_ratio": len(verified_set) / len(eligible_set) if eligible_set else None}


def main():
    action = Action("tenant-a", "export_summary", "order-demo", "v1", "archive-a")
    approval = PaperApproval(action_fingerprint(action), 10, 20)
    print(json.dumps({
        "notice": "offline fiction: no account, request, authorization or restore executed",
        "owner_same_tenant": same_owner_read("user-a", "tenant-a", "user-a", "tenant-a"),
        "owner_other_tenant": same_owner_read("user-a", "tenant-a", "user-a", "tenant-b"),
        "paper_same": compare_paper_approval(action, approval, 15),
        "paper_version_changed": compare_paper_approval(replace(action, version="v2"), approval, 15),
        "paper_expired": compare_paper_approval(action, approval, 20),
        "recovery_minutes": observed_recovery(120, 90, 190, 15, 60),
        "coverage": coverage({"a", "b", "c", "d"}, {"a", "b", "c"}, {"a", "b"}),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
