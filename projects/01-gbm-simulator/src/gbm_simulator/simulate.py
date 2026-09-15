"""GBM path simulation via the exact log-Euler discretization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class SimulationResult:
    """Container for Monte Carlo GBM output."""

    times: np.ndarray  # shape (n_steps + 1,)
    paths: np.ndarray  # shape (n_paths, n_steps + 1)
    params: dict[str, Any]
    stats: dict[str, Any]


def simulate_gbm(
    s0: float = 100.0,
    mu: float = 0.05,
    sigma: float = 0.2,
    t: float = 1.0,
    n_steps: int = 252,
    n_paths: int = 100,
    seed: int = 42,
) -> SimulationResult:
    """Simulate Geometric Brownian Motion price paths.

    The SDE

        dS_t = μ S_t dt + σ S_t dW_t

    admits the exact closed-form step

        S_{t+Δt} = S_t exp((μ − ½σ²)Δt + σ √Δt Z),  Z ~ N(0,1).

    Parameters
    ----------
    s0 :
        Initial spot price.
    mu :
        Annualized drift.
    sigma :
        Annualized volatility (diffusion coefficient).
    t :
        Horizon in years.
    n_steps :
        Number of discrete time steps.
    n_paths :
        Number of independent Monte Carlo paths.
    seed :
        Deterministic RNG seed (``numpy.random.default_rng``).

    Returns
    -------
    SimulationResult
        Times, paths, params, and summary stats suitable for umbrella JSON export.
    """
    if s0 <= 0:
        raise ValueError("s0 must be positive")
    if sigma < 0:
        raise ValueError("sigma must be non-negative")
    if t <= 0:
        raise ValueError("t must be positive")
    if n_steps < 1 or n_paths < 1:
        raise ValueError("n_steps and n_paths must be >= 1")

    rng = np.random.default_rng(seed)
    dt = t / n_steps
    times = np.linspace(0.0, t, n_steps + 1)

    z = rng.standard_normal((n_paths, n_steps))
    increments = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
    log_s = np.cumsum(increments, axis=1)
    log_s = np.concatenate([np.zeros((n_paths, 1)), log_s], axis=1)
    paths = s0 * np.exp(log_s)

    terminal = paths[:, -1]
    stats = {
        "mean_terminal": float(np.mean(terminal)),
        "std_terminal": float(np.std(terminal, ddof=1)) if n_paths > 1 else 0.0,
        "min_terminal": float(np.min(terminal)),
        "max_terminal": float(np.max(terminal)),
        "median_terminal": float(np.median(terminal)),
        "p05_terminal": float(np.percentile(terminal, 5)),
        "p95_terminal": float(np.percentile(terminal, 95)),
        "theoretical_mean": float(s0 * np.exp(mu * t)),
        "theoretical_var": float(
            (s0**2) * np.exp(2 * mu * t) * (np.exp(sigma**2 * t) - 1.0)
        ),
    }

    params = {
        "s0": float(s0),
        "mu": float(mu),
        "sigma": float(sigma),
        "t": float(t),
        "n_steps": int(n_steps),
        "n_paths": int(n_paths),
        "seed": int(seed),
        "model": "gbm",
        "scheme": "exact-log-euler",
    }

    return SimulationResult(times=times, paths=paths, params=params, stats=stats)
