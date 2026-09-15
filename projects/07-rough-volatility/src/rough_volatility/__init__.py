"""Rough Volatility / Rough Bergomi simulator (project 07).

Hybrid discrete scheme for fractional kernels with Hurst H ≈ 0.1,
forward-variance curve input, and NASDAQ-style IV surface calibration hooks.
"""

from .calibrate import calibrate_from_nasdaq_iv, forward_variance_from_iv
from .simulate import simulate_rough_bergomi

__all__ = [
    "simulate_rough_bergomi",
    "forward_variance_from_iv",
    "calibrate_from_nasdaq_iv",
]

__version__ = "0.1.0"
