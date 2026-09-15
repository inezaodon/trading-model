"""Portfolio weights and P&L mapping from asset log-return scenarios."""

from __future__ import annotations

from typing import Sequence

import numpy as np


def normalize_weights(weights: Sequence[float] | np.ndarray) -> np.ndarray:
    """Return weights that sum to 1; raise if empty or all-zero."""
    w = np.asarray(weights, dtype=float).reshape(-1)
    if w.size == 0:
        raise ValueError("weights must be non-empty")
    s = float(w.sum())
    if abs(s) < 1e-15:
        raise ValueError("weights must not sum to zero")
    return w / s


def portfolio_log_to_pnl(
    asset_log_returns: np.ndarray,
    weights: Sequence[float] | np.ndarray,
    portfolio_value: float = 1_000_000.0,
) -> np.ndarray:
    """Map multi-asset log-returns → portfolio P&L (currency units).

    Approximate simple portfolio return as ``w · (exp(r) − 1)``, then
    ``PnL = V0 * R``. Valid for moderate horizons; educational MC VaR.
    """
    if portfolio_value <= 0:
        raise ValueError("portfolio_value must be positive")
    r = np.asarray(asset_log_returns, dtype=float)
    if r.ndim != 2:
        raise ValueError("asset_log_returns must be (n_scenarios × n_assets)")
    w = normalize_weights(weights)
    if w.size != r.shape[1]:
        raise ValueError(
            f"weights length {w.size} != n_assets {r.shape[1]}"
        )
    simple = np.exp(r) - 1.0
    port_ret = simple @ w
    return portfolio_value * port_ret


def equal_weights(n: int) -> np.ndarray:
    if n < 1:
        raise ValueError("n must be >= 1")
    return np.full(n, 1.0 / n)
