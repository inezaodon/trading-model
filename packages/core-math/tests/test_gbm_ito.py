"""Tests for GBM and Itô helpers."""

from __future__ import annotations

import numpy as np
import pytest

from trading_model_math.gbm import simulate_gbm
from trading_model_math.ito import (
    apply_ito_log,
    expected_ito_correction,
    ito_drift_diffusion,
    ito_log_sde_coeffs,
    log_returns,
)


def test_gbm_shapes_and_seed_reproducibility():
    a = simulate_gbm(s0=100, mu=0.05, sigma=0.2, t=1.0, n_steps=32, n_paths=3, seed=7)
    b = simulate_gbm(s0=100, mu=0.05, sigma=0.2, t=1.0, n_steps=32, n_paths=3, seed=7)
    c = simulate_gbm(s0=100, mu=0.05, sigma=0.2, t=1.0, n_steps=32, n_paths=3, seed=8)

    assert a["S"].shape == (3, 33)
    assert a["v"].shape == (3, 33)
    assert a["times"].shape == (33,)
    np.testing.assert_allclose(a["S"], b["S"])
    assert not np.allclose(a["S"], c["S"])
    assert np.all(a["S"] > 0)


def test_gbm_zero_vol_is_deterministic_drift():
    out = simulate_gbm(s0=100, mu=0.1, sigma=0.0, t=1.0, n_steps=10, n_paths=2, seed=1)
    expected = 100 * np.exp(0.1 * out["times"])
    np.testing.assert_allclose(out["S"][0], expected, rtol=1e-12)
    np.testing.assert_allclose(out["S"][1], expected, rtol=1e-12)


def test_log_returns_and_ito_log():
    prices = np.array([100.0, 110.0, 99.0])
    lr = log_returns(prices)
    np.testing.assert_allclose(lr, np.diff(np.log(prices)))
    np.testing.assert_allclose(apply_ito_log(prices), np.log(prices))


def test_ito_log_coeffs():
    drift, diff = ito_log_sde_coeffs(0.05, 0.2)
    assert drift == pytest.approx(0.05 - 0.5 * 0.04)
    assert diff == pytest.approx(0.2)


def test_ito_lemma_identity_for_f_equals_s():
    # f(S)=S → f_S=1, f_SS=0 → drift=μS, diffusion=σS
    drift, diffusion = ito_drift_diffusion(100.0, 0.05, 0.2, 0.0, 1.0, 0.0)
    assert drift == pytest.approx(5.0)
    assert diffusion == pytest.approx(20.0)


def test_expected_ito_correction():
    assert expected_ito_correction(0.2, 0.01) == pytest.approx(0.5 * 0.04 * 0.01)
