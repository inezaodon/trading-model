/**
 * @trading-model/market-data
 *
 * NASDAQ Data Link OPT/ORATS Tables API client (mock + live) and
 * Greeks & Vols schema adapters.
 *
 * - https://data.nasdaq.com/databases/OPT
 * - NASDAQ Greeks and Vols specification
 */

export type {
  ClientOptions,
  DataMode,
  GreeksAndVolsMessage,
  OratsSurfaceRow,
  SurfaceArtifact,
} from "./types.js";

export {
  NasdaqDataLinkClient,
  createClient,
  mapTableRowToSurface,
  parseDatatableResponse,
} from "./client.js";

export {
  getMockSurface,
  listMockSymbols,
  reconstructStrikeIv,
} from "./mock.js";

export {
  adaptGreeksMessage,
  formatOptionSymbol,
  generateGreeksSnapshot,
  type SnapshotOptions,
} from "./greeks.js";
