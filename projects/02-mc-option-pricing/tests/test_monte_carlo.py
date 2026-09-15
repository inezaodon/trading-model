"""Tests for Monte Carlo European pricing."""

import math

import pytest

from mc_option_pricing.black_scholes import black_scholes_price
from mc_option_pricing.monte_carlo import price_european_mc
from mc_option_pricing.samples import SAMPLE_PARAMS, get_sample


def test_seed_reproducibility():
    a = price_european_mc(n_paths=5_000, seed=7)
    b = price_european_mc(n_paths=5_000, seed=7)
    c = price_european_mc(n_paths=5_000, seed=8)
    assert a["price"] == b["price"]
    assert a["stderr"] == b["stderr"]
    assert a["price"] != c["price"]


def test_json_schema_keys():
    out = price_european_mc(n_paths=2_000, seed=1)
    for key in ("price", "stderr", "bs_price", "paths_used", "params"):
        assert key in out
    assert out["paths_used"] == 2_000
    assert "ci_low" in out and "ci_high" in out
    assert out["ci_low"] <= out["price"] <= out["ci_high"]


def test_mc_close_to_bs_large_n():
    kwargs = dict(
        spot=100.0,
        strike=100.0,
        rate=0.05,
        vol=0.2,
        maturity=1.0,
        option_type="call",
        n_paths=200_000,
        n_steps=1,
        seed=123,
    )
    out = price_european_mc(**kwargs)
    assert abs(out["price"] - out["bs_price"]) < 0.15
    # BS should sit inside a wide CI almost surely at this N
    assert out["ci_low"] - 0.5 < out["bs_price"] < out["ci_high"] + 0.5


def test_put_call_parity_mc():
    common = dict(spot=100.0, strike=100.0, rate=0.05, vol=0.25, maturity=0.5, n_paths=80_000, seed=99)
    call = price_european_mc(option_type="call", **common)
    put = price_european_mc(option_type="put", **common)
    lhs = call["price"] - put["price"]
    rhs = common["spot"] - common["strike"] * math.exp(-common["rate"] * common["maturity"])
    assert lhs == pytest.approx(rhs, abs=0.25)


def test_zero_maturity():
    out = price_european_mc(spot=110, strike=100, maturity=0.0, option_type="call", n_paths=100, seed=1)
    assert out["price"] == pytest.approx(10.0)
    assert out["stderr"] == 0.0
    assert out["bs_price"] == pytest.approx(10.0)


def test_multi_step_matches_one_step_in_distribution():
    # Exact GBM: multi-step and one-step share the same terminal law in expectation;
    # with same seed the streams differ, so only check both near BS.
    bs = black_scholes_price(100, 100, 0.05, 0.2, 1.0, "call")
    one = price_european_mc(spot=100, strike=100, rate=0.05, vol=0.2, maturity=1.0, n_paths=100_000, n_steps=1, seed=3)
    multi = price_european_mc(spot=100, strike=100, rate=0.05, vol=0.2, maturity=1.0, n_paths=100_000, n_steps=64, seed=4)
    assert abs(one["price"] - bs) < 0.2
    assert abs(multi["price"] - bs) < 0.2


def test_sample_params_run():
    sample = get_sample("QQQ")
    out = price_european_mc(
        spot=sample["spot"],
        strike=sample["strike"],
        rate=sample["rate"],
        vol=sample["vol"],
        maturity=sample["maturity"],
        option_type=sample["option_type"],
        n_paths=5_000,
        seed=42,
    )
    assert out["price"] > 0
    assert out["bs_price"] > 0


def test_all_samples_have_required_keys():
    required = {"symbol", "spot", "strike", "rate", "vol", "maturity", "option_type"}
    for sym, params in SAMPLE_PARAMS.items():
        assert required.issubset(params.keys()), sym
