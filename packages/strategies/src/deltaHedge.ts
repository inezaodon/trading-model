import { bsCallDelta, bsCallPrice, mean } from "./math.js";
import type { EquityPoint, HedgeSimOptions, PathHedgeResult, PathSample } from "./types.js";

/**
 * Discrete-rebalancing delta hedge of a short European call on one simulated path.
 *
 * At each step we recompute delta (BS with constant vol, or Heston-local using √v_t),
 * trade the underlying to match −Δ (short option → short delta), and mark cash + option.
 */
export function simulateDeltaHedge(
  times: number[],
  path: PathSample,
  options: HedgeSimOptions = {},
): PathHedgeResult {
  const n = times.length;
  if (n < 2 || path.S.length !== n || path.v.length !== n) {
    throw new Error("times, S, and v must be non-empty and equal length (≥ 2)");
  }

  const S0 = path.S[0]!;
  const rate = options.rate ?? 0;
  const strike = options.strike ?? S0;
  const maturity = options.maturity ?? times[n - 1]!;
  const notional = options.notional ?? 1;
  const deltaMode = options.deltaMode ?? "heston";
  const meanVar = mean(path.v);
  const constantVol =
    options.constantVol ?? Math.sqrt(Math.max(meanVar, 1e-12));

  let cash = options.initialCash ?? 0;
  let shares = 0;
  const deltas: number[] = [];
  const equityCurve: EquityPoint[] = [];

  const volAt = (i: number): number => {
    if (deltaMode === "bs") return constantVol;
    return Math.sqrt(Math.max(path.v[i]!, 1e-12));
  };

  const tauAt = (t: number): number => Math.max(maturity - t, 0);

  // Open: sell one call, hedge with delta shares
  const sigma0 = volAt(0);
  const tau0 = tauAt(times[0]!);
  const opt0 = bsCallPrice(S0, strike, tau0, rate, sigma0);
  cash += notional * opt0;

  let delta = bsCallDelta(S0, strike, tau0, rate, sigma0);
  // Short call → hedge by holding −Δ shares of underlying (scaled by notional)
  const targetShares = -notional * delta;
  cash -= (targetShares - shares) * S0;
  shares = targetShares;
  deltas.push(delta);

  const markEquity = (i: number): number => {
    const S = path.S[i]!;
    const t = times[i]!;
    const sigma = volAt(i);
    const tau = tauAt(t);
    const opt = tau > 1e-12 ? bsCallPrice(S, strike, tau, rate, sigma) : Math.max(S - strike, 0);
    // Short option liability
    return cash + shares * S - notional * opt;
  };

  equityCurve.push({ t: times[0]!, equity: markEquity(0) });

  for (let i = 1; i < n; i++) {
    const t = times[i]!;
    const S = path.S[i]!;
    const dt = t - times[i - 1]!;
    // Financing on cash
    cash *= Math.exp(rate * dt);

    const sigma = volAt(i);
    const tau = tauAt(t);
    delta = bsCallDelta(S, strike, tau, rate, sigma);
    const newShares = -notional * delta;
    cash -= (newShares - shares) * S;
    shares = newShares;
    deltas.push(delta);
    equityCurve.push({ t, equity: markEquity(i) });
  }

  // Settle at maturity: buy back option at intrinsic (already marked), flatten shares
  const ST = path.S[n - 1]!;
  cash += shares * ST;
  shares = 0;
  const intrinsic = Math.max(ST - strike, 0);
  cash -= notional * intrinsic;

  const pnl = cash - (options.initialCash ?? 0);
  // Final equity point after settlement
  equityCurve[equityCurve.length - 1] = { t: times[n - 1]!, equity: cash };

  return { pnl, equityCurve, deltas };
}
