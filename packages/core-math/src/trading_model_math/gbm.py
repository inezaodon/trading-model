"""Geometric Brownian Motion (classical Black–Scholes / Itô baseline).

Simulates the SDE

    dS_t = μ S_t dt + σ S_t dW_t

via the exact log-Euler solution

    S_{t+Δt} = S_t exp((μ − ½σ²)Δt + σ √Δt Z),  Z ~ N(0,1).
"""

from __future__ import annotations

from typing import Any

import numpy as np


def simulate_gbm(
    s0: float = 100.0,
    mu: float = 0.05,
    sigma: float = 0.2,
    t: float = 1.0,
    n_steps: int = 252,
    n_paths: int = 1,
    seed: int | None = None,
) -> dict[str, Any]:
    """Simulate GBM price paths.

    Parameters
    ----------
    s0 :
        Initial spot.
    mu :
        Drift under the chosen measure.
    sigma :
        Constant diffusion coefficient.
    t :
        Horizon in years.
    n_steps :
        Number of time steps.
    n_paths :
        Number of independent Monte Carlo paths.
    seed :
        RNG seed for reproducibility.

    Returns
    -------
    dict
        Keys ``times`` (shape ``n_steps+1``) and ``S`` (shape ``n_paths × n_steps+1``).
        Variance slot ``v`` is filled with constant ``σ²`` for schema compatibility.
    """
    if s0 <= 0:
        raise ValueError("s0 must be positive")
    if sigma < 0:
        raise ValueError("sigma must be non-negative")
    if n_steps < 1 or n_paths < 1:
        raise ValueError("n_steps and n_paths must be >= 1")

    rng = np.random.default_rng(seed)
    dt = t / n_steps
    times = np.linspace(0.0, t, n_steps + 1)

    z = rng.standard_normal((n_paths, n_steps))
    increments = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
    log_s = np.cumsum(increments, axis=1)
    log_s = np.concatenate([np.zeros((n_paths, 1)), log_s], axis=1)
    s = s0 * np.exp(log_s)
    v = np.full_like(s, sigma**2)

    return {"times": times, "S": s, "v": v, "params": {"s0": s0, "mu": mu, "sigma": sigma, "t": t}}
