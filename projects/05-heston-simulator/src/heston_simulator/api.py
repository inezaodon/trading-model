"""JSON-ready API for the umbrella backend (``POST /api/v1/heston/run``)."""

from __future__ import annotations

from typing import Any

import numpy as np

from heston_simulator.simulate import NASDAQ_EQUITY_DEFAULTS, Scheme, simulate_heston


def to_jsonable(obj: Any) -> Any:
    """Convert NumPy arrays / scalars to plain JSON-serializable Python types."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    return obj


def run_heston(
    *,
    s0: float | None = None,
    v0: float | None = None,
    mu: float | None = None,
    kappa: float | None = None,
    theta: float | None = None,
    xi: float | None = None,
    rho: float | None = None,
    t: float | None = None,
    n_steps: int | None = None,
    n_paths: int | None = None,
    scheme: Scheme | None = None,
    seed: int | None = 42,
    prefer_core_math: bool = True,
) -> dict[str, Any]:
    """Run a Heston simulation and return a JSON-friendly payload.

    Paths are keyed ``S`` (spot) and ``v`` (variance). Default ``rho`` is negative
    (Nasdaq-style equity leverage). ``seed`` defaults to 42 for determinism.
    """
    defaults = NASDAQ_EQUITY_DEFAULTS
    params = {
        "s0": defaults["s0"] if s0 is None else s0,
        "v0": defaults["v0"] if v0 is None else v0,
        "mu": defaults["mu"] if mu is None else mu,
        "kappa": defaults["kappa"] if kappa is None else kappa,
        "theta": defaults["theta"] if theta is None else theta,
        "xi": defaults["xi"] if xi is None else xi,
        "rho": defaults["rho"] if rho is None else rho,
        "t": defaults["t"] if t is None else t,
        "n_steps": defaults["n_steps"] if n_steps is None else n_steps,
        "n_paths": defaults["n_paths"] if n_paths is None else n_paths,
        "scheme": defaults["scheme"] if scheme is None else scheme,
        "seed": seed,
    }

    raw = simulate_heston(**params, prefer_core_math=prefer_core_math)
    s = np.asarray(raw["S"], dtype=float)
    v = np.asarray(raw["v"], dtype=float)
    times = np.asarray(raw["times"], dtype=float)

    metrics = {
        "mean_terminal_S": float(np.mean(s[:, -1])),
        "std_terminal_S": float(np.std(s[:, -1], ddof=0)),
        "mean_terminal_v": float(np.mean(v[:, -1])),
        "mean_path_v": float(np.mean(v)),
        "min_S": float(np.min(s)),
        "max_S": float(np.max(s)),
    }

    # Empirical leverage check on first path increments when enough steps.
    if s.shape[1] >= 3 and s.shape[0] >= 1:
        dlog = np.diff(np.log(np.maximum(s, 1e-300)), axis=1).ravel()
        dv = np.diff(v, axis=1).ravel()
        if dlog.size > 1 and np.std(dlog) > 0 and np.std(dv) > 0:
            metrics["corr_dlogS_dv"] = float(np.corrcoef(dlog, dv)[0, 1])

    payload = {
        "slug": "heston",
        "times": times,
        "S": s,
        "v": v,
        "params": raw["params"],
        "metrics": metrics,
    }
    return to_jsonable(payload)
