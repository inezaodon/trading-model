"""Tests for Heston simulation (Euler + QE)."""

from __future__ import annotations

import numpy as np
import pytest

from heston_simulator.simulate import NASDAQ_EQUITY_DEFAULTS, simulate_heston


@pytest.mark.parametrize("scheme", ["qe", "euler"])
def test_shapes_positive_spot_nonneg_variance(scheme: str):
    out = simulate_heston(
        s0=100,
        v0=0.04,
        kappa=2.0,
        theta=0.04,
        xi=0.5,
        rho=-0.7,
        t=0.5,
        n_steps=48,
        n_paths=5,
        scheme=scheme,  # type: ignore[arg-type]
        seed=11,
        prefer_core_math=False,
    )
    assert out["S"].shape == (5, 49)
    assert out["v"].shape == (5, 49)
    assert out["times"].shape == (49,)
    assert np.all(out["S"] > 0)
    assert np.all(out["v"] >= 0)
    assert "S" in out and "v" in out


def test_seed_reproducible():
    kwargs = dict(
        s0=100,
        v0=0.04,
        kappa=1.5,
        theta=0.04,
        xi=0.4,
        rho=-0.6,
        t=1.0,
        n_steps=32,
        n_paths=2,
        scheme="qe",
        prefer_core_math=False,
    )
    a = simulate_heston(**kwargs, seed=42)
    b = simulate_heston(**kwargs, seed=42)
    c = simulate_heston(**kwargs, seed=99)
    np.testing.assert_allclose(a["S"], b["S"])
    np.testing.assert_allclose(a["v"], b["v"])
    assert not np.allclose(a["S"], c["S"])


def test_leverage_correlation_negative_rho():
    """With ρ < 0, spot drops co-occur with vol spikes on average (equity leverage)."""
    out = simulate_heston(
        s0=100,
        v0=0.04,
        kappa=1.0,
        theta=0.04,
        xi=0.8,
        rho=-0.9,
        t=1.0,
        n_steps=128,
        n_paths=200,
        scheme="euler",
        seed=3,
        prefer_core_math=False,
    )
    dlog_s = np.diff(np.log(out["S"]), axis=1)
    dv = np.diff(out["v"], axis=1)
    corr = np.corrcoef(dlog_s.ravel(), dv.ravel())[0, 1]
    assert corr < 0.0


def test_nasdaq_defaults_have_negative_rho():
    assert NASDAQ_EQUITY_DEFAULTS["rho"] < 0


def test_rejects_bad_rho():
    with pytest.raises(ValueError, match="rho"):
        simulate_heston(rho=1.5, n_steps=2, n_paths=1, seed=1, prefer_core_math=False)


def test_rejects_bad_s0():
    with pytest.raises(ValueError, match="s0"):
        simulate_heston(s0=0.0, n_steps=2, n_paths=1, seed=1, prefer_core_math=False)


def test_params_include_seed_and_scheme():
    out = simulate_heston(n_steps=4, n_paths=1, seed=7, scheme="euler", prefer_core_math=False)
    assert out["params"]["seed"] == 7
    assert out["params"]["scheme"] == "euler"
    assert out["params"]["rho"] < 0
    assert out["params"]["engine"] == "heston_simulator"
