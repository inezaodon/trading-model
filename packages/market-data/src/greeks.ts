/**
 * Adapter for NASDAQ Greeks and Vols message schema.
 * Can emit synthetic streaming-like snapshots for offline demos.
 *
 * Spec: https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/GreeksandVols_Specification.pdf
 */

import { getMockSurface, reconstructStrikeIv } from "./mock.js";
import type { GreeksAndVolsMessage, OratsSurfaceRow } from "./types.js";

export interface SnapshotOptions {
  underlying: string;
  /** Unix ms; defaults to Date.now() */
  timestamp?: number;
  /** Strike grid relative to spot (default ATM ± a few %) */
  moneyness?: number[];
  /** Days to expiry for synthetic options (default 30) */
  daysToExpiry?: number;
  /** Call (C) or Put (P) */
  right?: "C" | "P";
  /** Optional surface override (else mock) */
  surface?: OratsSurfaceRow;
}

/** OCC-style option symbol: ROOT + YYMMDD + C/P + strike*1000 (8 digits). */
export function formatOptionSymbol(
  underlying: string,
  expiry: Date,
  right: "C" | "P",
  strike: number,
): string {
  const root = underlying.toUpperCase().padEnd(6, " ").slice(0, 6).replace(/ /g, "");
  const yy = String(expiry.getUTCFullYear()).slice(-2);
  const mm = String(expiry.getUTCMonth() + 1).padStart(2, "0");
  const dd = String(expiry.getUTCDate()).padStart(2, "0");
  const strikeInt = Math.round(strike * 1000);
  const strikePart = String(strikeInt).padStart(8, "0");
  return `${root}${yy}${mm}${dd}${right}${strikePart}`;
}

function approxDelta(moneyness: number, right: "C" | "P"): number {
  // Rough Black–Scholes-ish ATM delta mapping for synthetic snapshots
  const callDelta = Math.max(0.05, Math.min(0.95, 0.5 - (moneyness - 1) * 4));
  return right === "C" ? callDelta : callDelta - 1;
}

function approxGreeks(
  spot: number,
  iv: number,
  delta: number,
  dte: number,
): Pick<
  GreeksAndVolsMessage,
  "gamma" | "vega" | "theta" | "rho" | "theoreticalPrice"
> {
  const t = Math.max(dte, 1) / 365;
  const gamma = Math.exp(-0.5 * (((delta - 0.5) * 4) ** 2)) / (spot * iv * Math.sqrt(t) * 2.5);
  const vega = (spot * Math.sqrt(t) * 0.01) * Math.exp(-(((delta - 0.5) * 2) ** 2));
  const theta = -((spot * iv) / (2 * Math.sqrt(t))) * 0.01 - 0.01;
  const rho = delta * spot * t * 0.01 * 0.02;
  const theoreticalPrice = Math.max(
    0.01,
    spot * Math.abs(delta) * iv * Math.sqrt(t) * 0.8,
  );
  return {
    gamma: round(gamma, 6),
    vega: round(vega, 6),
    theta: round(theta, 6),
    rho: round(rho, 6),
    theoreticalPrice: round(theoreticalPrice, 4),
  };
}

function round(n: number, dp: number): number {
  const f = 10 ** dp;
  return Math.round(n * f) / f;
}

function expiryFromDte(fromMs: number, dte: number): Date {
  const d = new Date(fromMs);
  d.setUTCDate(d.getUTCDate() + dte);
  return d;
}

/**
 * Generate a synthetic Greeks & Vols snapshot batch for one underlying,
 * using mock (or provided) surface skew.
 */
export function generateGreeksSnapshot(
  options: SnapshotOptions,
): GreeksAndVolsMessage[] {
  const underlying = options.underlying.trim().toUpperCase();
  const surface = options.surface ?? getMockSurface(underlying);
  const ts = options.timestamp ?? Date.now();
  const dte = options.daysToExpiry ?? 30;
  const right = options.right ?? "C";
  const moneyness = options.moneyness ?? [0.95, 0.98, 1.0, 1.02, 1.05];
  const expiry = expiryFromDte(ts, dte);

  return moneyness.map((m) => {
    const strike = round(surface.stockpx * m, 2);
    const delta = approxDelta(m, right);
    const iv = reconstructStrikeIv(surface.iv30, surface.slope, surface.deriv, Math.abs(delta));
    const greeks = approxGreeks(surface.stockpx, iv, Math.abs(delta), dte);
    return {
      timestamp: ts,
      option: formatOptionSymbol(underlying, expiry, right, strike),
      underlying,
      delta: round(delta, 6),
      ...greeks,
      impliedVolatility: round(iv, 6),
    };
  });
}

/** Parse / validate a raw message into GreeksAndVolsMessage (passthrough with coercion). */
export function adaptGreeksMessage(
  raw: Record<string, unknown>,
): GreeksAndVolsMessage {
  const num = (k: string, fb = 0): number => {
    const v = raw[k];
    if (typeof v === "number" && Number.isFinite(v)) return v;
    if (typeof v === "string") {
      const n = Number(v);
      if (Number.isFinite(n)) return n;
    }
    return fb;
  };
  const str = (k: string, fb = ""): string =>
    typeof raw[k] === "string" ? (raw[k] as string) : fb;

  return {
    timestamp: num("timestamp", Date.now()),
    option: str("option"),
    underlying: str("underlying").toUpperCase(),
    delta: num("delta"),
    gamma: num("gamma"),
    vega: num("vega"),
    theta: num("theta"),
    rho: num("rho"),
    impliedVolatility: num("impliedVolatility", num("iv")),
    theoreticalPrice: num("theoreticalPrice", num("theo")),
  };
}
