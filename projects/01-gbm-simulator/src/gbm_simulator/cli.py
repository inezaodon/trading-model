"""CLI for the GBM stock price simulator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gbm_simulator.calibrate import estimate_mu_sigma, load_price_csv
from gbm_simulator.export import simulation_to_json, write_json, write_plotly_json
from gbm_simulator.plotting import save_plot
from gbm_simulator.simulate import simulate_gbm

# Bundled sample data (QQQ-like synthetic series)
_PACKAGE_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_SAMPLE = _PACKAGE_ROOT / "data" / "qqq_sample.csv"
# When installed as a package, data lives next to the project root relative to cwd
_FALLBACK_SAMPLE = Path(__file__).resolve().parents[3] / "data" / "qqq_sample.csv"


def _resolve_sample() -> Path:
    for candidate in (_DEFAULT_SAMPLE, _FALLBACK_SAMPLE, Path("data/qqq_sample.csv")):
        if candidate.is_file():
            return candidate
    # Also check relative to project when run from monorepo root
    mono = Path("projects/01-gbm-simulator/data/qqq_sample.csv")
    if mono.is_file():
        return mono
    raise FileNotFoundError(
        "bundled sample data not found; pass --csv PATH explicitly"
    )


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="gbm-sim",
        description=(
            "Geometric Brownian Motion stock price simulator "
            "(dS = μ S dt + σ S dW). Educational / research only."
        ),
    )
    sub = p.add_subparsers(dest="command", required=True)

    sim = sub.add_parser("simulate", help="Simulate GBM Monte Carlo paths")
    sim.add_argument("--s0", type=float, default=100.0, help="Initial spot")
    sim.add_argument("--mu", type=float, default=0.05, help="Annualized drift")
    sim.add_argument("--sigma", type=float, default=0.2, help="Annualized volatility")
    sim.add_argument("--t", type=float, default=1.0, help="Horizon in years")
    sim.add_argument("--n-steps", type=int, default=252, help="Time steps")
    sim.add_argument("--n-paths", type=int, default=100, help="Monte Carlo paths")
    sim.add_argument("--seed", type=int, default=42, help="RNG seed")
    sim.add_argument("--json-out", type=Path, help="Write umbrella API JSON")
    sim.add_argument("--plotly-out", type=Path, help="Write Plotly figure JSON")
    sim.add_argument("--plot-out", type=Path, help="Write Matplotlib PNG")
    sim.add_argument(
        "--max-plot-paths",
        type=int,
        default=50,
        help="Max paths drawn in charts",
    )
    sim.add_argument(
        "--stdout-json",
        action="store_true",
        help="Print umbrella JSON payload to stdout",
    )

    cal = sub.add_parser(
        "calibrate",
        help="Estimate μ and σ from CSV prices (or bundled QQQ-like sample)",
    )
    cal.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Price CSV path (default: bundled data/qqq_sample.csv)",
    )
    cal.add_argument(
        "--dt",
        type=float,
        default=1.0 / 252.0,
        help="Time step between observations in years (default: 1/252)",
    )
    cal.add_argument(
        "--price-col",
        type=str,
        default=None,
        help="Price column name if CSV has a header",
    )
    cal.add_argument(
        "--simulate",
        action="store_true",
        help="After calibration, run a simulation with estimated params",
    )
    cal.add_argument("--n-steps", type=int, default=252)
    cal.add_argument("--n-paths", type=int, default=100)
    cal.add_argument("--t", type=float, default=1.0)
    cal.add_argument("--seed", type=int, default=42)
    cal.add_argument("--json-out", type=Path, help="Write simulation JSON if --simulate")
    cal.add_argument("--plotly-out", type=Path)
    cal.add_argument("--plot-out", type=Path)

    return p


def cmd_simulate(args: argparse.Namespace) -> int:
    result = simulate_gbm(
        s0=args.s0,
        mu=args.mu,
        sigma=args.sigma,
        t=args.t,
        n_steps=args.n_steps,
        n_paths=args.n_paths,
        seed=args.seed,
    )
    _emit_outputs(args, result)
    if not args.stdout_json and args.json_out is None:
        print(
            f"simulated {args.n_paths} paths × {args.n_steps} steps | "
            f"mean_terminal={result.stats['mean_terminal']:.4f} "
            f"(theory={result.stats['theoretical_mean']:.4f}) | seed={args.seed}"
        )
    return 0


def cmd_calibrate(args: argparse.Namespace) -> int:
    csv_path = args.csv if args.csv is not None else _resolve_sample()
    prices = load_price_csv(csv_path, price_col=args.price_col)
    est = estimate_mu_sigma(prices, dt=args.dt)
    print(json.dumps({"csv": str(csv_path), **est}, indent=2))

    if args.simulate:
        result = simulate_gbm(
            s0=est["s0"],
            mu=est["mu"],
            sigma=est["sigma"],
            t=args.t,
            n_steps=args.n_steps,
            n_paths=args.n_paths,
            seed=args.seed,
        )
        result.params["calibrated_from"] = str(csv_path)
        _emit_outputs(args, result)
        print(
            f"simulated from calibrated params | "
            f"mean_terminal={result.stats['mean_terminal']:.4f}"
        )
    return 0


def _emit_outputs(args: argparse.Namespace, result) -> None:
    if getattr(args, "stdout_json", False):
        print(json.dumps(simulation_to_json(result)))
    if args.json_out is not None:
        write_json(result, args.json_out)
        print(f"wrote JSON → {args.json_out}", file=sys.stderr)
    if args.plotly_out is not None:
        write_plotly_json(
            result,
            args.plotly_out,
            max_paths=getattr(args, "max_plot_paths", 50),
        )
        print(f"wrote Plotly JSON → {args.plotly_out}", file=sys.stderr)
    if args.plot_out is not None:
        save_plot(
            result,
            args.plot_out,
            max_paths=getattr(args, "max_plot_paths", 50),
        )
        print(f"wrote plot → {args.plot_out}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "simulate":
        return cmd_simulate(args)
    if args.command == "calibrate":
        return cmd_calibrate(args)
    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
