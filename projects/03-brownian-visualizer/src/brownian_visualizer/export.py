"""Export simulator results as chart-ready JSON for the umbrella web UI.

Schema (stable for ``POST /api/v1/brownian/run`` consumers):

```json
{
  "model": "brownian",
  "kind": "standard_bm_1d | scaled_bm_1d | standard_bm_2d | random_walk_bm_limit | ...",
  "params": { ... },
  "times": [0, ...],
  "series": [ {"label": "path_0", "y": [...]} ],          // 1D
  "trajectories": [ {"label": "path_0", "x": [...], "y": [...]} ]  // 2D
}
```
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


def _tolist(arr: np.ndarray | None) -> list[Any] | None:
    if arr is None:
        return None
    return np.asarray(arr, dtype=float).tolist()


def result_to_chart_json(result: dict[str, Any]) -> dict[str, Any]:
    """Convert a simulator result dict into chart-ready JSON payload."""
    kind = result.get("kind", "unknown")
    params = dict(result.get("params") or {})
    dim = int(result.get("dim", 1))

    payload: dict[str, Any] = {
        "model": "brownian",
        "kind": kind,
        "params": params,
        "dim": dim,
    }

    times = result.get("times")
    steps = result.get("steps")
    if times is not None:
        payload["times"] = _tolist(np.asarray(times))
    if steps is not None:
        payload["steps"] = _tolist(np.asarray(steps))

    # Prefer scaled / process level X over raw W when both exist
    if dim == 2 or ("X" in result and "Y" in result):
        x = np.asarray(result["X"], dtype=float)
        y = np.asarray(result["Y"], dtype=float)
        n_paths = x.shape[0]
        payload["trajectories"] = [
            {
                "label": f"path_{i}",
                "x": x[i].tolist(),
                "y": y[i].tolist(),
            }
            for i in range(n_paths)
        ]
        # Also expose series of each coordinate for multi-panel charts
        payload["series"] = [
            {"label": f"path_{i}_x", "y": x[i].tolist()} for i in range(n_paths)
        ] + [{"label": f"path_{i}_y", "y": y[i].tolist()} for i in range(n_paths)]
        return payload

    # 1D: X (scaled/RW) or W (standard BM) or S (raw walk)
    if "X" in result:
        data = np.asarray(result["X"], dtype=float)
        series_key = "X"
    elif "W" in result:
        data = np.asarray(result["W"], dtype=float)
        series_key = "W"
    elif "S" in result:
        data = np.asarray(result["S"], dtype=float)
        series_key = "S"
    else:
        raise ValueError("result must contain W, X, or S for 1D export")

    n_paths = data.shape[0]
    payload["series"] = [
        {"label": f"path_{i}", "y": data[i].tolist(), "field": series_key}
        for i in range(n_paths)
    ]
    # Include raw Wiener when scaled BM carried both
    if "W" in result and series_key != "W":
        w = np.asarray(result["W"], dtype=float)
        payload["wiener"] = [
            {"label": f"W_{i}", "y": w[i].tolist()} for i in range(w.shape[0])
        ]
    return payload


def write_chart_json(
    result: dict[str, Any],
    out: str | Path | None = None,
    *,
    indent: int = 2,
) -> str:
    """Serialize chart JSON to a file or return the string (and print if out is None)."""
    payload = result_to_chart_json(result)
    text = json.dumps(payload, indent=indent)
    if out:
        Path(out).write_text(text + ("\n" if not text.endswith("\n") else ""), encoding="utf-8")
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")
    return text
