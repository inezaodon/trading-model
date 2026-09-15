"""Itô lemma helpers and log-return transforms.

For f(t, S) under dS = μ S dt + σ S dW:

    df = (f_t + μ S f_S + ½ σ² S² f_SS) dt + σ S f_S dW

Special case f = log S yields the classic drift correction −½σ².
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def log_returns(prices: np.ndarray, axis: int = -1) -> np.ndarray:
    """Compute consecutive log-returns along ``axis``.

    Returns an array with one fewer element along ``axis``.
    """
    prices = np.asarray(prices, dtype=float)
    if prices.shape[axis] < 2:
        raise ValueError("need at least two prices for log returns")
    return np.diff(np.log(prices), axis=axis)


def apply_ito_log(prices: np.ndarray) -> np.ndarray:
    """Map positive spot paths to log-price paths (Itô coordinate change)."""
    prices = np.asarray(prices, dtype=float)
    if np.any(prices <= 0):
        raise ValueError("prices must be strictly positive for log transform")
    return np.log(prices)


def ito_drift_diffusion(
    s: float,
    mu: float,
    sigma: float,
    f_t: float,
    f_s: float,
    f_ss: float,
) -> tuple[float, float]:
    """Return (drift, diffusion) coefficients of df for f(t, S) under GBM.

    Parameters
    ----------
    s :
        Spot level.
    mu, sigma :
        GBM drift and vol.
    f_t, f_s, f_ss :
        Partial derivatives ∂f/∂t, ∂f/∂S, ∂²f/∂S² evaluated at (t, s).
    """
    drift = f_t + mu * s * f_s + 0.5 * (sigma**2) * (s**2) * f_ss
    diffusion = sigma * s * f_s
    return drift, diffusion


def ito_log_sde_coeffs(mu: float, sigma: float) -> tuple[float, float]:
    """Drift and diffusion of X = log S under GBM: dX = (μ − ½σ²)dt + σ dW."""
    return mu - 0.5 * sigma**2, sigma


def expected_ito_correction(
    sigma: float | np.ndarray,
    dt: float,
) -> float | np.ndarray:
    """Quadratic-variation correction ½ σ² Δt appearing in the log-Euler scheme."""
    return 0.5 * np.asarray(sigma, dtype=float) ** 2 * dt


def pathwise_ito_log_increment(
    s_prev: np.ndarray,
    s_next: np.ndarray,
    sigma: float | np.ndarray,
    dt: float,
    mu: float = 0.0,
) -> np.ndarray:
    """Residual of observed log-increment vs Itô-implied mean under GBM.

    Useful as a diagnostic when comparing simulated paths to the analytic
    log-mean (μ − ½σ²)Δt.
    """
    realized = np.log(np.asarray(s_next) / np.asarray(s_prev))
    mean = (mu - 0.5 * np.asarray(sigma, dtype=float) ** 2) * dt
    return realized - mean


def apply_scalar_ito(
    s: float,
    mu: float,
    sigma: float,
    f: Callable[[float], float],
    f_s: Callable[[float], float],
    f_ss: Callable[[float], float],
    f_t: float = 0.0,
) -> tuple[float, float]:
    """Evaluate Itô drift/diffusion for a time-homogeneous map f(S)."""
    return ito_drift_diffusion(s, mu, sigma, f_t, f_s(s), f_ss(s))
