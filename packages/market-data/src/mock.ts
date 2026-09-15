/**
 * Deterministic mock ORATS/OPT surfaces shaped like tech / Nasdaq-100 skew:
 * elevated short-dated IV and negative slope.
 *
 * Portal reference: https://data.nasdaq.com/databases/OPT
 */

import type { OratsSurfaceRow } from "./types.js";

const MOCK_DATE = "2024-09-13";

/** Seeded profiles for common symbols (decimal IVs). */
const PROFILES: Record<
  string,
  Omit<OratsSurfaceRow, "ticker" | "date">
> = {
  QQQ: {
    stockpx: 478.55,
    iv30: 0.195,
    iv60: 0.178,
    iv90: 0.168,
    slope: -3.85,
    deriv: 0.42,
    m1atmiv: 0.192,
    hv10: 0.142,
    hv20: 0.151,
    hv60: 0.163,
  },
  AAPL: {
    stockpx: 222.48,
    iv30: 0.228,
    iv60: 0.205,
    iv90: 0.192,
    slope: -4.2,
    deriv: 0.55,
    m1atmiv: 0.225,
    hv10: 0.168,
    hv20: 0.175,
    hv60: 0.188,
  },
  MSFT: {
    stockpx: 430.12,
    iv30: 0.188,
    iv60: 0.172,
    iv90: 0.164,
    slope: -3.45,
    deriv: 0.38,
    m1atmiv: 0.186,
    hv10: 0.135,
    hv20: 0.148,
    hv60: 0.159,
  },
  NDX: {
    stockpx: 19750.0,
    iv30: 0.182,
    iv60: 0.169,
    iv90: 0.161,
    slope: -3.7,
    deriv: 0.4,
    m1atmiv: 0.18,
    hv10: 0.138,
    hv20: 0.147,
    hv60: 0.158,
  },
};

/** Simple deterministic hash → [0, 1) for unknown tickers. */
function unitHash(symbol: string): number {
  let h = 2166136261;
  const s = symbol.toUpperCase();
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0) / 0xffffffff;
}

function genericTechSurface(symbol: string): OratsSurfaceRow {
  const u = unitHash(symbol);
  const stockpx = 80 + u * 420;
  // Elevated short IV relative to longer tenors; negative equity skew
  const iv30 = 0.17 + u * 0.08;
  const iv60 = iv30 * (0.9 - u * 0.03);
  const iv90 = iv60 * (0.94 - u * 0.02);
  return {
    ticker: symbol.toUpperCase(),
    date: MOCK_DATE,
    stockpx: Math.round(stockpx * 100) / 100,
    iv30: Math.round(iv30 * 10000) / 10000,
    iv60: Math.round(iv60 * 10000) / 10000,
    iv90: Math.round(iv90 * 10000) / 10000,
    slope: Math.round((-2.8 - u * 2.2) * 100) / 100,
    deriv: Math.round((0.3 + u * 0.35) * 100) / 100,
    m1atmiv: Math.round((iv30 - 0.003) * 10000) / 10000,
    hv10: Math.round((iv30 * 0.72) * 10000) / 10000,
    hv20: Math.round((iv30 * 0.78) * 10000) / 10000,
    hv60: Math.round((iv30 * 0.85) * 10000) / 10000,
  };
}

/**
 * Return a deterministic mock surface for `symbol`.
 * Known names (QQQ, AAPL, MSFT, NDX) use fixed tech/Nasdaq skew profiles.
 */
export function getMockSurface(symbol: string): OratsSurfaceRow {
  const key = symbol.trim().toUpperCase();
  const profile = PROFILES[key];
  if (profile) {
    return { ticker: key, date: MOCK_DATE, ...profile };
  }
  return genericTechSurface(key);
}

export function listMockSymbols(): string[] {
  return Object.keys(PROFILES);
}

/**
 * ORATS-style strike IV from ATM IV, slope, deriv, and delta.
 * IV(strike) ≈ ATMIV * (1 + (slope/1000 + (deriv/1000 * (delta*100-50)/2)) * (delta*100-50))
 */
export function reconstructStrikeIv(
  atmIv: number,
  slope: number,
  deriv: number,
  delta: number,
): number {
  const x = delta * 100 - 50;
  const skewTerm = slope / 1000 + (deriv / 1000) * (x / 2);
  return atmIv * (1 + skewTerm * x);
}
