"""Tests for JSON / Plotly export and CLI."""

from __future__ import annotations

import json
from pathlib import Path

from gbm_simulator.cli import main
from gbm_simulator.export import (
    simulation_to_json,
    to_plotly_figure_dict,
    write_json,
    write_plotly_json,
)
from gbm_simulator.simulate import simulate_gbm


def test_umbrella_json_contract():
    result = simulate_gbm(n_paths=3, n_steps=4, seed=1)
    payload = simulation_to_json(result)
    assert set(payload.keys()) == {"times", "paths", "params", "stats"}
    assert len(payload["times"]) == 5
    assert len(payload["paths"]) == 3
    assert len(payload["paths"][0]) == 5
    assert payload["params"]["seed"] == 1
    assert "mean_terminal" in payload["stats"]


def test_write_json_roundtrip(tmp_path: Path):
    result = simulate_gbm(n_paths=2, n_steps=3, seed=2)
    out = tmp_path / "out.json"
    write_json(result, out)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["params"]["n_paths"] == 2
    assert loaded["times"][0] == 0.0


def test_plotly_figure_dict():
    result = simulate_gbm(n_paths=10, n_steps=5, seed=3)
    fig = to_plotly_figure_dict(result, max_paths=4)
    # 4 paths + 1 mean trace
    assert len(fig["data"]) == 5
    assert fig["data"][-1]["name"] == "mean"
    assert "layout" in fig


def test_cli_simulate_json(tmp_path: Path):
    out = tmp_path / "sim.json"
    plotly = tmp_path / "fig.json"
    rc = main(
        [
            "simulate",
            "--n-paths",
            "5",
            "--n-steps",
            "10",
            "--seed",
            "42",
            "--json-out",
            str(out),
            "--plotly-out",
            str(plotly),
        ]
    )
    assert rc == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["params"]["seed"] == 42
    fig = json.loads(plotly.read_text(encoding="utf-8"))
    assert "data" in fig


def test_cli_calibrate_sample():
    rc = main(["calibrate"])
    assert rc == 0


def test_cli_stdout_json(capsys):
    rc = main(
        ["simulate", "--n-paths", "2", "--n-steps", "3", "--seed", "9", "--stdout-json"]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert set(payload.keys()) == {"times", "paths", "params", "stats"}


def test_write_plotly_json(tmp_path: Path):
    result = simulate_gbm(n_paths=3, n_steps=4, seed=0)
    path = write_plotly_json(result, tmp_path / "p.json", max_paths=2)
    assert path.is_file()
