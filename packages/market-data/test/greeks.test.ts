import assert from "node:assert/strict";
import { describe, it } from "node:test";
import {
  adaptGreeksMessage,
  formatOptionSymbol,
  generateGreeksSnapshot,
} from "../dist/index.js";

describe("Greeks & Vols adapter", () => {
  it("generates synthetic streaming-like snapshots", () => {
    const ts = 1_725_000_000_000;
    const batch = generateGreeksSnapshot({
      underlying: "QQQ",
      timestamp: ts,
      moneyness: [0.95, 1.0, 1.05],
      daysToExpiry: 30,
      right: "C",
    });
    assert.equal(batch.length, 3);
    for (const msg of batch) {
      assert.equal(msg.timestamp, ts);
      assert.equal(msg.underlying, "QQQ");
      assert.ok(msg.option.includes("QQQ"));
      assert.ok(Number.isFinite(msg.delta));
      assert.ok(Number.isFinite(msg.gamma));
      assert.ok(Number.isFinite(msg.vega));
      assert.ok(Number.isFinite(msg.theta));
      assert.ok(Number.isFinite(msg.rho));
      assert.ok(msg.impliedVolatility > 0);
      assert.ok(msg.theoreticalPrice > 0);
    }
    // ATM-ish middle point should have delta near 0.5 for calls
    assert.ok(Math.abs(batch[1].delta - 0.5) < 0.15);
  });

  it("formats OCC-style option symbols", () => {
    const exp = new Date(Date.UTC(2024, 8, 20));
    const sym = formatOptionSymbol("QQQ", exp, "C", 450);
    assert.equal(sym, "QQQ240920C00450000");
  });

  it("adapts raw messages to schema", () => {
    const msg = adaptGreeksMessage({
      timestamp: 123,
      option: "AAPL240920C00200000",
      underlying: "aapl",
      delta: 0.4,
      gamma: 0.02,
      vega: 0.1,
      theta: -0.05,
      rho: 0.01,
      impliedVolatility: 0.25,
      theoreticalPrice: 3.2,
    });
    assert.equal(msg.underlying, "AAPL");
    assert.equal(msg.impliedVolatility, 0.25);
  });
});
