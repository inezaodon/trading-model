"""Brownian motion / random walk visualizer fallback."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..serialize import downsample_paths, downsample_times, to_jsonable


def run(params: dict[str, Any]) -> dict[str, Any]:
    t = float(params.get("t", 1.0))
    n_steps = int(params.get("n_steps", 500))
    n_paths = int(params.get("n_paths", 6))
    drift = float(params.get("drift", 0.0))
    diffusion = float(params.get("diffusion", 1.0))
    seed = params.get("seed", 7)
    seed = int(seed) if seed is not None else None

    rng = np.random.default_rng(seed)
    dt = t / n_steps
    times = np.linspace(0.0, t, n_steps + 1)
    z = rng.standard_normal((n_paths, n_steps))
    increments = drift * dt + diffusion * np.sqrt(dt) * z
    paths = np.concatenate([np.zeros((n_paths, 1)), np.cumsum(increments, axis=1)], axis=1)

    # Quadratic variation along first path
    dq = np.diff(paths[0]) ** 2
    qv = np.concatenate([[0.0], np.cumsum(dq)])

    chart_paths = downsample_paths(paths)
    chart_times = downsample_times(times, chart_paths.shape[1])
    chart_qv = downsample_times(qv, chart_paths.shape[1])

    return to_jsonable(
        {
            "slug": "brownian",
            "engine": "fallback-inline",
            "params": {
                "t": t,
                "n_steps": n_steps,
                "n_paths": n_paths,
                "drift": drift,
                "diffusion": diffusion,
                "seed": seed,
            },
            "series": {
                "times": chart_times,
                "paths": chart_paths,
                "quadratic_variation": chart_qv,
            },
            "metrics": {
                "terminal_mean": float(paths[:, -1].mean()),
                "terminal_var": float(paths[:, -1].var()),
                "theoretical_var": float(diffusion**2 * t),
                "qv_final": float(qv[-1]),
                "theoretical_qv": float(diffusion**2 * t),
            },
        }
    )
