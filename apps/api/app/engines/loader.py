"""Engine loader — prefer project packages, else solid fallbacks."""

from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable

from .fallbacks import brownian, gbm, heston, mc_options, ou, rough_vol, var

# Repo root: apps/api/app/engines -> ../../../../
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

# Candidate module names that project agents may expose with a `run(params)` entrypoint
MODULE_CANDIDATES: dict[str, list[str]] = {
    "gbm": ["gbm_simulator", "gbm_simulator.engine", "gbm_simulator.api", "src.engine"],
    "mc-options": ["mc_option_pricing", "mc_options", "mc_option_pricing.engine", "src.engine"],
    "brownian": ["brownian_visualizer", "brownian", "brownian_visualizer.engine", "src.engine"],
    "ou": ["ornstein_uhlenbeck", "ou", "ornstein_uhlenbeck.engine", "src.engine"],
    "heston": ["heston_simulator", "heston", "heston_simulator.engine", "src.engine"],
    "var": ["monte_carlo_var", "mc_var", "monte_carlo_var.engine", "src.engine"],
    "rough-vol": ["rough_volatility", "rough_bergomi", "rough_volatility.engine", "src.engine"],
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


def _ensure_src_on_path(project_dir: Path) -> None:
    for candidate in (project_dir / "src", project_dir):
        if candidate.is_dir():
            path = str(candidate.resolve())
            if path not in sys.path:
                sys.path.insert(0, path)


def _try_project_run(slug: str) -> Callable[[dict[str, Any]], dict[str, Any]] | None:
    project_dir = PROJECT_DIRS.get(slug)
    if project_dir is None or not project_dir.exists():
        return None

    _ensure_src_on_path(project_dir)

    # Direct file hooks used by project agents
    for rel in ("api.py", "engine.py", "src/api.py", "src/engine.py", "src/run.py"):
        file_path = project_dir / rel
        if file_path.is_file():
            mod_name = f"_tm_project_{slug.replace('-', '_')}_{rel.replace('/', '_').replace('.', '_')}"
            spec = importlib.util.spec_from_file_location(mod_name, file_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(mod)
                    if hasattr(mod, "run") and callable(mod.run):
                        return mod.run
                except Exception:
                    continue

    for name in MODULE_CANDIDATES.get(slug, []):
        try:
            mod = importlib.import_module(name)
            if hasattr(mod, "run") and callable(mod.run):
                return mod.run
        except Exception:
            continue
    return None


def run_engine(slug: str, params: dict[str, Any]) -> dict[str, Any]:
    if slug not in FALLBACKS:
        raise KeyError(f"Unknown project slug: {slug}")

    project_run = _try_project_run(slug)
    if project_run is not None:
        try:
            result = project_run(params)
            if isinstance(result, dict):
                result = dict(result)
                result.setdefault("slug", slug)
                result["engine"] = result.get("engine", "project")
                return result
        except Exception as exc:
            # Fall through to fallback but annotate
            fallback = FALLBACKS[slug](params)
            fallback["engine"] = f"fallback-after-project-error:{type(exc).__name__}"
            return fallback

    return FALLBACKS[slug](params)
