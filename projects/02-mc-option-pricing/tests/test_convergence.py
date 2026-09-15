"""Tests for convergence study output."""

from mc_option_pricing.convergence import convergence_study


def test_convergence_arrays_align():
    out = convergence_study(
        spot=100,
        strike=100,
        rate=0.05,
        vol=0.2,
        maturity=1.0,
        path_counts=[500, 1_000, 5_000],
        seed=11,
    )
    n = len(out["n_paths"])
    assert n == 3
    assert len(out["mc_price"]) == n
    assert len(out["stderr"]) == n
    assert len(out["ci_low"]) == n
    assert len(out["ci_high"]) == n
    assert len(out["abs_error"]) == n
    assert out["bs_price"] > 0
    # SE should generally shrink as N grows (allow tiny noise)
    assert out["stderr"][-1] < out["stderr"][0]


def test_abs_error_tracks_bs():
    out = convergence_study(path_counts=[2_000], seed=1)
    assert out["abs_error"][0] == abs(out["mc_price"][0] - out["bs_price"])
