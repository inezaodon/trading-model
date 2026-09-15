"""JSON helpers — convert numpy arrays to nested Python lists."""

from __future__ import annotations

from typing import Any

import numpy as np


def to_jsonable(obj: Any) -> Any:
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, dict):
        return {k: to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    return obj


def downsample_paths(paths: np.ndarray, max_paths: int = 12, max_points: int = 400) -> np.ndarray:
    """Keep charts responsive for the browser."""
    arr = np.asarray(paths, dtype=float)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    n_paths, n_pts = arr.shape
    if n_paths > max_paths:
        idx = np.linspace(0, n_paths - 1, max_paths).astype(int)
        arr = arr[idx]
    if n_pts > max_points:
        jdx = np.linspace(0, n_pts - 1, max_points).astype(int)
        arr = arr[:, jdx]
    return arr


def downsample_times(times: np.ndarray, n_target: int) -> np.ndarray:
    times = np.asarray(times, dtype=float)
    if len(times) <= n_target:
        return times
    jdx = np.linspace(0, len(times) - 1, n_target).astype(int)
    return times[jdx]
