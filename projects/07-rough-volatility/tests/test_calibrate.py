"""Tests for NASDAQ-style IV → rough Bergomi calibration."""

from __future__ import annotations

import pytest

from rough_volatility.calibrate import (
    DEFAULT_NASDAQ_MOCK,
    calibrate_from_nasdaq_iv,
    forward_variance_from_iv,
)


def test_forward_variance_knots_increasing_maturities():
    knots = forward_variance_from_iv(0.22, 0.21, 0.20)
    assert len(knots) == 3
    assert knots[0][0] == pytest.approx(30 / 365)
    assert knots[1][0] == pytest.approx(60 / 365)
    assert knots[2][0] == pytest.approx(90 / 365)
    assert all(k[1] > 0 for k in knots)


def test_calibrate_qqq_mock_defaults():
    cal = calibrate_from_nasdaq_iv(
        DEFAULT_NASDAQ_MOCK["iv30"],
        DEFAULT_NASDAQ_MOCK["iv60"],
        DEFAULT_NASDAQ_MOCK["iv90"],
        slope=DEFAULT_NASDAQ_MOCK["slope"],
        s0=DEFAULT_NASDAQ_MOCK["s0"],
        symbol="QQQ",
    )
    assert cal["model"] == "rough_bergomi"
    assert cal["symbol"] == "QQQ"
    assert cal["params"]["hurst"] == pytest.approx(0.1)
    assert cal["params"]["rho"] < 0  # equity leverage
    assert cal["params"]["eta"] > 0
    assert len(cal["forward_variance_knots"]) == 3


def test_calibrate_rejects_nonpositive_iv():
    with pytest.raises(ValueError, match="implied vols"):
        calibrate_from_nasdaq_iv(0.0, 0.2, 0.2)
