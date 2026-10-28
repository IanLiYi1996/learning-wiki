"""A one-dimensional teaching experiment. No network, hardware, or dependencies."""

import argparse
import json
import math
from pathlib import Path


def rollout(feedback: bool, disturbance: float = -0.25) -> list[dict]:
    """Record post-action states; apply the disturbance after step 12's action."""
    position = 0.0
    rows = []
    for step in range(1, 41):
        if feedback:
            command = max(-0.1, min(0.1, 0.5 * (1.0 - position)))
        else:
            command = 0.1 if step <= 10 else 0.0
        position += command
        if step == 12:
            position += disturbance
        rows.append({
            "step": step, "action": command, "position": position,
            "error": 1.0 - position,
        })
    return rows


def self_test():
    open_loop = rollout(False)
    closed_loop = rollout(True)
    assert math.isclose(open_loop[-1]["position"], 0.75, abs_tol=1e-12)
    assert abs(closed_loop[-1]["error"]) < 1e-8
    assert all(abs(row["action"]) <= 0.1 for row in closed_loop)
    assert closed_loop[12]["action"] > 0
    assert math.isclose(rollout(False, 0.0)[-1]["position"], 1.0, abs_tol=1e-12)
    assert abs(rollout(True, 0.0)[-1]["error"]) < 1e-8
    return open_loop, closed_loop


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Optional JSON experiment record.")
    args = parser.parse_args()
    open_loop, closed_loop = self_test()
    result = {
        "scope": "dimensionless teaching model; not a robot simulator",
        "state_update": "position_next = position + action + disturbance",
        "disturbance": {"step": 12, "amount": -0.25, "timing": "after action"},
        "feedback_gain": 0.5,
        "action_limit": 0.1,
        "tests": "passed",
        "open_loop_final": open_loop[-1],
        "closed_loop_final": closed_loop[-1],
        "selected_steps": [
            {"step": step,
             "open_loop_position": open_loop[step - 1]["position"],
             "feedback_position": closed_loop[step - 1]["position"]}
            for step in (10, 12, 13, 16, 40)
        ],
        "open_loop_trace": open_loop,
        "feedback_trace": closed_loop,
    }
    if args.output:
        args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    summary = {key: value for key, value in result.items() if not key.endswith("trace")}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
