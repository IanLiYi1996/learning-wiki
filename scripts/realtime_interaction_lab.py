"""Offline realtime-interaction contracts, not a model or service.

Standard library only. No audio/video capture, network, files, weights, or APIs.
"""

from dataclasses import asdict, dataclass
import json
import math


def finite_number(value, name, *, positive=False):
    """Reject bools, nonfinite values and numbers outside float range."""
    if type(value) not in (int, float):
        raise ValueError(f"{name} must be a real number")
    try:
        converted = float(value)
    except (OverflowError, ValueError) as error:
        raise ValueError(f"{name} exceeds floating-point range") from error
    if not math.isfinite(converted) or (positive and converted <= 0):
        raise ValueError(f"invalid {name}")
    return converted


def nonnegative_number(value, name):
    value = finite_number(value, name)
    if value < 0:
        raise ValueError(f"{name} must be nonnegative")
    return value


def integer(value, name, *, minimum=1):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def checked_product(left, right, name):
    return finite_number(left * right, name)


def checked_sum(values, name):
    try:
        return finite_number(math.fsum(values), name)
    except OverflowError as error:
        raise ValueError(f"{name} exceeds floating-point range") from error


def stream_budget(chunk_ms, audio_in, audio_out, video_every, video_units,
                  face_units, window_minutes):
    """Steady-state nominal units, not compute or billing.

    Startup phase, text, tool payloads, summaries and per-modality weights omitted.
    """
    chunk_ms = finite_number(chunk_ms, "chunk_ms", positive=True)
    window_minutes = finite_number(window_minutes, "window_minutes", positive=True)
    video_every = integer(video_every, "video_every")
    streams = {
        "audio_in": nonnegative_number(audio_in, "audio_in"),
        "audio_out": nonnegative_number(audio_out, "audio_out"),
        "video_in": nonnegative_number(video_units, "video_units"),
        "face_out": nonnegative_number(face_units, "face_units"),
    }
    chunks = finite_number(60000 / chunk_ms, "chunks_per_minute")
    streams["video_in"] /= finite_number(video_every, "video_every")
    per_minute = {name: checked_product(chunks, units, name)
                  for name, units in streams.items()}
    total = checked_sum(per_minute.values(), "total_units_per_minute")
    return {
        "chunks_per_minute": chunks,
        "units_per_minute": per_minute,
        "total_units_per_minute": total,
        "recent_window_units": checked_product(total, window_minutes, "window units"),
    }


def serial_latency(components_ms):
    """A declared serial path, not an overlapping production trace."""
    if not isinstance(components_ms, dict) or not components_ms:
        raise ValueError("nonempty named serial components required")
    components = {}
    for name, value in components_ms.items():
        if type(name) is not str or not name.strip():
            raise ValueError("components need nonempty names")
        components[name] = nonnegative_number(value, name)
    return {
        "components_ms": components,
        "serial_total_ms": checked_sum(components.values(), "serial latency"),
    }


def block_alignment(chunk_ms):
    """Uniform arrivals plus whole-block waiting: a conditional toy bound."""
    chunk_ms = finite_number(chunk_ms, "chunk_ms", positive=True)
    return {"mean_wait_ms": chunk_ms / 2, "supremum_wait_ms": chunk_ms}


@dataclass(frozen=True)
class ToolResult:
    """A synthetic immutable observation, never a real tool execution."""

    task_id: str
    intent_version: int
    status: str
    observed_at: float
    payload: str

    def __post_init__(self):
        if type(self.task_id) is not str or not self.task_id.strip():
            raise ValueError("task_id required")
        integer(self.intent_version, "intent_version")
        if self.status not in ("partial", "final", "failed"):
            raise ValueError("unknown tool status")
        nonnegative_number(self.observed_at, "observed_at")
        if type(self.payload) is not str:
            raise ValueError("payload must be text")


def result_gate(result, current_task, current_version, now, max_age):
    """One read-only answer gate, not authorization or rollback.

    Freshness uses observation time, not mere arrival time.
    A rejected result is not deleted or cancelled externally.
    """
    if not isinstance(result, ToolResult):
        raise ValueError("typed ToolResult required")
    if type(current_task) is not str or not current_task.strip():
        raise ValueError("current_task required")
    integer(current_version, "current_version")
    now = nonnegative_number(now, "now")
    max_age = nonnegative_number(max_age, "max_age")
    if result.observed_at > now:
        raise ValueError("future observation cannot be admitted")
    if result.task_id != current_task:
        return "wrong-task"
    if result.intent_version != current_version:
        return "old-intent"
    if now - result.observed_at > max_age:
        return "expired"
    if result.status != "final":
        return "not-final"
    return "admit"


def timing_score(windows, predictions):
    """One-to-one matching for disjoint closed timing windows.

    Duplicate in-window outputs are false positives. No official metric implied.
    """
    intervals = []
    for item in windows:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise ValueError("windows must have two endpoints")
        start = nonnegative_number(item[0], "window start")
        end = nonnegative_number(item[1], "window end")
        if start > end:
            raise ValueError("window start exceeds end")
        intervals.append((start, end))
    if not intervals:
        raise ValueError("at least one expected window required")
    intervals.sort()
    if any(previous[1] >= current[0]
           for previous, current in zip(intervals, intervals[1:])):
        raise ValueError("closed windows must be strictly disjoint")
    predictions = sorted(nonnegative_number(value, "prediction")
                         for value in predictions)
    matched = set()
    for prediction in predictions:
        for index, (start, end) in enumerate(intervals):
            if index not in matched and start <= prediction <= end:
                matched.add(index)
                break
    tp = len(matched)
    fp = len(predictions) - tp
    fn = len(intervals) - tp
    return {
        "true_positives": tp, "false_positives": fp, "false_negatives": fn,
        "precision": tp / len(predictions) if predictions else 0.0,
        "recall": tp / len(intervals),
        "f1": 2 * tp / (2 * tp + fp + fn),
    }


def examples():
    results = [
        ToolResult("inventory", 1, "final", 1.2, "A: 12"),
        ToolResult("inventory", 2, "partial", 1.6, "B: pending"),
        ToolResult("inventory", 2, "final", 1.6, "B: 7"),
        ToolResult("other", 2, "final", 1.6, "irrelevant"),
        ToolResult("inventory", 2, "final", 0, "B: outdated"),
    ]
    return {
        "scope": "original offline teaching examples, not Higgs measurements",
        "budget": stream_budget(160, 2, 3, 5, 10, 2, 4),
        "latency": serial_latency({
            "capture": 80, "uplink": 25, "queue": 15, "model": 45,
            "decode": 20, "downlink": 25, "playback": 40,
        }),
        "alignment": block_alignment(160),
        "results": [
            {"result": asdict(result),
             "gate": result_gate(result, "inventory", 2, 2, 1)}
            for result in results
        ],
        "timing": timing_score([(1, 2), (5, 6), (9, 10)], [1.5, 1.6, 5.5, 12]),
    }


if __name__ == "__main__":
    print(json.dumps(examples(), ensure_ascii=False, indent=2, allow_nan=False))
