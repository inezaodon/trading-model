"""Tests for API run() and CLI."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ornstein_uhlenbeck import run
from ornstein_uhlenbeck.cli import main
from ornstein_uhlenbeck.sample_data import load_sample_rates, write_synthetic_csv


def test_run_simulate_jsonable():
    out = run({"mode": "simulate", "n_paths": 2, "n_steps": 16, "seed": 42})
    assert out["project"] == "ou"
    assert out["mode"] == "simulate"
    assert out["seed"] == 42
    assert len(out["paths"]) == 2
    assert len(out["times"]) == 17
    json.dumps(out)  # must be serializable


def test_run_fit_and_signals_on_sample():
    fit = run({"mode": "fit", "series": "rate", "seed": 42})
    assert fit["fit"]["kappa"] > 0
    assert "fred_series" in fit["series_meta"] or "Treasury" in fit["treasury_fred_note"]

    sig = run({"mode": "signals", "series": "spread_2s10s", "seed": 42})
    assert len(sig["zscore"]) == len(sig["series"])
    assert "equity" in sig
    json.dumps(sig)


def test_run_demo():
    demo = run({"mode": "demo", "seed": 42, "n_paths": 2})
    assert "simulate" in demo and "fit" in demo and "signals" in demo
    assert demo["math"]["sde"].startswith("dX")


def test_run_fit_custom_observations():
    obs = np.linspace(1.0, 2.0, 80) + 0.05 * np.random.default_rng(0).standard_normal(80)
    out = run({"mode": "fit", "observations": obs.tolist(), "dt": 1 / 252})
    assert out["n_obs"] == 80
    assert out["fit"]["kappa"] >= 0


def test_cli_simulate_stdout(capsys):
    rc = main(["simulate", "--n-steps", "8", "--n-paths", "1", "--seed", "1"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["mode"] == "simulate"
    assert payload["seed"] == 1


def test_cli_write_and_load_sample(tmp_path: Path):
    csv = tmp_path / "rates.csv"
    path = write_synthetic_csv(csv, seed=42)
    assert path.is_file()
    data = load_sample_rates(path)
    assert data["rate"].size == data["spread_2s10s"].size
    assert data["rate"].size > 100


def test_seed_default_is_42():
    a = run({"mode": "simulate", "n_steps": 10, "n_paths": 1})
    b = run({"mode": "simulate", "n_steps": 10, "n_paths": 1, "seed": 42})
    assert a["paths"][0]["X"] == b["paths"][0]["X"]
