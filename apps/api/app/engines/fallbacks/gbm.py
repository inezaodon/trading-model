"""GBM fallback — prefers packages.core-math when installed."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..serialize import downsample_paths, downsample_times, to_jsonable


def _simulate_inline(
    s0: float,
    mu: float,
    sigma: float,
    t: float,
    n_steps: int,
    n_paths: int,
    seed: int | None,
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    dt = t / n_steps
    times = np.linspace(0.0, t, n_steps + 1)
    z = rng.standard_normal((n_paths, n_steps))
    increments = (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
    log_s = np.cumsum(increments, axis=1)
    log_s = np.concatenate([np.zeros((n_paths, 1)), log_s], axis=1)
    s = s0 * np.exp(log_s)
    return {"times": times, "S": s}


def run(params: dict[str, Any]) -> dict[str, Any]:
    s0 = float(params.get("s0", 100.0))
    mu = float(params.get("mu", 0.08))
    sigma = float(params.get("sigma", 0.25))
    t = float(params.get("t", 1.0))
    n_steps = int(params.get("n_steps", 252))
    n_paths = int(params.get("n_paths", 8))
    seed = params.get("seed", 42)
    seed = int(seed) if seed is not None else None

    source = "fallback-inline"
    try:
        from trading_model_math import simulate_gbm  # type: ignore

        raw = simulate_gbm(
            s0=s0, mu=mu, sigma=sigma, t=t, n_steps=n_steps, n_paths=n_paths, seed=seed
        )
        source = "core-math"
    except Exception:
        raw = _simulate_inline(s0, mu, sigma, t, n_steps, n_paths, seed)

    times = np.asarray(raw["times"], dtype=float)
    paths = downsample_paths(np.asarray(raw["S"], dtype=float))
    times = downsample_times(times, paths.shape[1])
    terminal = np.asarray(raw["S"], dtype=float)[:, -1]

    return to_jsonable(
        {
            "slug": "gbm",
            "engine": source,
            "params": {
                "s0": s0,
                "mu": mu,
                "sigma": sigma,
                "t": t,
                "n_steps": n_steps,
                "n_paths": n_paths,
                "seed": seed,
            },
            "series": {"times": times, "paths": paths},
            "metrics": {
                "mean_terminal": float(terminal.mean()),
                "std_terminal": float(terminal.std()),
                "min_terminal": float(terminal.min()),
                "max_terminal": float(terminal.max()),
            },
        }
    )
