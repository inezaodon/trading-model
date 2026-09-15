"""Heuristic calibration from IV surface summaries to Heston / rough Bergomi params.

Maps NASDAQ-style ORATS fields (iv30, iv60, iv90, slope) into:

- Forward variance knots ξ₀(t) ≈ IV(t)²
- Heston (v0, θ, κ, ξ, ρ)
- Rough Bergomi (H, η, ρ, ξ₀ knots)

These are intentional simple heuristics for offline demos — not a full
least-squares smile calibration.
"""

from __future__ import annotations

from typing import Any


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def forward_variance_from_iv(
    iv30: float,
    iv60: float,
    iv90: float,
) -> list[list[float]]:
    """Convert constant-maturity IVs to forward-variance knots (maturity, ξ).

    Uses total variance w(T)=IV(T)² T and piecewise-constant forward variance
    between 30/60/90 day nodes (ACT/365 year fraction).
    """
    nodes = [
        (30.0 / 365.0, iv30),
        (60.0 / 365.0, iv60),
        (90.0 / 365.0, iv90),
    ]
    knots: list[list[float]] = []
    prev_t = 0.0
    prev_w = 0.0
    for t, iv in nodes:
        w = (iv**2) * t
        dt = t - prev_t
        fwd = (w - prev_w) / dt if dt > 0 else iv**2
        knots.append([t, max(fwd, 1e-8)])
        prev_t, prev_w = t, w
    return knots


def calibrate_heston_from_iv(
    iv30: float,
    iv60: float,
    iv90: float,
    slope: float = 0.0,
    s0: float = 100.0,
) -> dict[str, Any]:
    """Map IV + skew slope into a Heston parameter dict.

    Heuristics
    ----------
    - v0 ← iv30² (near-term variance)
    - θ ← iv90² (long-run level)
    - κ ← larger when the term structure decays quickly
    - ξ (vol-of-vol) ← grows with |slope|
    - ρ ← negative for equities; more negative when slope is more negative
    """
    v0 = max(iv30**2, 1e-8)
    theta = max(iv90**2, 1e-8)
    # Term-structure speed: how fast variance drifts from 30d to 90d
    mid = max(iv60**2, 1e-8)
    # Rough κ so that e^{-κ * 60/365} blends v0 → θ
    gap = abs(v0 - theta) + abs(mid - theta)
    kappa = _clamp(3.0 + 10.0 * gap, 0.5, 8.0)

    # Skew slope (ORATS-style, often O(1)); map to |ρ| and ξ
    # Negative slope → negative ρ (leverage)
    rho = _clamp(-0.55 + 0.15 * (slope / 10.0), -0.95, -0.15)
    xi = _clamp(0.35 + 0.08 * abs(slope), 0.2, 1.5)

    return {
        "model": "heston",
        "s0": s0,
        "v0": v0,
        "mu": 0.0,
        "kappa": kappa,
        "theta": theta,
        "xi": xi,
        "rho": rho,
        "scheme": "qe",
    }


def calibrate_rbergomi_from_iv(
    iv30: float,
    iv60: float,
    iv90: float,
    slope: float = 0.0,
    s0: float = 100.0,
    hurst: float = 0.1,
) -> dict[str, Any]:
    """Map IV + slope into rough Bergomi parameters.

    Defaults H=0.1 (Gatheral–Jaisson–Rosenbaum). η and ρ absorb skew intensity.
    """
    knots = forward_variance_from_iv(iv30, iv60, iv90)
    # η ↑ with |short skew|; ρ more negative with negative slope
    eta = _clamp(1.2 + 0.12 * abs(slope), 0.5, 3.5)
    rho = _clamp(-0.6 + 0.12 * (slope / 10.0), -0.95, -0.2)
    xi0_flat = max(iv60**2, 1e-8)

    return {
        "model": "rough_bergomi",
        "s0": s0,
        "mu": 0.0,
        "hurst": hurst,
        "eta": eta,
        "rho": rho,
        "xi0_flat": xi0_flat,
        "forward_variance_knots": knots,
    }


def calibrate_from_iv_surface(
    iv30: float,
    iv60: float,
    iv90: float,
    slope: float = 0.0,
    s0: float = 100.0,
    hurst: float = 0.1,
) -> dict[str, Any]:
    """Return both Heston and rough Bergomi calibrations plus forward-variance knots."""
    if min(iv30, iv60, iv90) <= 0:
        raise ValueError("implied vols must be positive")

    knots = forward_variance_from_iv(iv30, iv60, iv90)
    return {
        "inputs": {
            "iv30": iv30,
            "iv60": iv60,
            "iv90": iv90,
            "slope": slope,
            "s0": s0,
        },
        "forward_variance_knots": knots,
        "heston": calibrate_heston_from_iv(iv30, iv60, iv90, slope, s0),
        "rough_bergomi": calibrate_rbergomi_from_iv(
            iv30, iv60, iv90, slope, s0, hurst
        ),
    }
