"""Scenario generators: multivariate GBM and empirical bootstrap."""

from __future__ import annotations

from typing import Any, Literal

import numpy as np

Method = Literal["gbm", "bootstrap"]
_TRADING_DAYS = 252


def estimate_mu_cov(returns: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Daily mean vector and covariance from historical log-returns (T × N)."""
    r = np.asarray(returns, dtype=float)
    if r.ndim != 2 or r.shape[0] < 2:
        raise ValueError("returns must be T×N with T >= 2")
    mu = r.mean(axis=0)
    # Rowvar=False → variables in columns
    cov = np.cov(r, rowvar=False, ddof=1)
    if cov.ndim == 0:
        cov = np.array([[float(cov)]])
    # Numerical floor on diagonal
    diag = np.diag(cov).copy()
    diag = np.maximum(diag, 1e-12)
    np.fill_diagonal(cov, diag)
    return mu, cov


def simulate_gbm_horizon(
    mu_daily: np.ndarray,
    cov_daily: np.ndarray,
    horizon_days: int,
    n_scenarios: int,
    seed: int | None = None,
) -> np.ndarray:
    """Multi-asset GBM: cumulative log-return over ``horizon_days``.

    Under GBM, sum of daily log-returns ~ N(h μ, h Σ). We draw one
    multivariate normal per scenario for the horizon aggregate.
    """
    if horizon_days < 1:
        raise ValueError("horizon_days must be >= 1")
    if n_scenarios < 1:
        raise ValueError("n_scenarios must be >= 1")

    rng = np.random.default_rng(seed)
    mu_h = mu_daily * horizon_days
    cov_h = cov_daily * horizon_days
    # Stabilize covariance
    cov_h = 0.5 * (cov_h + cov_h.T)
    try:
        return rng.multivariate_normal(mu_h, cov_h, size=n_scenarios)
    except np.linalg.LinAlgError:
        jitter = np.eye(cov_h.shape[0]) * 1e-10
        return rng.multivariate_normal(mu_h, cov_h + jitter, size=n_scenarios)


def bootstrap_horizon(
    returns: np.ndarray,
    horizon_days: int,
    n_scenarios: int,
    seed: int | None = None,
) -> np.ndarray:
    """Empirical block bootstrap of joint daily returns, summed over horizon.

    Each scenario samples ``horizon_days`` historical days with replacement
    (iid day draws preserving cross-sectional dependence within a day) and
    sums log-returns.
    """
    r = np.asarray(returns, dtype=float)
    if r.ndim != 2 or r.shape[0] < 1:
        raise ValueError("returns must be T×N")
    if horizon_days < 1 or n_scenarios < 1:
        raise ValueError("horizon_days and n_scenarios must be >= 1")

    rng = np.random.default_rng(seed)
    t = r.shape[0]
    # indices shape: n_scenarios × horizon_days
    idx = rng.integers(0, t, size=(n_scenarios, horizon_days))
    # r[idx] → (n_scenarios, horizon_days, n_assets)
    sampled = r[idx]
    return sampled.sum(axis=1)


def generate_scenarios(
    returns: np.ndarray,
    method: Method = "gbm",
    horizon_days: int = 10,
    n_scenarios: int = 10_000,
    seed: int | None = 42,
) -> dict[str, Any]:
    """Produce scenario log-return matrix (n_scenarios × n_assets)."""
    method = method.lower()  # type: ignore[assignment]
    if method == "gbm":
        mu, cov = estimate_mu_cov(returns)
        scenarios = simulate_gbm_horizon(mu, cov, horizon_days, n_scenarios, seed)
        meta = {"mu_daily": mu, "cov_daily": cov}
    elif method == "bootstrap":
        scenarios = bootstrap_horizon(returns, horizon_days, n_scenarios, seed)
        meta = {}
    else:
        raise ValueError(f"unknown method: {method!r}; use 'gbm' or 'bootstrap'")

    return {
        "scenarios": scenarios,
        "method": method,
        "horizon_days": horizon_days,
        "n_scenarios": n_scenarios,
        "seed": seed,
        "meta": meta,
    }
