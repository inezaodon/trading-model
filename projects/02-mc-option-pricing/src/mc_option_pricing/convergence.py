"""Convergence study data for Monte Carlo vs Black–Scholes."""

from __future__ import annotations

from typing import Any, Literal, Sequence

from .monte_carlo import price_european_mc

OptionType = Literal["call", "put"]

DEFAULT_PATH_GRID: tuple[int, ...] = (500, 1_000, 2_000, 5_000, 10_000, 25_000, 50_000, 100_000)


def convergence_study(
    spot: float = 480.0,
    strike: float = 480.0,
    rate: float = 0.045,
    vol: float = 0.22,
    maturity: float = 0.25,
    option_type: OptionType = "call",
    path_counts: Sequence[int] | None = None,
    n_steps: int = 1,
    seed: int = 42,
    confidence: float = 0.95,
) -> dict[str, Any]:
    """Run MC pricing across a path-count grid for chart-ready convergence data.

    Returns JSON-friendly arrays suitable for Plotly / Chart.js::

        {
          "n_paths": [...],
          "mc_price": [...],
          "stderr": [...],
          "ci_low": [...],
          "ci_high": [...],
          "abs_error": [...],
          "bs_price": float,
          "params": {...}
        }

    Each path count uses a derived seed ``seed + i`` so runs are reproducible
    but not perfectly dependent across the grid.
    """
    counts = list(path_counts) if path_counts is not None else list(DEFAULT_PATH_GRID)
    if not counts:
        raise ValueError("path_counts must be non-empty")

    n_paths_out: list[int] = []
    mc_price: list[float] = []
    stderr: list[float] = []
    ci_low: list[float] = []
    ci_high: list[float] = []
    abs_error: list[float] = []
    bs_price: float | None = None

    for i, n in enumerate(counts):
        result = price_european_mc(
            spot=spot,
            strike=strike,
            rate=rate,
            vol=vol,
            maturity=maturity,
            option_type=option_type,
            n_paths=int(n),
            n_steps=n_steps,
            seed=seed + i,
            confidence=confidence,
        )
        if bs_price is None:
            bs_price = float(result["bs_price"])
        n_paths_out.append(int(result["paths_used"]))
        mc_price.append(float(result["price"]))
        stderr.append(float(result["stderr"]))
        ci_low.append(float(result["ci_low"]))
        ci_high.append(float(result["ci_high"]))
        abs_error.append(abs(float(result["price"]) - float(result["bs_price"])))

    assert bs_price is not None
    return {
        "n_paths": n_paths_out,
        "mc_price": mc_price,
        "stderr": stderr,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "abs_error": abs_error,
        "bs_price": bs_price,
        "params": {
            "spot": float(spot),
            "strike": float(strike),
            "rate": float(rate),
            "vol": float(vol),
            "maturity": float(maturity),
            "option_type": option_type,
            "n_steps": int(n_steps),
            "seed": int(seed),
            "confidence": float(confidence),
            "path_counts": [int(c) for c in counts],
        },
    }
