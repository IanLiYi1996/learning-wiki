"""Offline teaching models, NOT a sandbox, security checker or cloud benchmark.

Only standard-library arithmetic and synthetic records; no exec, network,
containers, VMs, account access, privileged operations, or file writes.
"""

import argparse
from dataclasses import dataclass
import json
import math


REQUIRED = ("runtime", "egress", "identity", "cleanup")
TRANSITIONS = {
    "requested": {"provisioning", "terminated"},
    "provisioning": {"ready", "terminated"},
    "ready": {"running", "paused", "terminated"},
    "running": {"paused", "exporting", "terminated"},
    "paused": {"provisioning", "terminated"},
    "exporting": {"terminated"},
    "terminated": set(),
}


def finite_number(value, name, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{name} must be a finite number")
    try:
        valid = math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid or value < 0 or (positive and value == 0):
        raise ValueError(f"{name} is outside the teaching model's range")
    return value


def integer(value, name, *, positive=False):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if value < 0 or (positive and value == 0):
        raise ValueError(f"{name} is outside the teaching model's range")
    return value


def admit(evidence):
    """Only literal True is accepted; missing, unknown and truthy strings fail."""
    failed = [key for key in REQUIRED if evidence.get(key) is not True]
    return {"admitted": not failed, "failed_gates": failed}


def select(candidates):
    """Compare latency ONLY among synthetically admitted candidate records."""
    checks, accepted, names = [], [], set()
    for row in candidates:
        name = row["name"]
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError("Candidate names must be nonempty and unique")
        names.add(name)
        latency = finite_number(row["first_command_ms"], "latency", positive=True)
        result = admit(row["evidence"])
        checks.append({"name": name, **result})
        if result["admitted"]:
            accepted.append((latency, name))
    return {"winner": min(accepted)[1] if accepted else None, "checks": checks}


def admission_demo():
    return select([
        {"name": "fast_unverified", "first_command_ms": 20,
         "evidence": {"runtime": None, "egress": True, "identity": True, "cleanup": True}},
        {"name": "wide_egress", "first_command_ms": 40,
         "evidence": {"runtime": True, "egress": False, "identity": True, "cleanup": True}},
        {"name": "vetted_example", "first_command_ms": 150,
         "evidence": dict.fromkeys(REQUIRED, True)},
        {"name": "slower_vetted", "first_command_ms": 300,
         "evidence": dict.fromkeys(REQUIRED, True)},
    ])


def capacity(arrival_per_second, service_seconds, target_utilization,
             warm_slots, memory_mib):
    """Steady-state toy arithmetic, NOT a tail-latency or sizing guarantee."""
    rate = finite_number(arrival_per_second, "arrival rate")
    duration = finite_number(service_seconds, "service time")
    utilization = finite_number(target_utilization, "utilization", positive=True)
    if utilization > 1:
        raise ValueError("utilization must not exceed 1")
    warm = integer(warm_slots, "warm slots")
    memory = integer(memory_mib, "memory MiB", positive=True)
    mean = finite_number(rate * duration, "mean concurrency")
    adjusted = finite_number(mean / utilization, "adjusted concurrency")
    online = math.ceil(adjusted)
    total = online + warm
    return {
        "mean_in_service": mean,
        "online_slots": online,
        "warm_slots": warm,
        "total_slots": total,
        "slot_memory_mib": total * memory,
        "assumptions": "steady-state mean; excludes host/control-plane/failure overhead",
    }


@dataclass
class Session:
    """A mutable teaching record, NOT identity verification or token validation."""

    tenant: str
    policy: str
    generation: int = 1
    state: str = "requested"

    def __post_init__(self):
        if not isinstance(self.tenant, str) or not self.tenant.strip():
            raise ValueError("tenant must be nonempty")
        if not isinstance(self.policy, str) or not self.policy.strip():
            raise ValueError("policy must be nonempty")
        integer(self.generation, "generation", positive=True)
        if self.state not in TRANSITIONS:
            raise ValueError("unknown state")

    def advance(self, new_state):
        if new_state not in TRANSITIONS[self.state]:
            raise ValueError(f"Invalid transition: {self.state} -> {new_state}")
        # Resuming makes old connection generations stale in this teaching model.
        if self.state == "paused" and new_state == "provisioning":
            self.generation += 1
        self.state = new_state

    def allows(self, tenant, generation, policy):
        return (isinstance(generation, int) and not isinstance(generation, bool)
                and tenant == self.tenant and generation == self.generation
                and policy == self.policy and self.state in {"ready", "running"})


def lifecycle_demo():
    session = Session("tenant-a", "policy-1")
    checks = {"before_ready": session.allows("tenant-a", 1, "policy-1")}
    session.advance("provisioning")
    session.advance("ready")
    session.advance("running")
    checks["correct_context"] = session.allows("tenant-a", 1, "policy-1")
    checks["wrong_tenant"] = session.allows("tenant-b", 1, "policy-1")
    checks["wrong_policy"] = session.allows("tenant-a", 1, "policy-2")
    session.advance("paused")
    checks["while_paused"] = session.allows("tenant-a", 1, "policy-1")
    session.advance("provisioning")
    session.advance("ready")
    checks["stale_generation"] = session.allows("tenant-a", 1, "policy-1")
    checks["new_generation"] = session.allows("tenant-a", 2, "policy-1")
    session.advance("terminated")
    checks["after_termination"] = session.allows("tenant-a", 2, "policy-1")
    return {"checks": checks, "final_state": session.state,
            "generation": session.generation}


def demos():
    return {
        "scope": "synthetic offline teaching only; not real security or performance evidence",
        "admission": admission_demo(),
        "capacity": capacity(2, 30, 0.7, 10, 512),
        "lifecycle": lifecycle_demo(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print deterministic JSON")
    args = parser.parse_args()
    result = demos()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    else:
        print("教学模型：不创建 sandbox，不验证真实隔离。")
        print("硬门槛后的胜者:", result["admission"]["winner"])
        print("容量算术:", result["capacity"])
        print("状态／上下文检查:", result["lifecycle"])


if __name__ == "__main__":
    main()
