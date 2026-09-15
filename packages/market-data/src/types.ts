/**
 * Types for NASDAQ Data Link Option Volatility Surfaces (ORATS / OPT)
 * and NASDAQ Greeks and Vols streaming schema.
 *
 * Refs:
 * - https://data.nasdaq.com/databases/OPT
 * - NASDAQ Greeks and Vols specification
 */

/** ORATS-style constant-maturity / skew summary row (Tables API shape). */
export interface OratsSurfaceRow {
  ticker: string;
  /** ISO date YYYY-MM-DD */
  date: string;
  /** Underlying spot */
  stockpx: number;
  /** 30-day constant-maturity IV (decimal, e.g. 0.22) */
  iv30: number;
  iv60: number;
  iv90: number;
  /** Skew slope (ORATS units; typically negative for equity/index) */
  slope: number;
  /** Skew curvature / derivative term */
  deriv: number;
  /** Optional month-1 ATM IV */
  m1atmiv?: number;
  /** Optional historical vol windows */
  hv10?: number;
  hv20?: number;
  hv60?: number;
}

/** Artifact contract written to artifacts/surface.json */
export interface SurfaceArtifact {
  source: "mock" | "nasdaq-data-link";
  fetchedAt: string;
  symbol: string;
  surface: OratsSurfaceRow;
  /** Strike IV reconstruction helper params echoed for downstream agents */
  reconstruction: {
    formula: string;
    note: string;
  };
}

/**
 * NASDAQ Greeks and Vols message schema.
 * Spec: GreeksandVols_Specification.pdf (nasdaqtrader.com)
 */
export interface GreeksAndVolsMessage {
  timestamp: number;
  option: string;
  underlying: string;
  delta: number;
  gamma: number;
  vega: number;
  theta: number;
  rho: number;
  impliedVolatility: number;
  theoreticalPrice: number;
}

export interface ClientOptions {
  /** Override process.env.NASDAQ_DATA_LINK_API_KEY */
  apiKey?: string | null;
  /** Force mock even if a key is present */
  forceMock?: boolean;
  /** Fetch implementation (tests / custom transport) */
  fetchImpl?: typeof fetch;
  /** Tables API base URL */
  baseUrl?: string;
  /** ORATS/OPT datatable code for Tables API */
  datatableCode?: string;
}

export type DataMode = "mock" | "live";
