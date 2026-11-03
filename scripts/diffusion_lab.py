"""Offline teaching arithmetic, not a diffusion trainer or hardware benchmark.

Python standard library only. No network, file writes, weights, or GPU calls.
All units are explicit; inputs are validated to keep examples reproducible.
"""

from dataclasses import dataclass
import json
import math


def finite(value, label="value", *, minimum=None, positive=False):
    try:
        valid = math.isfinite(value)
    except OverflowError as error:
        raise ValueError(f"{label} exceeds floating-point range") from error
    if not valid:
        raise ValueError(f"{label} must be finite")
    if positive and value <= 0:
        raise ValueError(f"{label} must be positive")
    if minimum is not None and value < minimum:
        raise ValueError(f"{label} must be >= {minimum}")
    return value


def finite_sum(values, label):
    """Reject intermediate overflow instead of returning a misleading score."""
    values = tuple(finite(value, label) for value in values)
    try:
        return finite(math.fsum(values), label)
    except OverflowError as error:
        raise ValueError(f"{label} exceeds floating-point range") from error


def integer(value, label="value", *, minimum=1):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{label} must be an integer >= {minimum}")
    return value


def sigmoid(value):
    """Stable logistic function, including large positive/negative logits."""
    finite(value)
    if value >= 0:
        return 1 / (1 + math.exp(-value))
    exp = math.exp(value)
    return exp / (1 + exp)


def dpo_pair(current_gap, reference_gap=0.0, beta=1.0):
    """Scalar toy log-probability gaps; NOT denoising-error likelihoods."""
    finite(current_gap, "current gap")
    finite(reference_gap, "reference gap")
    finite(beta, "beta", positive=True)
    logit = finite(beta * (current_gap - reference_gap), "logit")
    loss = max(0.0, -logit) + math.log1p(math.exp(-abs(logit)))
    return sigmoid(logit), loss


def normalized(values, epsilon=1e-8):
    """Population standard deviation plus epsilon; constant group => zeros."""
    values = tuple(values)
    if not values:
        raise ValueError("empty group")
    for value in values:
        finite(value, "reward")
    finite(epsilon, "epsilon", positive=True)
    if all(value == values[0] for value in values):
        return (0.0,) * len(values)
    # Rescale before centering/squaring: avoid sum overflow, squared-deviation
    # underflow, and a rounded nonzero advantage for an exactly constant group.
    scale = max(abs(value) for value in values)
    scaled = tuple(value / scale for value in values)
    mean = math.fsum(scaled) / len(scaled)
    centered = tuple(value - mean for value in scaled)
    std = math.hypot(*centered) / math.sqrt(len(centered))
    denominator = std + epsilon / scale
    if denominator == 0:
        return (0.0,) * len(values)
    return tuple(finite(value / denominator, "advantage") for value in centered)


def combined_advantages(channels, weights, *, per_channel=True, gates=None):
    """Illustrate normalization order and optional hard gates, not GDPO/DAPO.

    Each channel is a reward vector for the SAME ordered group of candidates.
    Gates mask the final advantage; no implicit second normalization.
    """
    channels = tuple(tuple(channel) for channel in channels)
    weights = tuple(weights)
    if type(per_channel) is not bool:
        raise ValueError("per_channel must be a boolean")
    if not channels or len(channels) != len(weights):
        raise ValueError("one weight per nonempty channel")
    count = len(channels[0])
    if not count or any(len(channel) != count for channel in channels):
        raise ValueError("channels must have the same nonzero length")
    for weight in weights:
        finite(weight, "weight", minimum=0)
    if not any(weights):
        raise ValueError("at least one positive weight")
    for channel in channels:
        for value in channel:
            finite(value, "reward")
    signals = tuple(normalized(channel) for channel in channels) if per_channel else channels
    result = tuple(finite_sum((weight * signal[i] for weight, signal in zip(weights, signals)),
                             "combined advantage")
                   for i in range(count))
    if not per_channel:
        result = normalized(result)
    if gates is not None:
        gates = tuple(gates)
        if len(gates) != count or any(type(gate) is not bool for gate in gates):
            raise ValueError("gates must be one boolean per candidate")
        result = tuple(value if gate else 0.0 for value, gate in zip(result, gates))
    return result


def conflicting(left, right):
    """Negative dot product in a toy shared parameter coordinate system."""
    left, right = tuple(left), tuple(right)
    if not left or len(left) != len(right):
        raise ValueError("matching nonempty directions required")
    for value in (*left, *right):
        finite(value, "direction")
    return finite_sum((a * b for a, b in zip(left, right)), "direction dot product") < 0


@dataclass(frozen=True)
class Roofline:
    compute_seconds: float
    memory_seconds: float
    lower_bound_seconds: float
    arithmetic_intensity: float
    bottleneck: str


def roofline(flops, traffic_bytes, peak_flops_s, bandwidth_bytes_s):
    for value, label in ((flops, "FLOPs"), (traffic_bytes, "traffic bytes")):
        finite(value, label, positive=True)
    finite(peak_flops_s, "peak FLOP/s", positive=True)
    finite(bandwidth_bytes_s, "bandwidth bytes/s", positive=True)
    compute = finite(flops / peak_flops_s, "compute seconds")
    memory = finite(traffic_bytes / bandwidth_bytes_s, "memory seconds")
    intensity = finite(flops / traffic_bytes, "arithmetic intensity")
    return Roofline(compute, memory, max(compute, memory), intensity,
                    "balanced" if compute == memory else
                    "memory" if memory > compute else "compute")


def video_tokens(width, height, frames, *, spatial=16, patch=2, temporal=4,
                 spatial_policy="floor", time_policy="floor"):
    """Calculator floor convention vs explicit padding/coverage alternatives.

    Neither policy is asserted to reproduce a real model's encoder exactly.
    """
    for value in (width, height, frames, spatial, patch, temporal):
        integer(value)
    if spatial_policy not in ("floor", "ceil") or time_policy not in ("floor", "ceil"):
        raise ValueError("policy must be floor or ceil")
    divisor = spatial * patch
    if spatial_policy == "floor":
        nw, nh = width // divisor, height // divisor
    else:
        nw, nh = (width + divisor - 1) // divisor, (height + divisor - 1) // divisor
    nt = 1 + ((frames - 1) // temporal if time_policy == "floor" else
              (frames - 1 + temporal - 1) // temporal)
    if nw == 0 or nh == 0:
        raise ValueError("floor policy produced an empty spatial grid")
    return nw, nh, nt, nw * nh * nt


def attention_flops(tokens, dim, sparsity=1.0):
    """Two FLOPs per MAC; only attention connections are sparsified."""
    integer(tokens)
    integer(dim)
    finite(sparsity, "sparsity", minimum=1)
    return finite(8 * tokens * dim ** 2 + 4 * tokens ** 2 * dim / sparsity,
                  "attention FLOPs")


def dit_flops(tokens, dim, ff_dim, layers, steps, *, cfg_branches=1,
              sparsity=1.0, cross_flops_per_layer=0.0):
    for value in (ff_dim, layers, steps, cfg_branches):
        integer(value)
    finite(cross_flops_per_layer, "cross-attention FLOPs", minimum=0)
    per_layer = (attention_flops(tokens, dim, sparsity) +
                 4 * tokens * dim * ff_dim + cross_flops_per_layer)
    return finite(per_layer * layers * steps * cfg_branches, "total DiT FLOPs")


def weight_memory(parameters, bytes_per_weight=2):
    """Raw weight capacity only, no activations, metadata or optimizer."""
    integer(parameters)
    finite(bytes_per_weight, "bytes per weight", positive=True)
    size = finite(parameters * bytes_per_weight, "raw weight bytes", positive=True)
    return {"bytes": size, "GB": size / 1e9, "GiB": size / 2 ** 30}


def oracle_accepts(reference, candidate, *, atol=1e-6, rtol=1e-5):
    """Flat-output correctness gate; speed is intentionally not an input."""
    reference, candidate = tuple(reference), tuple(candidate)
    finite(atol, "absolute tolerance", minimum=0)
    finite(rtol, "relative tolerance", minimum=0)
    if not reference or len(reference) != len(candidate):
        return False
    if not all(math.isfinite(value) for value in (*reference, *candidate)):
        return False
    def within_tolerance(a, b):
        # Common scaling keeps both the difference and tolerance finite.
        # Otherwise large finite values can turn this test into inf <= inf.
        scale = max(abs(a), abs(b), atol)
        return scale == 0 or abs(a / scale - b / scale) <= (
            atol / scale + rtol * (abs(a) / scale))
    return all(within_tolerance(a, b) for a, b in zip(reference, candidate))


def examples():
    return {
        "scope": "teaching arithmetic only; no GPU, model training or network",
        "dpo_zero": dpo_pair(0),
        "dpo_positive": dpo_pair(2),
        "constant_group": normalized([7, 7, 7]),
        "raw_mix": combined_advantages([[0, 100, 200], [2, 1, 0]], [1, 1],
                                       per_channel=False),
        "per_channel_mix": combined_advantages([[0, 100, 200], [2, 1, 0]], [1, 1]),
        "conflict": conflicting([1, 0], [-1, 0]),
        "roofline_A": roofline(10e12, 1e12, 100e12, 1e12).__dict__,
        "roofline_B": roofline(10e12, .01e12, 100e12, 1e12).__dict__,
        "video_floor": video_tokens(1280, 720, 16),
        "video_spatial_padding": video_tokens(1280, 720, 16, spatial_policy="ceil"),
        "video_full_coverage": video_tokens(1280, 720, 16, spatial_policy="ceil",
                                            time_policy="ceil"),
        "sparse_attention": attention_flops(100, 10, 4),
        "incorrect_whole_division": attention_flops(100, 10) / 4,
        "14B_BF16_raw_weights": weight_memory(14_000_000_000),
        "oracle_NaN_rejected": not oracle_accepts([.2, .4], [.2, math.nan]),
    }


if __name__ == "__main__":
    print(json.dumps(examples(), ensure_ascii=False, indent=2, allow_nan=False))
