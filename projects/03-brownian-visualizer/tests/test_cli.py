"""CLI integration tests."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    import os

    env = os.environ.copy()
    root = Path(__file__).resolve().parents[1]
    env["PYTHONPATH"] = str(root / "src") + (
        os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else ""
    )
    return subprocess.run(
        [sys.executable, "-m", "brownian_visualizer", *args],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(root),
        env=env,
    )


def test_cli_simulate_1d_stdout():
    proc = _run("simulate-1d", "--seed", "42", "--n-paths", "2", "--n-steps", "8")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["model"] == "brownian"
    assert payload["kind"] == "standard_bm_1d"
    assert len(payload["times"]) == 9
    assert len(payload["series"]) == 2


def test_cli_simulate_2d_out_file(tmp_path: Path):
    out = tmp_path / "traj.json"
    proc = _run(
        "simulate-2d",
        "--seed",
        "7",
        "--out",
        str(out),
        "--n-paths",
        "1",
        "--n-steps",
        "10",
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(out.read_text())
    assert payload["kind"] == "standard_bm_2d"
    assert len(payload["trajectories"]) == 1


def test_cli_random_walk_limit():
    proc = _run(
        "random-walk-limit",
        "--seed",
        "1",
        "--n-steps",
        "100",
        "--n-paths",
        "2",
    )
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["kind"] == "random_walk_bm_limit"
    assert payload["params"]["seed"] == 1


def test_cli_scaled_and_savefig(tmp_path: Path):
    pytest.importorskip("matplotlib")
    png = tmp_path / "demo.png"
    out = tmp_path / "scaled.json"
    proc = _run(
        "simulate-scaled",
        "--seed",
        "5",
        "--out",
        str(out),
        "--savefig",
        str(png),
        "--mu",
        "0.1",
        "--sigma",
        "0.5",
        "--n-steps",
        "20",
        "--n-paths",
        "1",
    )
    assert proc.returncode == 0, proc.stderr
    assert png.is_file() and png.stat().st_size > 0
    payload = json.loads(out.read_text())
    assert payload["kind"] == "scaled_bm_1d"


def test_cli_default_seed_in_params():
    proc = _run("random-walk", "--n-steps", "20", "--n-paths", "1")
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["params"]["seed"] == 42
