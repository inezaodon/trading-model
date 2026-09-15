"""Sample parameter sets calibrated to liquid tech / NASDAQ-style underlyings.

Spots and vols are illustrative mid-2020s levels for education — not live quotes.
Rates approximate a short USD funding level (~4.5%).
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

SAMPLE_PARAMS: dict[str, dict[str, Any]] = {
    "QQQ": {
        "symbol": "QQQ",
        "spot": 480.0,
        "strike": 480.0,
        "rate": 0.045,
        "vol": 0.22,
        "maturity": 0.25,
        "option_type": "call",
        "note": "NASDAQ-100 ETF — ATM quarterly call",
    },
    "AAPL": {
        "symbol": "AAPL",
        "spot": 230.0,
        "strike": 230.0,
        "rate": 0.045,
        "vol": 0.24,
        "maturity": 0.25,
        "option_type": "call",
        "note": "Large-cap tech — ATM quarterly call",
    },
    "MSFT": {
        "symbol": "MSFT",
        "spot": 420.0,
        "strike": 420.0,
        "rate": 0.045,
        "vol": 0.23,
        "maturity": 0.25,
        "option_type": "call",
        "note": "Large-cap tech — ATM quarterly call",
    },
    "NVDA": {
        "symbol": "NVDA",
        "spot": 120.0,
        "strike": 125.0,
        "rate": 0.045,
        "vol": 0.40,
        "maturity": 0.1667,
        "option_type": "call",
        "note": "High-beta semiconductor — mild OTM ~2m call",
    },
    "AMZN": {
        "symbol": "AMZN",
        "spot": 185.0,
        "strike": 185.0,
        "rate": 0.045,
        "vol": 0.28,
        "maturity": 0.5,
        "option_type": "put",
        "note": "E-commerce mega-cap — ATM semi-annual put",
    },
    "META": {
        "symbol": "META",
        "spot": 510.0,
        "strike": 500.0,
        "rate": 0.045,
        "vol": 0.30,
        "maturity": 0.25,
        "option_type": "call",
        "note": "Social / ads mega-cap — slight ITM quarterly call",
    },
    "GOOGL": {
        "symbol": "GOOGL",
        "spot": 175.0,
        "strike": 175.0,
        "rate": 0.045,
        "vol": 0.26,
        "maturity": 0.25,
        "option_type": "put",
        "note": "Search mega-cap — ATM quarterly put",
    },
    "TSLA": {
        "symbol": "TSLA",
        "spot": 250.0,
        "strike": 260.0,
        "rate": 0.045,
        "vol": 0.55,
        "maturity": 0.0833,
        "option_type": "call",
        "note": "High-vol EV — OTM ~1m call",
    },
    "AMD": {
        "symbol": "AMD",
        "spot": 160.0,
        "strike": 160.0,
        "rate": 0.045,
        "vol": 0.38,
        "maturity": 0.25,
        "option_type": "call",
        "note": "Semiconductor — ATM quarterly call",
    },
    "NFLX": {
        "symbol": "NFLX",
        "spot": 700.0,
        "strike": 680.0,
        "rate": 0.045,
        "vol": 0.32,
        "maturity": 0.25,
        "option_type": "put",
        "note": "Streaming mega-cap — mild ITM quarterly put",
    },
}


def get_sample(symbol: str) -> dict[str, Any]:
    """Return a deep copy of a named sample parameter set."""
    key = symbol.upper()
    if key not in SAMPLE_PARAMS:
        known = ", ".join(sorted(SAMPLE_PARAMS))
        raise KeyError(f"Unknown sample '{symbol}'. Known: {known}")
    return deepcopy(SAMPLE_PARAMS[key])


def list_samples() -> list[str]:
    """Sorted symbol keys for the sample catalog."""
    return sorted(SAMPLE_PARAMS)
