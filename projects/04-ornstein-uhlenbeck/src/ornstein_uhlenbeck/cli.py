"""CLI entrypoint — see ``python -m ornstein_uhlenbeck --help``."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from ornstein_uhlenbeck.api import DEFAULT_SEED, run
from ornstein_uhlenbeck.sample_data import write_synthetic_csv


def _write_json(payload: dict[str, Any], out: str | None) -> None:
    text = json.dumps(payload, indent=2)
    if out:
        Path(out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ornstein-uhlenbeck",
        description=(
            "Ornstein–Uhlenbeck mean-reversion simulator, fitter, "
            "and z-score spread demo (research only)."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add_common(p: argparse.ArgumentParser) -> None:
        p.add_argument("--seed", type=int, default=DEFAULT_SEED)
        p.add_argument("--out", default=None, help="Write JSON to path")

    sim = sub.add_parser("simulate", help="Simulate OU paths → JSON")
    add_common(sim)
    sim.add_argument("--x0", type=float, default=0.0)
    sim.add_argument("--kappa", type=float, default=3.0)
    sim.add_argument("--theta", type=float, default=0.0)
    sim.add_argument("--sigma", type=float, default=0.5)
    sim.add_argument("--t", type=float, default=1.0)
    sim.add_argument("--n-steps", type=int, default=252)
    sim.add_argument("--n-paths", type=int, default=1)
    sim.add_argument("--scheme", choices=("exact", "euler"), default="exact")

    fit = sub.add_parser("fit", help="Fit OU to sample rates/spreads → JSON")
    add_common(fit)
    fit.add_argument(
        "--series",
        choices=("rate", "spread_2s10s"),
        default="rate",
        help="Which bundled synthetic column to fit",
    )
    fit.add_argument(
        "--observations-json",
        default=None,
        help="JSON file with {\"observations\": [...], \"dt\": 1/252}",
    )

    sig = sub.add_parser("signals", help="Z-score spread signals → JSON")
    add_common(sig)
    sig.add_argument("--series", choices=("rate", "spread_2s10s"), default="spread_2s10s")
    sig.add_argument("--entry", type=float, default=1.5)
    sig.add_argument("--exit", type=float, default=0.25)
    sig.add_argument("--rolling-window", type=int, default=None)
    sig.add_argument("--observations-json", default=None)

    demo = sub.add_parser("demo", help="Full simulate+fit+signals demo → JSON")
    add_common(demo)
    demo.add_argument("--series", choices=("rate", "spread_2s10s"), default="spread_2s10s")
    demo.add_argument("--entry", type=float, default=1.5)
    demo.add_argument("--exit", type=float, default=0.25)
    demo.add_argument("--n-paths", type=int, default=3)

    gen = sub.add_parser("write-sample-data", help="Regenerate data/synthetic_rates.csv")
    gen.add_argument("--seed", type=int, default=DEFAULT_SEED)
    gen.add_argument("--out", default=None, help="CSV path (default: data/synthetic_rates.csv)")

    return parser


def _load_obs(path: str) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if "observations" not in raw:
        raise ValueError("observations-json must contain 'observations'")
    return {
        "observations": raw["observations"],
        "dt": raw.get("dt", 1.0 / 252.0),
        "use_sample": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "write-sample-data":
        path = write_synthetic_csv(
            Path(args.out) if args.out else None,
            seed=args.seed,
        )
        _write_json({"wrote": str(path), "seed": args.seed}, None)
        return 0

    params: dict[str, Any] = {"mode": args.command, "seed": args.seed}

    if args.command == "simulate":
        params.update(
            {
                "x0": args.x0,
                "kappa": args.kappa,
                "theta": args.theta,
                "sigma": args.sigma,
                "t": args.t,
                "n_steps": args.n_steps,
                "n_paths": args.n_paths,
                "scheme": args.scheme,
            }
        )
    elif args.command == "fit":
        if args.observations_json:
            params.update(_load_obs(args.observations_json))
        else:
            params["series"] = args.series
            params["use_sample"] = True
    elif args.command == "signals":
        if args.observations_json:
            params.update(_load_obs(args.observations_json))
        else:
            params["series"] = args.series
            params["use_sample"] = True
        params["entry"] = args.entry
        params["exit"] = args.exit
        if args.rolling_window is not None:
            params["rolling_window"] = args.rolling_window
    elif args.command == "demo":
        params["series"] = args.series
        params["entry"] = args.entry
        params["exit"] = args.exit
        params["n_paths"] = args.n_paths

    payload = run(params)
    _write_json(payload, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
