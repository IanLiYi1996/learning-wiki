"""Small, original weight-space exercises; Python stdlib, no training or downloads.

Run: python -B scripts/weight_space_lab.py
These synthetic networks do not reproduce the blog's LLM experiments.
Matrices use column-vector notation: output = W @ input + bias.
"""

from dataclasses import dataclass
import math


def matrix_shape(matrix):
    if not matrix or not matrix[0]:
        raise ValueError("A matrix must be nonempty")
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("A matrix must be rectangular")
    if any(not math.isfinite(value) for row in matrix for value in row):
        raise ValueError("Matrix entries must be finite")
    return len(matrix), width


def affine(weights, inputs, bias):
    rows, columns = matrix_shape(weights)
    if len(inputs) != columns or len(bias) != rows:
        raise ValueError("Affine dimensions do not match")
    if any(not math.isfinite(value) for value in (*inputs, *bias)):
        raise ValueError("Inputs and biases must be finite")
    return tuple(sum(w * x for w, x in zip(row, inputs)) + b
                 for row, b in zip(weights, bias))


@dataclass(frozen=True)
class Network:
    w1: tuple
    b1: tuple
    w2: tuple
    b2: tuple

    def __post_init__(self):
        hidden, _ = matrix_shape(self.w1)
        outputs, width = matrix_shape(self.w2)
        if hidden != width or len(self.b1) != hidden or len(self.b2) != outputs:
            raise ValueError("Network dimensions do not match")
        if any(not math.isfinite(value) for value in (*self.b1, *self.b2)):
            raise ValueError("Biases must be finite")

    def forward(self, inputs):
        hidden = tuple(max(0.0, value) for value in affine(self.w1, inputs, self.b1))
        return affine(self.w2, hidden, self.b2)

    @property
    def parameter_count(self):
        return (sum(map(len, self.w1)) + len(self.b1)
                + sum(map(len, self.w2)) + len(self.b2))


def controller(bugged=False):
    """Inputs (position, target); output logits (left, stay, right)."""
    w2 = ((-1.0, 1.0), (0.0, 0.0), (1.0, -1.0))
    if bugged:
        w2 = ((1.0, -1.0), (0.0, 0.0), (-1.0, 1.0))
    return Network(((-1.0, 1.0), (1.0, -1.0)), (0.0, 0.0), w2, (0.0, 0.0, 0.0))


def action(logits):
    if len(logits) != 3 or any(not math.isfinite(value) for value in logits):
        raise ValueError("Expected three finite controller logits")
    maximum = max(logits)
    # This teaching controller uses argmax, not the blog's stochastic sampling.
    return next(index for index in (1, 0, 2) if logits[index] == maximum)


def grid_score(network):
    correct = 0
    for position in range(11):
        for target in range(11):
            expected = 0 if position > target else 2 if position < target else 1
            correct += action(network.forward((position / 10, target / 10))) == expected
    return correct, 121


def permute_hidden(network, order):
    width = len(network.b1)
    if len(order) != width or sorted(order) != list(range(width)):
        raise ValueError("Permutation must contain every hidden index exactly once")
    return Network(
        tuple(network.w1[index] for index in order),
        tuple(network.b1[index] for index in order),
        tuple(tuple(row[index] for index in order) for row in network.w2),
        network.b2,
    )


def average_networks(first, second):
    if (matrix_shape(first.w1) != matrix_shape(second.w1)
            or matrix_shape(first.w2) != matrix_shape(second.w2)):
        raise ValueError("Cannot average networks with different shapes")

    def vector(a, b):
        return tuple((x + y) / 2 for x, y in zip(a, b))

    def matrix(a, b):
        return tuple(vector(x, y) for x, y in zip(a, b))

    return Network(matrix(first.w1, second.w1), vector(first.b1, second.b1),
                   matrix(first.w2, second.w2), vector(first.b2, second.b2))


def project_columns(weights, direction, columns):
    """Remove a synthetic direction only from selected columns.

    This is geometry, not a recipe for locating behaviors in real language models.
    Direction coordinates live in the matrix's output space.
    """
    rows, width = matrix_shape(weights)
    if len(direction) != rows or any(not math.isfinite(value) for value in direction):
        raise ValueError("Projection direction must match output dimensions and be finite")
    norm = math.hypot(*direction)
    if norm == 0 or not math.isfinite(norm):
        raise ValueError("Projection direction must have a finite nonzero norm")
    if (len(set(columns)) != len(columns)
            or any(not isinstance(index, int) or not 0 <= index < width for index in columns)):
        raise ValueError("Selected columns must be distinct valid indices")
    unit = tuple(value / norm for value in direction)
    result = [list(row) for row in weights]
    for column in columns:
        coefficient = sum(unit[row] * weights[row][column] for row in range(rows))
        for row in range(rows):
            result[row][column] -= unit[row] * coefficient
    return tuple(tuple(row) for row in result)


def run_exercises():
    fixed = controller()
    bugged = controller(bugged=True)
    renamed = permute_hidden(fixed, (1, 0))
    samples = [(p / 10, t / 10) for p in range(11) for t in range(11)]
    permutation_error = max(abs(a - b) for inputs in samples
                            for a, b in zip(fixed.forward(inputs), renamed.forward(inputs)))
    original = Network(((1.0,), (-1.0,)), (0.0, 0.0), ((1.0, 0.0),), (0.0,))
    equivalent = permute_hidden(original, (1, 0))
    averaged = average_networks(original, equivalent)
    weights = ((2.0, 3.0), (4.0, 5.0))
    projected = project_columns(weights, (1.0, 0.0), (0,))
    return {
        "controller_parameters": fixed.parameter_count,
        "bugged_grid": grid_score(bugged),
        "fixed_grid": grid_score(fixed),
        "hidden_permutation_max_error": permutation_error,
        "relu_at_one": original.forward((1.0,))[0],
        "equivalent_relu_at_one": equivalent.forward((1.0,))[0],
        "blind_average_at_one": averaged.forward((1.0,))[0],
        "partial_projection": projected,
        "untouched_column_direction_component": projected[0][1],
    }


if __name__ == "__main__":
    for name, value in run_exercises().items():
        print(f"{name}: {value}")
