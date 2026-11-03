"""CPU/stdlib teaching calculations; no SDK, model, network or training."""

import json
import math
from statistics import mean, stdev


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Expected a finite real number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError("Number outside supported range") from exc
    if not math.isfinite(result):
        raise ValueError("Expected a finite real number")
    return result


def positive_int(value):
    if type(value) is not int or value < 1:
        raise ValueError("Expected a positive integer")
    return value


def numbers(values):
    result = tuple(finite(value) for value in values)
    if not result:
        raise ValueError("Empty sequence")
    return result


def group_advantages(rewards, *, standardize=False, epsilon=1e-8):
    """Centered or sample-standardized relative reward, not causal credit."""
    rewards = numbers(rewards)
    if type(standardize) is not bool:
        raise ValueError("standardize must be boolean")
    epsilon = finite(epsilon)
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    center = mean(rewards)
    centered = tuple(finite(value - center) for value in rewards)
    if not standardize:
        return centered
    spread = stdev(rewards) if len(rewards) > 1 else 0.0
    if spread == 0:
        return (0.0,) * len(rewards)
    denominator = finite(spread + epsilon)
    return tuple(finite(value / denominator) for value in centered)


def clipped_signal(log_ratio, advantage, *, method="ppo", low=.8, high=1.2):
    """Return loss and dloss/dcurrent_logprob away from clipping boundaries.

    CISPO's detached multiplier is held fixed during differentiation.
    """
    log_ratio, advantage = finite(log_ratio), finite(advantage)
    low, high = finite(low), finite(high)
    if not 0 < low <= 1 <= high:
        raise ValueError("Ratio bounds must contain one and be positive")
    if method not in {"is", "ppo", "cispo"}:
        raise ValueError("Unknown objective")
    try:
        ratio = math.exp(log_ratio)
    except OverflowError as exc:
        raise ValueError("Ratio overflow") from exc
    ratio = finite(ratio)
    clipped = min(high, max(low, ratio))
    if method == "cispo":
        # Set old logprob to zero for this toy; does not change the derivative.
        return {"loss": finite(-clipped * advantage * log_ratio),
                "gradient": finite(-clipped * advantage), "ratio": ratio}
    objective = finite(ratio * advantage)
    is_clipped = method == "ppo" and clipped * advantage < objective
    return {"loss": finite(-clipped * advantage if is_clipped else -objective),
            "gradient": 0.0 if is_clipped else finite(-objective),
            "ratio": ratio}


def reductions(sequence_losses):
    """Each sequence nonempty; one answer per weight versus one token per weight."""
    rows = tuple(numbers(row) for row in sequence_losses)
    if not rows:
        raise ValueError("Empty batch")
    return {"sample_mean": finite(mean(mean(row) for row in rows)),
            "token_mean": finite(mean(value for row in rows for value in row))}


def gspo_ratio(current_logprobs, old_logprobs):
    current, old = numbers(current_logprobs), numbers(old_logprobs)
    if len(current) != len(old):
        raise ValueError("Token/logprob alignment mismatch")
    if any(value > 0 for value in current + old):
        raise ValueError("Logprob cannot be positive")
    difference = mean(finite(a - b) for a, b in zip(current, old))
    try:
        return finite(math.exp(difference))
    except OverflowError as exc:
        raise ValueError("Ratio overflow") from exc


def sequence_loss(objectives, *, normalization_sequences):
    """Zero contributions may be omitted from compute, not from the denominator."""
    size = positive_int(normalization_sequences)
    values = tuple(finite(value) for value in objectives)
    if len(values) > size:
        raise ValueError("Original denominator cannot be smaller than active batch")
    # Scale first to avoid overflow on finite, same-sign objectives.
    return finite(-math.fsum(value / size for value in values))


def dynamic_selection(correctness_groups, *, requested, candidate_budget):
    """Original toy with a finite candidate stream; no reward shaping is used."""
    requested, candidate_budget = positive_int(requested), positive_int(candidate_budget)
    if candidate_budget < requested:
        raise ValueError("Candidate budget must cover requested groups")
    selected, consumed = [], 0
    for group in correctness_groups:
        if consumed == candidate_budget or len(selected) == requested:
            break
        group = tuple(group)
        if len(group) < 2 or any(type(value) is not bool for value in group):
            raise ValueError("Need a complete boolean group of at least two candidates")
        consumed += 1
        if any(group) and not all(group):
            selected.append(group)
    return {"candidate_groups": consumed, "effective_groups": len(selected),
            "update_possible": bool(selected), "full_batch": len(selected) == requested}


def overlong_penalty(tokens, *, max_tokens, cache):
    max_tokens, cache = positive_int(max_tokens), positive_int(cache)
    if type(tokens) is not int or tokens < 0 or cache > max_tokens:
        raise ValueError("Invalid length parameters")
    start = max_tokens - cache
    if tokens <= start:
        return 0.0
    return -1.0 if tokens >= max_tokens else -(tokens - start) / cache


def examples():
    return {
        "centered": group_advantages([1, 1, 0, 0]),
        "sample_standardized": group_advantages([1, 1, 0, 0], standardize=True),
        "all_success": group_advantages([1, 1, 1, 1], standardize=True),
        "ppo_positive": clipped_signal(math.log(1.4), 1),
        "ppo_negative": clipped_signal(math.log(1.4), -1),
        "cispo_positive": clipped_signal(math.log(1.4), 1, method="cispo"),
        "reductions": reductions([[2], [0, 0, 0]]),
        "geometric_ratio": gspo_ratio(
            [-2 + math.log(1.2), -2 + math.log(.8)], [-2, -2]),
        "original_denominator_loss": sequence_loss([1, -1, 1], normalization_sequences=8),
        "active_only_loss": sequence_loss([1, -1, 1], normalization_sequences=3),
        "partial_dynamic_batch": dynamic_selection(
            [[True, True], [False, False], [True, False], [True, True]],
            requested=2, candidate_budget=4),
        "length_penalty": [overlong_penalty(tokens, max_tokens=100, cache=20)
                           for tokens in (80, 90, 100, 110)],
    }


if __name__ == "__main__":
    print(json.dumps(examples(), ensure_ascii=False, indent=2, allow_nan=False))
