"""CLI integration tests (offline)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "trading_model_math", *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_simulate_heston_stdout():
    proc = _run(
        "simulate-heston",
        "--symbol",
        "QQQ",
        "--seed",
        "42",
        "--n-paths",
        "2",
        "--n-steps",
        "8",
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["model"] == "heston"
    assert payload["symbol"] == "QQQ"
    assert "params" in payload
    assert len(payload["times"]) == 9
    assert len(payload["paths"]) == 2
    assert "S" in payload["paths"][0] and "v" in payload["paths"][0]


def test_cli_simulate_rbergomi_out_file(tmp_path: Path):
    out = tmp_path / "paths.json"
    proc = _run(
        "simulate-rbergomi",
        "--symbol",
        "NDX",
        "--seed",
        "7",
        "--n-paths",
        "1",
        "--n-steps",
        "10",
        "--out",
        str(out),
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(out.read_text())
    assert payload["model"] == "rough_bergomi"
    assert payload["symbol"] == "NDX"
    assert len(payload["paths"][0]["S"]) == 11


def test_cli_calibrate():
    proc = _run(
        "calibrate",
        "--iv30",
        "0.22",
        "--iv60",
        "0.21",
        "--iv90",
        "0.20",
        "--slope",
        "-1.5",
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert "heston" in payload and "rough_bergomi" in payload
    assert payload["heston"]["rho"] < 0


def test_cli_signatures_from_file(tmp_path: Path):
    paths = {
        "model": "heston",
        "symbol": "QQQ",
        "params": {},
        "times": [0.0, 0.5, 1.0],
        "paths": [{"S": [100.0, 101.0, 99.0], "v": [0.04, 0.05, 0.045]}],
    }
    path_file = tmp_path / "in.json"
    path_file.write_text(json.dumps(paths))
    proc = _run("signatures", "--path-json", str(path_file), "--level", "2")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["dim"] == len(payload["features"])
    assert payload["level"] == 2
