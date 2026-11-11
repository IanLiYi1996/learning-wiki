"""Synthetic memory and continuous-generation exercises; standard library only.

No model, network, audio/video, real memory store, file mutation or paid service.
"""

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
import json
import math


def number(value, label, *, minimum=None):
    if type(value) not in (int, float):
        raise ValueError(f"{label} must be a real number")
    try:
        value = float(value)
    except OverflowError as error:
        raise ValueError(f"{label} exceeds floating-point range") from error
    if not math.isfinite(value) or (minimum is not None and value < minimum):
        raise ValueError(f"invalid {label}")
    return value


def count(value, label, *, minimum=1):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{label} must be an integer >= {minimum}")
    return value


def name(value, label):
    if type(value) is not str or not value.strip():
        raise ValueError(f"{label} must be nonempty text")
    return value


def total(values, label):
    try:
        return number(math.fsum(values), label)
    except OverflowError as error:
        raise ValueError(f"{label} exceeds floating-point range") from error


@dataclass(frozen=True)
class MemoryNote:
    note_id: str
    tenant: str
    project: str
    source_id: str
    source_version: str
    observed_at: float
    valid_before: float
    state: str = "verified"

    def __post_init__(self):
        for field in ("note_id", "tenant", "project", "source_id", "source_version"):
            name(getattr(self, field), field)
        observed = number(self.observed_at, "observed_at", minimum=0)
        expiry = number(self.valid_before, "valid_before", minimum=0)
        if expiry < observed:
            raise ValueError("expiry precedes observation")
        if self.state not in ("verified", "hypothesis", "revoked"):
            raise ValueError("unknown evidence state")


def memory_gate(note, tenant, project, source_versions, now):
    """A declared-context gate, NOT independent fact verification or real ACL."""
    if not isinstance(note, MemoryNote):
        raise ValueError("typed memory note required")
    name(tenant, "tenant")
    name(project, "project")
    now = number(now, "now", minimum=0)
    if not isinstance(source_versions, dict):
        raise ValueError("source_versions must be a mapping")
    for key, value in source_versions.items():
        name(key, "source")
        name(value, "version")
    if note.observed_at > now:
        raise ValueError("future observation")
    if (note.tenant, note.project) != (tenant, project):
        return "wrong-scope"
    if note.state == "revoked":
        return "revoked"
    if note.state != "verified":
        return "unverified"
    if note.source_id not in source_versions:
        return "unknown-source"
    if source_versions[note.source_id] != note.source_version:
        return "wrong-version"
    if now >= note.valid_before:
        return "expired"
    return "admit"


def invalidate(changed, dependencies):
    """Mark a declared DAG and its descendants; never delete external records."""
    if not isinstance(dependencies, dict) or not dependencies:
        raise ValueError("nonempty dependency graph required")
    graph = {}
    for child, parents in dependencies.items():
        name(child, "node")
        if not isinstance(parents, (list, tuple)):
            raise ValueError("parents must be a list or tuple")
        parents = tuple(name(parent, "parent") for parent in parents)
        if len(set(parents)) != len(parents):
            raise ValueError("duplicate dependency")
        graph[child] = parents
    if any(parent not in graph for parents in graph.values() for parent in parents):
        raise ValueError("dangling dependency")
    pending, finished = set(graph), set()
    while pending:
        ready = {node for node in pending if all(parent in finished for parent in graph[node])}
        if not ready:
            raise ValueError("dependency cycle")
        pending -= ready
        finished |= ready
    if not isinstance(changed, (tuple, list)):
        raise ValueError("changed nodes must be a list or tuple")
    changed = tuple(name(node, "changed node") for node in changed)
    if not changed or any(node not in graph for node in changed):
        raise ValueError("known changed nodes required")
    affected = set(changed)
    while True:
        new = {child for child, parents in graph.items()
               if any(parent in affected for parent in parents)}
        if new <= affected:
            return tuple(sorted(affected))
        affected |= new


def cas_write(version, facts, expected_version, replacement):
    """Simulated compare-and-swap replacement; returns copies, not a real store."""
    count(version, "version", minimum=0)
    count(expected_version, "expected_version", minimum=0)
    for mapping in (facts, replacement):
        if not isinstance(mapping, dict):
            raise ValueError("fact mapping required")
        for key, value in mapping.items():
            name(key, "fact ID")
            name(value, "fact")
    if version != expected_version:
        return {"accepted": False, "version": version, "facts": dict(facts)}
    return {"accepted": True, "version": version + 1, "facts": dict(replacement)}


def break_even(build, baseline, online, update):
    """Minimum positive integer N with memory cost <= baseline; toy units only."""
    build, baseline, online, update = (
        number(value, label, minimum=0)
        for value, label in ((build, "build"), (baseline, "baseline"),
                             (online, "online"), (update, "update")))
    running = total((online, update), "memory running cost")
    saving = baseline - running
    if saving < 0 or (saving == 0 and build > 0):
        queries = None
    elif saving == 0:
        queries = 1
    else:
        queries = max(1, math.ceil(number(build / saving, "break-even ratio")))
    return {"net_saving_per_query": saving, "break_even_queries": queries}


def probability_vector(values):
    try:
        values = tuple(values)
    except TypeError as error:
        raise ValueError("probability sequence required") from error
    values = tuple(number(value, "probability", minimum=0) for value in values)
    if not values or any(value > 1 for value in values) \
            or not math.isclose(total(values, "probability sum"), 1, abs_tol=1e-12,
                                rel_tol=0):
        raise ValueError("normalized probability vector required")
    return values


def factorization_error(joint):
    if not isinstance(joint, (tuple, list)) \
            or any(not isinstance(row, (tuple, list)) for row in joint):
        raise ValueError("matrix of probabilities required")
    rows = tuple(tuple(row) for row in joint)
    if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("nonempty rectangular joint required")
    flat = probability_vector(value for row in rows for value in row)
    width = len(rows[0])
    rows = tuple(flat[index:index + width] for index in range(0, len(flat), width))
    first = tuple(total(row, "row marginal") for row in rows)
    second = tuple(total((row[col] for row in rows), "column marginal")
                   for col in range(width))
    product = tuple(tuple(left * right for right in second) for left in first)
    invalid = total((product[i][j] for i, row in enumerate(rows)
                     for j, value in enumerate(row) if value == 0), "invalid mass")
    tv = total((abs(value - product[i][j]) for i, row in enumerate(rows)
                for j, value in enumerate(row)), "TV sum") / 2
    return {"first_marginal": first, "second_marginal": second,
            "product": product, "invalid_mass": invalid, "total_variation": tv}


def integrate_linear(steps, method="euler", initial=1, duration=1):
    """dx/dt=x; bounded deterministic teaching solver, not a language sampler."""
    count(steps, "steps")
    if steps > 10000 or method not in ("euler", "heun"):
        raise ValueError("unknown method or teaching step budget exceeded")
    initial = number(initial, "initial")
    duration = number(duration, "duration", minimum=0)
    try:
        exact = number(initial * math.exp(duration), "exact result")
    except OverflowError as error:
        raise ValueError("exact result exceeds range") from error
    h, value = duration / steps, initial
    for _ in range(steps):
        proposal = number(value + h * value, "proposal")
        value = proposal if method == "euler" else \
            number(value + h / 2 * (value + proposal), "corrected result")
    return {"method": method, "steps": steps,
            "nfe": steps if method == "euler" else 2 * steps,
            "approximation": value, "exact": exact, "absolute_error": abs(value - exact)}


def map_contract(s=0, u=.5, t=1, value=1):
    """Three explicit scalar maps; semigroup alone cannot identify dx/dt=x."""
    s, u, t, value = (number(x, label) for x, label in
                      ((s, "s"), (u, "u"), (t, "t"), (value, "value")))
    if not 0 <= s <= u <= t <= 1:
        raise ValueError("ordered times in [0,1] required")
    exact_direct = number(math.exp(t - s) * value, "exact direct")
    exact_composed = number(math.exp(t - u) * math.exp(u - s) * value, "exact composed")
    euler_direct = number((1 + t - s) * value, "Euler direct")
    euler_composed = number((1 + t - u) * (1 + u - s) * value, "Euler composed")
    return {"exact_semigroup_error": abs(exact_direct - exact_composed),
            "euler_semigroup_error": abs(euler_direct - euler_composed),
            "identity_semigroup_error": 0.0,
            "identity_velocity_error": abs(value)}


def guidance_targets(weak, strong, strength):
    weak, strong = probability_vector(weak), probability_vector(strong)
    if len(weak) != len(strong):
        raise ValueError("matching vocabulary dimensions required")
    strength = number(strength, "strength", minimum=0)
    raw = tuple(number(w + strength * (s - w), "guided coordinate")
                for w, s in zip(weak, strong))
    valid = all(0 <= value <= 1 for value in raw) \
        and math.isclose(total(raw, "guided sum"), 1, abs_tol=1e-12, rel_tol=0)
    return {"raw": raw, "valid_probability_target": valid}


def dense_state_budget(length, vocabulary, embedding_dim, scalar_bytes=4):
    for value, label in ((length, "length"), (vocabulary, "vocabulary"),
                         (embedding_dim, "embedding_dim"), (scalar_bytes, "scalar_bytes")):
        count(value, label)
    bits = (vocabulary - 1).bit_length()
    return {"one_hot_bytes": length * vocabulary * scalar_bytes,
            "embedding_bytes": length * embedding_dim * scalar_bytes,
            "binary_coordinates": bits, "binary_float_state_bytes": length * bits * scalar_bytes}


def binary_reference_stats(sequence, repeat_probability=.9):
    """Two-symbol Markov reference, excludes first-token score; no real LM."""
    try:
        sequence = tuple(sequence)
    except TypeError as error:
        raise ValueError("token sequence required") from error
    if len(sequence) < 2 or any(token not in ("A", "B") for token in sequence):
        raise ValueError("at least two A/B tokens required")
    repeat_probability = number(repeat_probability, "repeat probability")
    if not 0 < repeat_probability < 1:
        raise ValueError("repeat probability must be strictly between zero and one")
    logps = tuple(math.log(repeat_probability if left == right else 1 - repeat_probability)
                  for left, right in zip(sequence, sequence[1:]))
    frequencies = Counter(sequence)
    entropy = -total((freq / len(sequence) * math.log(freq / len(sequence))
                      for freq in frequencies.values()), "entropy sum")
    return {"conditional_gppl": math.exp(-total(logps, "log probabilities") / len(logps)),
            "unigram_entropy": entropy}


def evaluation_count(steps, predictions_per_step=1, final_readout=0):
    count(steps, "steps")
    count(predictions_per_step, "predictions_per_step")
    count(final_readout, "final_readout", minimum=0)
    return steps * predictions_per_step + final_readout


def memory_examples():
    notes = [
        MemoryNote("current", "tenant-a", "project-a", "interface", "v2", 1, 20),
        MemoryNote("old", "tenant-a", "project-a", "interface", "v1", 1, 20),
        MemoryNote("guess", "tenant-a", "project-a", "interface", "v2", 1, 20, "hypothesis"),
        MemoryNote("expired", "tenant-a", "project-a", "interface", "v2", 1, 5),
        MemoryNote("other", "tenant-b", "project-a", "interface", "v2", 1, 20),
    ]
    original = {"alpha": "original"}
    first = cas_write(0, original, 0, {**original, "beta": "A wrote"})
    stale = cas_write(first["version"], first["facts"], 0,
                      {**original, "gamma": "B wrote"})
    retry = cas_write(first["version"], first["facts"], first["version"],
                      {**first["facts"], "gamma": "B wrote"})
    return {
        "admission": [{"note": asdict(note), "gate": memory_gate(
            note, "tenant-a", "project-a", {"interface": "v2"}, 10)} for note in notes],
        "invalidation": invalidate(["source"], {
            "source": (), "note": ("source",), "wiki": ("note",),
            "report": ("wiki",), "unrelated": ()}),
        "concurrency": {"stale_write": stale, "retry": retry,
                        "naive_last_write_facts": {**original, "gamma": "B wrote"}},
        "cost": break_even(120, 10, 7, 1),
    }


def flow_examples():
    return {
        "joint": factorization_error(((.5, 0), (0, .5))),
        "solver": [integrate_linear(1), integrate_linear(2),
                   integrate_linear(4), integrate_linear(1, "heun")],
        "maps": map_contract(),
        "guidance": guidance_targets((.9, .1), (.4, .6), 2),
        "measurement": {
            "repeating": binary_reference_stats("AAAAAA"),
            "alternating": binary_reference_stats("ABABAB"),
            "model_evaluations": evaluation_count(8, 2, 1),
            "state_budget": dense_state_budget(128, 50000, 64),
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--group", choices=("memory", "flow", "all"), default="all")
    selected = parser.parse_args().group
    examples = {"scope": "synthetic teaching, not paper or model reproduction"}
    if selected in ("memory", "all"):
        examples["memory"] = memory_examples()
    if selected in ("flow", "all"):
        examples["flow"] = flow_examples()
    print(json.dumps(examples, ensure_ascii=False, indent=2, allow_nan=False))
