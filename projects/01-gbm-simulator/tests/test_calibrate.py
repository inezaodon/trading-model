"""Tests for μ/σ calibration from CSV prices."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from gbm_simulator.calibrate import estimate_mu_sigma, load_price_csv

DATA = Path(__file__).resolve().parents[1] / "data" / "qqq_sample.csv"


def test_estimate_known_series():
    # Construct exact GBM-like log returns with known moments
    rng = np.random.default_rng(0)
    dt = 1 / 252
    true_mu, true_sigma = 0.1, 0.25
    n = 50_000
    z = rng.standard_normal(n)
    r = (true_mu - 0.5 * true_sigma**2) * dt + true_sigma * np.sqrt(dt) * z
    prices = 100 * np.exp(np.cumsum(np.concatenate([[0.0], r])))
    est = estimate_mu_sigma(prices, dt=dt)
    assert est["mu"] == pytest.approx(true_mu, abs=0.02)
    assert est["sigma"] == pytest.approx(true_sigma, abs=0.01)


def test_load_bundled_sample():
    assert DATA.is_file()
    prices = load_price_csv(DATA)
    assert prices.ndim == 1
    assert prices.size == 504
    assert np.all(prices > 0)


def test_calibrate_bundled_sample_reasonable():
    prices = load_price_csv(DATA)
    est = estimate_mu_sigma(prices)
    # Synthetic QQQ-like: mu~0.12, sigma~0.22 — allow wide band
    assert 0.0 < est["sigma"] < 0.6
    assert -0.5 < est["mu"] < 0.8
    assert est["s0"] == pytest.approx(float(prices[-1]))


def test_load_headerless_csv(tmp_path: Path):
    p = tmp_path / "prices.csv"
    p.write_text("100\n101\n99.5\n102\n", encoding="utf-8")
    prices = load_price_csv(p)
    np.testing.assert_allclose(prices, [100, 101, 99.5, 102])


def test_estimate_rejects_short_series():
    with pytest.raises(ValueError):
        estimate_mu_sigma(np.array([100.0]))
