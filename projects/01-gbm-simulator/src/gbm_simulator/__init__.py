"""Geometric Brownian Motion stock price simulator.

Educational / research Monte Carlo engine for the SDE

    dS_t = μ S_t dt + σ S_t dW_t

Standalone demo app for the trading-model umbrella (slug: ``gbm``).
Not investment advice — no live order routing.
"""

from __future__ import annotations

from gbm_simulator.calibrate import estimate_mu_sigma, load_price_csv
from gbm_simulator.export import simulation_to_json, write_json
from gbm_simulator.simulate import SimulationResult, simulate_gbm

__all__ = [
    "SimulationResult",
    "simulate_gbm",
    "estimate_mu_sigma",
    "load_price_csv",
    "simulation_to_json",
    "write_json",
    "__version__",
]

__version__ = "0.1.0"
