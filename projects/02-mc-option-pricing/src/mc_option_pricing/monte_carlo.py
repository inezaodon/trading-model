"""Risk-neutral Monte Carlo pricing of European options under GBM."""

from __future__ import annotations

import math
from typing import Any, Literal

import numpy as np

from .black_scholes import black_scholes_price

OptionType = Literal["call", "put"]


def _terminal_spots(
    spot: float,
    rate: float,
    vol: float,
    maturity: float,
    n_paths: int,
    n_steps: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Exact GBM terminal spots under the risk-neutral measure (μ = r).

    Uses the closed log-Euler step over ``n_steps`` intervals so the terminal
    law matches the exact lognormal distribution when increments are summed.
    """
    if n_steps < 1:
        raise ValueError("n_steps must be >= 1")
    dt = maturity / n_steps
    z = rng.standard_normal((n_paths, n_steps))
    increments = (rate - 0.5 * vol * vol) * dt + vol * np.sqrt(dt) * z
    log_st = np.log(spot) + increments.sum(axis=1)
    return np.exp(log_st)


def price_european_mc(
    spot: float = 480.0,
    strike: float = 480.0,
    rate: float = 0.045,
    vol: float = 0.22,
    maturity: float = 0.25,
    option_type: OptionType = "call",
    n_paths: int = 50_000,
    n_steps: int = 1,
    seed: int | None = 42,
    confidence: float = 0.95,
) -> dict[str, Any]:
    """Price a European call/put via risk-neutral Monte Carlo under GBM.

    Discounted payoff mean with sample standard error and a normal
    approximation confidence interval. Also returns the Black–Scholes
    closed-form price for comparison.

    Returns a JSON-friendly dict::

        {
          "price": float,
          "stderr": float,
          "ci_low": float,
          "ci_high": float,
          "bs_price": float,
          "paths_used": int,
          "params": {...}
        }
    """
    if spot <= 0 or strike <= 0:
        raise ValueError("spot and strike must be positive")
    if vol < 0:
        raise ValueError("vol must be non-negative")
    if maturity < 0:
        raise ValueError("maturity must be non-negative")
    if n_paths < 2:
        raise ValueError("n_paths must be >= 2")
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be in (0, 1)")

    params = {
        "spot": float(spot),
        "strike": float(strike),
        "rate": float(rate),
        "vol": float(vol),
        "maturity": float(maturity),
        "option_type": option_type,
        "n_paths": int(n_paths),
        "n_steps": int(n_steps),
        "seed": seed,
        "confidence": float(confidence),
    }

    bs = black_scholes_price(spot, strike, rate, vol, maturity, option_type)

    if maturity == 0.0:
        intrinsic = max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)
        return {
            "price": float(intrinsic),
            "stderr": 0.0,
            "ci_low": float(intrinsic),
            "ci_high": float(intrinsic),
            "bs_price": float(bs),
            "paths_used": int(n_paths),
            "params": params,
        }

    rng = np.random.default_rng(seed)
    st = _terminal_spots(spot, rate, vol, maturity, n_paths, n_steps, rng)

    if option_type == "call":
        payoffs = np.maximum(st - strike, 0.0)
    else:
        payoffs = np.maximum(strike - st, 0.0)

    discount = np.exp(-rate * maturity)
    discounted = discount * payoffs

    price = float(np.mean(discounted))
    # Sample SE of the mean (unbiased variance / sqrt(n))
    stderr = float(np.std(discounted, ddof=1) / np.sqrt(n_paths))

    # Normal approx z-score for common levels; default 95% → 1.95996398454
    z = float(_normal_ppf(0.5 + confidence / 2.0))
    half = z * stderr

    return {
        "price": price,
        "stderr": stderr,
        "ci_low": price - half,
        "ci_high": price + half,
        "bs_price": float(bs),
        "paths_used": int(n_paths),
        "params": params,
    }


def _normal_ppf(p: float) -> float:
    """Approximate standard normal quantile (Acklam / Beasley-Springer style)."""
    if p <= 0.0 or p >= 1.0:
        raise ValueError("p must be in (0, 1)")
    # Coefficients for rational approximation
    a = [
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    ]
    b = [
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    ]
    c = [
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    ]
    d = [
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e00,
        3.754408661907416e00,
    ]

    plow = 0.02425
    phigh = 1.0 - plow

    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        return (
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )
    if p > phigh:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        return -(
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )
    q = p - 0.5
    r = q * q
    return (
        (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
        / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
    )
