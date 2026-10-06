"""Engine loader: explicit adapter table mapping API params to project functions.

Each adapter is one function per slug. It translates the umbrella API parameter
names (see ``app/catalog.py``) to the real signature of the project package,
calls it, and reshapes the result into the payload the web pages expect:

    {"slug", "engine", "params", "series": {...}, "metrics": {...}, ...}

The raw project output is kept under extra keys (``project_result`` etc.) where
it does not collide with the UI contract.

Fallbacks (``engines/fallbacks``) are opt-in: set ``ALLOW_ENGINE_FALLBACK=1``.
By default a project failure propagates (HTTP 500 with the real error) and the
traceback is logged.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .fallbacks import brownian, gbm, heston, mc_options, ou, rough_vol, var
from .serialize import downsample_paths, downsample_times, to_jsonable

logger = logging.getLogger(__name__)

# Repo root: apps/api/app/engines -> trading/
REPO_ROOT = Path(__file__).resolve().parents[4]

PROJECT_DIRS: dict[str, Path] = {
    "gbm": REPO_ROOT / "projects" / "01-gbm-simulator",
    "mc-options": REPO_ROOT / "projects" / "02-mc-option-pricing",
    "brownian": REPO_ROOT / "projects" / "03-brownian-visualizer",
    "ou": REPO_ROOT / "projects" / "04-ornstein-uhlenbeck",
    "heston": REPO_ROOT / "projects" / "05-heston-simulator",
    "var": REPO_ROOT / "projects" / "06-monte-carlo-var",
    "rough-vol": REPO_ROOT / "projects" / "07-rough-volatility",
}

FALLBACKS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "gbm": gbm.run,
    "mc-options": mc_options.run,
    "brownian": brownian.run,
    "ou": ou.run,
    "heston": heston.run,
    "var": var.run,
    "rough-vol": rough_vol.run,
}


def _ensure_src_on_path(slug: str) -> None:
    """Make the project's ``src`` importable when it is not pip-installed."""
    project_dir = PROJECT_DIRS[slug]
    for candidate in (project_dir / "src", project_dir):
        if candidate.is_dir():
            path = str(candidate.resolve())
            if path not in sys.path:
                sys.path.insert(0, path)
    core = REPO_ROOT / "packages" / "core-math" / "src"
    if core.is_dir() and str(core) not in sys.path:
        sys.path.insert(0, str(core))


# --------------------------------------------------------------------------- helpers


def _get(params: dict[str, Any], key: str, default: Any) -> Any:
    v = params.get(key)
    return default if v is None else v


def _seed(params: dict[str, Any], default: int | None) -> int | None:
    v = params.get("seed", default)
    return int(v) if v is not None else None


def _chart_paths(times: Any, paths: Any) -> tuple[np.ndarray, np.ndarray]:
    p = downsample_paths(np.asarray(paths, dtype=float))
    t = downsample_times(np.asarray(times, dtype=float), p.shape[1])
    return t, p


# --------------------------------------------------------------------------- adapters


def _run_gbm(params: dict[str, Any]) -> dict[str, Any]:
    from gbm_simulator.simulate import simulate_gbm

    p = {
        "s0": float(_get(params, "s0", 100.0)),
        "mu": float(_get(params, "mu", 0.08)),
        "sigma": float(_get(params, "sigma", 0.25)),
        "t": float(_get(params, "t", 1.0)),
        "n_steps": int(_get(params, "n_steps", 252)),
        "n_paths": int(_get(params, "n_paths", 8)),
        "seed": _seed(params, 42),
    }
    res = simulate_gbm(**p)
    times, paths = _chart_paths(res.times, res.paths)
    terminal = np.asarray(res.paths, dtype=float)[:, -1]
    return {
        "params": p,
        "series": {"times": times, "paths": paths},
        "metrics": {
            "mean_terminal": float(terminal.mean()),
            "std_terminal": float(terminal.std()),
            "min_terminal": float(terminal.min()),
            "max_terminal": float(terminal.max()),
            **{f"theoretical_{k}": v for k, v in res.stats.items() if k.startswith("theoretical_")},
        },
        "stats": res.stats,
    }


def _run_mc_options(params: dict[str, Any]) -> dict[str, Any]:
    from mc_option_pricing.monte_carlo import _terminal_spots, price_european_mc

    option = str(_get(params, "option", "call")).lower()
    p = {
        "spot": float(_get(params, "s0", 100.0)),
        "strike": float(_get(params, "k", 100.0)),
        "rate": float(_get(params, "r", 0.03)),
        "vol": float(_get(params, "sigma", 0.2)),
        "maturity": float(_get(params, "t", 1.0)),
        "option_type": option,
        "n_paths": int(_get(params, "n_paths", 20000)),
        "n_steps": int(_get(params, "n_steps", 100)),
        "seed": _seed(params, 42),
    }
    res = price_european_mc(**p)

    # Terminal-price histogram for the chart. Same seed + same project sampler
    # as price_european_mc, so these are exactly the draws behind the price.
    rng = np.random.default_rng(p["seed"])
    st = _terminal_spots(p["spot"], p["rate"], p["vol"], p["maturity"], p["n_paths"], p["n_steps"], rng) \
        if p["maturity"] > 0 else np.full(2, p["spot"])
    counts, edges = np.histogram(st, bins=40)
    return {
        "params": {
            "s0": p["spot"], "k": p["strike"], "r": p["rate"], "sigma": p["vol"],
            "t": p["maturity"], "n_steps": p["n_steps"], "n_paths": p["n_paths"],
            "option": option, "seed": p["seed"],
        },
        "series": {"hist_edges": edges, "hist_counts": counts},
        "metrics": {
            "price": res["price"],
            "std_error": res["stderr"],
            "bs_reference": res["bs_price"],
            "abs_error_vs_bs": abs(res["price"] - res["bs_price"]),
            "ci_low": res["ci_low"],
            "ci_high": res["ci_high"],
            "mean_terminal": float(st.mean()),
        },
        # legacy flat keys that were exposed by the previous project wiring
        "price": res["price"],
        "stderr": res["stderr"],
        "bs_price": res["bs_price"],
        "ci_low": res["ci_low"],
        "ci_high": res["ci_high"],
        "paths_used": res["paths_used"],
    }


def _run_brownian(params: dict[str, Any]) -> dict[str, Any]:
    from brownian_visualizer.brownian import simulate_brownian_1d, simulate_scaled_brownian
    from brownian_visualizer.export import result_to_chart_json

    t = float(_get(params, "t", 1.0))
    n_steps = int(_get(params, "n_steps", 500))
    n_paths = int(_get(params, "n_paths", 6))
    drift = float(_get(params, "drift", 0.0))
    diffusion = float(_get(params, "diffusion", 1.0))
    seed = _seed(params, 7)

    if drift == 0.0 and diffusion == 1.0:
        sim = simulate_brownian_1d(t=t, n_steps=n_steps, n_paths=n_paths, seed=seed)
    else:
        sim = simulate_scaled_brownian(
            mu=drift, sigma=diffusion, t=t, n_steps=n_steps, n_paths=n_paths, seed=seed
        )
    chart = result_to_chart_json(sim)

    data = np.array([s["y"] for s in chart["series"]], dtype=float)
    times, paths = _chart_paths(chart["times"], data)
    qv = np.concatenate([[0.0], np.cumsum(np.diff(data[0]) ** 2)])
    qv_chart = downsample_times(qv, paths.shape[1])
    return {
        "params": {
            "t": t, "n_steps": n_steps, "n_paths": n_paths,
            "drift": drift, "diffusion": diffusion, "seed": seed,
        },
        "series": {"times": times, "paths": paths, "quadratic_variation": qv_chart},
        "metrics": {
            "terminal_mean": float(data[:, -1].mean()),
            "terminal_var": float(data[:, -1].var()),
            "theoretical_var": float(diffusion**2 * t),
            "qv_final": float(qv[-1]),
            "theoretical_qv": float(diffusion**2 * t),
        },
        "chart": chart,
    }


def _run_ou(params: dict[str, Any]) -> dict[str, Any]:
    from ornstein_uhlenbeck.api import run

    p = {
        "mode": "simulate",
        "x0": float(_get(params, "x0", 0.5)),
        "kappa": float(_get(params, "kappa", 3.0)),
        "theta": float(_get(params, "theta", 0.0)),
        "sigma": float(_get(params, "sigma", 0.4)),
        "t": float(_get(params, "t", 2.0)),
        "n_steps": int(_get(params, "n_steps", 500)),
        "n_paths": int(_get(params, "n_paths", 8)),
        "seed": _seed(params, 11),
    }
    if params.get("scheme") is not None:
        p["scheme"] = str(params["scheme"])
    res = run(p)
    raw = np.array([path["X"] for path in res["paths"]], dtype=float)
    times, paths = _chart_paths(res["times"], raw)
    mean = downsample_times(raw.mean(axis=0), paths.shape[1])
    kappa, sigma = p["kappa"], p["sigma"]
    metrics = dict(res["metrics"])
    metrics["half_life"] = float(np.log(2.0) / kappa) if kappa > 0 else None
    return {
        "params": res["params"],
        "series": {
            "times": times,
            "paths": paths,
            "mean": mean,
            "theta_line": [p["theta"]] * len(times),
        },
        "metrics": metrics,
        "mode": res["mode"],
        "project": res["project"],
        "disclaimer": res.get("disclaimer"),
    }


def _run_heston(params: dict[str, Any]) -> dict[str, Any]:
    from heston_simulator.api import run_heston

    kwargs: dict[str, Any] = {}
    for k in ("s0", "v0", "mu", "kappa", "theta", "xi", "rho", "t"):
        if params.get(k) is not None:
            kwargs[k] = float(params[k])
    for k in ("n_steps", "n_paths"):
        if params.get(k) is not None:
            kwargs[k] = int(params[k])
    if params.get("scheme") is not None:
        kwargs["scheme"] = str(params["scheme"])
    kwargs["seed"] = _seed(params, 42)

    res = run_heston(**kwargs)
    times, s = _chart_paths(res["times"], res["S"])
    _, v = _chart_paths(res["times"], res["v"])
    return {
        "params": res["params"],
        "series": {"times": times, "paths": s, "variance": v},
        "metrics": res["metrics"],
    }


def _run_var(params: dict[str, Any]) -> dict[str, Any]:
    from monte_carlo_var.api import run_var

    confidence = float(_get(params, "confidence", 0.95))
    levels = [confidence] + ([0.99] if abs(confidence - 0.99) > 1e-12 else [])
    n_sims = params.get("n_sims", params.get("n_scenarios"))
    notional = float(_get(params, "notional", 1_000_000.0))
    weights = params.get("weights")
    res = run_var(
        method=str(_get(params, "method", "gbm")),
        horizon_days=int(_get(params, "horizon_days", 10)),
        n_scenarios=int(n_sims if n_sims is not None else 10_000),
        confidence_levels=levels,
        weights=[float(w) for w in weights] if weights is not None else None,
        portfolio_value=notional,
        seed=_seed(params, 99),
    )
    hist = res["chart"]["pnl_histogram"]
    primary = res["metrics"]["by_confidence"][0]
    summary = res["metrics"]["pnl_summary"]
    metrics: dict[str, Any] = {
        "var": primary["var"],
        "cvar": primary["es"],
        "mean_pnl": summary["mean"],
        "std_pnl": summary["std"],
        "var_pct_notional": 100.0 * primary["var"] / notional,
        "cvar_pct_notional": 100.0 * primary["es"] / notional,
    }
    for m in res["metrics"]["by_confidence"][1:]:
        tag = f"{int(round(m['confidence'] * 100))}"
        metrics[f"var_{tag}"] = m["var"]
        metrics[f"cvar_{tag}"] = m["es"]
    out = dict(res)
    out["project_metrics"] = res["metrics"]
    out["metrics"] = metrics
    out["series"] = {
        "hist_edges": hist["bin_edges"],
        "hist_counts": hist["counts"],
        "pnl_sorted": res["chart"]["pnl_sorted"],
    }
    out["params"] = {
        **res["params"],
        "notional": notional,
        "n_sims": res["params"]["n_scenarios"],
        "confidence": confidence,
    }
    return out


def _run_rough_vol(params: dict[str, Any]) -> dict[str, Any]:
    from rough_volatility.simulate import simulate_rough_bergomi

    p = {
        "s0": float(_get(params, "s0", 100.0)),
        "mu": float(_get(params, "mu", 0.0)),
        "hurst": float(_get(params, "hurst", 0.1)),
        "eta": float(_get(params, "eta", 1.5)),
        "rho": float(_get(params, "rho", -0.7)),
        "t": float(_get(params, "t", 1.0)),
        "n_steps": int(_get(params, "n_steps", 126)),
        "n_paths": int(_get(params, "n_paths", 4)),
        "xi0_flat": float(_get(params, "xi0_flat", 0.04)),
        "seed": _seed(params, 42),
    }
    res = simulate_rough_bergomi(**p)
    times, s = _chart_paths(res["times"], res["S"])
    _, v = _chart_paths(res["times"], res["v"])
    s_raw = np.asarray(res["S"], dtype=float)
    v_raw = np.asarray(res["v"], dtype=float)
    return {
        "params": {k: val for k, val in res["params"].items() if k != "forward_variance_knots"},
        "series": {"times": times, "paths": s, "variance": v},
        "metrics": {
            "mean_terminal_s": float(s_raw[:, -1].mean()),
            "mean_terminal_v": float(v_raw[:, -1].mean()),
            "hurst": p["hurst"],
        },
        "xi0": res["xi0"],
    }


ADAPTERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "gbm": _run_gbm,
    "mc-options": _run_mc_options,
    "brownian": _run_brownian,
    "ou": _run_ou,
    "heston": _run_heston,
    "var": _run_var,
    "rough-vol": _run_rough_vol,
}


# --------------------------------------------------------------------------- dispatch


def fallback_allowed() -> bool:
    return os.environ.get("ALLOW_ENGINE_FALLBACK", "").strip().lower() in {"1", "true", "yes", "on"}


def run_engine(slug: str, params: dict[str, Any]) -> dict[str, Any]:
    if slug not in ADAPTERS:
        raise KeyError(f"Unknown project slug: {slug}")

    try:
        _ensure_src_on_path(slug)
        result = ADAPTERS[slug](params)
    except Exception as exc:
        logger.exception("Project engine %r failed (%s: %s)", slug, type(exc).__name__, exc)
        if not fallback_allowed():
            raise
        logger.warning("ALLOW_ENGINE_FALLBACK=1: serving inline fallback for %r", slug)
        fb = dict(FALLBACKS[slug](params))
        fb["engine"] = f"fallback-after-project-error:{type(exc).__name__}"
        return to_jsonable(fb)

    out = dict(result)
    out["slug"] = slug
    out["engine"] = "project"
    return to_jsonable(out)
