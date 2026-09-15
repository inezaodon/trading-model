#!/usr/bin/env node
/**
 * CLI for market-data package.
 *
 * Usage:
 *   node dist/cli.js surface --symbol QQQ --out ../../artifacts/surface.json
 */

import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createClient } from "./client.js";

function printHelp(): void {
  console.log(`Usage:
  node dist/cli.js surface --symbol <TICKER> [--out <path>]

Options:
  --symbol   Underlying ticker (default: QQQ)
  --out      Output JSON path (default: ../../artifacts/surface.json relative to package)
  --help     Show help
`);
}

function parseArgs(argv: string[]): {
  command: string;
  symbol: string;
  out: string;
  help: boolean;
} {
  const args = argv.slice(2);
  const command = args[0] ?? "help";
  let symbol = "QQQ";
  let out = "";
  let help = command === "help" || command === "--help" || args.includes("--help");

  for (let i = 1; i < args.length; i++) {
    const a = args[i];
    if (a === "--symbol" && args[i + 1]) {
      symbol = args[++i];
    } else if (a === "--out" && args[i + 1]) {
      out = args[++i];
    } else if (a === "--help") {
      help = true;
    }
  }

  if (!out) {
    // Default: repo artifacts/ (packages/market-data → ../../artifacts)
    const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
    out = path.resolve(packageRoot, "../../artifacts/surface.json");
  }

  return { command, symbol, out, help };
}

async function runSurface(symbol: string, outPath: string): Promise<void> {
  const client = createClient();
  const artifact = await client.getSurfaceArtifact(symbol);
  const abs = path.resolve(outPath);
  await mkdir(path.dirname(abs), { recursive: true });
  await writeFile(abs, JSON.stringify(artifact, null, 2) + "\n", "utf8");
  console.log(
    `Wrote ${artifact.source} surface for ${artifact.symbol} → ${abs}`,
  );
}

async function main(): Promise<void> {
  const { command, symbol, out, help } = parseArgs(process.argv);
  if (help || command !== "surface") {
    printHelp();
    if (command !== "surface" && !help) {
      process.exitCode = 1;
    }
    return;
  }
  await runSurface(symbol, out);
}

main().catch((err: unknown) => {
  console.error(err instanceof Error ? err.message : err);
  process.exitCode = 1;
});
