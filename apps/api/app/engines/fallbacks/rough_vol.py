"""Rough Bergomi / rough volatility fallback."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..serialize import downsample_paths, downsample_times, to_jsonable


def _kernel(times: np.ndarray, hurst: float) -> np.ndarray:
    n = len(times) - 1
    alpha = hurst + 0.5
    k = np.zeros((n, n), dtype=float)
    for i in range(n):
        t_i = times[i + 1]
        for j in range(i + 1):
            t0, t1 = times[j], times[j + 1]
            if i == j:
                dt = t1 - t0
                k[i, j] = (dt**hurst) / (hurst + 0.5) if hurst > 0 else np.sqrt(dt)
            else:
                u0, u1 = t_i - t1, t_i - t0
                k[i, j] = max((u1**alpha - max(u0, 0.0) ** alpha) / alpha, 0.0)
    return k


def _inline(
    s0: float,
    mu: float,
    hurst: float,
    eta: float,
    rho: float,
    t: float,
    n_steps: int,
    n_paths: int,
    xi0_flat: float,
    seed: int | None,
) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(seed)
    times = np.linspace(0.0, t, n_steps + 1)
    dt = t / n_steps
    sqrt_dt = np.sqrt(dt)
    kernel = _kernel(times, hurst)
    w_v = rng.standard_normal((n_paths, n_steps)) * sqrt_dt
    w_ind = rng.standard_normal((n_paths, n_steps)) * sqrt_dt
    w_s = rho * w_v + np.sqrt(max(0.0, 1.0 - rho**2)) * w_ind
    z = w_v @ kernel.T
    z_full = np.concatenate([np.zeros((n_paths, 1)), z], axis=1)
    t_safe = np.maximum(times, 0.0)
    v = xi0_flat * np.exp(
        eta * np.sqrt(2.0 * hurst) * z_full - 0.5 * eta**2 * (t_safe ** (2.0 * hurst))
    )
    v = np.maximum(v, 1e-16)
    s = np.empty((n_paths, n_steps + 1))
    s[:, 0] = s0
    for i in range(n_steps):
        s[:, i + 1] = s[:, i] * np.exp((mu - 0.5 * v[:, i]) * dt + np.sqrt(v[:, i]) * w_s[:, i])
    return {"times": times, "S": s, "v": v}


def run(params: dict[str, Any]) -> dict[str, Any]:
    s0 = float(params.get("s0", 100.0))
    mu = float(params.get("mu", 0.0))
    hurst = float(params.get("hurst", 0.1))
    eta = float(params.get("eta", 1.5))
    rho = float(params.get("rho", -0.7))
    t = float(params.get("t", 1.0))
    n_steps = int(params.get("n_steps", 126))
    n_paths = int(params.get("n_paths", 4))
    xi0_flat = float(params.get("xi0_flat", 0.04))
    seed = params.get("seed", 42)
    seed = int(seed) if seed is not None else None

    source = "fallback-inline"
    try:
        from trading_model_math import simulate_rough_bergomi  # type: ignore

        raw = simulate_rough_bergomi(
            s0=s0,
            mu=mu,
            hurst=hurst,
            eta=eta,
            rho=rho,
            t=t,
            n_steps=n_steps,
            n_paths=n_paths,
            xi0_flat=xi0_flat,
            seed=seed,
        )
        source = "core-math"
    except Exception:
        raw = _inline(s0, mu, hurst, eta, rho, t, n_steps, n_paths, xi0_flat, seed)

    times = np.asarray(raw["times"])
    s = np.asarray(raw["S"])
    v = np.asarray(raw["v"])
    chart_s = downsample_paths(s, max_paths=min(6, n_paths), max_points=300)
    chart_v = downsample_paths(v, max_paths=chart_s.shape[0], max_points=chart_s.shape[1])
    chart_t = downsample_times(times, chart_s.shape[1])

    return to_jsonable(
        {
            "slug": "rough-vol",
            "engine": source,
            "params": {
                "s0": s0,
                "mu": mu,
                "hurst": hurst,
                "eta": eta,
                "rho": rho,
                "t": t,
                "n_steps": n_steps,
                "n_paths": n_paths,
                "xi0_flat": xi0_flat,
                "seed": seed,
            },
            "series": {"times": chart_t, "paths": chart_s, "variance": chart_v},
            "metrics": {
                "mean_terminal_s": float(s[:, -1].mean()),
                "mean_terminal_v": float(v[:, -1].mean()),
                "hurst": hurst,
            },
        }
    )
