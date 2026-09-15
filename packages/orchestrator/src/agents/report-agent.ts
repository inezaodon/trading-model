import fs from "node:fs/promises";
import path from "node:path";
import { logAgent } from "../logger.js";
import type {
  AgentContext,
  AgentDefinition,
  AgentResult,
  BacktestArtifact,
  PathsArtifact,
  ReportArtifact,
  SurfaceArtifact,
} from "../types.js";

async function readJson<T>(filePath: string): Promise<T | null> {
  try {
    const raw = await fs.readFile(filePath, "utf8");
    return JSON.parse(raw) as T;
  } catch {
    return null;
  }
}

function pickSpot(surface: SurfaceArtifact | null): number | undefined {
  return surface?.spot ?? surface?.surface?.stockpx;
}

function pickIv30(surface: SurfaceArtifact | null): number | undefined {
  return surface?.iv30 ?? surface?.surface?.iv30;
}

function pickFinalSpot(paths: PathsArtifact | null): number | undefined {
  const s = paths?.paths?.[0]?.S ?? paths?.spot;
  return s?.length ? s[s.length - 1] : undefined;
}

function pickTermVar(paths: PathsArtifact | null): number | undefined {
  const v = paths?.paths?.[0]?.v ?? paths?.variance;
  return v?.length ? v[v.length - 1] : undefined;
}

function pickPnl(backtest: BacktestArtifact | null): number | undefined {
  if (!backtest) return undefined;
  if (typeof backtest.pnl === "number") return backtest.pnl;
  if (backtest.cumulativePnl != null) return backtest.cumulativePnl;
  if (Array.isArray(backtest.pnl)) {
    return backtest.pnl.reduce((a, b) => a + b, 0);
  }
  return backtest.metrics?.totalReturn;
}

function pickSharpe(backtest: BacktestArtifact | null): number | undefined {
  return backtest?.sharpe ?? backtest?.metrics?.sharpe;
}

async function runReportAgent(ctx: AgentContext): Promise<AgentResult> {
  const started = Date.now();
  const outPath = path.join(ctx.artifactsDir, "report.json");

  try {
    const surfacePath =
      ctx.outputs.surface ?? path.join(ctx.artifactsDir, "surface.json");
    const pathsPath = ctx.outputs.paths ?? path.join(ctx.artifactsDir, "paths.json");
    const backtestPath =
      ctx.outputs.backtest ?? path.join(ctx.artifactsDir, "backtest.json");

    logAgent("report-agent", "info", `Aggregating artifacts → ${outPath}`);

    const surface = await readJson<SurfaceArtifact>(surfacePath);
    const paths = await readJson<PathsArtifact>(pathsPath);
    const backtest = await readJson<BacktestArtifact>(backtestPath);

    const priorResults = (ctx.outputs.__agentResults
      ? JSON.parse(ctx.outputs.__agentResults)
      : []) as AgentResult[];

    const report: ReportArtifact = {
      generatedAt: new Date().toISOString(),
      symbol: ctx.symbol.toUpperCase(),
      task: ctx.task,
      mock: ctx.mock,
      agents: priorResults,
      surfacePath: surface ? surfacePath : undefined,
      pathsPath: paths ? pathsPath : undefined,
      backtestPath: backtest ? backtestPath : undefined,
      summary: {
        spot: pickSpot(surface),
        iv30: pickIv30(surface),
        pathCount: paths?.paths?.length ?? paths?.nPaths,
        finalSpot: pickFinalSpot(paths),
        terminalVariance: pickTermVar(paths),
        cumulativePnl: pickPnl(backtest),
        sharpe: pickSharpe(backtest),
      },
    };

    await fs.writeFile(outPath, JSON.stringify(report, null, 2) + "\n", "utf8");
    logAgent("report-agent", "ok", `Wrote ${outPath}`);
    return {
      agent: "report-agent",
      ok: true,
      outputs: { report: outPath },
      durationMs: Date.now() - started,
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    logAgent("report-agent", "error", message);
    return {
      agent: "report-agent",
      ok: false,
      outputs: {},
      error: message,
      durationMs: Date.now() - started,
    };
  }
}

export const reportAgent: AgentDefinition = {
  name: "report-agent",
  description: "Aggregate surface/paths/backtest into artifacts/report.json",
  run: runReportAgent,
};
