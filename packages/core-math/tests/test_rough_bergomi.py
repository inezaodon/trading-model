"""Tests for rough Bergomi hybrid scheme."""

from __future__ import annotations

import numpy as np
import pytest

from trading_model_math.rough_bergomi import simulate_rough_bergomi


def test_rbergomi_shapes_and_seed():
    knots = [(30 / 365, 0.05), (60 / 365, 0.045), (90 / 365, 0.04)]
    a = simulate_rough_bergomi(
        s0=100,
        hurst=0.1,
        eta=1.5,
        rho=-0.7,
        t=0.5,
        n_steps=40,
        n_paths=3,
        forward_variance_knots=knots,
        seed=5,
    )
    b = simulate_rough_bergomi(
        s0=100,
        hurst=0.1,
        eta=1.5,
        rho=-0.7,
        t=0.5,
        n_steps=40,
        n_paths=3,
        forward_variance_knots=knots,
        seed=5,
    )
    assert a["S"].shape == (3, 41)
    assert a["v"].shape == (3, 41)
    assert np.all(a["S"] > 0)
    assert np.all(a["v"] > 0)
    np.testing.assert_allclose(a["S"], b["S"])
    np.testing.assert_allclose(a["v"], b["v"])


def test_rbergomi_flat_forward_variance():
    out = simulate_rough_bergomi(
        s0=50,
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


def test_rbergomi_rejects_bad_hurst():
    with pytest.raises(ValueError):
        simulate_rough_bergomi(hurst=0.0, n_steps=2, n_paths=1, seed=1)
