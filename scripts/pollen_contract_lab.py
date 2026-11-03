"""Original CPU/stdlib Physical AI teaching; never connects to hardware."""

from bisect import bisect_right
from dataclasses import dataclass
import json
import math


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Expected a finite real number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError("Outside supported numeric range") from exc
    if not math.isfinite(result):
        raise ValueError("Expected a finite real number")
    return result


def vector(values, size):
    result = tuple(finite(value) for value in values)
    if len(result) != size:
        raise ValueError("Unexpected vector length")
    return result


def backproject(u, v, depth, *, fx, fy, cx, cy, unit):
    """Known pinhole intrinsics and explicit metric scale; no distortion model."""
    u, v, depth, fx, fy, cx, cy = map(finite, (u, v, depth, fx, fy, cx, cy))
    if fx <= 0 or fy <= 0 or depth <= 0:
        raise ValueError("Depth and focal lengths must be positive")
    if unit not in ("m", "mm"):
        raise ValueError("Relative or unspecified depth has no metric scale")
    z = depth if unit == "m" else depth / 1000
    return vector(((u - cx) * z / fx, (v - cy) * z / fy, z), 3)


def transform_yaw(point, *, translation, yaw_radians):
    """Teaching world<-camera transform restricted to yaw, not a full SE(3) API."""
    x, y, z = vector(point, 3)
    tx, ty, tz = vector(translation, 3)
    angle = finite(yaw_radians)
    c, s = math.cos(angle), math.sin(angle)
    return vector((c*x - s*y + tx, s*x + c*y + ty, z + tz), 3)


def orbita2d_forward(motors, *, ratios):
    """A/B motor radians -> ring/center output radians, following source model."""
    a, b = vector(motors, 2)
    ra, rb = vector(ratios, 2)
    if ra == 0 or rb == 0:
        raise ValueError("Singular reduction ratio")
    return vector((a / ra / 2 + b / rb / 2, a / ra / 2 - b / rb / 2), 2)


def orbita2d_inverse(outputs, *, ratios):
    ring, center = vector(outputs, 2)
    ra, rb = vector(ratios, 2)
    if ra == 0 or rb == 0:
        raise ValueError("Singular reduction ratio")
    return vector((ra * (ring + center), rb * (ring - center)), 2)


def quaternion_xyzw(values, *, order):
    """Normalize and explicitly reorder; magnitude cannot reveal wrong ordering."""
    values = vector(values, 4)
    if order == "wxyz":
        w, x, y, z = values
        values = (x, y, z, w)
    elif order != "xyzw":
        raise ValueError("Quaternion order must be explicit")
    norm = finite(math.hypot(*values))
    if norm == 0:
        raise ValueError("Zero quaternion")
    return tuple(value / norm for value in values)


def prior_observation(times, *, decision_time, max_age, sensor_clock, policy_clock):
    """Last causal observation in one identified clock; no nearest future sample."""
    if not isinstance(sensor_clock, str) or not sensor_clock.strip():
        raise ValueError("Missing clock identity")
    if not isinstance(policy_clock, str) or sensor_clock != policy_clock:
        raise ValueError("Convert clock domains before comparing timestamps")
    values = tuple(finite(value) for value in times)
    decision, age_limit = finite(decision_time), finite(max_age)
    if age_limit < 0 or any(a >= b for a, b in zip(values, values[1:])):
        raise ValueError("Need increasing timestamps and nonnegative age limit")
    index = bisect_right(values, decision) - 1
    if index < 0:
        return None
    age = finite(decision - values[index])
    return None if age > age_limit else {"index": index, "age_seconds": age}


@dataclass(frozen=True)
class ActionContract:
    names: tuple[str, ...]
    unit: str
    frame: str
    representation: str

    def __post_init__(self):
        if (type(self.names) is not tuple or not self.names or
            any(not isinstance(name, str) or not name.strip() for name in self.names) or
            len(set(self.names)) != len(self.names)):
            raise ValueError("Need unique ordered names")
        for value in (self.unit, self.frame, self.representation):
            if not isinstance(value, str) or not value.strip():
                raise ValueError("Incomplete action semantics")


def action_gate(values, actual, expected, *, sampled_at, now, max_age, enabled):
    """Teaching acceptance check, NOT an actuator controller or safety system.

    Rejecting a packet neither stops a robot nor selects its safe fallback.
    """
    if not isinstance(actual, ActionContract) or not isinstance(expected, ActionContract):
        raise ValueError("Need typed action contracts")
    vector(values, len(actual.names))
    sampled_at, now, max_age = map(finite, (sampled_at, now, max_age))
    if type(enabled) is not bool or max_age < 0:
        raise ValueError("Invalid gate parameters")
    reasons = []
    if not enabled:
        reasons.append("not_enabled")
    for field in ("names", "unit", "frame", "representation"):
        if getattr(actual, field) != getattr(expected, field):
            reasons.append("mismatch_" + field)
    if sampled_at > now:
        reasons.append("future_timestamp")
    elif finite(now - sampled_at) > max_age:
        reasons.append("stale")
    return {"accepted": not reasons, "reasons": reasons}


def latency_displacement(speed_mps, stage_seconds):
    """Constant-speed teaching estimate, not measured error or a safety margin."""
    speed = finite(speed_mps)
    stages = tuple(finite(value) for value in stage_seconds)
    if speed < 0 or not stages or any(value < 0 for value in stages):
        raise ValueError("Need nonnegative speed and nonempty latency stages")
    return finite(speed * finite(math.fsum(stages)))


def examples():
    expected = ActionContract(("ring", "center"), "rad", "orbita_output", "absolute_position")
    motor = ActionContract(("A", "B"), "rad", "motor", "absolute_position")
    point = backproject(420, 240, 500, fx=500, fy=500, cx=320, cy=240, unit="mm")
    return {
        "camera_point_m": point,
        "world_point_m": transform_yaw(point, translation=(1, 0, 0), yaw_radians=math.pi/2),
        "output_to_motors": orbita2d_inverse((.5, .5), ratios=(1, 1)),
        "motors_to_output": orbita2d_forward((1, 1), ratios=(1, 1)),
        "identity_quaternion_xyzw": quaternion_xyzw((1, 0, 0, 0), order="wxyz"),
        "causal_observation": prior_observation(
            (1.0, 1.03, 1.10), decision_time=1.06, max_age=.05,
            sensor_clock="monotonic-A", policy_clock="monotonic-A"),
        "mismatched_action": action_gate((1, 0), motor, expected,
            sampled_at=1, now=1.01, max_age=.1, enabled=True),
        "stale_action": action_gate((1, 0), expected, expected,
            sampled_at=1, now=1.25, max_age=.1, enabled=True),
        "latency_displacement_m": latency_displacement(.4, (.12, .08, .02)),
    }


if __name__ == "__main__":
    print(json.dumps(examples(), indent=2, ensure_ascii=False, allow_nan=False))
