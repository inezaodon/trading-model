export { bsCallDelta, bsCallPrice, maxDrawdown, mean, normCdf, sharpeRatio, stdev } from "./math.js";
export { simulateDeltaHedge } from "./deltaHedge.js";
export { volatilitySignal } from "./volSignal.js";
export { runBacktest } from "./backtest.js";
export type {
  BacktestMetrics,
  BacktestResult,
  EquityPoint,
  HedgeSimOptions,
  PathBundle,
  PathHedgeResult,
  PathSample,
  SurfaceSummary,
  VolSignalResult,
} from "./types.js";
export type { BacktestOptions } from "./backtest.js";
export type { VolSignalOptions } from "./volSignal.js";
