"""CLI for the Rough Volatility / Rough Bergomi simulator.

Commands
--------
- ``simulate`` — hybrid fractional-kernel paths → JSON
- ``calibrate`` — NASDAQ-style IV30/60/90 + slope → rough Bergomi params JSON
- ``run`` — calibrate (optional) then simulate → combined JSON artifact
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

from .calibrate import DEFAULT_NASDAQ_MOCK, calibrate_from_nasdaq_iv
from .simulate import path_metrics, simulate_rough_bergomi


def _write_json(payload: dict[str, Any], out: str | None) -> None:
    text = json.dumps(payload, indent=2)
    if out:
        Path(out).write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
        if not text.endswith("\n"):
            sys.stdout.write("\n")


def _result_to_jsonable(
    result: dict[str, Any],
    *,
    symbol: str,
    include_metrics: bool = True,
) -> dict[str, Any]:
    times = np.asarray(result["times"], dtype=float)
    s = np.asarray(result["S"], dtype=float)
    v = np.asarray(result["v"], dtype=float)
    xi0 = np.asarray(result["xi0"], dtype=float)
    paths = [{"S": s[i].tolist(), "v": v[i].tolist()} for i in range(s.shape[0])]
    payload: dict[str, Any] = {
        "model": "rough_bergomi",
        "symbol": symbol,
        "params": result.get("params", {}),
        "times": times.tolist(),
        "forward_variance_curve": xi0.tolist(),
        "paths": paths,
    }
    if include_metrics:
        payload["metrics"] = path_metrics(result)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rough-vol",
        description=(
            "Rough Bergomi simulator (H≈0.1 fractional hybrid scheme) "
            "with NASDAQ-style forward variance input"
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sim = sub.add_parser("simulate", help="Simulate rough Bergomi spot/variance paths")
    sim.add_argument("--symbol", default="QQQ")
    sim.add_argument("--s0", type=float, default=100.0)
    sim.add_argument("--mu", type=float, default=0.0)
    sim.add_argument("--hurst", type=float, default=0.1, help="Hurst exponent H (default 0.1)")
    sim.add_argument("--eta", type=float, default=1.5, help="Roughness / vol-of-vol amplitude")
    sim.add_argument("--rho", type=float, default=-0.7, help="Spot–vol correlation (leverage)")
    sim.add_argument("--t", type=float, default=1.0)
    sim.add_argument("--n-steps", type=int, default=64)
    sim.add_argument("--n-paths", type=int, default=4)
    sim.add_argument("--xi0-flat", type=float, default=0.04)
    sim.add_argument(
        "--knots",
        default=None,
        help='JSON list of [t, variance] knots, e.g. \'[[0.082,0.05],[0.164,0.04]]\'',
    )
    sim.add_argument("--seed", type=int, default=42)
    sim.add_argument("--out", default=None)

    cal = sub.add_parser(
        "calibrate",
        help="Calibrate rough Bergomi params from NASDAQ-style IV30/60/90 + slope",
    )
    cal.add_argument("--symbol", default=DEFAULT_NASDAQ_MOCK["symbol"])
    cal.add_argument("--iv30", type=float, default=DEFAULT_NASDAQ_MOCK["iv30"])
    cal.add_argument("--iv60", type=float, default=DEFAULT_NASDAQ_MOCK["iv60"])
    cal.add_argument("--iv90", type=float, default=DEFAULT_NASDAQ_MOCK["iv90"])
    cal.add_argument("--slope", type=float, default=DEFAULT_NASDAQ_MOCK["slope"])
    cal.add_argument("--s0", type=float, default=DEFAULT_NASDAQ_MOCK["s0"])
    cal.add_argument("--hurst", type=float, default=0.1)
    cal.add_argument("--out", default=None)

    run = sub.add_parser(
        "run",
        help="Calibrate from IV surface (or use explicit params) then simulate → JSON",
    )
    run.add_argument("--symbol", default=DEFAULT_NASDAQ_MOCK["symbol"])
    run.add_argument("--from-iv", action="store_true", help="Calibrate η,ρ,ξ₀ from IV fields")
    run.add_argument("--iv30", type=float, default=DEFAULT_NASDAQ_MOCK["iv30"])
    run.add_argument("--iv60", type=float, default=DEFAULT_NASDAQ_MOCK["iv60"])
    run.add_argument("--iv90", type=float, default=DEFAULT_NASDAQ_MOCK["iv90"])
    run.add_argument("--slope", type=float, default=DEFAULT_NASDAQ_MOCK["slope"])
    run.add_argument("--s0", type=float, default=DEFAULT_NASDAQ_MOCK["s0"])
    run.add_argument("--mu", type=float, default=0.0)
    run.add_argument("--hurst", type=float, default=0.1)
    run.add_argument("--eta", type=float, default=1.5)
    run.add_argument("--rho", type=float, default=-0.7)
    run.add_argument("--xi0-flat", type=float, default=0.04)
    run.add_argument("--knots", default=None)
    run.add_argument("--t", type=float, default=90.0 / 365.0)
    run.add_argument("--n-steps", type=int, default=90)
    run.add_argument("--n-paths", type=int, default=8)
    run.add_argument("--seed", type=int, default=42)
    run.add_argument("--out", default=None)

    return parser


def cmd_simulate(args: argparse.Namespace) -> dict[str, Any]:
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
    return _result_to_jsonable(result, symbol=args.symbol)


def cmd_calibrate(args: argparse.Namespace) -> dict[str, Any]:
    return calibrate_from_nasdaq_iv(
        iv30=args.iv30,
        iv60=args.iv60,
        iv90=args.iv90,
        slope=args.slope,
        s0=args.s0,
        hurst=args.hurst,
        symbol=args.symbol,
    )


def cmd_run(args: argparse.Namespace) -> dict[str, Any]:
    calibration = None
    if args.from_iv:
        calibration = calibrate_from_nasdaq_iv(
            iv30=args.iv30,
            iv60=args.iv60,
            iv90=args.iv90,
            slope=args.slope,
            s0=args.s0,
            hurst=args.hurst,
            symbol=args.symbol,
        )
        p = calibration["params"]
        s0, mu, hurst = p["s0"], p["mu"], p["hurst"]
        eta, rho = p["eta"], p["rho"]
        xi0_flat = p["xi0_flat"]
        knots = [tuple(k) for k in p["forward_variance_knots"]]
    else:
        s0, mu, hurst = args.s0, args.mu, args.hurst
        eta, rho = args.eta, args.rho
        xi0_flat = args.xi0_flat
        knots = json.loads(args.knots) if args.knots else None
        if knots is not None:
            knots = [tuple(k) for k in knots]

    result = simulate_rough_bergomi(
        s0=s0,
        mu=mu,
        hurst=hurst,
        eta=eta,
        rho=rho,
        t=args.t,
        n_steps=args.n_steps,
        n_paths=args.n_paths,
        forward_variance_knots=knots,
        xi0_flat=xi0_flat,
        seed=args.seed,
    )
    payload = _result_to_jsonable(result, symbol=args.symbol)
    if calibration is not None:
        payload["calibration"] = calibration
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    dispatch = {
        "simulate": cmd_simulate,
        "calibrate": cmd_calibrate,
        "run": cmd_run,
    }
    payload = dispatch[args.command](args)
    _write_json(payload, getattr(args, "out", None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
