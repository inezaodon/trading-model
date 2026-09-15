"""Tests for GBM simulation."""

from __future__ import annotations

import numpy as np
import pytest

from gbm_simulator.simulate import simulate_gbm


def test_shapes_and_seed_reproducibility():
    a = simulate_gbm(s0=100, mu=0.05, sigma=0.2, t=1.0, n_steps=32, n_paths=5, seed=7)
    b = simulate_gbm(s0=100, mu=0.05, sigma=0.2, t=1.0, n_steps=32, n_paths=5, seed=7)
    c = simulate_gbm(s0=100, mu=0.05, sigma=0.2, t=1.0, n_steps=32, n_paths=5, seed=8)

    assert a.paths.shape == (5, 33)
    assert a.times.shape == (33,)
    np.testing.assert_allclose(a.paths, b.paths)
    assert not np.allclose(a.paths, c.paths)
    assert np.all(a.paths > 0)
    assert a.params["seed"] == 7
    assert a.params["model"] == "gbm"


def test_zero_vol_is_deterministic_drift():
    out = simulate_gbm(s0=100, mu=0.1, sigma=0.0, t=1.0, n_steps=10, n_paths=2, seed=1)
    expected = 100 * np.exp(0.1 * out.times)
    np.testing.assert_allclose(out.paths[0], expected, rtol=1e-12)
    np.testing.assert_allclose(out.paths[1], expected, rtol=1e-12)


def test_initial_spot():
    out = simulate_gbm(s0=123.45, n_paths=4, n_steps=8, seed=0)
    np.testing.assert_allclose(out.paths[:, 0], 123.45)


def test_theoretical_mean_in_stats():
    out = simulate_gbm(s0=100, mu=0.08, sigma=0.15, t=1.0, n_paths=1, seed=1)
    assert out.stats["theoretical_mean"] == pytest.approx(100 * np.exp(0.08))


def test_invalid_inputs():
    with pytest.raises(ValueError):
        simulate_gbm(s0=-1)
    with pytest.raises(ValueError):
        simulate_gbm(sigma=-0.1)
    with pytest.raises(ValueError):
        simulate_gbm(n_steps=0)
    with pytest.raises(ValueError):
        simulate_gbm(t=0)
