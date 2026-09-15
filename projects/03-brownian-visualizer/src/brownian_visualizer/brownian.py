"""Wiener process (standard and scaled Brownian motion) in 1D and 2D.

A standard Brownian motion (Wiener process) \\(W_t\\) satisfies:

- \\(W_0 = 0\\) a.s.
- Independent increments
- \\(W_t - W_s \\sim \\mathcal{N}(0, t-s)\\) for \\(t > s\\)
- Almost-surely continuous paths

Discretization on a uniform grid with step \\(\\Delta t = T / n\\):

    W_{k\\Delta t} = W_{(k-1)\\Delta t} + \\sqrt{\\Delta t}\\, Z_k,\\quad Z_k \\sim N(0,1)

Scaled BM with drift: \\(X_t = x_0 + \\mu t + \\sigma W_t\\).
"""

from __future__ import annotations

from typing import Any

import numpy as np


def _validate_common(t: float, n_steps: int, n_paths: int) -> None:
    if t <= 0:
        raise ValueError("t must be positive")
    if n_steps < 1 or n_paths < 1:
        raise ValueError("n_steps and n_paths must be >= 1")


def simulate_brownian_1d(
    t: float = 1.0,
    n_steps: int = 252,
    n_paths: int = 1,
    seed: int | None = None,
) -> dict[str, Any]:
    """Simulate standard 1D Wiener process paths.

    Parameters
    ----------
    t :
        Horizon.
    n_steps :
        Number of time steps (grid has ``n_steps + 1`` points including 0).
    n_paths :
        Independent sample paths.
    seed :
        RNG seed for reproducibility.

    Returns
    -------
    dict
        ``times`` (n_steps+1,), ``W`` (n_paths, n_steps+1), ``params``.
    """
    _validate_common(t, n_steps, n_paths)
    rng = np.random.default_rng(seed)
    dt = t / n_steps
    times = np.linspace(0.0, t, n_steps + 1)
    z = rng.standard_normal((n_paths, n_steps))
    increments = np.sqrt(dt) * z
    w = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(increments, axis=1)], axis=1)
    return {
        "times": times,
        "W": w,
        "dim": 1,
        "kind": "standard_bm_1d",
        "params": {"t": t, "n_steps": n_steps, "n_paths": n_paths, "seed": seed},
    }


def simulate_scaled_brownian(
    x0: float = 0.0,
    mu: float = 0.0,
    sigma: float = 1.0,
    t: float = 1.0,
    n_steps: int = 252,
    n_paths: int = 1,
    seed: int | None = None,
) -> dict[str, Any]:
    """Simulate scaled Brownian motion with drift: X_t = x0 + μt + σ W_t.

    Parameters
    ----------
    x0 :
        Initial level.
    mu :
        Drift.
    sigma :
        Diffusion scale (must be non-negative).
    t, n_steps, n_paths, seed :
        As in :func:`simulate_brownian_1d`.
    """
    if sigma < 0:
        raise ValueError("sigma must be non-negative")
    base = simulate_brownian_1d(t=t, n_steps=n_steps, n_paths=n_paths, seed=seed)
    times = base["times"]
    w = base["W"]
    x = x0 + mu * times[np.newaxis, :] + sigma * w
    return {
        "times": times,
        "W": w,
        "X": x,
        "dim": 1,
        "kind": "scaled_bm_1d",
        "params": {
            "x0": x0,
            "mu": mu,
            "sigma": sigma,
            "t": t,
            "n_steps": n_steps,
            "n_paths": n_paths,
            "seed": seed,
        },
    }


def simulate_brownian_2d(
    t: float = 1.0,
    n_steps: int = 252,
    n_paths: int = 1,
    seed: int | None = None,
    sigma_x: float = 1.0,
    sigma_y: float = 1.0,
    rho: float = 0.0,
) -> dict[str, Any]:
    """Simulate a 2D Wiener process (planar Brownian motion).

    Components are correlated standard BMs:

        dW^x = σ_x dB^1
        dW^y = σ_y (ρ dB^1 + √(1−ρ²) dB^2)

    with independent standard BMs B¹, B².

    Returns
    -------
    dict
        ``times``, ``X`` / ``Y`` shaped (n_paths, n_steps+1), ``params``.
    """
    _validate_common(t, n_steps, n_paths)
    if abs(rho) > 1:
        raise ValueError("rho must be in [-1, 1]")
    if sigma_x < 0 or sigma_y < 0:
        raise ValueError("sigma_x and sigma_y must be non-negative")

    rng = np.random.default_rng(seed)
    dt = t / n_steps
    times = np.linspace(0.0, t, n_steps + 1)
    z1 = rng.standard_normal((n_paths, n_steps))
    z2 = rng.standard_normal((n_paths, n_steps))
    dx = sigma_x * np.sqrt(dt) * z1
    dy = sigma_y * np.sqrt(dt) * (rho * z1 + np.sqrt(max(0.0, 1.0 - rho**2)) * z2)
    x = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(dx, axis=1)], axis=1)
    y = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(dy, axis=1)], axis=1)
    return {
        "times": times,
        "X": x,
        "Y": y,
        "dim": 2,
        "kind": "standard_bm_2d",
        "params": {
            "t": t,
            "n_steps": n_steps,
            "n_paths": n_paths,
            "seed": seed,
            "sigma_x": sigma_x,
            "sigma_y": sigma_y,
            "rho": rho,
        },
    }
