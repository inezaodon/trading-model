#!/usr/bin/env node
/**
 * strategy-agent CLI — reads paths + surface JSON, writes artifacts/backtest.json
 *
 * Usage:
 *   strategy-agent [--paths <file>] [--surface <file>] [--out <file>] [--strategy <name>]
 */
import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { runBacktest } from "./backtest.js";
import type { PathBundle, SurfaceSummary } from "./types.js";

interface CliArgs {
  paths: string;
  surface: string;
  out: string;
  strategy: string;
  deltaMode: "bs" | "heston";
}

function parseArgs(argv: string[]): CliArgs {
  const args: CliArgs = {
    paths: "artifacts/paths.json",
    surface: "artifacts/surface.json",
    out: "artifacts/backtest.json",
    strategy: "delta-hedge",
    deltaMode: "heston",
  };

  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]!;
    const next = argv[i + 1];
    if (a === "--paths" && next) {
      args.paths = next;
      i++;
    } else if (a === "--surface" && next) {
      args.surface = next;
      i++;
    } else if (a === "--out" && next) {
      args.out = next;
      i++;
    } else if (a === "--strategy" && next) {
      args.strategy = next;
      i++;
    } else if (a === "--delta-mode" && next && (next === "bs" || next === "heston")) {
      args.deltaMode = next;
      i++;
    } else if (a === "--help" || a === "-h") {
      printHelp();
      process.exit(0);
    }
  }
  return args;
}

function printHelp(): void {
  console.log(`strategy-agent — delta-hedge / vol-signal backtest

Options:
  --paths <file>       Input path JSON (default: artifacts/paths.json)
  --surface <file>     Input surface JSON (default: artifacts/surface.json)
  --out <file>         Output backtest JSON (default: artifacts/backtest.json)
  --strategy <name>    Strategy label (default: delta-hedge)
  --delta-mode <mode>  bs | heston (default: heston)
`);
}

async function main(): Promise<void> {
  const args = parseArgs(process.argv.slice(2));

  const [pathsRaw, surfaceRaw] = await Promise.all([
    readFile(args.paths, "utf8"),
    readFile(args.surface, "utf8"),
  ]);

  const paths = JSON.parse(pathsRaw) as PathBundle;
  const surface = JSON.parse(surfaceRaw) as SurfaceSummary;

  validatePaths(paths);
  validateSurface(surface);

  const result = runBacktest(paths, surface, {
    strategy: args.strategy,
    deltaMode: args.deltaMode,
    constantVol: surface.iv30,
    strike: surface.spot,
  });

  // Contract output shape (signal is optional extra for debugging)
  const output = {
    symbol: result.symbol,
    strategy: result.strategy,
    pnl: result.pnl,
    equityCurve: result.equityCurve,
    metrics: result.metrics,
  };

  await mkdir(path.dirname(path.resolve(args.out)), { recursive: true });
  await writeFile(args.out, JSON.stringify(output, null, 2) + "\n", "utf8");

  console.log(
    JSON.stringify(
      {
        wrote: args.out,
        symbol: output.symbol,
        strategy: output.strategy,
        pnl: output.pnl,
        metrics: output.metrics,
      },
      null,
      2,
    ),
  );
}

function validatePaths(paths: PathBundle): void {
  if (!Array.isArray(paths.times) || paths.times.length < 2) {
    throw new Error("paths.times must be an array of length ≥ 2");
  }
  if (!Array.isArray(paths.paths) || paths.paths.length === 0) {
    throw new Error("paths.paths must be a non-empty array");
  }
  for (const [i, p] of paths.paths.entries()) {
    if (!p.S || !p.v || p.S.length !== paths.times.length || p.v.length !== paths.times.length) {
      throw new Error(`paths.paths[${i}] S/v length must match times`);
    }
  }
}

function validateSurface(surface: SurfaceSummary): void {
  if (!surface.symbol || typeof surface.symbol !== "string") {
    throw new Error("surface.symbol is required");
  }
  if (typeof surface.iv30 !== "number" || !Number.isFinite(surface.iv30)) {
    throw new Error("surface.iv30 must be a finite number");
  }
}

main().catch((err: unknown) => {
  console.error(err instanceof Error ? err.message : err);
  process.exit(1);
});
