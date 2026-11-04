"""Deterministic teaching exercises. No model, network, subprocess, or file writes."""

import argparse
from dataclasses import dataclass
import json
import math
from statistics import mean


SCORES = (0.2, 0.1, 0.4, 0.3, 0.5, 0.2, 0.8, 0.6)
TARGETS = (-4, 4)
OFFSETS = {"forward": (1, 2, 3, 4), "two_sided": (-4, -2, 2, 4)}
REFERENCE = (0.2, 0.4)


def best_of(scores, budget):
    if isinstance(budget, bool) or not isinstance(budget, int) or not 1 <= budget <= len(scores):
        raise ValueError("budget must be an integer within the available candidates")
    if not all(math.isfinite(value) for value in scores[:budget]):
        raise ValueError("candidate scores must be finite")
    return max(scores[:budget])


def sampling_demo():
    return [{"budget": budget, "best_score": best_of(SCORES, budget)}
            for budget in (2, 4, 8)]


def task_score(position, target):
    return 10 - abs(position - target)


def compare_improver(start, strategy, targets=TARGETS):
    offsets = OFFSETS[strategy]
    if not targets:
        raise ValueError("at least one target is required")
    final, initial = [], []
    for target in targets:
        initial_score = task_score(start, target)
        # Baseline is supplied to both arms; four candidate evaluations per target.
        candidate_scores = [task_score(start + offset, target) for offset in offsets]
        final.append(max([initial_score] + candidate_scores))
        initial.append(initial_score)
    return {
        "start": start,
        "strategy": strategy,
        "candidate_evaluations_per_target": len(offsets),
        "initial_mean": mean(initial),
        "final_mean": mean(final),
        "mean_gain": mean(final) - mean(initial),
    }


def transfer_demo():
    return [compare_improver(start, strategy)
            for start in (0, 2) for strategy in OFFSETS]


@dataclass(frozen=True)
class Candidate:
    name: str
    values: tuple
    latency_ms: float
    evaluator: str = "fixed-v1"
    claimed_score: float = 0


def admission(candidate, reference=REFERENCE, max_latency_ms=200):
    if candidate.evaluator != "fixed-v1":
        return False, "评价合同被修改"
    if len(candidate.values) != len(reference):
        return False, "输出形状错误"
    if not all(math.isfinite(value) for value in candidate.values):
        return False, "输出含 NaN 或 Inf"
    if not math.isfinite(candidate.latency_ms) or not 0 < candidate.latency_ms <= max_latency_ms:
        return False, "时间记录不满足预算"
    if not all(abs(a - b) <= 1e-9 for a, b in zip(candidate.values, reference)):
        return False, "结果偏离参考容差"
    return True, "通过正确性与预算检查"


def select_candidate(candidates):
    records, accepted = [], []
    for candidate in candidates:
        passed, reason = admission(candidate)
        records.append({"name": candidate.name, "accepted": passed, "reason": reason})
        if passed:
            accepted.append(candidate)
    winner = min(accepted, key=lambda candidate: candidate.latency_ms) if accepted else None
    return {"checks": records, "winner": winner.name if winner else None}


def gates_demo():
    # Values and times are invented records, not measured runtime.
    candidates = [
        Candidate("valid_fast", REFERENCE, 80, claimed_score=1),
        Candidate("nan_fast", (0.2, float("nan")), 1, claimed_score=999),
        Candidate("wrong_fast", (0.2, 0.9), 1, claimed_score=999),
        Candidate("changed_judge", REFERENCE, 1, evaluator="modified", claimed_score=999),
        Candidate("over_budget", REFERENCE, 500, claimed_score=999),
    ]
    return select_candidate(candidates)


def all_demos():
    return {"sampling": sampling_demo(), "transfer": transfer_demo(), "gates": gates_demo()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Export synthetic records for tests")
    args = parser.parse_args()
    result = all_demos()
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return
    print("A. 固定生成器：预算变大不等于生成方法学习了")
    for row in result["sampling"]:
        print(f"  候选预算 {row['budget']}，最好分数 {row['best_score']:.1f}")
    print("B. 人工策略四格对照：每题四次候选评价，初始评分统一提供")
    for row in result["transfer"]:
        print(f"  起点 {row['start']} / {row['strategy']}: "
              f"最终均分 {row['final_mean']:.1f}，增益 {row['mean_gain']:.1f}")
    print("C. 假想候选：先验收，再按时间记录选择")
    for row in result["gates"]["checks"]:
        print(f"  {row['name']}: {row['reason']}")
    print(f"  保留：{result['gates']['winner']}")
    print("以上是原创教学记录，不是模型训练、论文复现或真实运行时间。")


if __name__ == "__main__":
    main()
