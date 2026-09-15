"""Heston stochastic volatility fallback."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..serialize import downsample_paths, downsample_times, to_jsonable


def _euler(
    s0: float,
    v0: float,
    mu: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    t: float,
    n_steps: int,
    n_paths: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    dt = t / n_steps
    sqrt_dt = np.sqrt(dt)
    times = np.linspace(0.0, t, n_steps + 1)
    s = np.empty((n_paths, n_steps + 1))
    v = np.empty((n_paths, n_steps + 1))
    s[:, 0] = s0
    v[:, 0] = v0
    z_v = rng.standard_normal((n_paths, n_steps))
    z_ind = rng.standard_normal((n_paths, n_steps))
    z_s = rho * z_v + np.sqrt(max(0.0, 1.0 - rho**2)) * z_ind
    for i in range(n_steps):
        v_pos = np.maximum(v[:, i], 0.0)
        sqrt_v = np.sqrt(v_pos)
        v[:, i + 1] = np.maximum(
            v[:, i] + kappa * (theta - v_pos) * dt + xi * sqrt_v * sqrt_dt * z_v[:, i],
            0.0,
        )
        s[:, i + 1] = s[:, i] * np.exp((mu - 0.5 * v_pos) * dt + sqrt_v * sqrt_dt * z_s[:, i])
    return times, s, v


def run(params: dict[str, Any]) -> dict[str, Any]:
    s0 = float(params.get("s0", 100.0))
    v0 = float(params.get("v0", 0.04))
    mu = float(params.get("mu", 0.05))
    kappa = float(params.get("kappa", 2.0))
    theta = float(params.get("theta", 0.04))
    xi = float(params.get("xi", 0.5))
    rho = float(params.get("rho", -0.7))
    t = float(params.get("t", 1.0))
    n_steps = int(params.get("n_steps", 252))
    n_paths = int(params.get("n_paths", 6))
    scheme = str(params.get("scheme", "qe"))
    seed = params.get("seed", 42)
    seed = int(seed) if seed is not None else None

    source = "fallback-inline"
    try:
        from trading_model_math import simulate_heston  # type: ignore

        raw = simulate_heston(
            s0=s0,
            v0=v0,
            mu=mu,
            kappa=kappa,
            theta=theta,
            xi=xi,
            rho=rho,
            t=t,
            n_steps=n_steps,
            n_paths=n_paths,
            scheme=scheme if scheme in ("qe", "euler") else "qe",
            seed=seed,
        )
        times = np.asarray(raw["times"])
        s = np.asarray(raw["S"])
        v = np.asarray(raw["v"])
        source = "core-math"
    except Exception:
        rng = np.random.default_rng(seed)
        times, s, v = _euler(s0, v0, mu, kappa, theta, xi, rho, t, n_steps, n_paths, rng)

    chart_s = downsample_paths(s)
    chart_v = downsample_paths(v, max_paths=chart_s.shape[0], max_points=chart_s.shape[1])
    chart_t = downsample_times(times, chart_s.shape[1])

    return to_jsonable(
        {
            "slug": "heston",
            "engine": source,
            "params": {
                "s0": s0,
                "v0": v0,
                "mu": mu,
                "kappa": kappa,
                "theta": theta,
                "xi": xi,
                "rho": rho,
                "t": t,
                "n_steps": n_steps,
                "n_paths": n_paths,
                "scheme": scheme,
                "seed": seed,
            },
            "series": {"times": chart_t, "paths": chart_s, "variance": chart_v},
            "metrics": {
                "mean_terminal_s": float(s[:, -1].mean()),
                "mean_terminal_v": float(v[:, -1].mean()),
                "corr_dlogS_dv": float(
                    np.corrcoef(
                        np.diff(np.log(np.maximum(s[0], 1e-12))),
                        np.diff(v[0]),
                    )[0, 1]
                )
                if s.shape[1] > 2
                else None,
            },
        }
    )
