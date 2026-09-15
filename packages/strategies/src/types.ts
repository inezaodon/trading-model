/** Simulated path bundle from core-math (`artifacts/paths.json`). */
export interface PathBundle {
  times: number[];
  paths: PathSample[];
  model?: string;
  symbol?: string;
  params?: Record<string, number>;
}

export interface PathSample {
  /** Spot levels S_t along the path (same length as times). */
  S: number[];
  /** Instantaneous variance v_t along the path (same length as times). */
  v: number[];
}

/** Market IV surface summary from market-data (`artifacts/surface.json`). */
export interface SurfaceSummary {
  symbol: string;
  asOf?: string;
  spot?: number;
  iv30: number;
  iv60?: number;
  iv90?: number;
  slope?: number;
  deriv?: number;
  histVol?: number;
  [key: string]: unknown;
}

export interface EquityPoint {
  t: number;
  equity: number;
}

export interface BacktestMetrics {
  totalReturn: number;
  sharpe: number;
  maxDrawdown: number;
}

export interface BacktestResult {
  symbol: string;
  strategy: string;
  pnl: number;
  equityCurve: EquityPoint[];
  metrics: BacktestMetrics;
  signal?: VolSignalResult;
}

export interface VolSignalResult {
  /** Market implied variance from iv30². */
  marketImpliedVariance: number;
  /** Average model variance along paths (mean of v_t). */
  modelVariance: number;
  /** Realized variance from log returns across paths. */
  realizedVariance: number;
  /** Positive → model/realized richer than market (favor short vol), negative → long vol. */
  edge: number;
  /** Discrete signal in {-1, 0, +1}. */
  direction: -1 | 0 | 1;
}

export interface HedgeSimOptions {
  /** Risk-free rate (annualized). Default 0. */
  rate?: number;
  /** Option strike; default = S0. */
  strike?: number;
  /** Time to maturity in years at t=0; default = last time. */
  maturity?: number;
  /** Option notional (shares of underlying exposure). Default 1. */
  notional?: number;
  /** Initial cash / book equity. Default 0. */
  initialCash?: number;
  /**
   * Delta model: `bs` uses constant vol = sqrt(mean v) or iv30;
   * `heston` uses local instantaneous sqrt(v_t) for BS-style delta.
   */
  deltaMode?: "bs" | "heston";
  /** Override constant vol for BS mode (annualized). */
  constantVol?: number;
}

export interface PathHedgeResult {
  pnl: number;
  equityCurve: EquityPoint[];
  deltas: number[];
}
