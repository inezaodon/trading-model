#!/usr/bin/env python3
"""Evaluate ~150 financial series for the 7 stochastic-calculus projects.

Outputs:
  data/DATASET_SURVEY.md
  data/selected/manifest.json
  data/selected/*.csv (small samples for winners)
"""

from __future__ import annotations

import json
import math
import time
import traceback
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT_SURVEY = ROOT / "data" / "DATASET_SURVEY.md"
OUT_MANIFEST = ROOT / "data" / "selected" / "manifest.json"
OUT_SAMPLES = ROOT / "data" / "selected"
SAMPLE_ROWS = 60


# ---------------------------------------------------------------------------
# Candidate universe (~150)
# ---------------------------------------------------------------------------

NASDAQ100_MEGACAPS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "AVGO",
    "COST", "NFLX", "AMD", "PEP", "ADBE", "CSCO", "TMUS", "INTC", "CMCSA",
    "TXN", "QCOM", "INTU", "AMGN", "ISRG", "AMAT", "HON", "BKNG", "VRTX",
    "ADP", "SBUX", "GILD", "ADI", "MU", "LRCX", "PANW", "REGN", "MDLZ",
    "KLAC", "SNPS", "CDNS", "MELI", "PYPL", "CRWD", "MAR", "ORLY", "CTAS",
    "CSX", "ASML", "ABNB", "NXPI", "MRVL", "ADSK", "FTNT", "WDAY", "CPRT",
    "DASH", "PCAR", "ROST", "AEP", "PAYX", "ODFL", "FAST", "KDP", "EA",
    "VRSK", "BKR", "CTSH", "EXC", "XEL", "GEHC", "IDXX", "FANG", "CCEP",
    "ON", "ANSS", "TTD", "ZS", "CDW", "DXCM", "BIIB", "TEAM", "GFS",
]

ETFS = [
    "QQQ", "SPY", "IWM", "DIA", "VTI", "VOO", "XLK", "XLF", "XLE", "XLV",
    "XLI", "XLY", "XLP", "XLU", "XLB", "XLRE", "XLC", "SMH", "SOXX", "ARKK",
    "IWF", "IWD", "EEM", "EFA", "VEA", "VWO", "HYG", "LQD", "TLT", "IEF",
    "SHY", "TIP", "AGG", "BND", "GLD", "SLV", "USO", "UNG", "DBC", "VNQ",
    "XBI", "IBB", "KRE", "XOP", "JNK", "EMB", "TIP",
]

RATES = [
    "^TNX", "^IRX", "^TYX", "^FVX",  # Yahoo Treasury yield indices
    "TLT", "IEF", "SHY", "BIL", "SGOV", "TFLO",  # rate-sensitive ETFs / SOFR proxies
    "SHV", "USFR", "ICSH",
]

FX = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X", "USDCHF=X",
    "NZDUSD=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X", "DX-Y.NYB",  # dollar index
]

COMMODITIES = [
    "GC=F", "SI=F", "CL=F", "NG=F", "HG=F", "ZC=F", "ZS=F", "ZW=F",
    "ES=F", "NQ=F", "YM=F", "RTY=F", "BTC-USD", "ETH-USD",
]

# Logical pairs (evaluated as spread series after fetch)
PAIRS = [
    ("KO", "PEP"),
    ("XOM", "CVX"),
    ("MSFT", "AAPL"),
    ("GDX", "GLD"),
    ("HYG", "LQD"),
    ("IWM", "SPY"),
    ("XLK", "XLF"),
    ("EEM", "EFA"),
]

TREASURY_CSV = {
    "id": "UST_DAILY_TREASURY_YIELD",
    "ticker": "UST_YIELD_CURVE",
    "name": "US Daily Treasury Par Yield Curve (Treasury.gov)",
    "category": "rates_treasury",
    # Yearly CSV endpoints (the /all/all archive often 403s without browser cookies)
    "url_template": (
        "https://home.treasury.gov/resource-center/data-chart-center/"
        "interest-rates/daily-treasury-rates.csv/{year}/all"
        "?type=daily_treasury_yield_curve&field_tdr_date_value={year}"
        "&page&_format=csv"
    ),
    "years": list(range(2015, 2027)),
}


def build_candidates() -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []

    def add(ticker: str, category: str, name: str | None = None) -> None:
        t = ticker.strip()
        if not t or t in seen:
            return
        seen.add(t)
        out.append(
            {
                "id": t.replace("=", "_").replace("^", "").replace("-", "_").replace(".", "_"),
                "ticker": t,
                "name": name or t,
                "category": category,
                "source": "yfinance",
            }
        )

    for t in NASDAQ100_MEGACAPS:
        add(t, "nasdaq100_equity")
    for t in ETFS:
        add(t, "etf")
    for t in RATES:
        add(t, "rates")
    for t in FX:
        add(t, "fx")
    for t in COMMODITIES:
        add(t, "commodity_crypto")
    # Extra liquid names useful for OU pairs / VaR diversification
    extras = [
        "KO", "PEP", "XOM", "CVX", "JPM", "BAC", "WMT", "JNJ", "PG", "UNH",
        "HD", "MA", "V", "DIS", "BA", "CAT", "GS", "IBM", "CRM", "UBER",
        "SQ", "SHOP", "COIN", "PLTR", "SOFI", "NKE", "MCD", "T", "VZ",
        "GDX", "GDXJ",
    ]
    for t in extras:
        add(t, "liquid_equity" if t not in ("GDX", "GDXJ") else "commodity_etf")

    out.append(
        {
            "id": TREASURY_CSV["id"],
            "ticker": TREASURY_CSV["ticker"],
            "name": TREASURY_CSV["name"],
            "category": TREASURY_CSV["category"],
            "source": "treasury.gov",
            "url_template": TREASURY_CSV["url_template"],
        }
    )
    return out


# ---------------------------------------------------------------------------
# Fetch + score
# ---------------------------------------------------------------------------

@dataclass
class ScoreResult:
    id: str
    ticker: str
    name: str
    category: str
    source: str
    status: str
    error: str | None = None
    n_obs: int = 0
    start: str | None = None
    end: str | None = None
    history_years: float = 0.0
    avg_volume: float | None = None
    missing_pct: float = 100.0
    liquidity_score: float = 0.0
    history_score: float = 0.0
    completeness_score: float = 0.0
    total_score: float = 0.0
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    close_col: str = "Close"


def _safe_float(x: Any) -> float | None:
    try:
        if x is None or (isinstance(x, float) and math.isnan(x)):
            return None
        return float(x)
    except Exception:
        return None


def score_frame(
    meta: dict[str, Any],
    df: pd.DataFrame,
    price_col: str = "Close",
    volume_col: str | None = "Volume",
) -> ScoreResult:
    r = ScoreResult(
        id=meta["id"],
        ticker=meta["ticker"],
        name=meta["name"],
        category=meta["category"],
        source=meta.get("source", "yfinance"),
        status="ok",
        close_col=price_col,
    )
    if df is None or df.empty:
        r.status = "empty"
        r.error = "no rows"
        return r

    # Normalize columns
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy()
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

    if price_col not in df.columns:
        # try first numeric
        num = df.select_dtypes(include=[np.number]).columns
        if len(num) == 0:
            r.status = "empty"
            r.error = f"missing {price_col}"
            return r
        price_col = str(num[0])
        r.close_col = price_col

    s = df[price_col].astype(float)
    r.n_obs = int(s.notna().sum())
    if r.n_obs < 5:
        r.status = "too_short"
        r.error = f"only {r.n_obs} obs"
        return r

    idx = df.index
    if not isinstance(idx, pd.DatetimeIndex):
        try:
            idx = pd.to_datetime(idx)
        except Exception:
            pass
    if isinstance(idx, pd.DatetimeIndex) and len(idx):
        r.start = str(idx.min().date())
        r.end = str(idx.max().date())
        days = max((idx.max() - idx.min()).days, 1)
        r.history_years = round(days / 365.25, 2)

    missing = float(s.isna().mean() * 100.0)
    # Also count gaps vs business-day span if datetime
    r.missing_pct = round(missing, 3)

    if volume_col and volume_col in df.columns:
        vol = df[volume_col].astype(float)
        r.avg_volume = _safe_float(vol.mean())

    # Scores 0–100
    # History: 10y+ → 100, linear below
    r.history_score = round(min(100.0, (r.history_years / 10.0) * 100.0), 2)
    # Completeness: 0% missing → 100
    r.completeness_score = round(max(0.0, 100.0 - r.missing_pct * 5.0), 2)
    # Liquidity: log10(avg volume); 1e6 → ~60, 1e8 → 100; FX/rates without volume get category baseline
    if r.avg_volume and r.avg_volume > 0:
        r.liquidity_score = round(min(100.0, max(0.0, (math.log10(r.avg_volume) - 4.0) / 4.0 * 100.0)), 2)
    else:
        # FX/rates/commodities futures often lack comparable equity volume
        baseline = {
            "fx": 70.0,
            "rates": 65.0,
            "rates_treasury": 80.0,
            "commodity_crypto": 55.0,
            "etf": 40.0,
        }.get(meta["category"], 35.0)
        r.liquidity_score = baseline

    r.total_score = round(
        0.35 * r.liquidity_score + 0.40 * r.history_score + 0.25 * r.completeness_score,
        2,
    )
    r.tags = assign_tags(meta, r, s)
    return r


def assign_tags(meta: dict[str, Any], r: ScoreResult, prices: pd.Series) -> list[str]:
    tags: list[str] = []
    cat = meta["category"]
    ticker = meta["ticker"]

    liquid = (r.avg_volume or 0) >= 1e6 or cat in ("etf", "fx", "rates_treasury")
    long_hist = r.history_years >= 5.0
    clean = r.missing_pct < 2.0

    if liquid and long_hist and clean and cat in (
        "nasdaq100_equity",
        "etf",
        "liquid_equity",
        "commodity_crypto",
    ):
        tags.extend(["gbm", "heston", "rough-vol", "mc-options"])

    if cat in ("rates", "rates_treasury", "fx") or ticker in (
        "TLT", "IEF", "SHY", "HYG", "LQD", "BIL", "SGOV", "USFR", "TFLO"
    ):
        tags.append("ou")

    if cat == "etf" and liquid:
        tags.append("var")

    if ticker in ("QQQ", "SPY", "IWM", "TLT", "GLD", "HYG", "XLK", "XLF"):
        if "var" not in tags:
            tags.append("var")

    # Brownian: any residual / synthetic; tag liquid residuals
    if clean and r.n_obs >= 252:
        tags.append("brownian")

    # Heston/rough prefer equity with vol clustering — megacaps + QQQ
    if ticker in (
        "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AMD", "NFLX", "SPY"
    ):
        for t in ("gbm", "heston", "rough-vol", "mc-options"):
            if t not in tags:
                tags.append(t)

    return sorted(set(tags))


def fetch_yfinance(ticker: str, period: str = "max") -> pd.DataFrame:
    import yfinance as yf

    t = yf.Ticker(ticker)
    df = t.history(period=period, auto_adjust=True)
    if df is None or df.empty:
        # fallback shorter
        df = t.history(period="10y", auto_adjust=True)
    return df if df is not None else pd.DataFrame()


def fetch_treasury() -> pd.DataFrame:
    from io import BytesIO

    frames: list[pd.DataFrame] = []
    errors: list[str] = []
    for year in TREASURY_CSV["years"]:
        url = TREASURY_CSV["url_template"].format(year=year)
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; trading-model-dataset-scout/1.0)"},
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
            part = pd.read_csv(BytesIO(raw))
            if not part.empty:
                frames.append(part)
        except Exception as e:
            errors.append(f"{year}:{type(e).__name__}")
            continue
    if not frames:
        raise RuntimeError(f"Treasury.gov fetch failed for all years ({', '.join(errors)})")

    df = pd.concat(frames, ignore_index=True)
    date_col = None
    for c in df.columns:
        if "date" in c.lower():
            date_col = c
            break
    if date_col is None:
        date_col = df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).drop_duplicates(subset=[date_col]).set_index(date_col).sort_index()
    ten = None
    for c in df.columns:
        cl = c.lower().replace(" ", "")
        if cl in ("10yr", "10-yr", "10year") or ("10" in c and "yr" in c.lower()):
            ten = c
            break
    if ten is None:
        num = df.select_dtypes(include=[np.number]).columns
        ten = num[0] if len(num) else df.columns[0]
    out = pd.DataFrame({"Close": pd.to_numeric(df[ten], errors="coerce"), "Volume": np.nan})
    for c in df.columns:
        if c != ten:
            out[c] = pd.to_numeric(df[c], errors="coerce")
    return out


def evaluate_all(candidates: list[dict[str, Any]], sleep_s: float = 0.05) -> list[ScoreResult]:
    results: list[ScoreResult] = []
    for i, meta in enumerate(candidates):
        print(f"[{i+1}/{len(candidates)}] {meta['ticker']} ...", flush=True)
        try:
            if meta.get("source") == "treasury.gov":
                df = fetch_treasury()
                r = score_frame(meta, df, price_col="Close", volume_col=None)
                r.notes = "Primary series = 10Y par yield; full curve retained in sample"
            else:
                df = fetch_yfinance(meta["ticker"])
                r = score_frame(meta, df)
            results.append(r)
            # cache full frame lightly on result via side channel
            r._df = df  # type: ignore[attr-defined]
        except Exception as e:
            r = ScoreResult(
                id=meta["id"],
                ticker=meta["ticker"],
                name=meta["name"],
                category=meta["category"],
                source=meta.get("source", "yfinance"),
                status="error",
                error=f"{type(e).__name__}: {e}",
            )
            results.append(r)
            print(f"  FAIL: {r.error}", flush=True)
        time.sleep(sleep_s)
    return results


def build_pair_spreads(results: list[ScoreResult]) -> list[ScoreResult]:
    by_ticker = {r.ticker: r for r in results if r.status == "ok" and hasattr(r, "_df")}
    pair_results: list[ScoreResult] = []
    for a, b in PAIRS:
        if a not in by_ticker or b not in by_ticker:
            pair_results.append(
                ScoreResult(
                    id=f"SPREAD_{a}_{b}",
                    ticker=f"{a}-{b}",
                    name=f"Log-price spread {a} minus {b}",
                    category="pairs_spread",
                    source="derived",
                    status="error",
                    error="missing leg(s)",
                    tags=["ou"],
                )
            )
            continue
        dfa = by_ticker[a]._df  # type: ignore[attr-defined]
        dfb = by_ticker[b]._df  # type: ignore[attr-defined]
        if isinstance(dfa.columns, pd.MultiIndex):
            dfa = dfa.copy()
            dfa.columns = [c[0] if isinstance(c, tuple) else c for c in dfa.columns]
        if isinstance(dfb.columns, pd.MultiIndex):
            dfb = dfb.copy()
            dfb.columns = [c[0] if isinstance(c, tuple) else c for c in dfb.columns]
        ca = dfa["Close"].astype(float)
        cb = dfb["Close"].astype(float)
        joined = pd.concat([ca.rename("a"), cb.rename("b")], axis=1, sort=True).dropna()
        spread = np.log(joined["a"]) - np.log(joined["b"])
        sdf = pd.DataFrame({"Close": spread, "Volume": np.nan})
        meta = {
            "id": f"SPREAD_{a}_{b}",
            "ticker": f"{a}-{b}",
            "name": f"Log-price spread {a} − {b}",
            "category": "pairs_spread",
            "source": "derived",
        }
        r = score_frame(meta, sdf, volume_col=None)
        r.tags = sorted(set(r.tags + ["ou", "brownian"]))
        r.notes = f"spread = log({a}) - log({b}); good OU candidate if mean-reverting"
        r._df = sdf  # type: ignore[attr-defined]
        # Boost OU suitability into score note via slight completeness already
        pair_results.append(r)
    return pair_results


# ---------------------------------------------------------------------------
# Selection per project
# ---------------------------------------------------------------------------

PROJECTS = [
    ("gbm", "Geometric Brownian Motion Stock Price Simulator"),
    ("mc-options", "Monte Carlo Option Pricing"),
    ("brownian", "Brownian Motion & Random Walk Visualizer"),
    ("ou", "Ornstein–Uhlenbeck Mean Reversion"),
    ("heston", "Heston Stochastic Volatility Simulator"),
    ("var", "Monte Carlo Value-at-Risk Engine"),
    ("rough-vol", "Rough Volatility (Rough Bergomi) Simulator"),
]


def pick_winners(results: list[ScoreResult]) -> dict[str, list[dict[str, Any]]]:
    ok = [r for r in results if r.status == "ok"]

    def ranked(tag: str, n: int = 8, prefer_cats: list[str] | None = None) -> list[ScoreResult]:
        pool = [r for r in ok if tag in r.tags]
        if prefer_cats:
            pool = sorted(
                pool,
                key=lambda r: (
                    0 if r.category in prefer_cats else 1,
                    -r.total_score,
                    -r.history_years,
                ),
            )
        else:
            pool = sorted(pool, key=lambda r: (-r.total_score, -r.history_years))
        # de-dupe by ticker
        seen: set[str] = set()
        out: list[ScoreResult] = []
        for r in pool:
            if r.ticker in seen:
                continue
            seen.add(r.ticker)
            out.append(r)
            if len(out) >= n:
                break
        return out

    # Explicit curated preferences from PROGRESS.md, then fill by score
    prefer_equity = [
        "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AMD", "NFLX", "SPY"
    ]
    prefer_var = ["QQQ", "SPY", "IWM", "TLT", "GLD", "HYG", "IEF", "EEM"]
    prefer_ou = [
        "UST_YIELD_CURVE", "^TNX", "KO-PEP", "XOM-CVX", "HYG-LQD", "IWM-SPY",
        "EURUSD=X", "BIL", "SGOV", "USFR", "IEF", "TLT",
    ]

    def curated_then_fill(prefer: list[str], tag: str, n: int, prefer_cats: list[str] | None = None) -> list[ScoreResult]:
        by_t = {r.ticker: r for r in ok}
        chosen: list[ScoreResult] = []
        for t in prefer:
            if t in by_t and by_t[t].status == "ok":
                chosen.append(by_t[t])
            if len(chosen) >= n:
                return chosen
        for r in ranked(tag, n=n * 3, prefer_cats=prefer_cats):
            if r.ticker not in {c.ticker for c in chosen}:
                chosen.append(r)
            if len(chosen) >= n:
                break
        return chosen

    winners: dict[str, list[dict[str, Any]]] = {}

    gbm = curated_then_fill(prefer_equity, "gbm", 8, ["nasdaq100_equity", "etf"])
    winners["gbm"] = [_winner_entry(r, "Liquid equity/ETF with long clean history for μ,σ calibration") for r in gbm]

    mco = curated_then_fill(prefer_equity[:8], "mc-options", 6, ["nasdaq100_equity", "etf"])
    winners["mc-options"] = [
        _winner_entry(r, "Liquid underlying for EU call/put Monte Carlo; use risk-free from Treasury/SOFR proxy")
        for r in mco
    ]

    # Brownian: synthetic primary + optional real residual paths from top liquid
    brown = curated_then_fill(["QQQ", "SPY", "AAPL", "EURUSD=X"], "brownian", 4)
    winners["brownian"] = [
        {
            "id": "SYNTHETIC_WIENER",
            "ticker": "SYNTHETIC_WIENER",
            "name": "Synthetic Wiener process (no market data)",
            "category": "synthetic",
            "source": "generated",
            "total_score": 100.0,
            "tags": ["brownian"],
            "why": "Visualizer core path; market residuals optional for comparison",
            "status": "ok",
            "sample_csv": None,
        }
    ] + [_winner_entry(r, "Optional real residual / return path for comparison to Wiener") for r in brown[:3]]

    ou = curated_then_fill(prefer_ou, "ou", 8, ["pairs_spread", "rates", "rates_treasury", "fx"])
    # ensure spreads included if available
    spreads = [r for r in ok if r.category == "pairs_spread"]
    spreads = sorted(spreads, key=lambda r: -r.total_score)
    ou_merged: list[ScoreResult] = []
    for r in spreads[:4] + ou:
        if r.ticker not in {x.ticker for x in ou_merged}:
            ou_merged.append(r)
        if len(ou_merged) >= 8:
            break
    winners["ou"] = [
        _winner_entry(
            r,
            "Mean-reverting candidate (rates, FX, or pairs log-spread) for OU κ,θ,σ estimation",
        )
        for r in ou_merged
    ]

    heston = curated_then_fill(prefer_equity, "heston", 6, ["nasdaq100_equity", "etf"])
    winners["heston"] = [
        _winner_entry(r, "Equity with leverage/vol clustering for Heston v0,κ,θ,ξ,ρ calibration")
        for r in heston
    ]

    var = curated_then_fill(prefer_var, "var", 8, ["etf"])
    winners["var"] = [
        _winner_entry(r, "Diversified liquid ETF sleeve for multi-asset Monte Carlo VaR portfolio")
        for r in var
    ]

    rough = curated_then_fill(prefer_equity, "rough-vol", 6, ["nasdaq100_equity", "etf"])
    winners["rough-vol"] = [
        _winner_entry(r, "High-liquidity equity/ETF for realized-vol roughness / Hurst estimation")
        for r in rough
    ]

    return winners


def _winner_entry(r: ScoreResult, why: str) -> dict[str, Any]:
    return {
        "id": r.id,
        "ticker": r.ticker,
        "name": r.name,
        "category": r.category,
        "source": r.source,
        "total_score": r.total_score,
        "history_years": r.history_years,
        "avg_volume": r.avg_volume,
        "missing_pct": r.missing_pct,
        "n_obs": r.n_obs,
        "start": r.start,
        "end": r.end,
        "tags": r.tags,
        "why": why,
        "status": r.status,
        "sample_csv": f"data/selected/{r.id}.csv",
    }


def write_samples(winners: dict[str, list[dict[str, Any]]], results: list[ScoreResult]) -> None:
    OUT_SAMPLES.mkdir(parents=True, exist_ok=True)
    by_id = {r.id: r for r in results}
    written: set[str] = set()
    for items in winners.values():
        for w in items:
            rid = w["id"]
            if rid == "SYNTHETIC_WIENER" or rid in written:
                continue
            r = by_id.get(rid)
            if r is None or not hasattr(r, "_df"):
                w["sample_csv"] = None
                continue
            df = r._df  # type: ignore[attr-defined]
            if isinstance(df.columns, pd.MultiIndex):
                df = df.copy()
                df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
            cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]
            if not cols and "Close" in df.columns:
                cols = ["Close"]
            elif "Close" in df.columns and "Close" not in cols:
                cols = ["Close"] + cols
            sample = df[cols].tail(SAMPLE_ROWS).copy()
            path = OUT_SAMPLES / f"{rid}.csv"
            sample.to_csv(path, index_label="Date")
            w["sample_csv"] = f"data/selected/{rid}.csv"
            written.add(rid)


def write_manifest(winners: dict[str, list[dict[str, Any]]], results: list[ScoreResult]) -> None:
    ok = sum(1 for r in results if r.status == "ok")
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evaluated_count": len(results),
        "ok_count": ok,
        "scoring": {
            "total": "0.35*liquidity + 0.40*history + 0.25*completeness",
            "liquidity": "log10(avg_volume) scaled; category baseline if no volume",
            "history": "min(100, years/10*100)",
            "completeness": "max(0, 100 - missing_pct*5)",
            "tags": ["gbm", "heston", "ou", "var", "options/mc-options", "brownian", "rough-vol"],
        },
        "projects": {
            slug: {
                "title": title,
                "datasets": winners[slug],
            }
            for slug, title in PROJECTS
        },
    }
    OUT_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    OUT_MANIFEST.write_text(json.dumps(payload, indent=2) + "\n")


def write_survey_md(results: list[ScoreResult], winners: dict[str, list[dict[str, Any]]]) -> None:
    ok = [r for r in results if r.status == "ok"]
    fail = [r for r in results if r.status != "ok"]
    lines: list[str] = []
    lines.append("# Dataset Survey — Trading Model Umbrella")
    lines.append("")
    lines.append(f"**Generated (UTC):** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"**Candidates evaluated:** {len(results)}")
    lines.append(f"**OK / failed:** {len(ok)} / {len(fail)}")
    lines.append(f"**Sources:** Yahoo Finance (`yfinance`), Treasury.gov daily yield CSV, derived pairs spreads")
    lines.append("")
    lines.append("> Educational / research datasets only — not investment advice.")
    lines.append("")
    lines.append("## Scoring rubric (reiterated)")
    lines.append("")
    lines.append("| Component | Weight | Definition |")
    lines.append("| --- | --- | --- |")
    lines.append("| Liquidity | 0.35 | `log10(avg_volume)` scaled to 0–100; FX/rates/Treasury use category baselines when volume is absent |")
    lines.append("| History length | 0.40 | `min(100, history_years / 10 * 100)` — 10+ years full marks |")
    lines.append("| Completeness | 0.25 | `max(0, 100 - missing_pct * 5)` — penalizes NaNs |")
    lines.append("| **Total** | 1.00 | Weighted sum |")
    lines.append("")
    lines.append("**Suitability tags** (multi-label):")
    lines.append("")
    lines.append("- `gbm` / `heston` / `rough-vol` / `mc-options` — liquid equities & ETFs with ≥5y clean history")
    lines.append("- `ou` — rates, Treasury curve, FX, SOFR-proxy ETFs, pairs log-spreads")
    lines.append("- `var` — diversified liquid ETFs for portfolio VaR")
    lines.append("- `brownian` — synthetic Wiener primary; optional real residual paths")
    lines.append("")
    lines.append("## Top picks per project")
    lines.append("")
    for slug, title in PROJECTS:
        lines.append(f"### `{slug}` — {title}")
        lines.append("")
        lines.append("| Rank | Ticker | Score | Years | Avg volume | Missing % | Why |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for i, w in enumerate(winners[slug], 1):
            vol = w.get("avg_volume")
            vol_s = f"{vol:,.0f}" if isinstance(vol, (int, float)) and vol is not None else "—"
            years = w.get("history_years", "—")
            miss = w.get("missing_pct", "—")
            score = w.get("total_score", "—")
            lines.append(
                f"| {i} | `{w['ticker']}` | {score} | {years} | {vol_s} | {miss} | {w.get('why', '')} |"
            )
        lines.append("")

    lines.append("## Category coverage")
    lines.append("")
    cats: dict[str, int] = {}
    for r in results:
        cats[r.category] = cats.get(r.category, 0) + 1
    lines.append("| Category | Count |")
    lines.append("| --- | --- |")
    for k in sorted(cats):
        lines.append(f"| {k} | {cats[k]} |")
    lines.append("")

    lines.append("## Full ranked table (OK only)")
    lines.append("")
    lines.append("| Rank | Ticker | Category | Score | Liq | Hist | Comp | Years | Avg vol | Miss% | N | Tags | Status |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    ranked = sorted(ok, key=lambda r: -r.total_score)
    for i, r in enumerate(ranked, 1):
        vol_s = f"{r.avg_volume:,.0f}" if r.avg_volume else "—"
        tags = ",".join(r.tags) if r.tags else "—"
        lines.append(
            f"| {i} | `{r.ticker}` | {r.category} | {r.total_score} | {r.liquidity_score} | "
            f"{r.history_score} | {r.completeness_score} | {r.history_years} | {vol_s} | "
            f"{r.missing_pct} | {r.n_obs} | {tags} | {r.status} |"
        )
    lines.append("")

    if fail:
        lines.append("## Failures / incomplete")
        lines.append("")
        lines.append("| Ticker | Category | Status | Error |")
        lines.append("| --- | --- | --- | --- |")
        for r in fail:
            err = (r.error or "").replace("|", "/")
            lines.append(f"| `{r.ticker}` | {r.category} | {r.status} | {err} |")
        lines.append("")

    lines.append("## Method notes")
    lines.append("")
    lines.append("1. Built ~150 tickers across NASDAQ-100 names, broad ETFs, Treasury/SOFR proxies, FX, commodities/crypto, plus derived pairs spreads.")
    lines.append("2. Fetched `period=max` via `yfinance` (fallback `10y`); Treasury.gov CSV for the full par yield curve.")
    lines.append("3. Pair spreads: `log(A) - log(B)` on intersecting calendars.")
    lines.append("4. Winners favor PROGRESS.md hypotheses, then fill by total score + tag fit.")
    lines.append("5. Small CSV tails (60 rows) cached under `data/selected/` for offline demos.")
    lines.append("")
    lines.append("## Manifest")
    lines.append("")
    lines.append("Machine-readable winners: [`data/selected/manifest.json`](selected/manifest.json)")
    lines.append("")

    OUT_SURVEY.parent.mkdir(parents=True, exist_ok=True)
    OUT_SURVEY.write_text("\n".join(lines) + "\n")


def main() -> None:
    candidates = build_candidates()
    print(f"Built {len(candidates)} base candidates", flush=True)
    results = evaluate_all(candidates)
    pair_results = build_pair_spreads(results)
    results.extend(pair_results)
    print(f"Total evaluated including spreads: {len(results)}", flush=True)

    winners = pick_winners(results)
    write_samples(winners, results)
    write_manifest(winners, results)
    write_survey_md(results, winners)

    # Also dump raw scores JSON for audit
    raw_path = ROOT / "data" / "selected" / "scores_raw.json"
    serializable = []
    for r in results:
        d = asdict(r)
        serializable.append(d)
    raw_path.write_text(json.dumps(serializable, indent=2) + "\n")

    print(f"Wrote {OUT_SURVEY}", flush=True)
    print(f"Wrote {OUT_MANIFEST}", flush=True)
    print(f"OK={sum(1 for r in results if r.status=='ok')} FAIL={sum(1 for r in results if r.status!='ok')}")


if __name__ == "__main__":
    main()
