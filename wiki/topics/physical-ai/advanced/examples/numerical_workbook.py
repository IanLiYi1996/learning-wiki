"""Offline numerical checks for the handbook; standard library, no hardware."""

import argparse
import bisect
import json
import math
import random
from pathlib import Path


def fk(q, lengths=(1.0, 1.0)):
    a, b = q
    l1, l2 = lengths
    return (
        l1 * math.cos(a) + l2 * math.cos(a + b),
        l1 * math.sin(a) + l2 * math.sin(a + b),
    )


def jacobian(q, lengths=(1.0, 1.0)):
    a, b = q
    l1, l2 = lengths
    return (
        (-l1 * math.sin(a) - l2 * math.sin(a + b),
         -l2 * math.sin(a + b)),
        (l1 * math.cos(a) + l2 * math.cos(a + b),
         l2 * math.cos(a + b)),
    )


def solve2(matrix, rhs):
    a, b = matrix[0]
    c, d = matrix[1]
    det = a * d - b * c
    if abs(det) < 1e-18:
        raise ValueError("Singular 2x2 system")
    return ((d * rhs[0] - b * rhs[1]) / det,
            (-c * rhs[0] + a * rhs[1]) / det)


def damped_step(q, error, damping):
    j = jacobian(q)
    row0, row1 = j
    normal = (
        (sum(v * v for v in row0) + damping**2,
         sum(x * y for x, y in zip(row0, row1))),
        (sum(x * y for x, y in zip(row0, row1)),
         sum(v * v for v in row1) + damping**2),
    )
    z = solve2(normal, error)
    return tuple(j[0][i] * z[0] + j[1][i] * z[1] for i in (0, 1))


def numerical_ik(target=(1.2, 0.6)):
    q = (0.2, -0.4)
    for iteration in range(1, 201):
        current = fk(q)
        error = tuple(t - c for t, c in zip(target, current))
        if math.hypot(*error) < 1e-7:
            return {"iterations": iteration - 1, "q": q, "position": current,
                    "position_error": math.hypot(*error)}
        delta = damped_step(q, error, 0.05)
        norm = math.hypot(*delta)
        scale = min(1.0, 0.25 / max(norm, 1e-20))
        q = tuple(v + scale * dv for v, dv in zip(q, delta))
    raise AssertionError("IK did not converge")


def wilson(successes, trials, z=1.959963984540054):
    if not 0 <= successes <= trials or trials <= 0:
        raise ValueError("Invalid trial counts")
    phat = successes / trials
    den = 1 + z**2 / trials
    center = (phat + z**2 / (2 * trials)) / den
    half = z * math.sqrt(
        phat * (1 - phat) / trials + z**2 / (4 * trials**2)
    ) / den
    return (center - half, center + half)


def run():
    tests = []
    q = (0.3, -0.7)
    j = jacobian(q)
    epsilon = 1e-6
    max_j_error = 0.0
    for column in range(2):
        plus, minus = list(q), list(q)
        plus[column] += epsilon
        minus[column] -= epsilon
        numerical = [(p - m) / (2 * epsilon) for p, m in zip(fk(plus), fk(minus))]
        max_j_error = max(max_j_error, *(abs(numerical[r] - j[r][column])
                                       for r in range(2)))
    assert max_j_error < 1e-8
    tests.append("Analytic Jacobian agrees with central differences.")
    branches = ((0.0, math.pi / 2), (math.pi / 2, -math.pi / 2))
    for branch in branches:
        assert math.dist(fk(branch), (1.0, 1.0)) < 1e-12
    tests.append("Two analytic IK branches reach the same point.")
    result_ik = numerical_ik()
    assert result_ik["position_error"] < 1e-7
    tests.append("Damped numerical IK converges in the teaching configuration.")
    near_q = (0.0, 1e-6)
    error = (0.001, 0.0)
    inverse_delta = solve2(jacobian(near_q), error)
    damped_delta = damped_step(near_q, error, 0.1)
    assert math.hypot(*inverse_delta) > 1000
    assert math.hypot(*damped_delta) < 1e-5
    tests.append("Damping bounds the local update near a singular configuration.")
    stable = abs((1 - 0.5)**20)
    unstable = abs((1 - 2.2)**20)
    assert stable < 1e-5 and unstable > 30
    tests.append("Ideal scalar feedback matches the derived recurrence.")
    p_prior, r_measurement, z_measurement = 4.0, 1.0, 2.0
    k = p_prior / (p_prior + r_measurement)
    posterior = k * z_measurement
    p_simple = (1 - k) * p_prior
    p_joseph = (1 - k)**2 * p_prior + k**2 * r_measurement
    assert math.isclose(p_simple, p_joseph, abs_tol=1e-12)
    assert math.isclose(posterior, 1.6) and math.isclose(p_joseph, 0.8)
    tests.append("Scalar Kalman posterior and Joseph covariance agree.")
    targets = (-1.0, 1.0)
    mean_mse = sum(v**2 for v in targets) / 2
    mode_mse = sum((1.0 - v)**2 for v in targets) / 2
    assert mean_mse == 1.0 and mode_mse == 2.0
    tests.append("Multimodal squared error prefers an unsupported midpoint.")
    rng = random.Random(20261027)
    noisy = [0.6 * 0.7 + 0.8 * rng.gauss(0, 1) for _ in range(20000)]
    noise_mean = sum(noisy) / len(noisy)
    noise_var = sum((v - noise_mean)**2 for v in noisy) / len(noisy)
    assert abs(noise_mean - 0.42) < 0.02 and abs(noise_var - 0.64) < 0.02
    tests.append("Forward-noising sample moments match the specified Gaussian.")
    x_flow = -1.0
    for _ in range(10):
        x_flow += 0.1 * 3.0
    assert math.isclose(x_flow, 2.0, abs_tol=1e-12)
    tests.append("Constant-velocity flow reaches its endpoint; no model was trained.")
    w10, w100 = wilson(9, 10), wilson(90, 100)
    assert w10[0] < w100[0] and w10[1] > w100[1]
    assert math.isclose(wilson(0, 10)[0], 0.0, abs_tol=1e-15)
    tests.append("Equal empirical success rates have different Wilson intervals.")
    timestamps = [0.0, 0.05, 0.10, 0.15]
    query_time = 0.12
    causal_index = bisect.bisect_right(timestamps, query_time) - 1
    assert timestamps[causal_index] <= query_time
    assert timestamps[causal_index + 1] > query_time
    tests.append("Causal alignment selects only a sample already available.")
    return {
        "scope": "Teaching calculations only: no learned policy, physics engine, or hardware.",
        "tests_passed": len(tests), "checks": tests,
        "jacobian_max_abs_error": max_j_error,
        "analytic_ik": [{"q": v, "position": fk(v)} for v in branches],
        "numerical_ik": result_ik,
        "near_singular_update": {
            "inverse": inverse_delta, "inverse_norm": math.hypot(*inverse_delta),
            "damped": damped_delta, "damped_norm": math.hypot(*damped_delta),
        },
        "scalar_feedback_20_steps": {
            "stable_abs_error": stable, "unstable_abs_error": unstable,
        },
        "scalar_kalman": {"gain": k, "mean": posterior, "variance": p_joseph},
        "bimodal_mse": {"midpoint": mean_mse, "positive_mode": mode_mse},
        "forward_noising": {
            "sample_mean": noise_mean, "sample_variance": noise_var,
            "expected_mean": 0.42, "expected_variance": 0.64,
        },
        "constant_flow_endpoint": x_flow,
        "wilson_95": {"9_of_10": w10, "90_of_100": w100},
        "causal_alignment": {
            "query_time": query_time, "selected_time": timestamps[causal_index],
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run()
    if args.output:
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                               encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
