"""Chart-ready JSON export tests."""

from __future__ import annotations

import json
from pathlib import Path

from brownian_visualizer.brownian import simulate_brownian_1d, simulate_brownian_2d, simulate_scaled_brownian
from brownian_visualizer.export import result_to_chart_json, write_chart_json
from brownian_visualizer.random_walk import random_walk_to_bm_limit


def test_export_1d_series():
    r = simulate_brownian_1d(n_steps=10, n_paths=2, seed=1)
    payload = result_to_chart_json(r)
    assert payload["model"] == "brownian"
    assert payload["kind"] == "standard_bm_1d"
    assert payload["dim"] == 1
    assert len(payload["times"]) == 11
    assert len(payload["series"]) == 2
    assert payload["series"][0]["label"] == "path_0"
    assert len(payload["series"][0]["y"]) == 11
    assert "seed" in payload["params"]


def test_export_scaled_includes_wiener():
    r = simulate_scaled_brownian(mu=0.1, sigma=2.0, n_steps=8, n_paths=1, seed=2)
    payload = result_to_chart_json(r)
    assert payload["series"][0]["field"] == "X"
    assert "wiener" in payload
    assert len(payload["wiener"][0]["y"]) == 9


def test_export_2d_trajectories():
    r = simulate_brownian_2d(n_steps=20, n_paths=2, seed=3)
    payload = result_to_chart_json(r)
    assert payload["dim"] == 2
    assert len(payload["trajectories"]) == 2
    assert "x" in payload["trajectories"][0] and "y" in payload["trajectories"][0]
    assert len(payload["series"]) == 4  # x and y per path


def test_export_rw_limit():
    r = random_walk_to_bm_limit(n_steps=50, n_paths=1, seed=4)
    payload = result_to_chart_json(r)
    assert payload["kind"] == "random_walk_bm_limit"
    assert len(payload["series"][0]["y"]) == 51


def test_write_chart_json_file(tmp_path: Path):
    r = simulate_brownian_1d(n_steps=5, n_paths=1, seed=0)
    out = tmp_path / "chart.json"
    write_chart_json(r, out)
    loaded = json.loads(out.read_text())
    assert loaded["model"] == "brownian"
    assert len(loaded["series"]) == 1
