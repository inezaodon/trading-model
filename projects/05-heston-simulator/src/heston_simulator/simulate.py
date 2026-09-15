"""Heston SDEs: correlated Brownian spot + CIR variance (Euler / QE).

    dS_t = μ S_t dt + √v_t S_t dW^S
    dv_t = κ(θ − v_t) dt + ξ √v_t dW^v
    d⟨W^S, W^v⟩_t = ρ dt

Equity / Nasdaq calibrations typically use leverage ρ < 0.

Local implementation mirrors ``packages/core-math`` ``trading_model_math.heston``
and will re-export that package when it is installed (optional).
"""

from __future__ import annotations

from typing import Any, Literal

import numpy as np

Scheme = Literal["euler", "qe"]

# Nasdaq-style equity leverage defaults (illustrative research params).
NASDAQ_EQUITY_DEFAULTS: dict[str, Any] = {
    "s0": 100.0,
    "v0": 0.04,
    "mu": 0.05,
    "kappa": 2.0,
    "theta": 0.04,
    "xi": 0.5,
    "rho": -0.7,  # leverage: spot down ↔ vol up
    "t": 1.0,
    "n_steps": 252,
    "n_paths": 1,
    "scheme": "qe",
}


def _correlated_normals(
    rng: np.random.Generator,
    n_paths: int,
    n_steps: int,
    rho: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Generate correlated N(0,1) shocks (Z_v, Z_s) with Corr = ρ."""
    z_v = rng.standard_normal((n_paths, n_steps))
    z_ind = rng.standard_normal((n_paths, n_steps))
    z_s = rho * z_v + np.sqrt(max(0.0, 1.0 - rho**2)) * z_ind
    return z_v, z_s


def _simulate_heston_euler(
    s0: float,
    v0: float,
    mu: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    t: float,
    n_steps: int,
    n_paths: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Full-truncation Euler–Maruyama for Heston."""
    dt = t / n_steps
    sqrt_dt = np.sqrt(dt)
    times = np.linspace(0.0, t, n_steps + 1)

    s = np.empty((n_paths, n_steps + 1), dtype=float)
    v = np.empty((n_paths, n_steps + 1), dtype=float)
    s[:, 0] = s0
    v[:, 0] = v0

    z_v, z_s = _correlated_normals(rng, n_paths, n_steps, rho)

    for i in range(n_steps):
        v_pos = np.maximum(v[:, i], 0.0)
        sqrt_v = np.sqrt(v_pos)
        v[:, i + 1] = (
            v[:, i]
            + kappa * (theta - v_pos) * dt
            + xi * sqrt_v * sqrt_dt * z_v[:, i]
        )
        v[:, i + 1] = np.maximum(v[:, i + 1], 0.0)
        s[:, i + 1] = s[:, i] * np.exp(
            (mu - 0.5 * v_pos) * dt + sqrt_v * sqrt_dt * z_s[:, i]
        )

    return times, s, v


def _qe_variance_step(
    v: np.ndarray,
    kappa: float,
    theta: float,
    xi: float,
    dt: float,
    z: np.ndarray,
    u: np.ndarray,
    psi_c: float = 1.5,
) -> np.ndarray:
    """One Andersen QE step for the CIR variance process."""
    exp_k = np.exp(-kappa * dt)
    m = theta + (v - theta) * exp_k
    s2 = (
        v * xi**2 * exp_k * (1.0 - exp_k) / kappa
        + theta * xi**2 * (1.0 - exp_k) ** 2 / (2.0 * kappa)
    )
    m = np.maximum(m, 1e-16)
    psi = s2 / (m * m)

    v_next = np.empty_like(v)
    low = psi <= psi_c
    high = ~low

    if np.any(low):
        psi_l = psi[low]
        m_l = m[low]
        inv_psi = 1.0 / psi_l
        b2 = 2.0 * inv_psi - 1.0 + np.sqrt(2.0 * inv_psi) * np.sqrt(
            np.maximum(2.0 * inv_psi - 1.0, 0.0)
        )
        a = m_l / (1.0 + b2)
        b = np.sqrt(b2)
        v_next[low] = a * (b + z[low]) ** 2

    if np.any(high):
        psi_h = psi[high]
        m_h = m[high]
        p = (psi_h - 1.0) / (psi_h + 1.0)
        beta = (1.0 - p) / m_h
        u_h = u[high]
        v_next[high] = np.where(
            u_h <= p,
            0.0,
            np.log((1.0 - p) / np.maximum(1.0 - u_h, 1e-16)) / beta,
        )

    return np.maximum(v_next, 0.0)


def _simulate_heston_qe(
    s0: float,
    v0: float,
    mu: float,
    kappa: float,
    theta: float,
    xi: float,
    rho: float,
    t: float,
    n_steps: int,
    n_paths: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Andersen QE scheme with log-Euler spot update."""
    dt = t / n_steps
    times = np.linspace(0.0, t, n_steps + 1)

    s = np.empty((n_paths, n_steps + 1), dtype=float)
    v = np.empty((n_paths, n_steps + 1), dtype=float)
    s[:, 0] = s0
    v[:, 0] = v0

    z_v, z_s = _correlated_normals(rng, n_paths, n_steps, rho)
    u = rng.random((n_paths, n_steps))

    gamma1 = 0.5
    gamma2 = 0.5
    k0 = -rho * kappa * theta * dt / xi
    k1 = gamma1 * dt * (kappa * rho / xi - 0.5) - rho / xi
    k2 = gamma2 * dt * (kappa * rho / xi - 0.5) + rho / xi
    k3 = gamma1 * dt * (1.0 - rho**2)
    k4 = gamma2 * dt * (1.0 - rho**2)

    for i in range(n_steps):
        v[:, i + 1] = _qe_variance_step(
            v[:, i], kappa, theta, xi, dt, z_v[:, i], u[:, i]
        )
        log_s = (
            np.log(np.maximum(s[:, i], 1e-300))
            + mu * dt
            + k0
            + k1 * v[:, i]
            + k2 * v[:, i + 1]
            + np.sqrt(np.maximum(k3 * v[:, i] + k4 * v[:, i + 1], 0.0)) * z_s[:, i]
        )
        s[:, i + 1] = np.exp(log_s)

    return times, s, v


def _local_simulate_heston(
    s0: float = 100.0,
    v0: float = 0.04,
    mu: float = 0.05,
    kappa: float = 2.0,
    theta: float = 0.04,
    xi: float = 0.5,
    rho: float = -0.7,
    t: float = 1.0,
    n_steps: int = 252,
    n_paths: int = 1,
    scheme: Scheme = "qe",
    seed: int | None = None,
) -> dict[str, Any]:
    """Local full-truncation Euler or Andersen QE Heston simulator."""
    if s0 <= 0:
        raise ValueError("s0 must be positive")
    if v0 < 0 or theta < 0:
        raise ValueError("variances must be non-negative")
    if not -1.0 <= rho <= 1.0:
        raise ValueError("rho must be in [-1, 1]")
    if n_steps < 1 or n_paths < 1:
        raise ValueError("n_steps and n_paths must be >= 1")
    if t <= 0:
        raise ValueError("t must be positive")
    if scheme not in ("qe", "euler"):
        raise ValueError("scheme must be 'qe' or 'euler'")

    rng = np.random.default_rng(seed)
    if scheme == "euler":
        times, s, v = _simulate_heston_euler(
            s0, v0, mu, kappa, theta, xi, rho, t, n_steps, n_paths, rng
        )
    else:
        times, s, v = _simulate_heston_qe(
            s0, v0, mu, kappa, theta, xi, rho, t, n_steps, n_paths, rng
        )

    params = {
        "s0": float(s0),
        "v0": float(v0),
        "mu": float(mu),
        "kappa": float(kappa),
        "theta": float(theta),
        "xi": float(xi),
        "rho": float(rho),
        "t": float(t),
        "n_steps": int(n_steps),
        "n_paths": int(n_paths),
        "scheme": scheme,
        "seed": seed,
    }
    return {"times": times, "S": s, "v": v, "params": params}


def _try_core_math_simulate():
    """Return core-math ``simulate_heston`` if the optional package is present."""
    try:
        from trading_model_math.heston import simulate_heston as core_sim

        return core_sim
    except ImportError:
        return None


def simulate_heston(
    s0: float = 100.0,
    v0: float = 0.04,
    mu: float = 0.05,
    kappa: float = 2.0,
    theta: float = 0.04,
    xi: float = 0.5,
    rho: float = -0.7,
    t: float = 1.0,
    n_steps: int = 252,
    n_paths: int = 1,
    scheme: Scheme = "qe",
    seed: int | None = None,
    *,
    prefer_core_math: bool = True,
) -> dict[str, Any]:
    """Simulate Heston paths ``{times, S, v, params}``.

    Parameters
    ----------
    rho :
        Instantaneous correlation; equity / Nasdaq defaults are negative (leverage).
    scheme :
        ``"qe"`` (Andersen) or ``"euler"`` (full truncation).
    seed :
        RNG seed for reproducible paths.
    prefer_core_math :
        If True and ``trading_model_math`` is installed, delegate to it and
        normalize the returned params to this project's schema.
    """
    kwargs = dict(
        s0=s0,
        v0=v0,
        mu=mu,
        kappa=kappa,
        theta=theta,
        xi=xi,
        rho=rho,
        t=t,
        n_steps=n_steps,
        n_paths=n_paths,
        scheme=scheme,
        seed=seed,
    )

    core_sim = _try_core_math_simulate() if prefer_core_math else None
    if core_sim is not None:
        out = core_sim(**kwargs)
        # Normalize params so JSON contract always includes seed / grid sizes.
        params = dict(out.get("params", {}))
        params.update(
            {
                "s0": float(s0),
                "v0": float(v0),
                "mu": float(mu),
                "kappa": float(kappa),
                "theta": float(theta),
                "xi": float(xi),
                "rho": float(rho),
                "t": float(t),
                "n_steps": int(n_steps),
                "n_paths": int(n_paths),
                "scheme": scheme,
                "seed": seed,
                "engine": "trading_model_math",
            }
        )
        return {"times": out["times"], "S": out["S"], "v": out["v"], "params": params}

    out = _local_simulate_heston(**kwargs)
    out["params"]["engine"] = "heston_simulator"
    return out
