"""Frozen v4 predictor for the center-biased hyperedge stopping time.

Declared empirical domain:
    integer 3 <= k <= 50
    integer 10 <= N = C/(k*sigma) <= 128
    0.30 <= p_bias <= 1.90

k=3 is evaluated with the exact finite-state Markov equation.  k>=4 uses an
asymptotically constrained crossover formula calibrated before the final blind
test.  The coefficients in this file must not be changed after blind testing.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.integrate import quad
from scipy.special import ndtr

from drift_experiments import exact_drifted_markov_mean


FORMULA_VERSION = "v4-frozen-2026-07-16"
DECLARED_DOMAIN = {"k": (3, 50), "N": (10, 128), "p_bias": (0.30, 1.90)}

NEUTRAL = np.array(
    [
        0.9786734790849152,
        0.07791864389785301,
        -0.0002386298853250784,
        0.034276618118409735,
        0.037685431785988814,
        -0.02140919460254579,
    ]
)

NEGATIVE = np.array(
    [
        0.9951869624112,
        -0.06302295949875837,
        0.29654515984507435,
        0.002944320823716644,
        0.03271181564278306,
        -0.01834282426997094,
        3.395470202184467,
        0.8276455665213841,
        -1.5558147857766718,
        -1.4511997918910629,
        -0.3658515975464068,
        0.6237490541075682,
    ]
)

POSITIVE = np.array(
    [
        -0.14901719885348683,
        -0.6574882634476589,
        -0.0685003751870206,
        0.19324662708763604,
        -0.026101319067934694,
        0.047102887362463916,
        -2.2522946176368173,
        0.20136600837710275,
        1.0440556575021949,
        1.2967286984825956,
        0.3250732778880787,
        -0.5053941409144954,
    ]
)


def _neutral_constant(k: float, N: float) -> float:
    if k == 3:
        return 1.0
    q = k - 3.0
    features = np.array([1.0, q, q * q, math.log(k / 3.0), 1.0 / N, q / N])
    return float(features @ NEUTRAL)


def _gaussian_max_mean(count: int) -> float:
    if count == 1:
        return 0.0
    return float(
        quad(
            lambda x: 1.0 - ndtr(x) ** count - (1.0 - ndtr(x)) ** count,
            0.0,
            np.inf,
            epsabs=1e-11,
        )[0]
    )


def _correction_design(k: float, N: float, x: float) -> np.ndarray:
    lk = math.log(k / 10.0)
    ln = math.log(N / 20.0)
    s = x / (1.0 + x)
    h = x / (1.0 + x) ** 2
    lx = math.log1p(x)
    base = np.array([1.0, lk, ln, lk * lk, ln * ln, lk * ln])
    return np.concatenate((h * base, h * s * base[:3], h * lx * base[:3]))


def _validate(k: int, N: int, p_bias: float) -> None:
    if not isinstance(k, int) or not isinstance(N, int):
        raise TypeError("k and N must be integers")
    if not 3 <= k <= 50:
        raise ValueError("declared formula domain requires 3 <= k <= 50")
    if not 10 <= N <= 128:
        raise ValueError("declared formula domain requires 10 <= N <= 128")
    if not 0.30 <= p_bias <= 1.90:
        raise ValueError("declared formula domain requires 0.30 <= p_bias <= 1.90")


def predict_stopping_time(k: int, N: int, p_bias: float) -> float:
    """Predict E[tau] in hyperedge-local transaction counts."""
    _validate(k, N, p_bias)
    if k == 3:
        if abs(p_bias - 1.0) < 1e-14:
            return float(N * N)
        return exact_drifted_markov_mean(k, N, p_bias)[0]

    a0 = max(_neutral_constant(float(k), float(N)), 0.1)
    neutral_time = a0 * N * N
    delta = p_bias - 1.0
    if abs(delta) < 1e-14:
        return max(float(N), neutral_time)

    if delta < 0:
        t_star = k * N / (2.0 * (-delta))
        x = neutral_time / t_star
        base = neutral_time / (1.0 + x)
        prediction = base * math.exp(float(_correction_design(k, N, x) @ NEGATIVE))
        upper = t_star
    else:
        t_star = k * (k - 1) * N / (2.0 * delta)
        x = neutral_time / t_star
        kappa = _gaussian_max_mean(k - 1)
        c_theory = kappa * math.sqrt(2.0 * a0 / (k - 1.0))
        competition = c_theory * x * x / (1.0 + x) ** 1.5
        base = neutral_time / (1.0 + x + competition)
        prediction = base * math.exp(float(_correction_design(k, N, x) @ POSITIVE))
        upper = t_star

    # Enforce the two rigorous path/martingale bounds.  Clipping is normally
    # inactive in the calibrated domain and protects extrapolation at corners.
    return min(max(float(N), prediction), upper)
