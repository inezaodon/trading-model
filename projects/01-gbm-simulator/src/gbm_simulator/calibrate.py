"""Estimate GBM drift and volatility from historical prices."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


def load_price_csv(
    path: str | Path,
    price_col: str | None = None,
) -> np.ndarray:
    """Load a 1-D price series from CSV.

    Accepts either a single numeric column or a headered CSV with a close/price
    column (``close``, ``adj_close``, ``adj close``, ``price``, or last column).
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"CSV not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        first = f.readline().strip()

    tokens = [t.strip().lower() for t in first.split(",")]
    has_header = any(not _is_float(tok) for tok in tokens)

    if has_header:
        data = np.genfromtxt(
            path, delimiter=",", names=True, dtype=None, encoding="utf-8"
        )
        names = [n.lower() for n in data.dtype.names]  # type: ignore[union-attr]
        col = _resolve_price_column(names, price_col)
        prices = np.asarray(data[col], dtype=float)
    else:
        raw = np.loadtxt(path, delimiter=",")
        if raw.ndim == 1:
            prices = raw.astype(float)
        else:
            prices = raw[:, -1].astype(float)

    if prices.size < 2:
        raise ValueError("need at least two prices to estimate returns")
    if np.any(prices <= 0) or np.any(~np.isfinite(prices)):
        raise ValueError("prices must be positive and finite")
    return prices


def estimate_mu_sigma(
    prices: np.ndarray,
    dt: float = 1.0 / 252.0,
) -> dict[str, Any]:
    """MLE-style annualized μ and σ from log returns.

    For GBM, log returns over Δt are i.i.d. normal:

        r_i = log(S_{i}/S_{i-1}) ~ N((μ − ½σ²)Δt, σ² Δt)

    Unbiased sample variance of r gives σ; μ is recovered from the mean.
    """
    prices = np.asarray(prices, dtype=float)
    if prices.ndim != 1 or prices.size < 2:
        raise ValueError("prices must be a 1-D array with length >= 2")
    if dt <= 0:
        raise ValueError("dt must be positive")

    log_rets = np.diff(np.log(prices))
    mean_r = float(np.mean(log_rets))
    var_r = float(np.var(log_rets, ddof=1)) if log_rets.size > 1 else 0.0
    sigma = float(np.sqrt(var_r / dt))
    mu = float(mean_r / dt + 0.5 * sigma**2)

    return {
        "mu": mu,
        "sigma": sigma,
        "n_obs": int(prices.size),
        "n_returns": int(log_rets.size),
        "dt": float(dt),
        "mean_log_return": mean_r,
        "std_log_return": float(np.sqrt(var_r)),
        "s0": float(prices[-1]),
        "s_start": float(prices[0]),
    }


def _is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def _resolve_price_column(names: list[str], price_col: str | None) -> str:
    if price_col is not None:
        key = price_col.lower()
        for n in names:
            if n == key:
                return n
        raise KeyError(f"column {price_col!r} not in {names}")

    preferred = ("close", "adj_close", "adjclose", "price", "last")
    for cand in preferred:
        for n in names:
            if n.replace(" ", "") == cand:
                return n
    return names[-1]
