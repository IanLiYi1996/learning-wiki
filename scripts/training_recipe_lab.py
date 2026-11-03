"""Offline teaching contracts for a training recipe; not a model trainer.

Standard library only: no tokenizer, model weights, GPU, file writes or network.
"""

from dataclasses import asdict, dataclass
from decimal import Decimal, DecimalException, localcontext
import json
import math


def count(value, name, minimum=1):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def finite(value, name, *, positive=False):
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be a real number, not a selector")
    try:
        valid = math.isfinite(value)
    except OverflowError as error:
        raise ValueError(f"{name} exceeds floating-point range") from error
    if not valid or (positive and value <= 0):
        raise ValueError(f"invalid {name}")
    return value


def rollout_counts(prompts, samples_per_prompt, updates, aborted=0):
    """An update is not an additional generation; no minibatch assumption."""
    for value, name in ((prompts, "prompts"), (samples_per_prompt, "samples per prompt"),
                        (updates, "updates")):
        count(value, name)
    count(aborted, "aborted", 0)
    generated = prompts * samples_per_prompt
    if aborted > generated:
        raise ValueError("aborted count exceeds generated count")
    return {"generated_responses": generated, "valid_responses": generated - aborted,
            "optimizer_updates": updates}


def zero_success_probability(success_probability, draws):
    """Independent Bernoulli toy only; not a model's true solvability estimate."""
    finite(success_probability, "success probability")
    count(draws, "draws")
    if not 0 <= success_probability <= 1:
        raise ValueError("probability must be in [0,1]")
    if success_probability == 0:
        return 1.0
    if success_probability == 1:
        return 0.0
    try:
        exponent = draws * math.log1p(-success_probability)
    except OverflowError:
        # Integer conversion can overflow although draws*p remains finite.
        with localcontext() as context:
            context.prec = 60
            exact_scale = Decimal(draws) * Decimal.from_float(
                math.log1p(-success_probability))
            if exact_scale < -750:
                return 0.0
            exponent = float(exact_scale)
    return math.exp(exponent)


def masked_nll(logprobs, loss_masks):
    """Token-average toy NLL. Nonempty selected tokens required."""
    logprobs, loss_masks = tuple(logprobs), tuple(loss_masks)
    if not logprobs or len(logprobs) != len(loss_masks):
        raise ValueError("matching nonempty probability and mask vectors required")
    if any(type(mask) is not bool for mask in loss_masks):
        raise ValueError("mask selectors must be booleans")
    for value in logprobs:
        finite(value, "log probability")
        if value > 0:
            raise ValueError("log probabilities cannot be positive")
    selected = tuple(-value for value, mask in zip(logprobs, loss_masks) if mask)
    if not selected:
        raise ValueError("no supervised tokens")
    # Scale before the mean to avoid a finite-input fsum overflow.
    scale = max(selected)
    return 0.0 if scale == 0 else scale * (math.fsum(value / scale for value in selected)
                                          / len(selected))


def replay_contract(sampled_ids, replay_ids, action_masks, loss_masks, old_logprobs):
    """Verify a synthetic authoritative token record, NOT real logprobs.

    Context uses None or zero placeholders; selected loss must be a model action.
    Model actions may be loss-masked. New-policy probabilities may legitimately
    differ; this contract does not require old == new probability.
    """
    sampled_ids, replay_ids = tuple(sampled_ids), tuple(replay_ids)
    action_masks, loss_masks, old_logprobs = (
        tuple(action_masks), tuple(loss_masks), tuple(old_logprobs))
    if not sampled_ids:
        raise ValueError("empty token record")
    if any(len(values) != len(sampled_ids)
           for values in (action_masks, loss_masks, old_logprobs)):
        raise ValueError("misaligned record fields")
    for token in (*sampled_ids, *replay_ids):
        count(token, "token ID", 0)
    for action, loss, logp in zip(action_masks, loss_masks, old_logprobs):
        if type(action) is not bool or type(loss) is not bool:
            raise ValueError("action/loss masks must be booleans")
        if loss and not action:
            raise ValueError("environment observation cannot be a sampled policy action")
        if action:
            finite(logp, "old sampled-action log probability")
            if logp > 0:
                raise ValueError("positive action log probability")
        elif logp is not None:
            finite(logp, "context placeholder")
            if logp != 0:
                raise ValueError("context has no sampled-action probability")
    return sampled_ids == replay_ids


def termination_contract(status):
    """Three named synthetic states; not a universal timeout classification."""
    contracts = {
        "passed": {"valid_reward": True, "reward": 1},
        "task_failed": {"valid_reward": True, "reward": 0},
        "infra_aborted": {"valid_reward": False, "reward": None},
    }
    if status not in contracts:
        raise ValueError("status must be typed before deciding reward validity")
    return dict(contracts[status])


def resource_days(nodes, days, gpus_per_node=8):
    count(nodes, "nodes")
    count(gpus_per_node, "GPUs per node")
    finite(days, "days", positive=True)
    try:
        with localcontext() as context:
            context.prec = 60
            duration = Decimal(days) if type(days) is int else Decimal.from_float(days)
            node_duration = Decimal(nodes) * duration
            gpu_duration = node_duration * Decimal(gpus_per_node)
            node_days = finite(float(node_duration), "node-days")
            gpu_days = finite(float(gpu_duration), "GPU-days")
    except (OverflowError, DecimalException) as error:
        raise ValueError("resource duration exceeds floating-point range") from error
    return {"node_days": node_days, "gpu_days": gpu_days}


@dataclass(frozen=True)
class EvalContract:
    task_version: str
    tools: str
    simulator: str
    judge: str
    decoding: str
    budget: str
    samples: int
    aggregation: str
    context_management: str
    failure_policy: str
    evaluation_window: str
    search_locale: str
    leakage_filter: str

    def __post_init__(self):
        count(self.samples, "evaluation samples")
        for name, value in asdict(self).items():
            if name != "samples" and (type(value) is not str or not value.strip()):
                raise ValueError(f"missing evaluation field: {name}")


def protocol_differences(left, right):
    if not isinstance(left, EvalContract) or not isinstance(right, EvalContract):
        raise ValueError("two explicit evaluation contracts required")
    return tuple(name for name in asdict(left)
                 if getattr(left, name) != getattr(right, name))


def examples():
    contract = EvalContract("toy-v1", "fixed-tools", "user-A", "judge-A", "temp=0.7",
                            "1K output", 4, "mean-success", "full-history",
                            "typed-retry-policy", "toy-window-A", "toy-locale", "toy-filter-v1")
    changed = EvalContract("toy-v1", "fixed-tools", "user-B", "judge-A", "temp=0.7",
                           "1K output", 4, "any-success", "full-history",
                           "typed-retry-policy", "toy-window-A", "toy-locale", "toy-filter-v1")
    ids = [11, 12, 13, 14]
    return {
        "scope": "teaching arithmetic and contracts; no training, GPU or network",
        "rollout_count": rollout_counts(256, 16, 2),
        "zero_of_16_at_p_005": zero_success_probability(.05, 16),
        "assistant_only_nll": masked_nll([-.1, -2, -.2, -3], [False, True, False, True]),
        "incorrect_all_token_nll": masked_nll([-.1, -2, -.2, -3], [True] * 4),
        "exact_replay": replay_contract(ids, ids, [False, True, False, True],
                                        [False, True, False, True], [None, -.2, None, -.8]),
        "drift_rejected": not replay_contract(ids, [11, 12, 99, 14],
                                              [False, True, False, True],
                                              [False, True, False, True],
                                              [None, -.2, None, -.8]),
        "infra_aborted": termination_contract("infra_aborted"),
        "hypothetical_resource_days": resource_days(64, 13),
        "protocol_differences": protocol_differences(contract, changed),
    }


if __name__ == "__main__":
    print(json.dumps(examples(), ensure_ascii=False, indent=2, allow_nan=False))
