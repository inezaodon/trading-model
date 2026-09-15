"""JSON-friendly ``run()`` entrypoint for the umbrella API.

Contract (aligned with ``POST /api/v1/ou/run``):

Request body fields (all optional with defaults)::

    {
      "mode": "simulate" | "fit" | "signals" | "demo",
      "seed": 42,
      ... mode-specific params ...
    }

Always returns a JSON-serializable dict with ``project``, ``mode``,
``seed``, and result payload.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from ornstein_uhlenbeck.fit import fit_ou
from ornstein_uhlenbeck.sample_data import generate_synthetic_rates, load_sample_rates
from ornstein_uhlenbeck.signals import zscore_signals
from ornstein_uhlenbeck.simulate import simulate_ou, stationary_std

DEFAULT_SEED = 42


def _tolist(x: Any) -> Any:
    if isinstance(x, np.ndarray):
        if np.issubdtype(x.dtype, np.floating):
            return [None if not np.isfinite(v) else float(v) for v in x.tolist()]
        return x.tolist()
    if isinstance(x, (np.floating, float)):
        v = float(x)
        return None if not np.isfinite(v) else v
    if isinstance(x, (np.integer, int)):
        return int(x)
    if isinstance(x, dict):
        return {str(k): _tolist(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_tolist(v) for v in x]
    return x


def run(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Dispatch OU workflows and return chart-ready JSON."""
    p = dict(params or {})
    mode = str(p.get("mode", "demo")).lower()
    seed = int(p.get("seed", DEFAULT_SEED))

    if mode == "simulate":
        payload = _run_simulate(p, seed)
    elif mode == "fit":
        payload = _run_fit(p, seed)
    elif mode == "signals":
        payload = _run_signals(p, seed)
    elif mode == "demo":
        payload = _run_demo(p, seed)
    else:
        raise ValueError(
            f"unknown mode {mode!r}; expected simulate|fit|signals|demo"
        )

    return {
        "project": "ou",
        "slug": "ou",
        "title": "Ornstein–Uhlenbeck Mean Reversion",
        "mode": mode,
        "seed": seed,
        "disclaimer": (
            "Educational / research only — not investment advice; "
            "no live order routing."
        ),
        **payload,
    }


def _run_simulate(p: dict[str, Any], seed: int) -> dict[str, Any]:
    result = simulate_ou(
        x0=float(p.get("x0", 0.0)),
        kappa=float(p.get("kappa", 3.0)),
        theta=float(p.get("theta", 0.0)),
        sigma=float(p.get("sigma", 0.5)),
        t=float(p.get("t", 1.0)),
        n_steps=int(p.get("n_steps", 252)),
        n_paths=int(p.get("n_paths", 1)),
        scheme=str(p.get("scheme", "exact")),  # type: ignore[arg-type]
        seed=seed,
    )
    kappa = result["params"]["kappa"]
    sigma = result["params"]["sigma"]
    ss = stationary_std(kappa, sigma) if kappa > 0 else None
    return {
        "times": _tolist(result["times"]),
        "paths": [{"X": _tolist(result["X"][i])} for i in range(result["X"].shape[0])],
        "params": result["params"],
        "metrics": {
            "terminal_mean": float(np.mean(result["X"][:, -1])),
            "terminal_std": float(np.std(result["X"][:, -1], ddof=0)),
            "stationary_std": ss,
        },
    }


def _series_from_params(p: dict[str, Any], seed: int) -> tuple[np.ndarray, float, dict[str, Any]]:
    """Resolve an observation series for fit / signals."""
    series_key = str(p.get("series", "rate"))
    if "observations" in p:
        x = np.asarray(p["observations"], dtype=float).ravel()
        dt = float(p.get("dt", 1.0 / 252.0))
        meta = {"source": "request.observations"}
        return x, dt, meta

    if p.get("use_sample", True):
        data = load_sample_rates()
        if series_key not in ("rate", "spread_2s10s"):
            raise ValueError("series must be 'rate' or 'spread_2s10s'")
        return data[series_key], float(data["dt"]), {
            "source": data["source"],
            "path": data.get("path"),
            "fred_series": data["fred_series"],
            "notes": data["notes"],
            "series": series_key,
        }

    synth = generate_synthetic_rates(seed=seed)
    key = "rate" if series_key == "rate" else "spread_2s10s"
    return synth[key], float(synth["dt"]), {
        "source": synth["source"],
        "fred_series": synth["fred_series"],
        "notes": synth["notes"],
        "series": series_key,
        "true_params": synth.get("true_params_rate") if key == "rate" else None,
    }


def _run_fit(p: dict[str, Any], seed: int) -> dict[str, Any]:
    x, dt, meta = _series_from_params(p, seed)
    fitted = fit_ou(x, dt=dt)
    return {
        "series_meta": meta,
        "n_obs": int(x.size),
        "series_preview": {
            "head": _tolist(x[:10]),
            "tail": _tolist(x[-10:]),
            "mean": float(np.mean(x)),
            "std": float(np.std(x, ddof=1)),
        },
        "fit": _tolist(fitted),
        "treasury_fred_note": (
            "Sample path is synthetic. For Treasury/FRED: download "
            "DGS2, DGS10, T10Y2Y, or SOFR, pass the column as "
            "`observations`, set `dt=1/252`, and call mode=fit."
        ),
    }


def _run_signals(p: dict[str, Any], seed: int) -> dict[str, Any]:
    x, dt, meta = _series_from_params(p, seed)
    fitted = fit_ou(x, dt=dt)
    entry = float(p.get("entry", 1.5))
    exit_ = float(p.get("exit", 0.25))
    rolling = p.get("rolling_window")
    if rolling is not None:
        sig = zscore_signals(
            x,
            entry=entry,
            exit=exit_,
            rolling_window=int(rolling),
        )
    else:
        sig = zscore_signals(
            x,
            theta=fitted["theta"],
            kappa=fitted["kappa"],
            sigma=fitted["sigma"],
            entry=entry,
            exit=exit_,
        )
    return {
        "series_meta": meta,
        "fit": _tolist(fitted),
        "times": list(range(x.size)),
        "series": _tolist(x),
        "zscore": _tolist(sig["zscore"]),
        "positions": _tolist(sig["positions"]),
        "equity": _tolist(sig["equity"]),
        "metrics": sig["metrics"],
        "signal_params": {
            "mode": sig["mode"],
            "entry": sig["entry"],
            "exit": sig["exit"],
            "model": _tolist(sig["model"]),
        },
    }


def _run_demo(p: dict[str, Any], seed: int) -> dict[str, Any]:
    """End-to-end: simulate → fit synthetic rates → z-score signals."""
    sim = _run_simulate(
        {
            "x0": float(p.get("x0", 3.5)),
            "kappa": float(p.get("kappa", 2.5)),
            "theta": float(p.get("theta", 4.0)),
            "sigma": float(p.get("sigma", 0.8)),
            "t": float(p.get("t", 2.0)),
            "n_steps": int(p.get("n_steps", 504)),
            "n_paths": int(p.get("n_paths", 3)),
            "scheme": p.get("scheme", "exact"),
        },
        seed,
    )
    fit_payload = _run_fit({"use_sample": True, "series": p.get("series", "rate")}, seed)
    sig_payload = _run_signals(
        {
            "use_sample": True,
            "series": p.get("series", "spread_2s10s"),
            "entry": p.get("entry", 1.5),
            "exit": p.get("exit", 0.25),
        },
        seed,
    )
    return {
        "simulate": sim,
        "fit": fit_payload,
        "signals": sig_payload,
        "math": {
            "sde": "dX = kappa (theta - X) dt + sigma dW",
            "half_life": "ln(2) / kappa",
            "stationary_std": "sigma / sqrt(2 kappa)",
        },
    }
