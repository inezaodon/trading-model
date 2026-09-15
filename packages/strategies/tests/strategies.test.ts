import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, it } from "node:test";
import {
  bsCallDelta,
  bsCallPrice,
  maxDrawdown,
  normCdf,
  runBacktest,
  sharpeRatio,
  simulateDeltaHedge,
  volatilitySignal,
} from "../src/index.js";
import type { PathBundle, SurfaceSummary } from "../src/index.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fixtures = path.join(__dirname, "..", "fixtures");

function loadFixtures(): { paths: PathBundle; surface: SurfaceSummary } {
  const paths = JSON.parse(readFileSync(path.join(fixtures, "paths.json"), "utf8")) as PathBundle;
  const surface = JSON.parse(
    readFileSync(path.join(fixtures, "surface.json"), "utf8"),
  ) as SurfaceSummary;
  return { paths, surface };
}

describe("math helpers", () => {
  it("normCdf is ~0.5 at 0 and monotonic", () => {
    assert.ok(Math.abs(normCdf(0) - 0.5) < 1e-4);
    assert.ok(normCdf(-2) < normCdf(0));
    assert.ok(normCdf(2) > normCdf(0));
  });

  it("bsCallDelta ATM ≈ 0.5–0.6 with r=0", () => {
    const d = bsCallDelta(100, 100, 1, 0, 0.2);
    assert.ok(d > 0.5 && d < 0.6);
  });

  it("bsCallPrice is positive and ≥ intrinsic for calls", () => {
    const px = bsCallPrice(100, 100, 1, 0, 0.2);
    assert.ok(px > 0);
    assert.ok(px >= 0);
  });

  it("maxDrawdown and sharpeRatio behave sensibly", () => {
    assert.equal(maxDrawdown([100, 110, 90, 95], 100), (110 - 90) / 100);
    const s = sharpeRatio([0.01, -0.005, 0.02, 0.01], 1 / 252);
    assert.ok(Number.isFinite(s));
  });
});

describe("simulateDeltaHedge", () => {
  it("returns finite PnL and equity curve on fixture path", () => {
    const { paths } = loadFixtures();
    const result = simulateDeltaHedge(paths.times, paths.paths[0]!, {
      deltaMode: "heston",
      strike: 450,
      maturity: 0.5,
    });
    assert.ok(Number.isFinite(result.pnl));
    assert.equal(result.equityCurve.length, paths.times.length);
    assert.equal(result.deltas.length, paths.times.length);
    for (const p of result.equityCurve) {
      assert.ok(Number.isFinite(p.equity));
    }
  });

  it("BS and Heston modes both run", () => {
    const { paths, surface } = loadFixtures();
    const bs = simulateDeltaHedge(paths.times, paths.paths[0]!, {
      deltaMode: "bs",
      constantVol: surface.iv30,
      strike: surface.spot,
    });
    const heston = simulateDeltaHedge(paths.times, paths.paths[0]!, {
      deltaMode: "heston",
      strike: surface.spot,
    });
    assert.ok(Number.isFinite(bs.pnl));
    assert.ok(Number.isFinite(heston.pnl));
  });

  it("rejects mismatched lengths", () => {
    assert.throws(() =>
      simulateDeltaHedge([0, 1], { S: [100], v: [0.04] }, {}),
    );
  });
});

describe("volatilitySignal", () => {
  it("compares model variance to market iv30²", () => {
    const { paths, surface } = loadFixtures();
    const sig = volatilitySignal(paths, surface);
    assert.ok(sig.marketImpliedVariance > 0);
    assert.ok(sig.modelVariance > 0);
    assert.ok(sig.realizedVariance > 0);
    assert.ok([-1, 0, 1].includes(sig.direction));
    assert.ok(Number.isFinite(sig.edge));
  });

  it("emits short-vol when model variance >> market", () => {
    const { paths } = loadFixtures();
    const richMarket: SurfaceSummary = { symbol: "QQQ", iv30: 0.05, spot: 450 };
    const sig = volatilitySignal(paths, richMarket, { threshold: 0.01 });
    assert.equal(sig.direction, -1);
  });
});

describe("runBacktest", () => {
  it("produces contract-shaped backtest result", () => {
    const { paths, surface } = loadFixtures();
    const result = runBacktest(paths, surface, {
      strategy: "delta-hedge",
      deltaMode: "heston",
    });

    assert.equal(result.symbol, "QQQ");
    assert.equal(result.strategy, "delta-hedge");
    assert.ok(Number.isFinite(result.pnl));
    assert.ok(result.equityCurve.length >= 2);
    assert.ok(Number.isFinite(result.metrics.totalReturn));
    assert.ok(Number.isFinite(result.metrics.sharpe));
    assert.ok(result.metrics.maxDrawdown >= 0);
    assert.ok(result.signal);
  });

  it("serializes to backtest.json contract keys", () => {
    const { paths, surface } = loadFixtures();
    const result = runBacktest(paths, surface);
    const payload = {
      symbol: result.symbol,
      strategy: result.strategy,
      pnl: result.pnl,
      equityCurve: result.equityCurve,
      metrics: result.metrics,
    };
    const keys = Object.keys(payload).sort();
    assert.deepEqual(keys, ["equityCurve", "metrics", "pnl", "strategy", "symbol"]);
    assert.deepEqual(
      Object.keys(payload.metrics).sort(),
      ["maxDrawdown", "sharpe", "totalReturn"],
    );
  });
});
