"""Z-score / spread mean-reversion signal demo (research only).

Given a fitted (or assumed) OU process, the standardized deviation from
the long-run mean is

    z_t = (X_t − θ) / σ_∞ ,   σ_∞ = σ / √(2κ)

Trading rules (demo, not advice):

- Enter long when z < −entry
- Enter short when z > +entry
- Exit when |z| < exit

Also supports a rolling empirical z-score when no model params are given.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ornstein_uhlenbeck.simulate import stationary_std


def model_zscore(
    series: np.ndarray,
    theta: float,
    kappa: float,
    sigma: float,
) -> np.ndarray:
    """OU model z-score using stationary std."""
    x = np.asarray(series, dtype=float).ravel()
    ss = stationary_std(kappa, sigma)
    if ss <= 0:
        raise ValueError("stationary std must be positive")
    return (x - theta) / ss


def rolling_zscore(series: np.ndarray, window: int = 60) -> np.ndarray:
    """Empirical rolling z-score; leading points that lack history are NaN."""
    x = np.asarray(series, dtype=float).ravel()
    if window < 2:
        raise ValueError("window must be >= 2")
    if x.size < window:
        raise ValueError("series shorter than rolling window")

    z = np.full(x.size, np.nan, dtype=float)
    # Cumulative sums for O(n) rolling mean/var
    c1 = np.concatenate([[0.0], np.cumsum(x)])
    c2 = np.concatenate([[0.0], np.cumsum(x * x)])
    for i in range(window - 1, x.size):
        s = c1[i + 1] - c1[i + 1 - window]
        q = c2[i + 1] - c2[i + 1 - window]
        mean = s / window
        var = q / window - mean * mean
        std = np.sqrt(max(var, 0.0))
        z[i] = 0.0 if std < 1e-15 else (x[i] - mean) / std
    return z


def zscore_signals(
    series: np.ndarray,
    *,
    theta: float | None = None,
    kappa: float | None = None,
    sigma: float | None = None,
    entry: float = 1.5,
    exit: float = 0.25,
    rolling_window: int | None = None,
) -> dict[str, Any]:
    """Build z-scores and discrete position signals (−1 / 0 / +1).

    If ``kappa``/``theta``/``sigma`` are provided, uses model z-scores.
    Otherwise (or if ``rolling_window`` is set) uses rolling empirical z.
    """
    x = np.asarray(series, dtype=float).ravel()
    if x.size < 2:
        raise ValueError("series must contain at least 2 observations")
    if entry <= 0:
        raise ValueError("entry must be positive")
    if exit < 0 or exit >= entry:
        raise ValueError("exit must satisfy 0 <= exit < entry")

    use_rolling = rolling_window is not None or any(
        v is None for v in (theta, kappa, sigma)
    )
    if use_rolling:
        window = int(rolling_window or min(60, max(10, x.size // 5)))
        z = rolling_zscore(x, window=window)
        mode = "rolling"
        model = {"rolling_window": window}
    else:
        assert theta is not None and kappa is not None and sigma is not None
        z = model_zscore(x, theta=theta, kappa=kappa, sigma=sigma)
        mode = "model"
        model = {
            "theta": float(theta),
            "kappa": float(kappa),
            "sigma": float(sigma),
            "stationary_std": stationary_std(kappa, sigma),
        }

    positions = np.zeros(x.size, dtype=int)
    pos = 0
    for i, zi in enumerate(z):
        if not np.isfinite(zi):
            positions[i] = pos
            continue
        if pos == 0:
            if zi <= -entry:
                pos = 1
            elif zi >= entry:
                pos = -1
        elif pos == 1 and zi >= -exit:
            pos = 0
        elif pos == -1 and zi <= exit:
            pos = 0
        positions[i] = pos

    # Position known at close of prior bar earns next ΔX (research metric only)
    pnl = np.zeros(x.size, dtype=float)
    pnl[1:] = positions[:-1] * np.diff(x)
    equity = np.cumsum(pnl)

    finite_z = z[np.isfinite(z)]
    n_entries = int(np.sum(np.diff(positions, prepend=0) != 0) // 2 + (positions[0] != 0))

    return {
        "mode": mode,
        "model": model,
        "entry": float(entry),
        "exit": float(exit),
        "zscore": z,
        "positions": positions,
        "pnl": pnl,
        "equity": equity,
        "metrics": {
            "n_obs": int(x.size),
            "n_finite_z": int(finite_z.size),
            "mean_z": float(np.mean(finite_z)) if finite_z.size else None,
            "std_z": float(np.std(finite_z, ddof=1)) if finite_z.size > 1 else None,
            "total_pnl": float(equity[-1]),
            "max_drawdown": float(_max_drawdown(equity)),
            "n_position_changes": int(np.sum(np.diff(positions, prepend=0) != 0)),
            "n_entries_approx": n_entries,
            "time_in_market": float(np.mean(positions != 0)),
        },
        "disclaimer": (
            "Research / education only. Not investment advice. "
            "No live order routing."
        ),
    }


def _max_drawdown(equity: np.ndarray) -> float:
    peak = np.maximum.accumulate(equity)
    dd = equity - peak
    return float(dd.min()) if dd.size else 0.0
