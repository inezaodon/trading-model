"""Sample rate / spread series for OU demos.

Ships a **synthetic** daily rate path that behaves like a short Treasury
yield (OU mean-reverting). For live calibration, pull:

- **FRED** (https://fred.stlouisfed.org/): ``DGS2``, ``DGS10``, ``SOFR``,
  ``T10Y2Y`` (2s10s) — requires a free API key for bulk JSON, or download CSV.
- **Treasury.gov** CSV archives for constant-maturity yields.
- Yahoo ``^TNX`` (10Y yield) via ``yfinance`` for a quick spot check.

This module never calls external APIs; it only documents the fit workflow
and generates reproducible synthetic series with a fixed seed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from ornstein_uhlenbeck.simulate import simulate_ou

# Bundled CSV next to package data or under project data/
_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_DEFAULT_CSV = _DATA_DIR / "synthetic_rates.csv"

# Plausible short-rate OU (annualized units, daily steps)
_SYNTH_KAPPA = 2.5
_SYNTH_THETA = 4.0  # ~4% yield
_SYNTH_SIGMA = 0.8
_SYNTH_X0 = 3.5
_SYNTH_SEED = 42
_SYNTH_N = 504  # ~2y daily


FRED_SERIES_NOTES: dict[str, str] = {
    "DGS2": "2-Year Treasury Constant Maturity Rate (FRED)",
    "DGS10": "10-Year Treasury Constant Maturity Rate (FRED)",
    "T10Y2Y": "10Y–2Y Treasury spread / curve slope (FRED)",
    "SOFR": "Secured Overnight Financing Rate (FRED)",
    "^TNX": "CBOE 10-Year Treasury Yield Index (Yahoo)",
}


def generate_synthetic_rates(
    n_obs: int = _SYNTH_N,
    seed: int = _SYNTH_SEED,
    dt: float = 1.0 / 252.0,
) -> dict[str, Any]:
    """Generate a synthetic daily rate path from a known OU."""
    t = n_obs * dt
    sim = simulate_ou(
        x0=_SYNTH_X0,
        kappa=_SYNTH_KAPPA,
        theta=_SYNTH_THETA,
        sigma=_SYNTH_SIGMA,
        t=t,
        n_steps=n_obs,
        n_paths=1,
        scheme="exact",
        seed=seed,
    )
    # Drop t=0 duplicate step count: times has n_obs+1 points; use all
    rates = sim["X"][0]
    times = sim["times"]
    # Also build a synthetic 2s10s-like spread (second OU)
    spread_sim = simulate_ou(
        x0=0.5,
        kappa=1.8,
        theta=0.25,
        sigma=0.35,
        t=t,
        n_steps=n_obs,
        n_paths=1,
        scheme="exact",
        seed=seed + 1,
    )
    return {
        "times": times,
        "rate": rates,
        "spread_2s10s": spread_sim["X"][0],
        "dt": dt,
        "true_params_rate": {
            "kappa": _SYNTH_KAPPA,
            "theta": _SYNTH_THETA,
            "sigma": _SYNTH_SIGMA,
            "x0": _SYNTH_X0,
        },
        "source": "synthetic",
        "seed": seed,
        "notes": (
            "Synthetic OU rates for offline demos. To fit live Treasury / "
            "FRED series: download DGS2/DGS10/T10Y2Y/SOFR CSV, load the "
            "level or spread column, then call fit_ou(series, dt=1/252)."
        ),
        "fred_series": FRED_SERIES_NOTES,
    }


def write_synthetic_csv(path: Path | None = None, seed: int = _SYNTH_SEED) -> Path:
    """Write ``date,rate,spread_2s10s`` CSV under ``data/``."""
    out = path or _DEFAULT_CSV
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = generate_synthetic_rates(seed=seed)
    n = payload["rate"].size
    # Fake business-day index starting 2023-01-03
    dates = np.arange("2023-01-03", np.datetime64("2023-01-03") + n, dtype="datetime64[D]")
    with out.open("w", encoding="utf-8") as fh:
        fh.write("date,rate,spread_2s10s\n")
        for d, r, s in zip(dates, payload["rate"], payload["spread_2s10s"], strict=True):
            fh.write(f"{d},{r:.8f},{s:.8f}\n")
    return out


def load_sample_rates(path: Path | None = None) -> dict[str, Any]:
    """Load bundled CSV or generate on the fly if missing."""
    csv_path = path or _DEFAULT_CSV
    if not csv_path.is_file():
        write_synthetic_csv(csv_path)

    dates: list[str] = []
    rates: list[float] = []
    spreads: list[float] = []
    with csv_path.open(encoding="utf-8") as fh:
        header = fh.readline()
        if "rate" not in header:
            raise ValueError(f"unexpected CSV header in {csv_path}")
        for line in fh:
            line = line.strip()
            if not line:
                continue
            date, rate, spread = line.split(",")
            dates.append(date)
            rates.append(float(rate))
            spreads.append(float(spread))

    return {
        "dates": dates,
        "rate": np.asarray(rates, dtype=float),
        "spread_2s10s": np.asarray(spreads, dtype=float),
        "dt": 1.0 / 252.0,
        "path": str(csv_path),
        "source": "synthetic_csv",
        "fred_series": FRED_SERIES_NOTES,
        "notes": (
            "Loaded synthetic sample. Replace with FRED/Treasury CSV for "
            "real calibration (DGS2, DGS10, T10Y2Y, SOFR)."
        ),
    }
