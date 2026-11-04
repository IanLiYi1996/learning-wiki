"""Original stdlib teaching exercises, not the upstream evaluator or trainer.

No networking, model inference, external data, GPU, or filesystem writes.
"""

import json
import math
import re


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("a finite real number, not bool, is required")
    return float(value)


def validate_grid(output, size):
    """A deliberately small, strict palette/grid exercise on parsed objects."""
    if type(size) is not int or size <= 0:
        raise ValueError("size must be a positive integer")
    if not isinstance(output, dict):
        raise ValueError("output must be an object")
    palette, rows = output.get("palette"), output.get("pixels")
    if not isinstance(palette, list) or not 2 <= len(palette) <= 8:
        raise ValueError("palette requires 2–8 colors")
    if not all(isinstance(color, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", color)
               for color in palette):
        raise ValueError("colors require #RRGGBB")
    if not isinstance(rows, list) or len(rows) != size:
        raise ValueError("wrong number of rows")
    grid = []
    for row in rows:
        if isinstance(row, str):
            if len(row) != size or not re.fullmatch(r"[0-7]+", row):
                raise ValueError("row must have S digits in 0–7")
            row = [int(char) for char in row]
        if not isinstance(row, list) or len(row) != size:
            raise ValueError("wrong row width")
        if not all(type(index) is int and 0 <= index < len(palette) for index in row):
            raise ValueError("invalid palette index")
        grid.append(tuple(row))
    return tuple(palette), tuple(grid)


def render_rgb(output, size):
    palette, grid = validate_grid(output, size)
    colors = [tuple(int(color[offset:offset + 2], 16) for offset in (1, 3, 5))
              for color in palette]
    return tuple(tuple(colors[index] for index in row) for row in grid)


def flat_rgb(output, size):
    rgb = render_rgb(output, size)
    return all(pixel == rgb[0][0] for row in rgb for pixel in row)


def denominator_summary(scores):
    """None means invalid or missing, NOT a genuinely valid zero score."""
    valid = [number(score) for score in scores if score is not None]
    if any(not 0 <= score <= 1 for score in valid):
        raise ValueError("teaching score must be in [0, 1]")
    expected = len(scores)
    total = math.fsum(valid)
    return {
        "expected": expected, "valid": len(valid),
        "coverage": len(valid) / expected if expected else None,
        "all_expected_mean": total / expected if expected else None,
        "valid_only_mean": total / len(valid) if valid else None,
    }


def relative_aggregate(methods):
    """Three finite raw metrics, with an explicitly supplied comparison set."""
    if len(methods) < 2:
        raise ValueError("need at least two methods")
    values = {}
    for name, row in methods.items():
        if not isinstance(name, str) or not name or len(row) != 3:
            raise ValueError("each named method needs exactly three metrics")
        values[name] = tuple(number(value) for value in row)
    minimum = [min(row[index] for row in values.values()) for index in range(3)]
    span = [max(row[index] for row in values.values()) - minimum[index]
            for index in range(3)]
    if any(delta == 0 or not math.isfinite(delta) for delta in span):
        raise ValueError("each metric needs a finite, nonconstant range")
    return {name: 100 * math.fsum((row[index] - minimum[index]) / span[index]
                                 for index in range(3)) / 3
            for name, row in values.items()}


def positions(size, base=16):
    if type(size) is not int or type(base) is not int or min(size, base) <= 0:
        raise ValueError("positive integer dimensions required")
    return {"size": size, "positions": size * size, "relative": (size / base) ** 2}


def grouped_success(members):
    """Toy illustration of all-members-success units, not a benchmark harness."""
    if not members or any(type(value) is not bool for value in members):
        raise ValueError("nonempty boolean observations required")
    return all(members)


def averages(benchmarks):
    """Input contains official units ALREADY scored, not arbitrary questions."""
    if not benchmarks:
        raise ValueError("need scored benchmarks")
    totals, units, means = [], 0, []
    for row in benchmarks:
        if not row:
            raise ValueError("empty benchmark")
        values = [number(value) for value in row]
        if any(not 0 <= value <= 1 for value in values):
            raise ValueError("scores must be in [0, 1]")
        total = math.fsum(values)
        totals.append(total)
        units += len(values)
        means.append(total / len(values))
    return {"official_unit_weighted": math.fsum(totals) / units,
            "benchmark_equal_weighted": math.fsum(means) / len(means)}


def demo():
    square = {"palette": ["#FFFFFF", "#000000"],
              "pixels": ["0000", "0110", "0110", "0000"]}
    aliases = {"palette": ["#FFFFFF", "#ffffff"], "pixels": ["01", "10"]}
    methods = {"A": [0.2] * 3, "B": [0.4] * 3, "C": [0.6] * 3}
    return {
        "square_center_rgb": render_rgb(square, 4)[1][1],
        "square_flat": flat_rgb(square, 4),
        "duplicate_colors_flat": flat_rgb(aliases, 2),
        "denominators": denominator_summary([1.0, 0.5, None, None]),
        "relative_B_before": round(relative_aggregate(methods)["B"], 8),
        "relative_B_after": round(relative_aggregate({**methods, "D": [1.0] * 3})["B"], 8),
        "sizes": [positions(size) for size in (16, 32, 64, 128)],
        "paired_unit": grouped_success([True, False]),
        "different_averages": averages([[1.0] * 9, [0.0]]),
    }


if __name__ == "__main__":
    print(json.dumps(demo(), ensure_ascii=False, indent=2, allow_nan=False))
