"""trading_model_math — stochastic calculus engines for research trading models."""

from .calibrate import calibrate_from_iv_surface
from .gbm import simulate_gbm
from .heston import simulate_heston
from .ito import apply_ito_log, log_returns, ito_drift_diffusion
from .rough_bergomi import simulate_rough_bergomi
from .signatures import truncated_signature

__all__ = [
    "simulate_gbm",
    "apply_ito_log",
    "log_returns",
    "ito_drift_diffusion",
    "simulate_heston",
    "simulate_rough_bergomi",
    "truncated_signature",
    "calibrate_from_iv_surface",
]

__version__ = "0.1.0"
