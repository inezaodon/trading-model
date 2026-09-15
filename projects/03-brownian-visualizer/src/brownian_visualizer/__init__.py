"""Brownian motion & random walk visualizer — 1D and 2D Wiener processes.

Educational / research only — not investment advice.
"""

from .brownian import simulate_brownian_1d, simulate_brownian_2d, simulate_scaled_brownian
from .export import result_to_chart_json, write_chart_json
from .random_walk import random_walk_to_bm_limit, simulate_simple_random_walk

__all__ = [
    "simulate_brownian_1d",
    "simulate_brownian_2d",
    "simulate_scaled_brownian",
    "simulate_simple_random_walk",
    "random_walk_to_bm_limit",
    "result_to_chart_json",
    "write_chart_json",
]

__version__ = "0.1.0"
