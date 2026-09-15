"""CLI for Brownian motion & random walk visualization JSON.

Examples
--------
    python -m brownian_visualizer simulate-1d --seed 42 --n-paths 3
    python -m brownian_visualizer simulate-2d --seed 7 --out paths.json
    python -m brownian_visualizer random-walk-limit --n-steps 2000 --seed 1
    python -m brownian_visualizer simulate-scaled --mu 0.1 --sigma 0.5 --savefig demo.png
"""

from __future__ import annotations

import argparse
from typing import Any

from .brownian import simulate_brownian_1d, simulate_brownian_2d, simulate_scaled_brownian
from .export import write_chart_json
from .random_walk import (
    random_walk_to_bm_limit,
    simulate_random_walk_2d,
    simulate_simple_random_walk,
)


def _common_flags() -> argparse.ArgumentParser:
    """Shared --seed / --out / --savefig for every subcommand."""
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--seed", type=int, default=42, help="RNG seed (default 42)")
    common.add_argument("--out", default=None, help="Write JSON to path (default: stdout)")
    common.add_argument(
        "--savefig",
        default=None,
        help="Optional matplotlib PNG/PDF path (requires [plot] extra)",
    )
    return common


def build_parser() -> argparse.ArgumentParser:
    common = _common_flags()
    parser = argparse.ArgumentParser(
        prog="brownian-visualizer",
        description="Brownian motion & random walk visualizer (chart-ready JSON)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p1 = sub.add_parser("simulate-1d", help="Standard 1D Wiener process", parents=[common])
    p1.add_argument("--t", type=float, default=1.0)
    p1.add_argument("--n-steps", type=int, default=252)
    p1.add_argument("--n-paths", type=int, default=3)

    ps = sub.add_parser("simulate-scaled", help="Scaled BM: x0 + μt + σW", parents=[common])
    ps.add_argument("--x0", type=float, default=0.0)
    ps.add_argument("--mu", type=float, default=0.0)
    ps.add_argument("--sigma", type=float, default=1.0)
    ps.add_argument("--t", type=float, default=1.0)
    ps.add_argument("--n-steps", type=int, default=252)
    ps.add_argument("--n-paths", type=int, default=3)

    p2 = sub.add_parser("simulate-2d", help="2D Wiener process trajectories", parents=[common])
    p2.add_argument("--t", type=float, default=1.0)
    p2.add_argument("--n-steps", type=int, default=252)
    p2.add_argument("--n-paths", type=int, default=1)
    p2.add_argument("--sigma-x", type=float, default=1.0)
    p2.add_argument("--sigma-y", type=float, default=1.0)
    p2.add_argument("--rho", type=float, default=0.0)

    rw = sub.add_parser(
        "random-walk", help="Simple 1D random walk (integer steps)", parents=[common]
    )
    rw.add_argument("--n-steps", type=int, default=1000)
    rw.add_argument("--n-paths", type=int, default=3)
    rw.add_argument("--p", type=float, default=0.5)

    lim = sub.add_parser(
        "random-walk-limit",
        help="Donsker-scaled random walk → BM limit (1D series)",
        parents=[common],
    )
    lim.add_argument("--n-steps", type=int, default=2000)
    lim.add_argument("--n-paths", type=int, default=3)
    lim.add_argument("--t", type=float, default=1.0)
    lim.add_argument("--p", type=float, default=0.5)

    rw2 = sub.add_parser("random-walk-2d", help="2D lattice random walk", parents=[common])
    rw2.add_argument("--n-steps", type=int, default=1000)
    rw2.add_argument("--n-paths", type=int, default=1)

    return parser

def _run(args: argparse.Namespace) -> dict[str, Any]:
    seed = args.seed
    cmd = args.command
    if cmd == "simulate-1d":
        return simulate_brownian_1d(
            t=args.t, n_steps=args.n_steps, n_paths=args.n_paths, seed=seed
        )
    if cmd == "simulate-scaled":
        return simulate_scaled_brownian(
            x0=args.x0,
            mu=args.mu,
            sigma=args.sigma,
            t=args.t,
            n_steps=args.n_steps,
            n_paths=args.n_paths,
            seed=seed,
        )
    if cmd == "simulate-2d":
        return simulate_brownian_2d(
            t=args.t,
            n_steps=args.n_steps,
            n_paths=args.n_paths,
            seed=seed,
            sigma_x=args.sigma_x,
            sigma_y=args.sigma_y,
            rho=args.rho,
        )
    if cmd == "random-walk":
        return simulate_simple_random_walk(
            n_steps=args.n_steps, n_paths=args.n_paths, p=args.p, seed=seed
        )
    if cmd == "random-walk-limit":
        return random_walk_to_bm_limit(
            n_steps=args.n_steps,
            n_paths=args.n_paths,
            t=args.t,
            p=args.p,
            seed=seed,
        )
    if cmd == "random-walk-2d":
        return simulate_random_walk_2d(
            n_steps=args.n_steps, n_paths=args.n_paths, seed=seed
        )
    raise ValueError(f"unknown command: {cmd}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = _run(args)

    if args.savefig:
        from .plot import save_demo_figure

        save_demo_figure(result, args.savefig)

    write_chart_json(result, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
