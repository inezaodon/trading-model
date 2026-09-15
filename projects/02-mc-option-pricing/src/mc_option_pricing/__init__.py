"""Monte Carlo European option pricing under geometric Brownian motion."""

from .black_scholes import black_scholes_price
from .convergence import convergence_study
from .monte_carlo import price_european_mc
from .samples import SAMPLE_PARAMS, get_sample

__all__ = [
    "black_scholes_price",
    "convergence_study",
    "get_sample",
    "price_european_mc",
    "SAMPLE_PARAMS",
]

__version__ = "0.1.0"
