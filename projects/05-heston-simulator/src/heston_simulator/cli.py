"""CLI for the Heston stochastic volatility simulator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from heston_simulator.api import run_heston
from heston_simulator.simulate import NASDAQ_EQUITY_DEFAULTS


def build_parser() -> argparse.ArgumentParser:
    d = NASDAQ_EQUITY_DEFAULTS
    p = argparse.ArgumentParser(
        prog="heston-sim",
        description=(
            "Simulate Heston stochastic volatility paths "
            "(correlated Brownian + CIR variance; Euler or QE). "
            "Default rho < 0 (Nasdaq-style equity leverage)."
        ),
    )
    p.add_argument("--s0", type=float, default=d["s0"], help="Initial spot")
    p.add_argument("--v0", type=float, default=d["v0"], help="Initial variance")
    p.add_argument("--mu", type=float, default=d["mu"], help="Drift")
    p.add_argument("--kappa", type=float, default=d["kappa"], help="Mean-reversion speed")
    p.add_argument("--theta", type=float, default=d["theta"], help="Long-run variance")
    p.add_argument("--xi", type=float, default=d["xi"], help="Vol-of-vol")
    p.add_argument(
        "--rho",
        type=float,
        default=d["rho"],
        help="Spot–variance correlation (equity default < 0)",
    )
    p.add_argument("--t", type=float, default=d["t"], help="Horizon in years")
    p.add_argument("--n-steps", type=int, default=d["n_steps"], dest="n_steps")
    p.add_argument("--n-paths", type=int, default=d["n_paths"], dest="n_paths")
    p.add_argument(
        "--scheme",
        choices=("qe", "euler"),
        default=d["scheme"],
        help="Variance discretization: Andersen QE or full-truncation Euler",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=42,
        help="RNG seed for reproducible paths (default: 42)",
    )
    p.add_argument(
        "--no-core-math",
        action="store_true",
        help="Force local engine even if trading_model_math is installed",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write JSON to this path (default: stdout)",
    )
    p.add_argument(
        "--compact",
        action="store_true",
        help="Compact JSON (no indentation)",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result: dict[str, Any] = run_heston(
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
            prefer_core_math=not args.no_core_math,
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(result, indent=None if args.compact else 2)
    if args.output is not None:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
