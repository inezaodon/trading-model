import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  NasdaqDataLinkClient,
  createClient,
  getMockSurface,
  listMockSymbols,
  mapTableRowToSurface,
  parseDatatableResponse,
  reconstructStrikeIv,
} from "../dist/index.js";

describe("mock ORATS / OPT surfaces", () => {
  it("returns deterministic QQQ tech/Nasdaq skew (elevated short IV, negative slope)", () => {
    const a = getMockSurface("QQQ");
    const b = getMockSurface("qqq");
    assert.deepEqual(a, b);
    assert.equal(a.ticker, "QQQ");
    assert.ok(a.iv30 > a.iv60);
    assert.ok(a.iv60 > a.iv90);
    assert.ok(a.slope < 0);
    assert.ok(a.stockpx > 0);
    assert.ok(a.deriv > 0);
  });

  it("covers AAPL and MSFT profiles", () => {
    for (const sym of ["AAPL", "MSFT"]) {
      const s = getMockSurface(sym);
      assert.equal(s.ticker, sym);
      assert.ok(s.iv30 > s.iv90);
      assert.ok(s.slope < 0);
    }
    assert.ok(listMockSymbols().includes("QQQ"));
  });

  it("reconstructs strike IV with ORATS formula", () => {
    const atm = 0.2;
    const ivAtm = reconstructStrikeIv(atm, -4, 0.5, 0.5);
    assert.ok(Math.abs(ivAtm - atm) < 1e-9);
    const otmPut = reconstructStrikeIv(atm, -4, 0.5, 0.25);
    assert.ok(otmPut > atm);
  });
});

describe("NasdaqDataLinkClient", () => {
  it("uses mock mode without API key", async () => {
    const prev = process.env.NASDAQ_DATA_LINK_API_KEY;
    delete process.env.NASDAQ_DATA_LINK_API_KEY;
    try {
      const client = createClient({ forceMock: true });
      assert.equal(client.mode, "mock");
      const surface = await client.getOptionVolatilitySurface("QQQ");
      assert.equal(surface.ticker, "QQQ");
      const artifact = await client.getSurfaceArtifact("QQQ");
      assert.equal(artifact.source, "mock");
      assert.equal(artifact.symbol, "QQQ");
      assert.ok(artifact.reconstruction.formula.includes("slope/1000"));
    } finally {
      if (prev !== undefined) process.env.NASDAQ_DATA_LINK_API_KEY = prev;
    }
  });

  it("parses Tables API datatable JSON shape", () => {
    const body = {
      datatable: {
        columns: [
          { name: "ticker" },
          { name: "date" },
          { name: "stockpx" },
          { name: "iv30" },
          { name: "iv60" },
          { name: "iv90" },
          { name: "slope" },
          { name: "deriv" },
        ],
        data: [["QQQ", "2024-09-13", 478.55, 0.195, 0.178, 0.168, -3.85, 0.42]],
      },
    };
    const row = parseDatatableResponse(body, "QQQ");
    assert.ok(row);
    assert.equal(row!.ticker, "QQQ");
    assert.equal(row!.iv30, 0.195);
    assert.equal(row!.slope, -3.85);
  });

  it("maps alias column names", () => {
    const row = mapTableRowToSurface(
      { symbol: "AAPL", trade_date: "2024-01-02", spot: 100, iv_30: 0.2, iv_60: 0.18, iv_90: 0.17, slope: -3, curvature: 0.4 },
      "AAPL",
    );
    assert.equal(row.ticker, "AAPL");
    assert.equal(row.stockpx, 100);
    assert.equal(row.iv30, 0.2);
    assert.equal(row.deriv, 0.4);
  });

  it("falls back to mock when live fetch fails", async () => {
    const failingFetch: typeof fetch = async () => {
      throw new Error("network down");
    };
    const client = new NasdaqDataLinkClient({
      apiKey: "test-key",
      fetchImpl: failingFetch,
    });
    assert.equal(client.mode, "live");
    const surface = await client.getOptionVolatilitySurface("MSFT");
    assert.equal(surface.ticker, "MSFT");
    assert.ok(surface.slope < 0);
  });

  it("uses live response when fetch succeeds", async () => {
    const okFetch: typeof fetch = async () =>
      new Response(
        JSON.stringify({
          datatable: {
            columns: [
              { name: "ticker" },
              { name: "date" },
              { name: "stockpx" },
              { name: "iv30" },
              { name: "iv60" },
              { name: "iv90" },
              { name: "slope" },
              { name: "deriv" },
            ],
            data: [["QQQ", "2024-09-14", 480, 0.21, 0.19, 0.18, -4.1, 0.5]],
          },
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      );

    const client = new NasdaqDataLinkClient({
      apiKey: "test-key",
      fetchImpl: okFetch,
    });
    const artifact = await client.getSurfaceArtifact("QQQ");
    assert.equal(artifact.source, "nasdaq-data-link");
    assert.equal(artifact.surface.iv30, 0.21);
    assert.equal(artifact.surface.stockpx, 480);
  });
});
