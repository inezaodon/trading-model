"""Matplotlib plotting helpers for GBM paths."""

from __future__ import annotations

import os
from pathlib import Path

# Prefer a non-interactive backend in headless / CI environments.
if os.environ.get("MPLBACKEND") is None:
    os.environ.setdefault("MPLBACKEND", "Agg")

import matplotlib

matplotlib.use(os.environ.get("MPLBACKEND", "Agg"), force=False)
import matplotlib.pyplot as plt
import numpy as np

from gbm_simulator.simulate import SimulationResult


def plot_paths(
    result: SimulationResult,
    max_paths: int = 50,
    title: str = "GBM Monte Carlo Paths",
    ax: plt.Axes | None = None,
) -> plt.Axes:
    """Plot a subset of simulated paths plus the cross-sectional mean."""
    own_fig = ax is None
    if ax is None:
        _, ax = plt.subplots(figsize=(10, 5))

    n_show = min(max_paths, result.paths.shape[0])
    for i in range(n_show):
        ax.plot(result.times, result.paths[i], alpha=0.35, linewidth=0.9)

    mean_path = np.mean(result.paths, axis=0)
    ax.plot(result.times, mean_path, color="black", linewidth=2.0, label="mean")

    ax.set_xlabel("Time (years)")
    ax.set_ylabel("Price")
    ax.set_title(title)
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)

    if own_fig:
        plt.tight_layout()
    return ax


def save_plot(
    result: SimulationResult,
    path: str | Path,
    max_paths: int = 50,
    dpi: int = 120,
) -> Path:
    """Render and save a PNG of simulated paths."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    plot_paths(result, max_paths=max_paths, ax=ax)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path
