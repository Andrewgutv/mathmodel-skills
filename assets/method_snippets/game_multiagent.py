from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class PayoffResult:
    row_best_response: int
    col_best_response: int
    expected_value: float


def analyze_2x2_game(payoff_matrix: np.ndarray) -> PayoffResult:
    row_best = int(np.argmax(np.min(payoff_matrix, axis=1)))
    col_best = int(np.argmin(np.max(payoff_matrix, axis=0)))
    expected = float(payoff_matrix[row_best, col_best])
    return PayoffResult(row_best_response=row_best, col_best_response=col_best, expected_value=expected)


def simulate_decentralized_frequency(
    initial_units: float,
    initial_frequency: float,
    suppression: float,
    resupply: float,
    steps: int = 30,
):
    units = [initial_units]
    frequency = [initial_frequency]
    for _ in range(steps):
        next_units = max(0.0, units[-1] + resupply - suppression * frequency[-1])
        next_freq = max(0.0, frequency[-1] * (0.95 + 0.05 * (next_units > 0)))
        units.append(next_units)
        frequency.append(next_freq)
    return np.array(units), np.array(frequency)
