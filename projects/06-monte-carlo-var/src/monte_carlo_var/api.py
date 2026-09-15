"""JSON-friendly API entry used by the umbrella backend.

``POST /api/v1/var/run`` → ``run_var(params)``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import numpy as np

from .data import DEFAULT_TICKERS, load_portfolio_returns
from .engine import compute_var_es, histogram_bins, summarize_pnl
from .portfolio import equal_weights, normalize_weights, portfolio_log_to_pnl
from .scenarios import generate_scenarios


def _as_float_list(x: Sequence[float] | np.ndarray | None, n: int) -> list[float]:
    if x is None:
        return equal_weights(n).tolist()
    w = normalize_weights(x)
    if w.size != n:
        raise ValueError(f"expected {n} weights, got {w.size}")
    return w.tolist()


def run_var(
    *,
    method: str = "gbm",
    horizon_days: int = 10,
    n_scenarios: int = 10_000,
    confidence_levels: Sequence[float] | None = None,
    weights: Sequence[float] | None = None,
    portfolio_value: float = 1_000_000.0,
    seed: int = 42,
    prefer_download: bool = False,
    returns_csv: str | Path | None = None,
    include_histogram: bool = True,
    include_pnl_sample: bool = False,
    pnl_sample_size: int = 500,
) -> dict[str, Any]:
    """Run Monte Carlo VaR/ES and return a JSON-serializable dict.

    Parameters mirror CLI flags and the umbrella API body.
    """
    if confidence_levels is None:
        confidence_levels = (0.95, 0.99)

    data = load_portfolio_returns(
        prefer_download=prefer_download,
        csv_path=Path(returns_csv) if returns_csv else None,
        seed=seed,
    )
    tickers = data["tickers"]
    returns = np.asarray(data["returns"], dtype=float)
    n_assets = returns.shape[1]
    w = _as_float_list(weights, n_assets)

    scen = generate_scenarios(
        returns,
        method=method,  # type: ignore[arg-type]
        horizon_days=horizon_days,
        n_scenarios=n_scenarios,
        seed=seed,
    )
    pnl = portfolio_log_to_pnl(scen["scenarios"], w, portfolio_value=portfolio_value)

    metrics = [compute_var_es(pnl, confidence=float(c)) for c in confidence_levels]

    payload: dict[str, Any] = {
        "project": "var",
        "slug": "var",
        "version": "0.1.0",
        "disclaimer": (
            "Educational / research only — not investment advice. "
            "No live order routing."
        ),
        "params": {
            "method": scen["method"],
            "horizon_days": horizon_days,
            "n_scenarios": n_scenarios,
            "confidence_levels": [float(c) for c in confidence_levels],
            "weights": w,
            "tickers": tickers,
            "portfolio_value": portfolio_value,
            "seed": seed,
        },
        "data": {
            "source": data.get("source"),
            "n_days": data.get("n_days"),
            "tickers": tickers,
        },
        "metrics": {
            "by_confidence": metrics,
            "pnl_summary": summarize_pnl(pnl),
        },
        "chart": {},
    }

    if include_histogram:
        payload["chart"]["pnl_histogram"] = histogram_bins(pnl)

    # Sorted P&L for optional loss curve (downsampled)
    sorted_pnl = np.sort(pnl)
    step = max(1, len(sorted_pnl) // 200)
    payload["chart"]["pnl_sorted"] = sorted_pnl[::step].tolist()

    if include_pnl_sample:
        rng = np.random.default_rng(seed)
        k = min(pnl_sample_size, pnl.size)
        idx = rng.choice(pnl.size, size=k, replace=False)
        payload["pnl_sample"] = pnl[idx].tolist()

    # Compact risk table for UI
    payload["risk_table"] = [
        {
            "confidence": m["confidence"],
            "var": m["var"],
            "es": m["es"],
            "var_pct": m["var"] / portfolio_value,
            "es_pct": m["es"] / portfolio_value,
        }
        for m in metrics
    ]

    return payload


# Default equal-weight demo basket
DEFAULT_WEIGHTS = equal_weights(len(DEFAULT_TICKERS)).tolist()
