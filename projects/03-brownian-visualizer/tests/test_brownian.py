"""Tests for Wiener / scaled BM simulators."""

from __future__ import annotations

import numpy as np
import pytest

from brownian_visualizer.brownian import (
    simulate_brownian_1d,
    simulate_brownian_2d,
    simulate_scaled_brownian,
)


def test_standard_bm_starts_at_zero_and_shape():
    r = simulate_brownian_1d(t=1.0, n_steps=100, n_paths=4, seed=42)
    assert r["W"].shape == (4, 101)
    assert r["times"].shape == (101,)
    assert np.allclose(r["W"][:, 0], 0.0)
    assert r["times"][0] == 0.0 and r["times"][-1] == 1.0
    assert r["kind"] == "standard_bm_1d"


def test_bm_seed_reproducible():
    a = simulate_brownian_1d(n_steps=50, n_paths=2, seed=123)
    b = simulate_brownian_1d(n_steps=50, n_paths=2, seed=123)
    c = simulate_brownian_1d(n_steps=50, n_paths=2, seed=999)
    assert np.allclose(a["W"], b["W"])
    assert not np.allclose(a["W"], c["W"])


def test_bm_increment_variance():
    """Empirical Var(W_t) ≈ t for standard BM (Monte Carlo)."""
    t = 1.0
    n_paths = 8000
    r = simulate_brownian_1d(t=t, n_steps=64, n_paths=n_paths, seed=7)
    terminal = r["W"][:, -1]
    # E[W_t]=0, Var=t
    assert abs(terminal.mean()) < 0.05
    assert abs(terminal.var(ddof=1) - t) < 0.08


def test_scaled_bm_identity_when_mu0_sigma1():
    base = simulate_brownian_1d(n_steps=40, n_paths=2, seed=5)
    scaled = simulate_scaled_brownian(
        x0=0.0, mu=0.0, sigma=1.0, n_steps=40, n_paths=2, seed=5
    )
    assert np.allclose(base["W"], scaled["X"])
    assert np.allclose(base["W"], scaled["W"])


def test_scaled_bm_drift_and_scale():
    r = simulate_scaled_brownian(
        x0=10.0, mu=2.0, sigma=0.0, t=1.0, n_steps=10, n_paths=1, seed=0
    )
    # sigma=0 → deterministic line x0 + mu t
    expected = 10.0 + 2.0 * r["times"]
    assert np.allclose(r["X"][0], expected)


def test_brownian_2d_shape_and_origin():
    r = simulate_brownian_2d(n_steps=80, n_paths=3, seed=11, rho=0.5)
    assert r["X"].shape == (3, 81)
    assert r["Y"].shape == (3, 81)
    assert np.allclose(r["X"][:, 0], 0.0)
    assert np.allclose(r["Y"][:, 0], 0.0)
    assert r["dim"] == 2


def test_brownian_2d_rejects_bad_rho():
    with pytest.raises(ValueError, match="rho"):
        simulate_brownian_2d(rho=1.5, n_steps=10, seed=1)


def test_validation():
    with pytest.raises(ValueError):
        simulate_brownian_1d(t=0, n_steps=10)
    with pytest.raises(ValueError):
        simulate_scaled_brownian(sigma=-1, n_steps=10)
