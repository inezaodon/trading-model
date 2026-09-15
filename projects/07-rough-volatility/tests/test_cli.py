"""CLI smoke tests — JSON output and seed determinism."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from rough_volatility.cli import main


def test_cli_simulate_stdout_json(capsys: pytest.CaptureFixture[str]):
    rc = main(
        [
            "simulate",
            "--s0",
            "100",
            "--hurst",
            "0.1",
            "--n-steps",
            "8",
            "--n-paths",
            "2",
            "--seed",
            "42",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["model"] == "rough_bergomi"
    assert payload["params"]["seed"] == 42
    assert payload["params"]["hurst"] == 0.1
    assert len(payload["times"]) == 9
    assert len(payload["paths"]) == 2
    assert "metrics" in payload


def test_cli_calibrate_and_run_from_iv(capsys: pytest.CaptureFixture[str]):
    assert main(["calibrate", "--iv30", "0.22", "--iv60", "0.21", "--iv90", "0.20"]) == 0
    cal = json.loads(capsys.readouterr().out)
    assert cal["params"]["forward_variance_knots"]

    assert (
        main(
            [
                "run",
                "--from-iv",
                "--iv30",
                "0.22",
                "--iv60",
                "0.21",
                "--iv90",
                "0.20",
                "--n-steps",
                "10",
                "--n-paths",
                "2",
                "--seed",
                "99",
            ]
        )
        == 0
    )
    run = json.loads(capsys.readouterr().out)
    assert run["calibration"]["model"] == "rough_bergomi"
    assert run["params"]["seed"] == 99
    assert len(run["paths"]) == 2


def test_module_entrypoint_json(tmp_path: Path):
    out = tmp_path / "out.json"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "rough_volatility",
            "simulate",
            "--n-steps",
            "4",
            "--n-paths",
            "1",
            "--seed",
            "1",
            "--out",
            str(out),
        ],
        check=True,
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parents[1]),
        env={**dict(**__import__("os").environ), "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src")},
    )
    assert proc.returncode == 0
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["model"] == "rough_bergomi"
    assert data["params"]["seed"] == 1
