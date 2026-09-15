"""Monte Carlo European option pricing fallback."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..serialize import to_jsonable


def run(params: dict[str, Any]) -> dict[str, Any]:
    s0 = float(params.get("s0", 100.0))
    k = float(params.get("k", 100.0))
    r = float(params.get("r", 0.03))
    sigma = float(params.get("sigma", 0.2))
    t = float(params.get("t", 1.0))
    n_steps = int(params.get("n_steps", 100))
    n_paths = int(params.get("n_paths", 20000))
    option = str(params.get("option", "call")).lower()
    seed = params.get("seed", 42)
    seed = int(seed) if seed is not None else None

    rng = np.random.default_rng(seed)
    dt = t / max(n_steps, 1)
    z = rng.standard_normal((n_paths, n_steps))
    increments = (r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
    log_s = np.sum(increments, axis=1)
    s_t = s0 * np.exp(log_s)

    if option == "put":
        payoff = np.maximum(k - s_t, 0.0)
    else:
        payoff = np.maximum(s_t - k, 0.0)
        option = "call"

    discount = np.exp(-r * t)
    price = float(discount * payoff.mean())
    se = float(discount * payoff.std(ddof=1) / np.sqrt(n_paths))

    # Black–Scholes closed form for reference
    from math import erf, sqrt, log, exp

    def _ncdf(x: float) -> float:
        return 0.5 * (1.0 + erf(x / sqrt(2.0)))

    d1 = (log(s0 / k) + (r + 0.5 * sigma**2) * t) / (sigma * sqrt(t))
    d2 = d1 - sigma * sqrt(t)
    if option == "call":
        bs = s0 * _ncdf(d1) - k * exp(-r * t) * _ncdf(d2)
    else:
        bs = k * exp(-r * t) * _ncdf(-d2) - s0 * _ncdf(-d1)

    # Histogram of terminal prices for chart
    hist_counts, hist_edges = np.histogram(s_t, bins=40)

    return to_jsonable(
        {
            "slug": "mc-options",
            "engine": "fallback-inline",
            "params": {
                "s0": s0,
                "k": k,
                "r": r,
                "sigma": sigma,
                "t": t,
                "n_steps": n_steps,
                "n_paths": n_paths,
                "option": option,
                "seed": seed,
            },
            "series": {
                "hist_edges": hist_edges,
                "hist_counts": hist_counts,
                "sample_payoffs": payoff[:200],
            },
            "metrics": {
                "price": price,
                "std_error": se,
                "bs_reference": float(bs),
                "abs_error_vs_bs": abs(price - bs),
                "mean_terminal": float(s_t.mean()),
            },
        }
    )
