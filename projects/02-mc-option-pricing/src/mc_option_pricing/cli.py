"""CLI for Monte Carlo European option pricing (JSON stdout for umbrella API)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .convergence import DEFAULT_PATH_GRID, convergence_study
from .monte_carlo import price_european_mc
from .samples import get_sample, list_samples


def _write_json(payload: dict[str, Any], out: str | None) -> None:
    text = json.dumps(payload, indent=2)
    if out:
        Path(out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")


def _price_params(args: argparse.Namespace) -> dict[str, Any]:
    """Resolve pricing kwargs, optionally starting from a named sample."""
    base: dict[str, Any] = {
        "spot": 480.0,
        "strike": 480.0,
        "rate": 0.045,
        "vol": 0.22,
        "maturity": 0.25,
        "option_type": "call",
    }
    if getattr(args, "sample", None):
        sample = get_sample(args.sample)
        for key in ("spot", "strike", "rate", "vol", "maturity", "option_type"):
            base[key] = sample[key]

    # Overlay CLI values. When --sample is used, only keep destinations the
    # user explicitly passed (tracked by _StoreExplicit).
    provided = getattr(args, "_explicit", set())
    mapping = {
        "spot": "spot",
        "strike": "strike",
        "rate": "rate",
        "vol": "vol",
        "maturity": "maturity",
        "option_type": "option_type",
    }
    for dest, key in mapping.items():
        if dest in provided or not getattr(args, "sample", None):
            base[key] = getattr(args, dest)
    return base


class _StoreExplicit(argparse.Action):
    """Record which option destinations were explicitly set on the CLI."""

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Any,
        option_string: str | None = None,
    ) -> None:
        setattr(namespace, self.dest, values)
        explicit = getattr(namespace, "_explicit", None)
        if explicit is None:
            explicit = set()
            setattr(namespace, "_explicit", explicit)
        explicit.add(self.dest)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mc-option-pricing",
        description=(
            "Risk-neutral Monte Carlo European call/put pricing under GBM, "
            "with Black–Scholes comparison (educational / research only)."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- price ---
    p = sub.add_parser("price", help="MC price + SE/CI + Black–Scholes reference")
    p.add_argument("--sample", default=None, help=f"Named sample: {', '.join(list_samples())}")
    p.add_argument("--spot", type=float, default=480.0, action=_StoreExplicit)
    p.add_argument("--strike", type=float, default=480.0, action=_StoreExplicit)
    p.add_argument("--rate", type=float, default=0.045, action=_StoreExplicit)
    p.add_argument("--vol", type=float, default=0.22, action=_StoreExplicit)
    p.add_argument("--maturity", type=float, default=0.25, action=_StoreExplicit)
    p.add_argument(
        "--option-type",
        dest="option_type",
        choices=("call", "put"),
        default="call",
        action=_StoreExplicit,
    )
    p.add_argument("--n-paths", type=int, default=50_000)
    p.add_argument("--n-steps", type=int, default=1)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--confidence", type=float, default=0.95)
    p.add_argument("--out", default=None, help="Write JSON to path instead of stdout")

    # --- converge ---
    c = sub.add_parser("converge", help="MC convergence grid vs Black–Scholes")
    c.add_argument("--sample", default=None, help=f"Named sample: {', '.join(list_samples())}")
    c.add_argument("--spot", type=float, default=480.0, action=_StoreExplicit)
    c.add_argument("--strike", type=float, default=480.0, action=_StoreExplicit)
    c.add_argument("--rate", type=float, default=0.045, action=_StoreExplicit)
    c.add_argument("--vol", type=float, default=0.22, action=_StoreExplicit)
    c.add_argument("--maturity", type=float, default=0.25, action=_StoreExplicit)
    c.add_argument(
        "--option-type",
        dest="option_type",
        choices=("call", "put"),
        default="call",
        action=_StoreExplicit,
    )
    c.add_argument(
        "--path-counts",
        default=None,
        help="Comma-separated path counts (default: built-in grid)",
    )
    c.add_argument("--n-steps", type=int, default=1)
    c.add_argument("--seed", type=int, default=42)
    c.add_argument("--confidence", type=float, default=0.95)
    c.add_argument("--out", default=None)

    # --- samples ---
    s = sub.add_parser("samples", help="List sample NASDAQ-style parameter sets")
    s.add_argument("--out", default=None)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "_explicit"):
        args._explicit = set()

    if args.command == "samples":
        catalog = {sym: get_sample(sym) for sym in list_samples()}
        _write_json({"samples": catalog}, args.out)
        return 0

    market = _price_params(args)

    if args.command == "price":
        result = price_european_mc(
            spot=market["spot"],
            strike=market["strike"],
            rate=market["rate"],
            vol=market["vol"],
            maturity=market["maturity"],
            option_type=market["option_type"],
            n_paths=args.n_paths,
            n_steps=args.n_steps,
            seed=args.seed,
            confidence=args.confidence,
        )
        if getattr(args, "sample", None):
            result["params"]["sample"] = args.sample.upper()
        _write_json(result, args.out)
        return 0

    if args.command == "converge":
        if args.path_counts:
            counts = [int(x.strip()) for x in args.path_counts.split(",") if x.strip()]
        else:
            counts = list(DEFAULT_PATH_GRID)
        result = convergence_study(
            spot=market["spot"],
            strike=market["strike"],
            rate=market["rate"],
            vol=market["vol"],
            maturity=market["maturity"],
            option_type=market["option_type"],
            path_counts=counts,
            n_steps=args.n_steps,
            seed=args.seed,
            confidence=args.confidence,
        )
        if getattr(args, "sample", None):
            result["params"]["sample"] = args.sample.upper()
        _write_json(result, args.out)
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
