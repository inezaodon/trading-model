"""Tests for random walk and Donsker scaling."""

from __future__ import annotations

import numpy as np
import pytest

from brownian_visualizer.random_walk import (
    random_walk_to_bm_limit,
    simulate_random_walk_2d,
    simulate_simple_random_walk,
)


def test_simple_rw_steps_pm_one():
    r = simulate_simple_random_walk(n_steps=200, n_paths=5, seed=42)
    assert r["S"].shape == (5, 201)
    assert np.allclose(r["S"][:, 0], 0.0)
    diffs = np.diff(r["S"], axis=1)
    assert set(np.unique(diffs)).issubset({-1.0, 1.0})


def test_rw_seed_reproducible():
    a = simulate_simple_random_walk(n_steps=100, n_paths=2, seed=3)
    b = simulate_simple_random_walk(n_steps=100, n_paths=2, seed=3)
    assert np.allclose(a["S"], b["S"])


def test_biased_walk_drifts_positive():
    r = simulate_simple_random_walk(n_steps=5000, n_paths=200, p=0.7, seed=1)
    # E[S_n] = n(2p-1) = 5000*0.4 = 2000
    mean_end = r["S"][:, -1].mean()
    assert mean_end > 1500


def test_donsker_scaling_unit_time_variance():
    """For large n, Var(X_1) ≈ 1 under symmetric walk."""
    r = random_walk_to_bm_limit(n_steps=5000, n_paths=4000, t=1.0, p=0.5, seed=99)
    assert r["X"].shape == (4000, 5001)
    assert np.allclose(r["X"][:, 0], 0.0)
    assert abs(r["times"][-1] - 1.0) < 1e-12
    var = r["X"][:, -1].var(ddof=1)
    assert abs(var - 1.0) < 0.08


def test_donsker_matches_manual_scale():
    walk = simulate_simple_random_walk(n_steps=100, n_paths=2, seed=8)
    lim = random_walk_to_bm_limit(n_steps=100, n_paths=2, t=2.0, seed=8)
    assert np.allclose(lim["X"], walk["S"] / np.sqrt(100))
    assert np.allclose(lim["times"], np.linspace(0.0, 2.0, 101))


def test_rw_2d():
    r = simulate_random_walk_2d(n_steps=50, n_paths=2, seed=4)
    assert r["X"].shape == (2, 51)
    assert r["Y"].shape == (2, 51)
    # Manhattan step: exactly one coordinate changes by ±1 each step
    dx = np.diff(r["X"], axis=1)
    dy = np.diff(r["Y"], axis=1)
    assert np.all((np.abs(dx) + np.abs(dy)) == 1.0)


def test_invalid_p():
    with pytest.raises(ValueError):
        simulate_simple_random_walk(p=1.5, n_steps=10)
