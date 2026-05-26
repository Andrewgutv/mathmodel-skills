from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import curve_fit


@dataclass
class RegressionResult:
    params: np.ndarray
    mse: float
    y_hat: np.ndarray


def exp_decay_model(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    return a * np.exp(-b * x) + c


def logistic_curve(x: np.ndarray, L: float, k: float, x0: float) -> np.ndarray:
    return L / (1.0 + np.exp(-k * (x - x0)))


def fit_curve(model, x: np.ndarray, y: np.ndarray, p0=None) -> RegressionResult:
    params, _ = curve_fit(model, x, y, p0=p0, maxfev=20000)
    y_hat = model(x, *params)
    mse = float(np.mean((y - y_hat) ** 2))
    return RegressionResult(params=params, mse=mse, y_hat=y_hat)
