"""Tests for OU fitting."""

from __future__ import annotations

import numpy as np
import pytest

from ornstein_uhlenbeck.fit import fit_ou
from ornstein_uhlenbeck.simulate import simulate_ou


def test_fit_recovers_params_approximately():
    # Daily AR(1) κ estimates are noisy on short samples; use a long path.
    true = {"kappa": 2.5, "theta": 4.0, "sigma": 0.8, "x0": 3.5}
    dt = 1.0 / 252.0
    t = 20.0
    sim = simulate_ou(
        x0=true["x0"],
        kappa=true["kappa"],
        theta=true["theta"],
        sigma=true["sigma"],
        t=t,
        n_steps=int(t / dt),
        n_paths=1,
        scheme="exact",
        seed=0,
    )
    fitted = fit_ou(sim["X"][0], dt=dt)

    assert fitted["method"] == "ar1_exact"
    assert fitted["kappa"] == pytest.approx(true["kappa"], rel=0.35)
    assert fitted["theta"] == pytest.approx(true["theta"], rel=0.1)
    assert fitted["sigma"] == pytest.approx(true["sigma"], rel=0.1)
    assert fitted["half_life"] == pytest.approx(np.log(2) / fitted["kappa"])


def test_fit_rejects_short_series():
    with pytest.raises(ValueError):
        fit_ou(np.array([1.0, 2.0]), dt=1 / 252)


def test_fit_sample_rates_column():
    from ornstein_uhlenbeck.sample_data import generate_synthetic_rates

    data = generate_synthetic_rates(seed=42)
    fitted = fit_ou(data["rate"], dt=data["dt"])
    true = data["true_params_rate"]
    assert fitted["kappa"] > 0
    assert fitted["theta"] == pytest.approx(true["theta"], rel=0.2)
