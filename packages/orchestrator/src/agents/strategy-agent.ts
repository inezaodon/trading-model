import fs from "node:fs/promises";
import path from "node:path";
import { logAgent } from "../logger.js";
import { fileExists, strategiesCli } from "../paths.js";
import { runCommandOrThrow } from "../spawn.js";
import { flattenSurfaceForStrategies } from "../surface.js";
import type {
  AgentContext,
  AgentDefinition,
  AgentResult,
  BacktestArtifact,
  PathsArtifact,
  SurfaceArtifact,
} from "../types.js";

async function readPaths(pathsPath: string): Promise<PathsArtifact | null> {
  try {
    const raw = await fs.readFile(pathsPath, "utf8");
    return JSON.parse(raw) as PathsArtifact;
  } catch {
    return null;
  }
}

function firstSpotSeries(paths: PathsArtifact | null): number[] {
  if (!paths) return [100, 101, 99, 102];
  if (paths.paths?.[0]?.S?.length) return paths.paths[0].S;
  if (paths.spot?.length) return paths.spot;
  return [100, 101, 99, 102];
}

/** Placeholder backtest when strategies CLI is missing. */
function placeholderBacktest(
  symbol: string,
  paths: PathsArtifact | null,
): BacktestArtifact {
  const spot = firstSpotSeries(paths);
  const times = paths?.times ?? spot.map((_, i) => i / 252);
  const stepPnl: number[] = [];
  let cumulative = 0;
  for (let i = 1; i < spot.length; i++) {
    const ret = (spot[i]! - spot[i - 1]!) / spot[i - 1]!;
    const step = -0.5 * ret * 100;
    stepPnl.push(step);
    cumulative += step;
  }
  const mean = stepPnl.length ? cumulative / stepPnl.length : 0;
  const variance =
    stepPnl.length > 1
      ? stepPnl.reduce((s, x) => s + (x - mean) ** 2, 0) / (stepPnl.length - 1)
      : 0;
  const sharpe = variance > 0 ? (mean / Math.sqrt(variance)) * Math.sqrt(252) : 0;
  let peak = 0;
  let maxDd = 0;
  let running = 0;
  const equityCurve: Array<{ t: number; equity: number }> = [{ t: times[0] ?? 0, equity: 0 }];
  for (let i = 0; i < stepPnl.length; i++) {
    running += stepPnl[i]!;
    peak = Math.max(peak, running);
    maxDd = Math.min(maxDd, running - peak);
    equityCurve.push({ t: times[i + 1] ?? (i + 1) / 252, equity: running });
  }

  return {
    symbol: symbol.toUpperCase(),
    strategy: "delta-hedge-placeholder",
    pnl: cumulative,
    equityCurve,
    metrics: {
      totalReturn: cumulative,
      sharpe,
      maxDrawdown: maxDd,
    },
    cumulativePnl: cumulative,
    sharpe,
    maxDrawdown: maxDd,
    mock: true,
    warning: "strategies CLI missing — wrote placeholder backtest",
  };
}

async function runStrategyAgent(ctx: AgentContext): Promise<AgentResult> {
  const started = Date.now();
  const outPath = path.join(ctx.artifactsDir, "backtest.json");
  const pathsPath = ctx.outputs.paths ?? path.join(ctx.artifactsDir, "paths.json");
  const surfacePath =
    ctx.outputs.surface ?? path.join(ctx.artifactsDir, "surface.json");
  const cli = strategiesCli(ctx.repoRoot);

  try {
    if (!ctx.mock && fileExists(cli)) {
      logAgent("strategy-agent", "info", `Running strategies CLI → ${outPath}`);
      // market-data nests ORATS fields under `.surface`; strategies wants flat iv30/spot.
      let surfaceForCli = surfacePath;
      try {
        const raw = JSON.parse(await fs.readFile(surfacePath, "utf8")) as SurfaceArtifact;
        const flat = flattenSurfaceForStrategies(raw);
        if (typeof (raw as SurfaceArtifact).iv30 !== "number") {
          surfaceForCli = path.join(ctx.artifactsDir, "surface.strategies.json");
          await fs.writeFile(surfaceForCli, JSON.stringify(flat, null, 2) + "\n", "utf8");
          logAgent(
            "strategy-agent",
            "info",
            `Normalized nested surface → ${surfaceForCli}`,
          );
        }
      } catch (normErr) {
        const msg = normErr instanceof Error ? normErr.message : String(normErr);
        logAgent("strategy-agent", "warn", `surface normalize skipped: ${msg}`);
      }

      // Actual CLI: node dist/cli.js --paths … --surface … --out … (no subcommand)
      await runCommandOrThrow(
        process.execPath,
        [
          cli,
          "--paths",
          pathsPath,
          "--surface",
          surfaceForCli,
          "--out",
          outPath,
          "--strategy",
          "delta-hedge",
        ],
        { cwd: ctx.repoRoot },
      );
      logAgent("strategy-agent", "ok", `Wrote ${outPath}`);
      return {
        agent: "strategy-agent",
        ok: true,
        outputs: { backtest: outPath },
        durationMs: Date.now() - started,
      };
    }

    if (!ctx.mock && !fileExists(cli)) {
      logAgent(
        "strategy-agent",
        "warn",
        `strategies CLI missing at ${cli}; using placeholder backtest`,
      );
    } else {
      logAgent("strategy-agent", "info", "Mock mode — generating placeholder backtest");
    }

    const paths = await readPaths(pathsPath);
    const backtest = placeholderBacktest(ctx.symbol, paths);
    await fs.writeFile(outPath, JSON.stringify(backtest, null, 2) + "\n", "utf8");
    logAgent("strategy-agent", "ok", `Wrote placeholder ${outPath}`);
    return {
      agent: "strategy-agent",
      ok: true,
      outputs: { backtest: outPath },
      warning: backtest.warning,
      durationMs: Date.now() - started,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    logAgent("strategy-agent", "error", message);
    return {
      agent: "strategy-agent",
      ok: false,
      outputs: {},
      error: message,
      durationMs: Date.now() - started,
    };
  }
}

export const strategyAgent: AgentDefinition = {
  name: "strategy-agent",
  description: "Run strategy backtest → artifacts/backtest.json",
  run: runStrategyAgent,
};
