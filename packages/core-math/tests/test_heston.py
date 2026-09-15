"""Tests for Heston simulation."""

from __future__ import annotations

import numpy as np
import pytest

from trading_model_math.heston import simulate_heston


@pytest.mark.parametrize("scheme", ["qe", "euler"])
def test_heston_shapes_positive_spot(scheme: str):
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
    )
    assert out["S"].shape == (5, 49)
    assert out["v"].shape == (5, 49)
    assert np.all(out["S"] > 0)
    assert np.all(out["v"] >= 0)


def test_heston_seed_reproducible():
    kwargs = dict(
        s0=100, v0=0.04, kappa=1.5, theta=0.04, xi=0.4, rho=-0.6,
        t=1.0, n_steps=32, n_paths=2, scheme="qe",
    )
    a = simulate_heston(**kwargs, seed=42)
    b = simulate_heston(**kwargs, seed=42)
    c = simulate_heston(**kwargs, seed=99)
    np.testing.assert_allclose(a["S"], b["S"])
    np.testing.assert_allclose(a["v"], b["v"])
    assert not np.allclose(a["S"], c["S"])


def test_heston_leverage_correlation_negative_rho():
    """With ρ < 0, large negative spot moves should co-occur with vol spikes on average."""
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
    )
    dlog_s = np.diff(np.log(out["S"]), axis=1)
    dv = np.diff(out["v"], axis=1)
    corr = np.corrcoef(dlog_s.ravel(), dv.ravel())[0, 1]
    assert corr < 0.0


def test_heston_rejects_bad_rho():
    with pytest.raises(ValueError):
        simulate_heston(rho=1.5, n_steps=2, n_paths=1, seed=1)
