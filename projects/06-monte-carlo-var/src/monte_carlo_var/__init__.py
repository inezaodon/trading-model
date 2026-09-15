"""Monte Carlo Value-at-Risk engine for multi-asset portfolios."""

from .api import run_var
from .engine import compute_var_es, summarize_pnl

__all__ = ["run_var", "compute_var_es", "summarize_pnl", "__version__"]

__version__ = "0.1.0"
