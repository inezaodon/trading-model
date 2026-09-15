"""Tests for VaR / ES engine and scenario generators."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from monte_carlo_var.api import run_var
from monte_carlo_var.data import (
    DEFAULT_TICKERS,
    generate_synthetic_returns,
    load_portfolio_returns,
    write_sample_csv,
)
from monte_carlo_var.engine import compute_var_es, summarize_pnl
from monte_carlo_var.portfolio import normalize_weights, portfolio_log_to_pnl
from monte_carlo_var.scenarios import generate_scenarios

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "sample_returns.csv"


@pytest.fixture(scope="module", autouse=True)
def ensure_sample_csv():
    if not DATA.exists():
        write_sample_csv(path=DATA, seed=42)
    yield


def test_default_tickers():
    assert DEFAULT_TICKERS == ("QQQ", "SPY", "IWM", "TLT", "GLD")


def test_synthetic_reproducible():
    a = generate_synthetic_returns(seed=7, n_days=100)
    b = generate_synthetic_returns(seed=7, n_days=100)
    np.testing.assert_allclose(a["returns"], b["returns"])


def test_load_bundled_returns():
    data = load_portfolio_returns(prefer_download=False, seed=42)
    assert data["returns"].shape[1] == 5
    assert data["n_days"] >= 100
    assert set(data["tickers"]) == set(DEFAULT_TICKERS)


def test_normalize_weights():
    w = normalize_weights([1, 1, 1, 1, 1])
    np.testing.assert_allclose(w.sum(), 1.0)
    with pytest.raises(ValueError):
        normalize_weights([0, 0, 0])


def test_var_es_known_distribution():
    # Symmetric around 0 → 95% VaR ≈ +1.645 * std for normal losses convention
    rng = np.random.default_rng(0)
    pnl = rng.normal(0.0, 1.0, size=200_000)
    m = compute_var_es(pnl, confidence=0.95)
    assert m["var"] == pytest.approx(1.64485, rel=0.05)
    assert m["es"] > m["var"]


def test_es_exceeds_var():
    rng = np.random.default_rng(1)
    pnl = rng.standard_t(df=5, size=50_000)  # fat tails
    m95 = compute_var_es(pnl, 0.95)
    m99 = compute_var_es(pnl, 0.99)
    assert m95["es"] >= m95["var"] - 1e-9
    assert m99["var"] >= m95["var"] - 1e-6


def test_gbm_scenarios_shape_and_seed():
    data = load_portfolio_returns()
    s1 = generate_scenarios(data["returns"], method="gbm", n_scenarios=1000, seed=42)
    s2 = generate_scenarios(data["returns"], method="gbm", n_scenarios=1000, seed=42)
    assert s1["scenarios"].shape == (1000, 5)
    np.testing.assert_allclose(s1["scenarios"], s2["scenarios"])


def test_bootstrap_scenarios():
    data = load_portfolio_returns()
    s = generate_scenarios(
        data["returns"], method="bootstrap", horizon_days=5, n_scenarios=500, seed=3
    )
    assert s["scenarios"].shape == (500, 5)


def test_portfolio_pnl_sign():
    # All assets +10% log ≈ gain
    log_r = np.full((10, 5), np.log(1.1))
    pnl = portfolio_log_to_pnl(log_r, [0.2] * 5, portfolio_value=100.0)
    assert np.all(pnl > 0)


def test_run_var_json_contract():
    out = run_var(
        method="gbm",
        horizon_days=10,
        n_scenarios=2000,
        confidence_levels=(0.95, 0.99),
        seed=42,
    )
    assert out["project"] == "var"
    assert out["params"]["seed"] == 42
    assert len(out["risk_table"]) == 2
    assert out["risk_table"][0]["confidence"] == 0.95
    assert out["risk_table"][0]["var"] > 0
    assert out["risk_table"][1]["var"] >= out["risk_table"][0]["var"] - 1e-6
    assert "pnl_histogram" in out["chart"]
    # JSON serializable
    json.dumps(out)


def test_run_var_bootstrap_custom_weights():
    w = [0.3, 0.25, 0.15, 0.2, 0.1]
    out = run_var(method="bootstrap", weights=w, n_scenarios=1500, seed=11)
    assert out["params"]["weights"] == pytest.approx(w)
    assert summarize_pnl(np.array([1.0, 2.0, 3.0]))["mean"] == pytest.approx(2.0)


def test_cli_run(tmp_path, monkeypatch):
    import os

    out = tmp_path / "var.json"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "monte_carlo_var",
            "run",
            "--method",
            "gbm",
            "--n-scenarios",
            "1000",
            "--seed",
            "42",
            "--out",
            str(out),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(out.read_text())
    assert payload["slug"] == "var"
    assert payload["params"]["n_scenarios"] == 1000
