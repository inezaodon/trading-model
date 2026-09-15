"""Monte Carlo portfolio VaR / CVaR fallback."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..serialize import to_jsonable

# Annualized vols / corr inspired by liquid ETF basket (research stub, not live data)
_DEFAULT_VOLS = {
    "QQQ": 0.22,
    "SPY": 0.16,
    "IWM": 0.24,
    "TLT": 0.18,
    "GLD": 0.15,
    "HYG": 0.10,
}


def _corr_matrix(n: int) -> np.ndarray:
    """Simple equicorrelation-style block with rate/commodity tilt."""
    c = np.full((n, n), 0.35)
    np.fill_diagonal(c, 1.0)
    if n >= 4:
        c[3, :3] = c[:3, 3] = -0.2  # TLT vs equities
    if n >= 5:
        c[4, :3] = c[:3, 4] = 0.1
    # Ensure PSD via nearest diagonal loading
    eigvals, eigvecs = np.linalg.eigh(c)
    eigvals = np.maximum(eigvals, 1e-8)
    c = eigvecs @ np.diag(eigvals) @ eigvecs.T
    d = np.sqrt(np.diag(c))
    c = c / np.outer(d, d)
    return c


def run(params: dict[str, Any]) -> dict[str, Any]:
    notional = float(params.get("notional", 1_000_000.0))
    horizon_days = int(params.get("horizon_days", 10))
    n_sims = int(params.get("n_sims", 20000))
    confidence = float(params.get("confidence", 0.95))
    tickers = list(params.get("tickers", ["QQQ", "SPY", "IWM", "TLT", "GLD", "HYG"]))
    weights = np.asarray(params.get("weights", [0.3, 0.25, 0.15, 0.15, 0.1, 0.05]), dtype=float)
    seed = params.get("seed", 99)
    seed = int(seed) if seed is not None else None

    n = len(tickers)
    if len(weights) != n:
        weights = np.ones(n) / n
    weights = weights / weights.sum()

    vols = np.array([_DEFAULT_VOLS.get(t, 0.2) for t in tickers], dtype=float)
    corr = _corr_matrix(n)
    cov = np.outer(vols, vols) * corr

    rng = np.random.default_rng(seed)
    # Horizon scaling from annual
    scale = np.sqrt(horizon_days / 252.0)
    chol = np.linalg.cholesky(cov)
    z = rng.standard_normal((n_sims, n))
    rets = (z @ chol.T) * scale  # approximate zero-mean Gaussian returns

    port_ret = rets @ weights
    pnl = notional * port_ret
    losses = -pnl  # positive = loss

    alpha = confidence
    var = float(np.quantile(losses, alpha))
    cvar = float(losses[losses >= var].mean()) if np.any(losses >= var) else var

    hist_counts, hist_edges = np.histogram(pnl, bins=50)

    return to_jsonable(
        {
            "slug": "var",
            "engine": "fallback-inline",
            "params": {
                "notional": notional,
                "horizon_days": horizon_days,
                "n_sims": n_sims,
                "confidence": confidence,
                "tickers": tickers,
                "weights": weights.tolist(),
                "seed": seed,
            },
            "series": {
                "hist_edges": hist_edges,
                "hist_counts": hist_counts,
                "sample_pnl": pnl[:300],
            },
            "metrics": {
                "var": var,
                "cvar": cvar,
                "mean_pnl": float(pnl.mean()),
                "std_pnl": float(pnl.std()),
                "var_pct_notional": 100.0 * var / notional,
                "cvar_pct_notional": 100.0 * cvar / notional,
            },
        }
    )
