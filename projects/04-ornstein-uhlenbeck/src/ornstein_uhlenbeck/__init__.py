"""Ornstein–Uhlenbeck mean-reversion engines (research / education only).

Simulates, fits, and demos z-score signals for the SDE

    dX_t = κ(θ − X_t) dt + σ dW_t

Not investment advice. No live order routing.
"""

from __future__ import annotations

from ornstein_uhlenbeck.api import run
from ornstein_uhlenbeck.fit import fit_ou
from ornstein_uhlenbeck.signals import zscore_signals
from ornstein_uhlenbeck.simulate import simulate_ou

__all__ = [
    "simulate_ou",
    "fit_ou",
    "zscore_signals",
    "run",
    "__version__",
]

__version__ = "0.1.0"
