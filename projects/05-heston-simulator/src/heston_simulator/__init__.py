"""Heston stochastic volatility simulator — demo app for the trading-model umbrella.

Simulates the Heston SDEs with correlated Brownian motions and CIR variance
using full-truncation Euler or Andersen's QE scheme. Equity / Nasdaq-style
defaults use leverage correlation ρ < 0.
"""

from __future__ import annotations

from heston_simulator.simulate import NASDAQ_EQUITY_DEFAULTS, Scheme, simulate_heston
from heston_simulator.api import run_heston, to_jsonable

__all__ = [
    "NASDAQ_EQUITY_DEFAULTS",
    "Scheme",
    "simulate_heston",
    "run_heston",
    "to_jsonable",
]

__version__ = "0.1.0"
