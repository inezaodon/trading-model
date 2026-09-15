/**
 * NASDAQ Data Link Tables API client for ORATS / OPT volatility surfaces.
 *
 * Live: GET https://data.nasdaq.com/api/v3/datatables/{code}.json
 * Demo: deterministic mock when no API key (or on fetch failure).
 *
 * Refs: https://data.nasdaq.com/databases/OPT
 */

import { getMockSurface } from "./mock.js";
import type {
  ClientOptions,
  DataMode,
  OratsSurfaceRow,
  SurfaceArtifact,
} from "./types.js";

const DEFAULT_BASE = "https://data.nasdaq.com/api/v3/datatables";
/** ORATS option volatility surface table (OPT database family). */
const DEFAULT_TABLE = "ORATS/VOLSURF";

const RECONSTRUCTION = {
  formula:
    "IV(strike) ≈ ATMIV * (1 + (slope/1000 + (deriv/1000 * (delta*100-50)/2)) * (delta*100-50))",
  note: "ORATS-style summary; feeds forward variance ξ0(t) and Heston θ / v0",
} as const;

function resolveApiKey(options: ClientOptions): string | undefined {
  if (options.forceMock) return undefined;
  if (options.apiKey === null) return undefined;
  if (typeof options.apiKey === "string" && options.apiKey.length > 0) {
    return options.apiKey;
  }
  const env = process.env.NASDAQ_DATA_LINK_API_KEY;
  return env && env.length > 0 ? env : undefined;
}

function asNumber(v: unknown, fallback = 0): number {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string" && v.trim() !== "") {
    const n = Number(v);
    if (Number.isFinite(n)) return n;
  }
  return fallback;
}

function asString(v: unknown, fallback = ""): string {
  return typeof v === "string" ? v : fallback;
}

/**
 * Map a Nasdaq Data Link datatable row (column names → values) to OratsSurfaceRow.
 * Accepts both lowercase ORATS field names and common aliases.
 */
export function mapTableRowToSurface(
  row: Record<string, unknown>,
  fallbackTicker: string,
): OratsSurfaceRow {
  const get = (...keys: string[]): unknown => {
    for (const k of keys) {
      if (k in row) return row[k];
      const lower = k.toLowerCase();
      for (const rk of Object.keys(row)) {
        if (rk.toLowerCase() === lower) return row[rk];
      }
    }
    return undefined;
  };

  return {
    ticker: asString(get("ticker", "symbol"), fallbackTicker).toUpperCase(),
    date: asString(get("date", "trade_date"), new Date().toISOString().slice(0, 10)),
    stockpx: asNumber(get("stockpx", "stock_price", "spot", "underlying_price")),
    iv30: asNumber(get("iv30", "iv_30")),
    iv60: asNumber(get("iv60", "iv_60")),
    iv90: asNumber(get("iv90", "iv_90")),
    slope: asNumber(get("slope")),
    deriv: asNumber(get("deriv", "derivative", "curvature")),
    m1atmiv: optionalNum(get("m1atmiv", "m1_atm_iv")),
    hv10: optionalNum(get("hv10", "hv_10")),
    hv20: optionalNum(get("hv20", "hv_20")),
    hv60: optionalNum(get("hv60", "hv_60")),
  };
}

function optionalNum(v: unknown): number | undefined {
  if (v === undefined || v === null || v === "") return undefined;
  const n = asNumber(v, Number.NaN);
  return Number.isFinite(n) ? n : undefined;
}

/** Parse Nasdaq Data Link datatable JSON into column→value objects. */
export function parseDatatableResponse(
  body: unknown,
  fallbackTicker: string,
): OratsSurfaceRow | null {
  if (!body || typeof body !== "object") return null;
  const root = body as Record<string, unknown>;
  const datatable = (root.datatable ?? root) as Record<string, unknown>;
  const columns = datatable.columns as Array<{ name?: string } | string> | undefined;
  const data = datatable.data as unknown[][] | undefined;

  if (Array.isArray(columns) && Array.isArray(data) && data.length > 0) {
    const names = columns.map((c) =>
      typeof c === "string" ? c : asString(c?.name, ""),
    );
    const first = data[0];
    const row: Record<string, unknown> = {};
    for (let i = 0; i < names.length; i++) {
      row[names[i]] = first[i];
    }
    return mapTableRowToSurface(row, fallbackTicker);
  }

  // Already an object row or array of objects
  if (Array.isArray(datatable.data) && datatable.data.length > 0) {
    const first = datatable.data[0];
    if (first && typeof first === "object" && !Array.isArray(first)) {
      return mapTableRowToSurface(first as Record<string, unknown>, fallbackTicker);
    }
  }

  if ("iv30" in root || "ticker" in root) {
    return mapTableRowToSurface(root, fallbackTicker);
  }

  return null;
}

export class NasdaqDataLinkClient {
  private readonly apiKey: string | undefined;
  private readonly fetchImpl: typeof fetch;
  private readonly baseUrl: string;
  private readonly datatableCode: string;
  private readonly forceMock: boolean;

  constructor(options: ClientOptions = {}) {
    this.forceMock = Boolean(options.forceMock);
    this.apiKey = resolveApiKey(options);
    this.fetchImpl = options.fetchImpl ?? fetch;
    this.baseUrl = options.baseUrl ?? DEFAULT_BASE;
    this.datatableCode = options.datatableCode ?? DEFAULT_TABLE;
  }

  get mode(): DataMode {
    return this.apiKey && !this.forceMock ? "live" : "mock";
  }

  /**
   * Fetch (or mock) the latest ORATS-style volatility surface summary for `symbol`.
   * Live failures fall back to mock so offline / CI pipelines keep working.
   */
  async getOptionVolatilitySurface(symbol: string): Promise<OratsSurfaceRow> {
    const ticker = symbol.trim().toUpperCase();
    if (!ticker) {
      throw new Error("symbol is required");
    }

    if (this.mode === "mock") {
      return getMockSurface(ticker);
    }

    try {
      return await this.fetchLiveSurface(ticker);
    } catch {
      return getMockSurface(ticker);
    }
  }

  /** Build the artifact contract for artifacts/surface.json */
  async getSurfaceArtifact(symbol: string): Promise<SurfaceArtifact> {
    const ticker = symbol.trim().toUpperCase();
    let source: SurfaceArtifact["source"] = "mock";
    let surface: OratsSurfaceRow;

    if (this.mode === "live") {
      try {
        surface = await this.fetchLiveSurface(ticker);
        source = "nasdaq-data-link";
      } catch {
        surface = getMockSurface(ticker);
        source = "mock";
      }
    } else {
      surface = getMockSurface(ticker);
    }

    return {
      source,
      fetchedAt: new Date().toISOString(),
      symbol: ticker,
      surface,
      reconstruction: { ...RECONSTRUCTION },
    };
  }

  private async fetchLiveSurface(ticker: string): Promise<OratsSurfaceRow> {
    const url = new URL(`${this.baseUrl}/${this.datatableCode}.json`);
    url.searchParams.set("ticker", ticker);
    url.searchParams.set("api_key", this.apiKey!);
    // Prefer most recent row when the table supports date filters
    url.searchParams.set("qopts.per_page", "1");

    const res = await this.fetchImpl(url.toString(), {
      headers: { Accept: "application/json" },
    });

    if (!res.ok) {
      throw new Error(`Nasdaq Data Link HTTP ${res.status}`);
    }

    const body: unknown = await res.json();
    const mapped = parseDatatableResponse(body, ticker);
    if (!mapped) {
      throw new Error("Unable to parse Nasdaq Data Link datatable response");
    }
    return mapped;
  }
}

/** Convenience: mock-first client from env. */
export function createClient(options?: ClientOptions): NasdaqDataLinkClient {
  return new NasdaqDataLinkClient(options);
}
