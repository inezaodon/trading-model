import { simulateDeltaHedge } from "./deltaHedge.js";
import { maxDrawdown, mean, sharpeRatio } from "./math.js";
import type {
  BacktestResult,
  EquityPoint,
  HedgeSimOptions,
  PathBundle,
  SurfaceSummary,
} from "./types.js";
import { volatilitySignal } from "./volSignal.js";

export interface BacktestOptions extends HedgeSimOptions {
  /** Strategy label written to output. Default `delta-hedge`. */
  strategy?: string;
  /** Scale hedge PnL by vol-signal direction (−1 short, +1 long, 0 flat→neutral carry). Default true. */
  useVolSignal?: boolean;
  /** Vol-signal edge threshold. */
  signalThreshold?: number;
}

/**
 * Run delta-hedge backtest across all paths, optionally sized by the vol signal.
 * Produces average equity curve and aggregate metrics for `artifacts/backtest.json`.
 */
export function runBacktest(
  paths: PathBundle,
  surface: SurfaceSummary,
  options: BacktestOptions = {},
): BacktestResult {
  if (paths.paths.length === 0) {
    throw new Error("paths.paths must be non-empty");
  }

  const strategy = options.strategy ?? "delta-hedge";
  const useVolSignal = options.useVolSignal ?? true;
  const signal = volatilitySignal(paths, surface, {
    threshold: options.signalThreshold,
  });

  // Hedge as short-vol book; flip PnL if signal says long vol
  const sign = useVolSignal ? (signal.direction === 0 ? 1 : signal.direction === -1 ? 1 : -1) : 1;

  const hedgeOpts: HedgeSimOptions = {
    rate: options.rate,
    strike: options.strike ?? surface.spot,
    maturity: options.maturity,
    notional: options.notional,
    initialCash: options.initialCash,
    deltaMode: options.deltaMode ?? "heston",
    constantVol: options.constantVol ?? surface.iv30,
  };

  const pnls: number[] = [];
  const curves: EquityPoint[][] = [];

  for (const path of paths.paths) {
    const result = simulateDeltaHedge(paths.times, path, hedgeOpts);
    pnls.push(sign * result.pnl);
    curves.push(
      result.equityCurve.map((p) => ({
        t: p.t,
        equity: sign * p.equity,
      })),
    );
  }

  const avgPnl = mean(pnls);
  const equityCurve = averageEquityCurves(curves);
  const equities = equityCurve.map((p) => p.equity);

  // Period returns from average equity curve
  const returns: number[] = [];
  for (let i = 1; i < equities.length; i++) {
    const prev = equities[i - 1]!;
    const curr = equities[i]!;
    // Use absolute increment relative to |prev| or 1 to keep finite when equity ~ 0
    const base = Math.max(Math.abs(prev), 1);
    returns.push((curr - prev) / base);
  }

  const times = paths.times;
  const dt =
    times.length >= 2 ? (times[times.length - 1]! - times[0]!) / (times.length - 1) : undefined;

  const initial = equities[0] ?? 0;
  const final = equities[equities.length - 1] ?? avgPnl;
  // Reference capital: spot (one-share book) so returns are portfolio-scale
  const refCapital = Math.max(surface.spot ?? hedgeOpts.strike ?? 1, 1);
  const totalReturn = (final - initial) / refCapital;

  const metrics = {
    totalReturn,
    sharpe: sharpeRatio(returns, dt),
    maxDrawdown: maxDrawdown(equities, refCapital),
  };

  const symbol = surface.symbol || paths.symbol || "UNKNOWN";

  return {
    symbol,
    strategy,
    pnl: avgPnl,
    equityCurve,
    metrics,
    signal,
  };
}

function averageEquityCurves(curves: EquityPoint[][]): EquityPoint[] {
  if (curves.length === 0) return [];
  const len = curves[0]!.length;
  const out: EquityPoint[] = [];
  for (let i = 0; i < len; i++) {
    let sum = 0;
    const t = curves[0]![i]!.t;
    for (const c of curves) {
      sum += c[i]?.equity ?? 0;
    }
    out.push({ t, equity: sum / curves.length });
  }
  return out;
}
