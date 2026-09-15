"""Tests for rough Bergomi hybrid simulation."""

from __future__ import annotations

import numpy as np
import pytest

from rough_volatility.simulate import path_metrics, simulate_rough_bergomi


def test_shapes_positivity_and_seed_reproducibility():
    knots = [(30 / 365, 0.05), (60 / 365, 0.045), (90 / 365, 0.04)]
    kwargs = dict(
        s0=100.0,
        hurst=0.1,
        eta=1.5,
        rho=-0.7,
        t=0.5,
        n_steps=40,
        n_paths=3,
        forward_variance_knots=knots,
        seed=5,
    )
    a = simulate_rough_bergomi(**kwargs)
    b = simulate_rough_bergomi(**kwargs)
    assert a["S"].shape == (3, 41)
    assert a["v"].shape == (3, 41)
    assert a["xi0"].shape == (41,)
    assert np.all(a["S"] > 0)
    assert np.all(a["v"] > 0)
    np.testing.assert_allclose(a["S"], b["S"])
    np.testing.assert_allclose(a["v"], b["v"])
    assert a["params"]["seed"] == 5
    assert a["params"]["hurst"] == pytest.approx(0.1)


def test_flat_forward_variance_initial():
    out = simulate_rough_bergomi(
        s0=50.0,
        hurst=0.15,
        eta=1.0,
        rho=-0.5,
        t=0.25,
        n_steps=20,
        n_paths=2,
        xi0_flat=0.09,
        seed=1,
    )
    assert out["params"]["xi0_flat"] == 0.09
    assert out["v"][0, 0] == pytest.approx(0.09, rel=1e-6)
    assert out["xi0"][0] == pytest.approx(0.09, rel=1e-6)


def test_rejects_bad_hurst_and_s0():
    with pytest.raises(ValueError, match="hurst"):
        simulate_rough_bergomi(hurst=0.0, n_steps=2, n_paths=1, seed=1)
    with pytest.raises(ValueError, match="s0"):
        simulate_rough_bergomi(s0=-1.0, n_steps=2, n_paths=1, seed=1)


def test_path_metrics():
    out = simulate_rough_bergomi(n_steps=16, n_paths=5, t=0.25, seed=7, hurst=0.1)
    m = path_metrics(out)
    assert m["n_paths"] == 5
    assert m["n_steps"] == 16
    assert m["terminal_S_mean"] > 0
    assert m["terminal_v_mean"] > 0
