import fs from "node:fs/promises";
import path from "node:path";
import { logAgent } from "../logger.js";
import { fileExists, marketDataCli } from "../paths.js";
import { runCommandOrThrow } from "../spawn.js";
import type { AgentContext, AgentDefinition, AgentResult, SurfaceArtifact } from "../types.js";

function mockSurface(symbol: string): SurfaceArtifact {
  const sym = symbol.toUpperCase();
  const spot = sym === "QQQ" ? 450 : 100;
  const date = new Date().toISOString().slice(0, 10);
  const row = {
    ticker: sym,
    date,
    stockpx: spot,
    iv30: 0.18,
    iv60: 0.2,
    iv90: 0.21,
    slope: -1.4,
    deriv: 0.08,
  };
  // Dual shape: flat (strategies) + nested ORATS row (market-data contract).
  return {
    source: "mock",
    fetchedAt: new Date().toISOString(),
    symbol: sym,
    spot,
    asOf: date,
    mock: true,
    iv30: row.iv30,
    iv60: row.iv60,
    iv90: row.iv90,
    slope: row.slope,
    deriv: row.deriv,
    forwardVariance: [0.0324, 0.036, 0.04, 0.0441],
    surface: row,
    reconstruction: {
      formula:
        "IV(strike) ≈ ATMIV * (1 + (slope/1000 + (deriv/1000 * (delta*100-50)/2)) * (delta*100-50))",
      note: "Orchestrator inline mock for offline demo",
    },
  };
}

async function runMarketAgent(ctx: AgentContext): Promise<AgentResult> {
  const started = Date.now();
  const outPath = path.join(ctx.artifactsDir, "surface.json");
  const cli = marketDataCli(ctx.repoRoot);

  try {
    if (!ctx.mock && fileExists(cli)) {
      logAgent("market-agent", "info", `Running market-data CLI → ${outPath}`);
      await runCommandOrThrow(
        process.execPath,
        [cli, "surface", "--symbol", ctx.symbol, "--out", outPath],
        { cwd: ctx.repoRoot },
      );
      logAgent("market-agent", "ok", `Wrote ${outPath}`);
      return {
        agent: "market-agent",
        ok: true,
        outputs: { surface: outPath },
        durationMs: Date.now() - started,
      };
    }

    if (!ctx.mock && !fileExists(cli)) {
      logAgent(
        "market-agent",
        "warn",
        `market-data CLI missing at ${cli}; using inline mock surface`,
      );
    } else {
      logAgent("market-agent", "info", "Mock mode — generating inline surface");
    }

    const surface = mockSurface(ctx.symbol);
    await fs.writeFile(outPath, JSON.stringify(surface, null, 2) + "\n", "utf8");
    logAgent("market-agent", "ok", `Wrote mock ${outPath}`);
    return {
      agent: "market-agent",
      ok: true,
      outputs: { surface: outPath },
      warning: ctx.mock ? undefined : "Used inline mock; market-data CLI not available",
      durationMs: Date.now() - started,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    logAgent("market-agent", "error", message);
    return {
      agent: "market-agent",
      ok: false,
      outputs: {},
      error: message,
      durationMs: Date.now() - started,
    };
  }
}

export const marketAgent: AgentDefinition = {
  name: "market-agent",
  description: "Fetch or mock NASDAQ-style IV surface → artifacts/surface.json",
  run: runMarketAgent,
};
