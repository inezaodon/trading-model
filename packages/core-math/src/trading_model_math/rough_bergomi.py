"""Rough Bergomi hybrid / kernel approximation.

Rough Bergomi variance (Bayer–Friz–Gatheral):

    v_t = ξ₀(t) exp(η √(2H) Z_t − ½ η² t^{2H})

where Z is a Volterra / Riemann–Liouville-type Gaussian process with kernel

    K(t,s) ∝ (t − s)^{H − 1/2},  H ≈ 0.1.

This module uses a practical hybrid discrete scheme:

1. Build a lower-triangular kernel matrix on the time grid.
2. Drive Z via a Cholesky-style (or hybrid Euler) convolution of white noise.
3. Interpolate a piecewise-linear forward variance curve ξ₀ from knots.
4. Evolve the spot with correlated Brownian noise (leverage ρ).

References: Gatheral–Jaisson–Rosenbaum; Bayer–Friz–Gatheral (2016).
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np


def _forward_variance_curve(
    times: np.ndarray,
    knots: Sequence[tuple[float, float]] | None,
    flat: float = 0.04,
) -> np.ndarray:
    """Piecewise-linear ξ₀(t) from (maturity, variance) knots; constant if none."""
    if not knots:
        return np.full_like(times, flat, dtype=float)

    maturities = np.asarray([k[0] for k in knots], dtype=float)
    variances = np.asarray([k[1] for k in knots], dtype=float)
    order = np.argsort(maturities)
    maturities = maturities[order]
    variances = variances[order]

    # Extrapolate flat beyond endpoints
    xi = np.interp(times, maturities, variances, left=variances[0], right=variances[-1])
    return np.maximum(xi, 1e-12)


def _rl_kernel_matrix(times: np.ndarray, hurst: float) -> np.ndarray:
    """Discrete Riemann–Liouville kernel K_{ij} ≈ ∫_{t_j}^{t_{j+1}} (t_i − s)^{H−1/2} ds.

    For i > j we use the exact antiderivative of (t − s)^{H−1/2}; diagonal uses
    a local Euler weight so the scheme remains hybrid (hybrid Euler + kernel).
    """
    n = len(times) - 1
    alpha = hurst + 0.5  # exponent + 1 for antiderivative: ∫ u^{H-1/2} = u^{H+1/2}/(H+1/2)
    h_half = hurst - 0.5
    K = np.zeros((n, n), dtype=float)

    for i in range(n):
        t_i = times[i + 1]
        for j in range(i + 1):
            t0 = times[j]
            t1 = times[j + 1]
            if i == j:
                # Local hybrid weight on [t_j, t_{j+1}]
                dt = t1 - t0
                K[i, j] = (dt**hurst) / (hurst + 0.5) if hurst > 0 else np.sqrt(dt)
            else:
                # ∫_{t0}^{t1} (t_i − s)^{H−1/2} ds
                u0 = t_i - t1
                u1 = t_i - t0
                if alpha == 0:
                    K[i, j] = np.log(u1 / max(u0, 1e-300))
                else:
                    K[i, j] = (u1**alpha - max(u0, 0.0) ** alpha) / alpha
                # For H < 1/2, h_half < 0; keep non-negative measure
                K[i, j] = max(K[i, j], 0.0)

    # Normalize so Var(Z_{t_n}) ≈ t_n^{2H} under white-noise drive (hybrid scaling)
    # Scaling factor √(2H) is applied outside via η√(2H).
    return K


def _volterra_field(
    kernel: np.ndarray,
    white: np.ndarray,
) -> np.ndarray:
    """Z path increments: Z_{t_{i+1}} = Σ_j K_{ij} W_j  (white already scaled by √Δt)."""
    # white: (n_paths, n_steps); kernel: (n_steps, n_steps)
    return white @ kernel.T


def simulate_rough_bergomi(
    s0: float = 100.0,
    mu: float = 0.0,
    hurst: float = 0.1,
    eta: float = 1.5,
    rho: float = -0.7,
    t: float = 1.0,
    n_steps: int = 252,
    n_paths: int = 1,
    forward_variance_knots: Sequence[tuple[float, float]] | None = None,
    xi0_flat: float = 0.04,
    seed: int | None = None,
) -> dict[str, Any]:
    """Simulate rough Bergomi spot and instantaneous variance paths.

    Parameters
    ----------
    hurst :
        Hurst exponent H (≈ 0.1 for equities).
    eta :
        Vol-of-vol / roughness amplitude.
    rho :
        Correlation between spot Brownian and the driving noise of Z.
    forward_variance_knots :
        Sequence of ``(maturity_years, forward_variance)`` knots for ξ₀(t).
    xi0_flat :
        Constant forward variance when no knots are supplied.
    """
    if s0 <= 0:
        raise ValueError("s0 must be positive")
    if not 0.0 < hurst < 1.0:
        raise ValueError("hurst must be in (0, 1)")
    if not -1.0 <= rho <= 1.0:
        raise ValueError("rho must be in [-1, 1]")
    if n_steps < 1 or n_paths < 1:
        raise ValueError("n_steps and n_paths must be >= 1")

    rng = np.random.default_rng(seed)
    times = np.linspace(0.0, t, n_steps + 1)
    dt = t / n_steps
    sqrt_dt = np.sqrt(dt)

    xi0 = _forward_variance_curve(times, forward_variance_knots, flat=xi0_flat)
    kernel = _rl_kernel_matrix(times, hurst)

    # Driving noises: W^v for the Volterra field, correlated W^s for the spot
    w_v = rng.standard_normal((n_paths, n_steps)) * sqrt_dt
    w_ind = rng.standard_normal((n_paths, n_steps)) * sqrt_dt
    w_s = rho * w_v + np.sqrt(max(0.0, 1.0 - rho**2)) * w_ind

    z = _volterra_field(kernel, w_v)  # (n_paths, n_steps) values at t_1..t_n
    # Prepend Z_0 = 0
    z_full = np.concatenate([np.zeros((n_paths, 1)), z], axis=1)

    # Variance: v_t = ξ₀(t) exp(η√(2H) Z_t − ½ η² t^{2H})
    t_safe = np.maximum(times, 0.0)
    log_v = (
        eta * np.sqrt(2.0 * hurst) * z_full
        - 0.5 * eta**2 * (t_safe ** (2.0 * hurst))
    )
    v = xi0 * np.exp(log_v)
    v = np.maximum(v, 1e-16)

    # Spot: hybrid Euler under rough variance (log scheme).
    # w_s already includes √dt, so the diffusion term is √v_t * W^s_increment.
    s = np.empty((n_paths, n_steps + 1), dtype=float)
    s[:, 0] = s0
    for i in range(n_steps):
        vol = np.sqrt(v[:, i])
        s[:, i + 1] = s[:, i] * np.exp((mu - 0.5 * v[:, i]) * dt + vol * w_s[:, i])

    params = {
        "s0": s0,
        "mu": mu,
        "hurst": hurst,
        "eta": eta,
        "rho": rho,
        "t": t,
        "xi0_flat": xi0_flat,
        "forward_variance_knots": (
            [list(k) for k in forward_variance_knots]
            if forward_variance_knots is not None
            else None
        ),
    }
    return {"times": times, "S": s, "v": v, "params": params}
