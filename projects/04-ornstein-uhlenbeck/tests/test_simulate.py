"""Tests for OU simulation."""

from __future__ import annotations

import numpy as np
import pytest

from ornstein_uhlenbeck.simulate import simulate_ou, stationary_std


def test_shapes_and_seed_reproducibility():
    a = simulate_ou(x0=1.0, kappa=2.0, theta=0.5, sigma=0.3, t=1.0, n_steps=32, n_paths=3, seed=7)
    b = simulate_ou(x0=1.0, kappa=2.0, theta=0.5, sigma=0.3, t=1.0, n_steps=32, n_paths=3, seed=7)
    c = simulate_ou(x0=1.0, kappa=2.0, theta=0.5, sigma=0.3, t=1.0, n_steps=32, n_paths=3, seed=8)

    assert a["X"].shape == (3, 33)
    assert a["times"].shape == (33,)
    np.testing.assert_allclose(a["X"], b["X"])
    assert not np.allclose(a["X"], c["X"])
    assert a["params"]["seed"] == 7


def test_zero_sigma_is_deterministic_mean_reversion():
    out = simulate_ou(
        x0=2.0, kappa=1.0, theta=0.0, sigma=0.0, t=1.0, n_steps=10, n_paths=2, seed=1
    )
    expected = 2.0 * np.exp(-1.0 * out["times"])
    np.testing.assert_allclose(out["X"][0], expected, rtol=1e-12)
    np.testing.assert_allclose(out["X"][1], expected, rtol=1e-12)


def test_euler_scheme_runs():
    out = simulate_ou(
        x0=0.0, kappa=5.0, theta=1.0, sigma=0.2, t=0.5, n_steps=50, n_paths=1,
        scheme="euler", seed=0,
    )
    assert out["X"].shape == (1, 51)
    assert out["params"]["scheme"] == "euler"


def test_stationary_std():
    assert stationary_std(2.0, 0.5) == pytest.approx(0.5 / np.sqrt(4.0))


def test_validation():
    with pytest.raises(ValueError):
        simulate_ou(kappa=-1.0)
    with pytest.raises(ValueError):
        simulate_ou(sigma=-0.1)
    with pytest.raises(ValueError):
        simulate_ou(n_steps=0)
