"""Optional matplotlib static demos (savefig). Primary deliverable is JSON."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def save_demo_figure(result: dict[str, Any], out: str | Path) -> Path:
    """Save a simple static plot for a simulator result.

    Requires the optional ``plot`` extra (matplotlib).
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:  # pragma: no cover - exercised when matplotlib missing
        raise ImportError(
            "matplotlib is required for savefig demos; "
            "install with: pip install 'brownian-visualizer[plot]'"
        ) from exc

    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    kind = result.get("kind", "brownian")
    fig, ax = plt.subplots(figsize=(8, 5))

    if "Y" in result and "X" in result:
        x = result["X"]
        y = result["Y"]
        for i in range(x.shape[0]):
            ax.plot(x[i], y[i], lw=1.0, alpha=0.85, label=f"path_{i}")
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_aspect("equal", adjustable="datalim")
        ax.set_title(f"2D trajectory — {kind}")
    else:
        times = result.get("times")
        if times is None:
            times = result.get("steps")
        if "X" in result:
            data = result["X"]
        elif "W" in result:
            data = result["W"]
        else:
            data = result["S"]
        for i in range(data.shape[0]):
            ax.plot(times, data[i], lw=1.0, alpha=0.85, label=f"path_{i}")
        ax.set_xlabel("t" if "times" in result else "step")
        ax.set_ylabel("value")
        ax.set_title(f"1D path — {kind}")

    if result.get("params", {}).get("n_paths", 1) <= 8:
        ax.legend(loc="best", fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path
