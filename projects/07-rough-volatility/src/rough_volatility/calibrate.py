"""Map NASDAQ-style IV surface summaries to rough Bergomi parameters.

Uses ORATS / NASDAQ Data Link constant-maturity fields:

- ``iv30``, ``iv60``, ``iv90`` → forward variance knots ξ₀(t) ≈ IV(t)²
- ``slope`` → roughness amplitude η and leverage ρ

See ``docs/NASDAQ_IV.md`` in this project and the umbrella
``docs/NASDAQ_DATA.md`` for field definitions.
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
    if min(iv30, iv60, iv90) <= 0:
        raise ValueError("implied vols must be positive")

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


def calibrate_from_nasdaq_iv(
    iv30: float,
    iv60: float,
    iv90: float,
    slope: float = -1.5,
    s0: float = 100.0,
    hurst: float = 0.1,
    symbol: str = "QQQ",
) -> dict[str, Any]:
    """Heuristic calibration from NASDAQ-style IV30/60/90 + skew slope.

    Defaults match Gatheral–Jaisson–Rosenbaum equity roughness (H ≈ 0.1)
    and negative leverage typical of Nasdaq-100 / QQQ underlyings.
    """
    if min(iv30, iv60, iv90) <= 0:
        raise ValueError("implied vols must be positive")
    if not 0.0 < hurst < 1.0:
        raise ValueError("hurst must be in (0, 1)")
    if s0 <= 0:
        raise ValueError("s0 must be positive")

    knots = forward_variance_from_iv(iv30, iv60, iv90)
    eta = _clamp(1.2 + 0.12 * abs(slope), 0.5, 3.5)
    rho = _clamp(-0.6 + 0.12 * (slope / 10.0), -0.95, -0.2)
    xi0_flat = max(iv60**2, 1e-8)

    return {
        "model": "rough_bergomi",
        "symbol": symbol,
        "inputs": {
            "iv30": iv30,
            "iv60": iv60,
            "iv90": iv90,
            "slope": slope,
            "s0": s0,
            "hurst": hurst,
        },
        "params": {
            "s0": s0,
            "mu": 0.0,
            "hurst": hurst,
            "eta": eta,
            "rho": rho,
            "xi0_flat": xi0_flat,
            "forward_variance_knots": knots,
        },
        "forward_variance_knots": knots,
        "notes": (
            "Heuristic mapping from NASDAQ Data Link / ORATS-style IV summaries; "
            "not a full smile least-squares calibration. Educational use only."
        ),
    }


# Default mock QQQ-like surface for offline demos (deterministic).
DEFAULT_NASDAQ_MOCK = {
    "symbol": "QQQ",
    "iv30": 0.22,
    "iv60": 0.21,
    "iv90": 0.20,
    "slope": -1.5,
    "s0": 450.0,
}
