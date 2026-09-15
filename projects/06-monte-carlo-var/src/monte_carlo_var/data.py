"""Sample ETF daily returns for QQQ, SPY, IWM, TLT, GLD.

Bundled CSV is preferred. If missing, synthetic correlated returns are
generated with a fixed seed so demos and tests stay offline-friendly.
Optional live download via yfinance when ``prefer_download=True``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

DEFAULT_TICKERS = ("QQQ", "SPY", "IWM", "TLT", "GLD")

# Annualized drift / vol priors used for synthetic paths (educational only).
_SYNTH_MU = {
    "QQQ": 0.12,
    "SPY": 0.10,
    "IWM": 0.09,
    "TLT": 0.02,
    "GLD": 0.04,
}
_SYNTH_SIGMA = {
    "QQQ": 0.22,
    "SPY": 0.16,
    "IWM": 0.20,
    "TLT": 0.12,
    "GLD": 0.15,
}

# Approximate correlation skeleton (equities correlated; TLT/GLD diversifiers).
_CORR = np.array(
    [
        [1.00, 0.90, 0.80, -0.25, 0.05],
        [0.90, 1.00, 0.85, -0.20, 0.08],
        [0.80, 0.85, 1.00, -0.15, 0.10],
        [-0.25, -0.20, -0.15, 1.00, 0.15],
        [0.05, 0.08, 0.10, 0.15, 1.00],
    ],
    dtype=float,
)

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
_SAMPLE_CSV = _DATA_DIR / "sample_returns.csv"
_TRADING_DAYS = 252


def _cholesky_corr(corr: np.ndarray) -> np.ndarray:
    """Stabilize correlation and return Cholesky factor."""
    c = 0.5 * (corr + corr.T)
    eigvals, eigvecs = np.linalg.eigh(c)
    eigvals = np.clip(eigvals, 1e-10, None)
    c = eigvecs @ np.diag(eigvals) @ eigvecs.T
    # Renormalize diagonal to 1
    d = np.sqrt(np.diag(c))
    c = c / np.outer(d, d)
    return np.linalg.cholesky(c)


def generate_synthetic_returns(
    tickers: tuple[str, ...] = DEFAULT_TICKERS,
    n_days: int = 756,
    seed: int = 42,
) -> dict[str, Any]:
    """Generate correlated Gaussian daily log-returns for the ETF basket."""
    n = len(tickers)
    rng = np.random.default_rng(seed)
    L = _cholesky_corr(_CORR[:n, :n])
    z = rng.standard_normal((n_days, n))
    shocks = z @ L.T

    mu = np.array([_SYNTH_MU.get(t, 0.06) for t in tickers]) / _TRADING_DAYS
    sigma = np.array([_SYNTH_SIGMA.get(t, 0.18) for t in tickers]) / np.sqrt(_TRADING_DAYS)
    returns = mu + shocks * sigma

    # Simple business-day-ish index labels (not calendar-accurate).
    dates = [f"2022-01-{(i % 28) + 1:02d}" for i in range(n_days)]  # placeholder labels
    # Better: sequential ISO-like day counters for CSV readability
    dates = [f"D{i:04d}" for i in range(n_days)]

    return {
        "tickers": list(tickers),
        "dates": dates,
        "returns": returns.astype(float),
        "source": "synthetic",
        "seed": seed,
        "n_days": n_days,
    }


def write_sample_csv(
    path: Path | None = None,
    tickers: tuple[str, ...] = DEFAULT_TICKERS,
    n_days: int = 756,
    seed: int = 42,
) -> Path:
    """Materialize bundled sample returns CSV."""
    path = path or _SAMPLE_CSV
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = generate_synthetic_returns(tickers=tickers, n_days=n_days, seed=seed)
    header = "date," + ",".join(payload["tickers"])
    lines = [header]
    for i, d in enumerate(payload["dates"]):
        row = ",".join(f"{x:.10f}" for x in payload["returns"][i])
        lines.append(f"{d},{row}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def load_returns_csv(path: Path | None = None) -> dict[str, Any]:
    """Load daily returns matrix from CSV (date + ticker columns)."""
    path = path or _SAMPLE_CSV
    text = path.read_text(encoding="utf-8").strip().splitlines()
    if not text:
        raise ValueError(f"empty returns file: {path}")
    header = text[0].split(",")
    tickers = header[1:]
    dates: list[str] = []
    rows: list[list[float]] = []
    for line in text[1:]:
        parts = line.split(",")
        dates.append(parts[0])
        rows.append([float(x) for x in parts[1:]])
    returns = np.asarray(rows, dtype=float)
    return {
        "tickers": tickers,
        "dates": dates,
        "returns": returns,
        "source": str(path),
        "n_days": returns.shape[0],
    }


def try_download_yfinance(
    tickers: tuple[str, ...] = DEFAULT_TICKERS,
    period: str = "3y",
) -> dict[str, Any] | None:
    """Attempt live Yahoo Finance download; return None on any failure."""
    try:
        import yfinance as yf  # type: ignore
    except ImportError:
        return None
    try:
        data = yf.download(
            list(tickers),
            period=period,
            auto_adjust=True,
            progress=False,
            threads=False,
        )
        if data is None or data.empty:
            return None
        close = data["Close"] if "Close" in data.columns.get_level_values(0) else data
        if hasattr(close, "columns"):
            # MultiIndex or flat
            cols = list(close.columns)
            if isinstance(cols[0], tuple):
                close = data["Close"]
            ordered = [t for t in tickers if t in close.columns]
            if len(ordered) != len(tickers):
                return None
            px = close[list(tickers)].dropna()
        else:
            return None
        if px.shape[0] < 60:
            return None
        log_ret = np.log(px / px.shift(1)).dropna()
        return {
            "tickers": list(tickers),
            "dates": [str(d.date()) for d in log_ret.index],
            "returns": log_ret.to_numpy(dtype=float),
            "source": "yfinance",
            "n_days": int(log_ret.shape[0]),
        }
    except Exception:
        return None


def load_portfolio_returns(
    prefer_download: bool = False,
    csv_path: Path | None = None,
    seed: int = 42,
) -> dict[str, Any]:
    """Resolve returns: optional download → bundled CSV → synthetic regenerate."""
    if prefer_download:
        live = try_download_yfinance()
        if live is not None:
            return live

    path = csv_path or _SAMPLE_CSV
    if path.exists():
        return load_returns_csv(path)

    write_sample_csv(path=path, seed=seed)
    out = load_returns_csv(path)
    out["source"] = "synthetic"
    out["seed"] = seed
    return out
