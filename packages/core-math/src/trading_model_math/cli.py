"""Argparse CLI for Node orchestrator: ``python -m trading_model_math …``.

Commands
--------
- ``simulate-heston`` — Heston Monte Carlo paths → JSON
- ``simulate-rbergomi`` — rough Bergomi hybrid paths → JSON
- ``calibrate`` — IV30/60/90 + slope → model params JSON
- ``signatures`` — truncated signature features from a path JSON
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from .calibrate import calibrate_from_iv_surface
from .heston import simulate_heston
from .rough_bergomi import simulate_rough_bergomi
from .signatures import signature_feature_dict, truncated_signature


def _paths_to_jsonable(
    model: str,
    symbol: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    """Pack simulator output into the artifact path schema."""
    times = np.asarray(result["times"], dtype=float)
    s = np.asarray(result["S"], dtype=float)
    v = np.asarray(result["v"], dtype=float)
    paths = [{"S": s[i].tolist(), "v": v[i].tolist()} for i in range(s.shape[0])]
    return {
        "model": model,
        "symbol": symbol,
        "params": result.get("params", {}),
        "times": times.tolist(),
        "paths": paths,
    }


def _write_json(payload: dict[str, Any], out: str | None) -> None:
    text = json.dumps(payload, indent=2)
    if out:
        Path(out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")


def _add_sim_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--symbol", default="QQQ")
    p.add_argument("--s0", type=float, default=100.0)
    p.add_argument("--mu", type=float, default=0.0)
    p.add_argument("--t", type=float, default=1.0)
    p.add_argument("--n-steps", type=int, default=64)
    p.add_argument("--n-paths", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--rho", type=float, default=-0.7)
    p.add_argument("--out", default=None, help="Write JSON to path instead of stdout")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_model_math",
        description="Stochastic calculus engines for trading-model",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- simulate-heston ---
    h = sub.add_parser("simulate-heston", help="Simulate Heston SV paths")
    _add_sim_common(h)
    h.add_argument("--v0", type=float, default=0.04)
    h.add_argument("--kappa", type=float, default=2.0)
    h.add_argument("--theta", type=float, default=0.04)
    h.add_argument("--xi", type=float, default=0.5)
    h.add_argument("--scheme", choices=("qe", "euler"), default="qe")

    # --- simulate-rbergomi ---
    r = sub.add_parser("simulate-rbergomi", help="Simulate rough Bergomi paths")
    _add_sim_common(r)
    r.add_argument("--hurst", type=float, default=0.1)
    r.add_argument("--eta", type=float, default=1.5)
    r.add_argument("--xi0-flat", type=float, default=0.04)
    r.add_argument(
        "--knots",
        default=None,
        help='JSON list of [t, variance] knots, e.g. \'[[0.08,0.05],[0.25,0.04]]\'',
    )

    # --- calibrate ---
    c = sub.add_parser("calibrate", help="Calibrate from IV30/60/90 + slope")
    c.add_argument("--iv30", type=float, required=True)
    c.add_argument("--iv60", type=float, required=True)
    c.add_argument("--iv90", type=float, required=True)
    c.add_argument("--slope", type=float, default=-1.5)
    c.add_argument("--s0", type=float, default=100.0)
    c.add_argument("--hurst", type=float, default=0.1)
    c.add_argument("--out", default=None)

    # --- signatures ---
    s = sub.add_parser("signatures", help="Truncated signature features")
    s.add_argument(
        "--path-json",
        default=None,
        help="Path to paths.json; if omitted, read JSON from stdin",
    )
    s.add_argument("--level", type=int, default=2)
    s.add_argument("--path-index", type=int, default=0, help="Which path in paths[]")
    s.add_argument("--out", default=None)

    return parser


def cmd_simulate_heston(args: argparse.Namespace) -> dict[str, Any]:
    result = simulate_heston(
        s0=args.s0,
        v0=args.v0,
        mu=args.mu,
        kappa=args.kappa,
        theta=args.theta,
        xi=args.xi,
        rho=args.rho,
        t=args.t,
        n_steps=args.n_steps,
        n_paths=args.n_paths,
        scheme=args.scheme,
        seed=args.seed,
    )
    return _paths_to_jsonable("heston", args.symbol, result)


def cmd_simulate_rbergomi(args: argparse.Namespace) -> dict[str, Any]:
    knots = json.loads(args.knots) if args.knots else None
    if knots is not None:
        knots = [tuple(k) for k in knots]
    result = simulate_rough_bergomi(
        s0=args.s0,
        mu=args.mu,
        hurst=args.hurst,
        eta=args.eta,
        rho=args.rho,
        t=args.t,
        n_steps=args.n_steps,
        n_paths=args.n_paths,
        forward_variance_knots=knots,
        xi0_flat=args.xi0_flat,
        seed=args.seed,
    )
    return _paths_to_jsonable("rough_bergomi", args.symbol, result)


def cmd_calibrate(args: argparse.Namespace) -> dict[str, Any]:
    return calibrate_from_iv_surface(
        iv30=args.iv30,
        iv60=args.iv60,
        iv90=args.iv90,
        slope=args.slope,
        s0=args.s0,
        hurst=args.hurst,
    )


def cmd_signatures(args: argparse.Namespace) -> dict[str, Any]:
    if args.path_json:
        raw = Path(args.path_json).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    payload = json.loads(raw)

    if "paths" in payload:
        entry = payload["paths"][args.path_index]
        s = np.asarray(entry["S"], dtype=float)
        v = np.asarray(entry["v"], dtype=float) if "v" in entry else None
        from .signatures import signature_features_from_sv_path

        feat = signature_features_from_sv_path(s, v, level=args.level)
        return {
            "model": payload.get("model", "unknown"),
            "symbol": payload.get("symbol"),
            "level": args.level,
            "path_index": args.path_index,
            "dim": int(feat.size),
            "features": feat.tolist(),
        }

    # Bare path array: {"path": [[x1,y1], ...]} or {"S": [...]}
    if "S" in payload:
        return signature_feature_dict(
            np.asarray(payload["S"], dtype=float),
            np.asarray(payload["v"], dtype=float) if "v" in payload else None,
            level=args.level,
        )
    if "path" in payload:
        feat = truncated_signature(np.asarray(payload["path"], dtype=float), level=args.level)
        return {"level": args.level, "dim": int(feat.size), "features": feat.tolist()}

    raise ValueError("JSON must contain 'paths', 'S', or 'path'")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    dispatch = {
        "simulate-heston": cmd_simulate_heston,
        "simulate-rbergomi": cmd_simulate_rbergomi,
        "calibrate": cmd_calibrate,
        "signatures": cmd_signatures,
    }
    payload = dispatch[args.command](args)
    _write_json(payload, getattr(args, "out", None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
