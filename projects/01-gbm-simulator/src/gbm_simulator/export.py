"""JSON / Plotly export for umbrella API and web charts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from gbm_simulator.simulate import SimulationResult


def simulation_to_json(result: SimulationResult) -> dict[str, Any]:
    """Serialize a simulation to the umbrella API payload shape.

    Contract::

        {
          "times": [...],
          "paths": [[...], ...],
          "params": {...},
          "stats": {...}
        }
    """
    return {
        "times": _tolist(result.times),
        "paths": _tolist(result.paths),
        "params": dict(result.params),
        "stats": dict(result.stats),
    }


def write_json(result: SimulationResult, path: str | Path) -> Path:
    """Write umbrella JSON payload to disk."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = simulation_to_json(result)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def to_plotly_figure_dict(
    result: SimulationResult,
    max_paths: int = 50,
    title: str = "GBM Monte Carlo Paths",
) -> dict[str, Any]:
    """Build a Plotly figure dict (no plotly dependency required to serialize).

    Suitable for ``plotly.io.from_json`` / frontend Plotly.newPlot consumption.
    """
    n_show = min(max_paths, result.paths.shape[0])
    times = _tolist(result.times)
    traces: list[dict[str, Any]] = []
    for i in range(n_show):
        traces.append(
            {
                "type": "scatter",
                "mode": "lines",
                "x": times,
                "y": _tolist(result.paths[i]),
                "line": {"width": 1},
                "opacity": 0.45,
                "showlegend": False,
                "name": f"path_{i}",
            }
        )

    # Mean path overlay
    mean_path = np.mean(result.paths, axis=0)
    traces.append(
        {
            "type": "scatter",
            "mode": "lines",
            "x": times,
            "y": _tolist(mean_path),
            "line": {"width": 2.5, "color": "#1a1a1a"},
            "name": "mean",
            "opacity": 1.0,
        }
    )

    return {
        "data": traces,
        "layout": {
            "title": {"text": title},
            "xaxis": {"title": "Time (years)"},
            "yaxis": {"title": "Price"},
            "template": "plotly_white",
            "margin": {"l": 60, "r": 20, "t": 50, "b": 50},
        },
    }


def write_plotly_json(
    result: SimulationResult,
    path: str | Path,
    max_paths: int = 50,
) -> Path:
    """Write Plotly figure JSON for web embedding."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = to_plotly_figure_dict(result, max_paths=max_paths)
    path.write_text(json.dumps(fig, indent=2), encoding="utf-8")
    return path


def _tolist(arr: np.ndarray) -> list[Any]:
    return np.asarray(arr, dtype=float).tolist()
