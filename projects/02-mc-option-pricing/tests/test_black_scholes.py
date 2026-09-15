"""Tests for Black–Scholes closed form."""

import math

import pytest

from mc_option_pricing.black_scholes import black_scholes_price


def test_atm_call_put_parity():
    s, k, r, vol, t = 100.0, 100.0, 0.05, 0.2, 1.0
    call = black_scholes_price(s, k, r, vol, t, "call")
    put = black_scholes_price(s, k, r, vol, t, "put")
    # C - P = S - K e^{-rT}
    assert call - put == pytest.approx(s - k * math.exp(-r * t), rel=1e-12)


def test_known_call_reference():
    # Classic textbook-ish ATM: S=K=100, r=0.05, σ=0.2, T=1
    price = black_scholes_price(100, 100, 0.05, 0.2, 1.0, "call")
    assert price == pytest.approx(10.450583572185565, rel=1e-10)


def test_zero_maturity_intrinsic():
    assert black_scholes_price(110, 100, 0.05, 0.2, 0.0, "call") == pytest.approx(10.0)
    assert black_scholes_price(90, 100, 0.05, 0.2, 0.0, "put") == pytest.approx(10.0)
    assert black_scholes_price(90, 100, 0.05, 0.2, 0.0, "call") == pytest.approx(0.0)


def test_zero_vol_forward():
    s, k, r, t = 100.0, 105.0, 0.05, 1.0
    call = black_scholes_price(s, k, r, 0.0, t, "call")
    forward = s * math.exp(r * t)
    expected = math.exp(-r * t) * max(forward - k, 0.0)
    assert call == pytest.approx(expected)


def test_invalid_inputs():
    with pytest.raises(ValueError):
        black_scholes_price(-1, 100, 0.05, 0.2, 1.0)
    with pytest.raises(ValueError):
        black_scholes_price(100, 100, 0.05, -0.1, 1.0)
    with pytest.raises(ValueError):
        black_scholes_price(100, 100, 0.05, 0.2, 1.0, "straddle")  # type: ignore[arg-type]
