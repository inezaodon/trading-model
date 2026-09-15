import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { flattenSurfaceForStrategies } from "../src/surface.js";

describe("flattenSurfaceForStrategies", () => {
  it("passes through already-flat surfaces", () => {
    const flat = flattenSurfaceForStrategies({
      symbol: "QQQ",
      spot: 450,
      iv30: 0.18,
      iv60: 0.19,
    });
    assert.equal(flat.iv30, 0.18);
    assert.equal(flat.spot, 450);
  });

  it("flattens nested market-data ORATS row", () => {
    const flat = flattenSurfaceForStrategies({
      source: "mock",
      symbol: "QQQ",
      surface: {
        ticker: "QQQ",
        date: "2024-09-13",
        stockpx: 478.55,
        iv30: 0.195,
        iv60: 0.178,
        iv90: 0.168,
        slope: -3.85,
        deriv: 0.42,
      },
    });
    assert.equal(flat.symbol, "QQQ");
    assert.equal(flat.spot, 478.55);
    assert.equal(flat.iv30, 0.195);
    assert.equal(flat.slope, -3.85);
  });
});
