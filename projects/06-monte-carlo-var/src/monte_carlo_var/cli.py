"""CLI: ``monte-carlo-var`` / ``python -m monte_carlo_var``.

Emits JSON for the umbrella API and local demos.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .api import run_var
from .data import write_sample_csv


def _parse_floats(text: str) -> list[float]:
    parts = [p.strip() for p in text.replace(";", ",").split(",") if p.strip()]
    return [float(p) for p in parts]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="monte-carlo-var",
        description=(
            "Monte Carlo portfolio VaR / Expected Shortfall "
            "(GBM or empirical bootstrap)."
        ),
    )
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Simulate scenarios and compute VaR/ES JSON")
    run.add_argument(
        "--method",
        choices=("gbm", "bootstrap"),
        default="gbm",
        help="Scenario engine",
    )
    run.add_argument("--horizon-days", type=int, default=10)
    run.add_argument("--n-scenarios", type=int, default=10_000)
    run.add_argument(
        "--confidence",
        default="0.95,0.99",
        help="Comma-separated confidence levels",
    )
    run.add_argument(
        "--weights",
        default=None,
        help="Comma-separated portfolio weights (default: equal)",
    )
    run.add_argument("--portfolio-value", type=float, default=1_000_000.0)
    run.add_argument("--seed", type=int, default=42)
    run.add_argument(
        "--returns-csv",
        default=None,
        help="Optional path to date,ticker,... daily log-return CSV",
    )
    run.add_argument(
        "--download",
        action="store_true",
        help="Try yfinance download before bundled/synthetic sample",
    )
    run.add_argument(
        "--pnl-sample",
        action="store_true",
        help="Include a random P&L sample in JSON",
    )
    run.add_argument("--out", default=None, help="Write JSON to path (default: stdout)")

    gen = sub.add_parser("gen-sample", help="Write bundled synthetic ETF returns CSV")
    gen.add_argument("--n-days", type=int, default=756)
    gen.add_argument("--seed", type=int, default=42)
    gen.add_argument("--out", default=None, help="CSV path (default: data/sample_returns.csv)")

    return p


def _write_json(payload: dict[str, Any], out: str | None) -> None:
    text = json.dumps(payload, indent=2)
    if out:
        Path(out).write_text(text + ("\n" if not text.endswith("\n") else ""), encoding="utf-8")
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "gen-sample":
        path = write_sample_csv(
            path=Path(args.out) if args.out else None,
            n_days=args.n_days,
            seed=args.seed,
        )
        _write_json({"wrote": str(path), "n_days": args.n_days, "seed": args.seed}, None)
        return 0

    if args.command == "run":
        weights = _parse_floats(args.weights) if args.weights else None
        conf = _parse_floats(args.confidence)
        payload = run_var(
            method=args.method,
            horizon_days=args.horizon_days,
            n_scenarios=args.n_scenarios,
            confidence_levels=conf,
            weights=weights,
            portfolio_value=args.portfolio_value,
            seed=args.seed,
            prefer_download=args.download,
            returns_csv=args.returns_csv,
            include_pnl_sample=args.pnl_sample,
        )
        _write_json(payload, args.out)
        return 0

    parser.error(f"unknown command {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
