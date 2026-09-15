"""Tests for z-score signals."""

from __future__ import annotations

import numpy as np
import pytest

from ornstein_uhlenbeck.signals import model_zscore, rolling_zscore, zscore_signals
from ornstein_uhlenbeck.simulate import simulate_ou, stationary_std


def test_model_zscore_scale():
    kappa, sigma, theta = 2.0, 0.5, 1.0
    x = np.array([1.0, 1.0 + stationary_std(kappa, sigma)])
    z = model_zscore(x, theta=theta, kappa=kappa, sigma=sigma)
    np.testing.assert_allclose(z, [0.0, 1.0])


def test_rolling_zscore_shape():
    x = np.linspace(0, 1, 100) + 0.01 * np.random.default_rng(0).standard_normal(100)
    z = rolling_zscore(x, window=20)
    assert z.shape == (100,)
    assert np.all(np.isnan(z[:19]))
    assert np.all(np.isfinite(z[19:]))


def test_zscore_signals_mean_reverting_path():
    sim = simulate_ou(
        x0=0.0, kappa=4.0, theta=0.0, sigma=0.4, t=2.0, n_steps=500, n_paths=1, seed=11
    )
    sig = zscore_signals(
        sim["X"][0],
        theta=0.0,
        kappa=4.0,
        sigma=0.4,
        entry=1.2,
        exit=0.2,
    )
    assert sig["mode"] == "model"
    assert sig["positions"].shape == sim["X"][0].shape
    assert set(np.unique(sig["positions"])).issubset({-1, 0, 1})
    assert "total_pnl" in sig["metrics"]
    assert "Research" in sig["disclaimer"]


def test_entry_exit_validation():
    with pytest.raises(ValueError):
        zscore_signals(np.arange(10.0), rolling_window=5, entry=1.0, exit=1.5)
