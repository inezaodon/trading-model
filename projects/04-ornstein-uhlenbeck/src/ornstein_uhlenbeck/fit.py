"""Fit Ornstein–Uhlenbeck parameters from a discrete time series.

Uses the AR(1) / OLS map of the exact OU transition:

    X_{i+1} = a + b X_i + ε_i

with

    b = e^{-κ Δt},  a = θ(1 − b),
    Var(ε) = σ² (1 − b²) / (2κ)   (or σ² Δt when κ ≈ 0).

This is the standard rate / spread calibration used on Treasury yields,
SOFR, and pairs spreads (research only — cite FRED / Treasury.gov for
live series; this package ships synthetic sample rates).
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ornstein_uhlenbeck.simulate import stationary_std


def fit_ou(
    series: np.ndarray,
    dt: float = 1.0 / 252.0,
) -> dict[str, Any]:
    """Estimate (κ, θ, σ) from an observed path via AR(1) OLS.

    Parameters
    ----------
    series :
        1-D array of observed levels (rates, spreads, residuals).
    dt :
        Time between observations in years (default: daily = 1/252).

    Returns
    -------
    dict
        Fitted ``kappa``, ``theta``, ``sigma``, ``half_life``,
        ``stationary_std``, regression diagnostics, and ``dt``.
    """
    x = np.asarray(series, dtype=float).ravel()
    if x.size < 3:
        raise ValueError("series must contain at least 3 observations")
    if dt <= 0:
        raise ValueError("dt must be positive")
    if not np.all(np.isfinite(x)):
        raise ValueError("series must be finite")

    x_lag = x[:-1]
    x_next = x[1:]
    n = x_lag.size

    # OLS: X_{t+1} = a + b X_t
    sx = float(np.sum(x_lag))
    sy = float(np.sum(x_next))
    sxx = float(np.sum(x_lag * x_lag))
    sxy = float(np.sum(x_lag * x_next))
    denom = n * sxx - sx * sx
    if abs(denom) < 1e-18:
        raise ValueError("degenerate series: zero variance in lag")

    b = (n * sxy - sx * sy) / denom
    a = (sy - b * sx) / n

    resid = x_next - (a + b * x_lag)
    sse = float(np.sum(resid * resid))
    sigma_eps = float(np.sqrt(sse / max(n - 2, 1)))

    # Map AR(1) → OU
    if b <= 0 or b >= 1:
        # Outside mean-reverting AR(1) regime; fall back to Euler map
        # ΔX = κ(θ − X)dt + …  ⇒  regress ΔX on X: slope = −κ dt
        dx = np.diff(x)
        sx2 = float(np.sum(x_lag * x_lag))
        sxd = float(np.sum(x_lag * dx))
        slope = sxd / sx2 if sx2 > 0 else 0.0
        kappa = float(max(-slope / dt, 0.0))
        theta = float(np.mean(x))
        sigma = float(np.std(dx, ddof=1) / np.sqrt(dt)) if n > 1 else 0.0
        method = "euler_fallback"
        b_eff = float(np.exp(-kappa * dt)) if kappa > 0 else 1.0
        a_eff = theta * (1.0 - b_eff)
    else:
        kappa = float(-np.log(b) / dt)
        theta = float(a / (1.0 - b))
        if kappa < 1e-12:
            sigma = float(sigma_eps / np.sqrt(dt))
        else:
            # Var(ε) = σ² (1 − e^{-2κΔt}) / (2κ)
            factor = (1.0 - b * b) / (2.0 * kappa)
            sigma = float(sigma_eps / np.sqrt(max(factor, 1e-18)))
        method = "ar1_exact"
        b_eff = float(b)
        a_eff = float(a)

    half_life = float(np.log(2.0) / kappa) if kappa > 1e-12 else float("inf")
    try:
        ss = stationary_std(kappa, sigma) if kappa > 1e-12 else float("inf")
    except ValueError:
        ss = float("inf")

    r2 = 0.0
    sst = float(np.sum((x_next - np.mean(x_next)) ** 2))
    if sst > 0:
        r2 = float(1.0 - sse / sst)

    return {
        "kappa": kappa,
        "theta": theta,
        "sigma": sigma,
        "half_life": half_life,
        "stationary_std": ss,
        "dt": float(dt),
        "n_obs": int(x.size),
        "method": method,
        "ar1": {"a": a_eff, "b": b_eff, "sigma_eps": sigma_eps, "r2": r2},
    }
