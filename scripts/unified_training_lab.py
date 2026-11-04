"""Original stdlib arithmetic, not an upstream trainer or model reproduction.

No network, weights, GPU, autograd, verifier, subprocess, or file writes.
"""

import json
import math


def real(value, lower=0.0, upper=None):
    if type(value) not in (int, float):
        raise ValueError("finite real numbers, not bool or strings, are required")
    try:
        value = float(value)
    except OverflowError as exc:
        raise ValueError("number is too large") from exc
    if not math.isfinite(value) or value < lower or (upper is not None and value > upper):
        raise ValueError("number outside the finite allowed range")
    return value


def integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("integer outside the allowed range")
    return value


def binary(values):
    if not values or any(type(value) is not int or value not in (0, 1) for value in values):
        raise ValueError("a nonempty sequence of binary integers is required")
    return values


def distribution(values):
    if not values:
        raise ValueError("empty distribution")
    values = [real(value, upper=1) for value in values]
    if not math.isclose(math.fsum(values), 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError("distribution must sum to one")
    return values


def success_target(probabilities, rewards):
    probabilities, rewards = distribution(probabilities), binary(rewards)
    if len(probabilities) != len(rewards):
        raise ValueError("shape mismatch")
    mass = math.fsum(p * r for p, r in zip(probabilities, rewards))
    if mass == 0:
        raise ValueError("success-conditioned target is undefined")
    return {"success_mass": mass,
            "target": [p * r / mass for p, r in zip(probabilities, rewards)]}


def response_weights(rewards):
    rewards = binary(rewards)
    count = sum(rewards)
    scale = len(rewards) / count if count else 0.0
    return [scale * reward for reward in rewards]


def finite_prompt_mass(success_probability, samples):
    p, samples = real(success_probability, upper=1), integer(samples, 1)
    if p in (0, 1) or samples == 1:
        return p
    return -math.expm1(samples * math.log1p(-p))


def pass_at_k(samples, correct, k):
    """Combinatorial estimator; not a guaranteed answer-selection mechanism."""
    samples = integer(samples, 1)
    correct, k = integer(correct), integer(k, 1)
    if correct > samples or k > samples:
        raise ValueError("counts exceed the sample pool")
    if samples - correct < k:
        return 1.0
    return 1 - math.comb(samples - correct, k) / math.comb(samples, k)


def loss_stats(nll, weights, target_mask):
    """Explicit target mask counts zero-weight responses but not prompts/pad."""
    if not (len(nll) == len(weights) == len(target_mask)):
        raise ValueError("shape mismatch")
    if any(type(value) is not bool for value in target_mask):
        raise ValueError("target mask must contain booleans")
    nll, weights = [real(value) for value in nll], [real(value) for value in weights]
    if any(weight != 0 and not target for weight, target in zip(weights, target_mask)):
        raise ValueError("non-target positions cannot carry learning weight")
    numerator = math.fsum(loss * weight for loss, weight in zip(nll, weights))
    if not math.isfinite(numerator):
        raise ValueError("weighted numerator overflow")
    denominator = sum(target_mask)
    return {"numerator": numerator, "denominator": denominator,
            "mean": numerator / denominator if denominator else None}


def pooled_mean(parts):
    if not parts:
        return None
    numerator = math.fsum(real(num) for num, den in parts)
    denominator = sum(integer(den) for num, den in parts)
    if any(den == 0 and num != 0 for num, den in parts):
        raise ValueError("positive numerator with no target positions")
    return numerator / denominator if denominator else None


def source_probabilities(token_fractions, mean_lengths):
    fractions = distribution(token_fractions)
    if len(fractions) != len(mean_lengths):
        raise ValueError("shape mismatch")
    lengths = [real(value) for value in mean_lengths]
    if any(length == 0 for length in lengths):
        raise ValueError("mean lengths must be positive")
    rates = [fraction / length for fraction, length in zip(fractions, lengths)]
    total = math.fsum(rates)
    if not math.isfinite(total) or total <= 0:
        raise ValueError("mixture rate overflow or underflow")
    return [rate / total for rate in rates]


def schedule(name, progress, average=0.005):
    t, a = real(progress, upper=1), real(average, upper=0.25)
    if name == "constant":
        return a
    if name == "decay":
        return 2 * a * (1 - t)
    if name == "growth":
        return 2 * a * t
    if name == "half":
        return max(0.0, 4 * a * (1 - 2 * t))
    raise ValueError("unknown schedule")


def dense_compute(parameters, pretrain, midtrain, rollout, mix):
    parameters = integer(parameters, 1)
    pretrain, midtrain, rollout, mix = map(integer, (pretrain, midtrain, rollout, mix))
    total = parameters * (6 * (pretrain + midtrain) + 8 * rollout + 6 * mix)
    return {"estimated_total_flops": total,
            "beyond_shared_pretrain_flops": total - 6 * parameters * pretrain}


def demo():
    parts = [(16, 2), (0, 3)]
    return {
        "conditional_target": success_target([0.6, 0.2, 0.2], [1, 0, 1]),
        "one_success_weights": response_weights([1, 0, 0, 0]),
        "three_success_weights": response_weights([1, 1, 1, 0]),
        "all_wrong_weights": response_weights([0, 0, 0, 0]),
        "finite_N4": [finite_prompt_mass(p, 4) for p in (0.25, 0.75)],
        "token_loss": loss_stats([99, 2, 2, 3, 3, 3], [0, 4, 4, 0, 0, 0],
                                 [False, True, True, True, True, True]),
        "pooled_microbatches": pooled_mean(parts),
        "unweighted_microbatch_means": (16 / 2 + 0 / 3) / 2,
        "half_tokens_row_probabilities": source_probabilities([0.5, 0.5], [2, 8]),
        "schedule_points": {name: [schedule(name, t) for t in (0, 0.25, 0.5, 0.75, 1)]
                            for name in ("constant", "decay", "growth", "half")},
        "sampled_pass_at_k": {str(k): pass_at_k(4, 1, k) for k in (1, 2, 4)},
        "compute_toy": dense_compute(1000, 100, 20, 30, 10),
    }


if __name__ == "__main__":
    print(json.dumps(demo(), ensure_ascii=False, indent=2, allow_nan=False))
