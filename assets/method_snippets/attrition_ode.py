from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from scipy.integrate import solve_ivp


@dataclass
class AttritionParams:
    alpha_before: float
    beta_before: float
    alpha_after: float
    beta_after: float
    noncombat_a: float = 0.0
    noncombat_b: float = 0.0
    reinforcement_a: float = 0.0
    reinforcement_b: float = 0.0
    t0: float = 10.0


def phased_attrition_rhs(params: AttritionParams) -> Callable[[float, np.ndarray], np.ndarray]:
    def rhs(t: float, y: np.ndarray) -> np.ndarray:
        a_force, b_force = y
        if t < params.t0:
            alpha = params.alpha_before
            beta = params.beta_before
        else:
            alpha = params.alpha_after
            beta = params.beta_after

        da = -alpha * b_force - params.noncombat_a + params.reinforcement_a
        db = -beta * a_force - params.noncombat_b + params.reinforcement_b
        return np.array([da, db], dtype=float)

    return rhs


def simulate_attrition(
    initial_a: float,
    initial_b: float,
    params: AttritionParams,
    t_end: float = 60.0,
    num_points: int = 300,
):
    t_eval = np.linspace(0.0, t_end, num_points)
    solution = solve_ivp(
        phased_attrition_rhs(params),
        (0.0, t_end),
        np.array([initial_a, initial_b], dtype=float),
        t_eval=t_eval,
        dense_output=True,
    )
    return solution
