"""Exact and Euler discretizations of the Ornstein–Uhlenbeck SDE.

    dX_t = κ(θ − X_t) dt + σ dW_t

Exact transition (Vasicek):

    X_{t+Δt} = X_t e^{-κ Δt} + θ(1 − e^{-κ Δt})
               + σ √((1 − e^{-2κ Δt}) / (2κ)) Z,   Z ~ N(0,1)

When κ → 0 the diffusion term collapses to σ √Δt (Brownian limit).
"""

from __future__ import annotations

from typing import Any, Literal

import numpy as np

Scheme = Literal["exact", "euler"]


def _diffusion_scale(kappa: float, sigma: float, dt: float) -> float:
    """Conditional std of the OU increment over ``dt``."""
    if abs(kappa) < 1e-12:
        return float(sigma * np.sqrt(dt))
    return float(sigma * np.sqrt((1.0 - np.exp(-2.0 * kappa * dt)) / (2.0 * kappa)))


def simulate_ou(
    x0: float = 0.0,
    kappa: float = 3.0,
    theta: float = 0.0,
    sigma: float = 0.5,
    t: float = 1.0,
    n_steps: int = 252,
    n_paths: int = 1,
    scheme: Scheme = "exact",
    seed: int | None = None,
) -> dict[str, Any]:
    """Simulate Ornstein–Uhlenbeck paths.

    Parameters
    ----------
    x0 :
        Initial level.
    kappa :
        Mean-reversion speed (must be >= 0).
    theta :
        Long-run mean.
    sigma :
        Diffusion coefficient (must be >= 0).
    t :
        Horizon (same units as ``kappa`` inverse, typically years).
    n_steps :
        Number of time steps.
    n_paths :
        Independent Monte Carlo paths.
    scheme :
        ``exact`` (default) or Euler–Maruyama ``euler``.
    seed :
        RNG seed for reproducibility.

    Returns
    -------
    dict
        ``times`` (n_steps+1,), ``X`` (n_paths, n_steps+1), ``params``.
    """
    if kappa < 0:
        raise ValueError("kappa must be non-negative")
    if sigma < 0:
        raise ValueError("sigma must be non-negative")
    if n_steps < 1 or n_paths < 1:
        raise ValueError("n_steps and n_paths must be >= 1")
    if t <= 0:
        raise ValueError("t must be positive")
    if scheme not in ("exact", "euler"):
        raise ValueError("scheme must be 'exact' or 'euler'")

    rng = np.random.default_rng(seed)
    dt = t / n_steps
    times = np.linspace(0.0, t, n_steps + 1)
    z = rng.standard_normal((n_paths, n_steps))

    x = np.empty((n_paths, n_steps + 1), dtype=float)
    x[:, 0] = x0

    if scheme == "exact":
        decay = float(np.exp(-kappa * dt))
        pull = theta * (1.0 - decay)
        scale = _diffusion_scale(kappa, sigma, dt)
        for i in range(n_steps):
            x[:, i + 1] = x[:, i] * decay + pull + scale * z[:, i]
    else:
        sqrt_dt = float(np.sqrt(dt))
        for i in range(n_steps):
            x[:, i + 1] = (
                x[:, i]
                + kappa * (theta - x[:, i]) * dt
                + sigma * sqrt_dt * z[:, i]
            )

    return {
        "times": times,
        "X": x,
        "params": {
            "x0": float(x0),
            "kappa": float(kappa),
            "theta": float(theta),
            "sigma": float(sigma),
            "t": float(t),
            "n_steps": int(n_steps),
            "n_paths": int(n_paths),
            "scheme": scheme,
            "seed": seed,
        },
    }


def stationary_std(kappa: float, sigma: float) -> float:
    """Stationary standard deviation σ / √(2κ)."""
    if kappa <= 0:
        raise ValueError("kappa must be positive for a finite stationary variance")
    return float(sigma / np.sqrt(2.0 * kappa))
