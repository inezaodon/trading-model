"""Ornstein–Uhlenbeck mean-reversion fallback (exact discretization)."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..serialize import downsample_paths, downsample_times, to_jsonable


def run(params: dict[str, Any]) -> dict[str, Any]:
    x0 = float(params.get("x0", 0.5))
    kappa = float(params.get("kappa", 3.0))
    theta = float(params.get("theta", 0.0))
    sigma = float(params.get("sigma", 0.4))
    t = float(params.get("t", 2.0))
    n_steps = int(params.get("n_steps", 500))
    n_paths = int(params.get("n_paths", 8))
    seed = params.get("seed", 11)
    seed = int(seed) if seed is not None else None

    rng = np.random.default_rng(seed)
    dt = t / n_steps
    times = np.linspace(0.0, t, n_steps + 1)
    paths = np.empty((n_paths, n_steps + 1), dtype=float)
    paths[:, 0] = x0

    # Exact OU transition
    exp_k = np.exp(-kappa * dt)
    var = (sigma**2) * (1.0 - np.exp(-2.0 * kappa * dt)) / (2.0 * kappa) if kappa > 1e-12 else sigma**2 * dt
    std = np.sqrt(max(var, 0.0))

    for i in range(n_steps):
        z = rng.standard_normal(n_paths)
        paths[:, i + 1] = theta + (paths[:, i] - theta) * exp_k + std * z

    chart_paths = downsample_paths(paths)
    chart_times = downsample_times(times, chart_paths.shape[1])
    mean_path = paths.mean(axis=0)
    chart_mean = downsample_times(mean_path, chart_paths.shape[1])

    return to_jsonable(
        {
            "slug": "ou",
            "engine": "fallback-inline",
            "params": {
                "x0": x0,
                "kappa": kappa,
                "theta": theta,
                "sigma": sigma,
                "t": t,
                "n_steps": n_steps,
                "n_paths": n_paths,
                "seed": seed,
            },
            "series": {
                "times": chart_times,
                "paths": chart_paths,
                "mean": chart_mean,
                "theta_line": [theta] * len(chart_times),
            },
            "metrics": {
                "terminal_mean": float(paths[:, -1].mean()),
                "terminal_std": float(paths[:, -1].std()),
                "half_life": float(np.log(2.0) / kappa) if kappa > 0 else None,
                "stationary_var": float(sigma**2 / (2.0 * kappa)) if kappa > 0 else None,
            },
        }
    )
