import type { SurfaceArtifact } from "./types.js";

/**
 * Flatten market-data SurfaceArtifact (nested ORATS row) into the
 * strategies SurfaceSummary shape expected by the backtest CLI.
 */
export function flattenSurfaceForStrategies(
  raw: SurfaceArtifact | Record<string, unknown>,
): Record<string, unknown> {
  const s = raw as SurfaceArtifact;
  const nested = s.surface;

  if (typeof s.iv30 === "number" && Number.isFinite(s.iv30)) {
    return {
      symbol: s.symbol,
      asOf: s.asOf ?? nested?.date ?? s.fetchedAt,
      spot: s.spot ?? nested?.stockpx,
      iv30: s.iv30,
      iv60: s.iv60 ?? nested?.iv60,
      iv90: s.iv90 ?? nested?.iv90,
      slope: s.slope ?? nested?.slope,
      deriv: s.deriv ?? nested?.deriv,
      source: s.source,
    };
  }

  if (nested && typeof nested.iv30 === "number") {
    return {
      symbol: s.symbol || nested.ticker,
      asOf: nested.date ?? s.fetchedAt,
      spot: nested.stockpx,
      iv30: nested.iv30,
      iv60: nested.iv60,
      iv90: nested.iv90,
      slope: nested.slope,
      deriv: nested.deriv,
      histVol: (nested as { hv60?: number }).hv60,
      source: s.source,
    };
  }

  throw new Error("Cannot flatten surface: missing iv30");
}
