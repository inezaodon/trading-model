"""VaR and Expected Shortfall (CVaR) from simulated P&L."""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np


def compute_var_es(
    pnl: np.ndarray | Sequence[float],
    confidence: float = 0.95,
) -> dict[str, float]:
    """Historical / Monte Carlo VaR and ES from a P&L sample.

    Convention (loss-positive risk numbers):
    - Sort P&L ascending (worst losses first / most negative).
    - VaR_α = − quantile_{1−α}(PnL)  so a loss shows as positive VaR.
    - ES_α  = − mean(PnL | PnL ≤ −VaR)  (average loss beyond VaR).

    Parameters
    ----------
    pnl :
        Simulated portfolio profit-and-loss (positive = gain).
    confidence :
        e.g. 0.95 or 0.99.
    """
    x = np.asarray(pnl, dtype=float).reshape(-1)
    if x.size < 2:
        raise ValueError("need at least 2 P&L scenarios")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")

    alpha = 1.0 - confidence
    q = float(np.quantile(x, alpha, method="linear"))
    var = -q
    tail = x[x <= q]
    if tail.size == 0:
        # Degenerate: all mass above quantile edge case
        es = var
    else:
        es = float(-tail.mean())

    return {
        "confidence": float(confidence),
        "var": float(var),
        "es": float(es),
        "quantile_pnl": q,
        "n_tail": int(tail.size),
    }


def summarize_pnl(pnl: np.ndarray | Sequence[float]) -> dict[str, float]:
    """Basic P&L distribution summary for API / charts."""
    x = np.asarray(pnl, dtype=float).reshape(-1)
    return {
        "mean": float(x.mean()),
        "std": float(x.std(ddof=1)) if x.size > 1 else 0.0,
        "min": float(x.min()),
        "max": float(x.max()),
        "p01": float(np.quantile(x, 0.01)),
        "p05": float(np.quantile(x, 0.05)),
        "p50": float(np.quantile(x, 0.50)),
        "p95": float(np.quantile(x, 0.95)),
        "p99": float(np.quantile(x, 0.99)),
    }


def histogram_bins(
    pnl: np.ndarray,
    n_bins: int = 50,
) -> dict[str, Any]:
    """Chart-ready histogram of P&L."""
    counts, edges = np.histogram(pnl, bins=n_bins)
    centers = 0.5 * (edges[:-1] + edges[1:])
    return {
        "counts": counts.astype(int).tolist(),
        "bin_edges": edges.tolist(),
        "bin_centers": centers.tolist(),
    }
