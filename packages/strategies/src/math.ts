/** Standard normal CDF via Abramowitz & Stegun approximation. */
export function normCdf(x: number): number {
  if (!Number.isFinite(x)) return x > 0 ? 1 : 0;
  const t = 1 / (1 + 0.2316419 * Math.abs(x));
  const d = 0.3989422804014327 * Math.exp((-x * x) / 2);
  const p =
    d *
    t *
    (0.319381530 +
      t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))));
  return x > 0 ? 1 - p : p;
}

/** Black–Scholes call delta. */
export function bsCallDelta(
  S: number,
  K: number,
  T: number,
  r: number,
  sigma: number,
): number {
  if (S <= 0 || K <= 0) return 0;
  if (T <= 1e-12 || sigma <= 1e-12) return S >= K ? 1 : 0;
  const volSqrtT = sigma * Math.sqrt(T);
  const d1 = (Math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / volSqrtT;
  return normCdf(d1);
}

/** Black–Scholes call price (for marking the option book). */
export function bsCallPrice(
  S: number,
  K: number,
  T: number,
  r: number,
  sigma: number,
): number {
  if (S <= 0 || K <= 0) return 0;
  if (T <= 1e-12 || sigma <= 1e-12) return Math.max(S - K, 0);
  const volSqrtT = sigma * Math.sqrt(T);
  const d1 = (Math.log(S / K) + (r + 0.5 * sigma * sigma) * T) / volSqrtT;
  const d2 = d1 - volSqrtT;
  return S * normCdf(d1) - K * Math.exp(-r * T) * normCdf(d2);
}

/** Mean of a numeric array. */
export function mean(xs: number[]): number {
  if (xs.length === 0) return 0;
  let s = 0;
  for (const x of xs) s += x;
  return s / xs.length;
}

/** Sample standard deviation (population-style with N, for sharpe on short series). */
export function stdev(xs: number[]): number {
  if (xs.length < 2) return 0;
  const m = mean(xs);
  let v = 0;
  for (const x of xs) {
    const d = x - m;
    v += d * d;
  }
  return Math.sqrt(v / (xs.length - 1));
}

/**
 * Max drawdown of an equity series.
 * Dollar peak-to-trough is normalized by `scale` (e.g. spot notional) so
 * PnL curves that start near zero remain well-behaved.
 */
export function maxDrawdown(equity: number[], scale = 1): number {
  if (equity.length === 0) return 0;
  const denom = Math.max(Math.abs(scale), 1e-12);
  let peak = equity[0]!;
  let mdd = 0;
  for (const e of equity) {
    if (e > peak) peak = e;
    const dd = (peak - e) / denom;
    if (dd > mdd) mdd = dd;
  }
  return mdd;
}

/**
 * Annualized Sharpe-ish ratio from period returns.
 * Assumes `dt` is the step in years; if omitted, uses 1/sqrt(N) scaling.
 */
export function sharpeRatio(returns: number[], dtYears?: number): number {
  if (returns.length < 2) return 0;
  const m = mean(returns);
  const s = stdev(returns);
  if (s < 1e-15) return 0;
  const scale =
    dtYears !== undefined && dtYears > 0
      ? Math.sqrt(1 / dtYears)
      : Math.sqrt(returns.length);
  return (m / s) * scale;
}
