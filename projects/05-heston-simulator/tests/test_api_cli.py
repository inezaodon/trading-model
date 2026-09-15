"""Tests for JSON API and CLI."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from heston_simulator.api import run_heston, to_jsonable
from heston_simulator.cli import main


def test_run_heston_json_contract():
    payload = run_heston(
        n_steps=16,
        n_paths=3,
        seed=42,
        scheme="qe",
        prefer_core_math=False,
    )
    assert payload["slug"] == "heston"
    assert "times" in payload
    assert "S" in payload
    assert "v" in payload
    assert "params" in payload
    assert "metrics" in payload

    assert isinstance(payload["times"], list)
    assert isinstance(payload["S"], list)
    assert isinstance(payload["v"], list)
    assert len(payload["S"]) == 3
    assert len(payload["S"][0]) == 17
    assert len(payload["v"]) == 3
    assert payload["params"]["rho"] < 0
    assert payload["params"]["seed"] == 42

    # Round-trip JSON serialization
    text = json.dumps(payload)
    again = json.loads(text)
    assert again["S"][0][0] == pytest.approx(100.0)


def test_run_heston_deterministic_seed():
    a = run_heston(n_steps=8, n_paths=1, seed=123, prefer_core_math=False)
    b = run_heston(n_steps=8, n_paths=1, seed=123, prefer_core_math=False)
    assert a["S"] == b["S"]
    assert a["v"] == b["v"]


def test_to_jsonable_nested():
    import numpy as np

    obj = {"x": np.array([1.0, 2.0]), "y": np.float64(3.5)}
    out = to_jsonable(obj)
    assert out == {"x": [1.0, 2.0], "y": 3.5}


def test_cli_stdout(capsys):
    code = main(
        [
            "--n-steps",
            "4",
            "--n-paths",
            "1",
            "--seed",
            "42",
            "--scheme",
            "euler",
            "--no-core-math",
            "--compact",
        ]
    )
    assert code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["slug"] == "heston"
    assert "S" in data and "v" in data
    assert data["params"]["seed"] == 42
    assert data["params"]["rho"] < 0


def test_cli_writes_file(tmp_path: Path):
    out = tmp_path / "paths.json"
    code = main(
        [
            "--n-steps",
            "4",
            "--n-paths",
            "2",
            "--seed",
            "7",
            "--no-core-math",
            "-o",
            str(out),
        ]
    )
    assert code == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["S"][0][0] == pytest.approx(100.0)
    assert len(data["v"]) == 2


def test_cli_bad_rho_exits_nonzero():
    code = main(["--rho", "2.0", "--n-steps", "2", "--no-core-math"])
    assert code == 2
