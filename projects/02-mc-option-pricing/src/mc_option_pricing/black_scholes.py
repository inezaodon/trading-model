"""Black–Scholes closed-form prices for European calls and puts."""

from __future__ import annotations

import math
from typing import Literal

OptionType = Literal["call", "put"]


def _norm_cdf(x: float) -> float:
    """Standard normal CDF via math.erf (no SciPy dependency)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def black_scholes_price(
    spot: float,
    strike: float,
    rate: float,
    vol: float,
    maturity: float,
    option_type: OptionType = "call",
) -> float:
    """European Black–Scholes price under constant rates and volatility.

    Parameters
    ----------
    spot :
        Spot price S0 (> 0).
    strike :
        Strike K (> 0).
    rate :
        Continuously compounded risk-free rate r.
    vol :
        Black–Scholes volatility σ (≥ 0).
    maturity :
        Time to expiry T in years (≥ 0).
    option_type :
        ``"call"`` or ``"put"``.
    """
    if spot <= 0 or strike <= 0:
        raise ValueError("spot and strike must be positive")
    if vol < 0:
        raise ValueError("vol must be non-negative")
    if maturity < 0:
        raise ValueError("maturity must be non-negative")
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")

    if maturity == 0.0 or vol == 0.0:
        intrinsic = max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)
        if maturity == 0.0:
            return float(intrinsic)
        # Zero vol, T > 0: discounted deterministic forward payoff
        forward = spot * math.exp(rate * maturity)
        if option_type == "call":
            return math.exp(-rate * maturity) * max(forward - strike, 0.0)
        return math.exp(-rate * maturity) * max(strike - forward, 0.0)

    sqrt_t = math.sqrt(maturity)
    d1 = (math.log(spot / strike) + (rate + 0.5 * vol * vol) * maturity) / (vol * sqrt_t)
    d2 = d1 - vol * sqrt_t

    if option_type == "call":
        return spot * _norm_cdf(d1) - strike * math.exp(-rate * maturity) * _norm_cdf(d2)
    return strike * math.exp(-rate * maturity) * _norm_cdf(-d2) - spot * _norm_cdf(-d1)
