"""Tests for signatures and calibration."""

from __future__ import annotations

import numpy as np
import pytest

from trading_model_math.calibrate import (
    calibrate_from_iv_surface,
    forward_variance_from_iv,
)
from trading_model_math.signatures import (
    batch_signature_features,
    truncated_signature,
)


def test_truncated_signature_level1_is_total_increment():
    path = np.array([[0.0, 0.0], [1.0, 2.0], [1.5, 2.5]])
    sig = truncated_signature(path, level=1)
    np.testing.assert_allclose(sig, np.array([1.5, 2.5]))


def test_truncated_signature_level2_dim():
    # d=2 → level1: 2, level2: 4 → total 6
    path = np.linspace(0, 1, 10).reshape(-1, 1)
    path = np.column_stack([path, path**2])
    sig = truncated_signature(path, level=2)
    assert sig.shape == (6,)


def test_truncated_signature_level3_dim():
    # d=1 → 1 + 1 + 1 = 3
    path = np.linspace(0, 1, 8)
    sig = truncated_signature(path, level=3)
    assert sig.shape == (3,)
    assert np.isfinite(sig).all()


def test_batch_signature_features():
    s = np.exp(np.cumsum(np.random.default_rng(0).normal(0, 0.01, size=(4, 20)), axis=1))
    s = 100 * s / s[:, :1]
    v = np.full_like(s, 0.04)
    feats = batch_signature_features(s, v, level=2)
    assert feats.shape[0] == 4
    assert feats.shape[1] > 0


def test_forward_variance_knots_positive():
    knots = forward_variance_from_iv(0.22, 0.21, 0.20)
    assert len(knots) == 3
    assert all(k[1] > 0 for k in knots)
    assert knots[0][0] == pytest.approx(30 / 365)


def test_calibrate_from_iv_surface_equity_leverage():
    cal = calibrate_from_iv_surface(0.25, 0.23, 0.22, slope=-2.0, s0=400.0)
    assert cal["heston"]["rho"] < 0
    assert cal["rough_bergomi"]["rho"] < 0
    assert cal["rough_bergomi"]["hurst"] == 0.1
    assert cal["heston"]["v0"] == pytest.approx(0.25**2)
    assert len(cal["forward_variance_knots"]) == 3


def test_calibrate_rejects_nonpositive_iv():
    with pytest.raises(ValueError):
        calibrate_from_iv_surface(0.0, 0.2, 0.2)
