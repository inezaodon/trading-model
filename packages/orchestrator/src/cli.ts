#!/usr/bin/env node
import { parseArgs, printHelp } from "./args.js";
import { logPipeline } from "./logger.js";
import { runPipeline } from "./runner.js";

async function main(): Promise<void> {
  const flags = parseArgs(process.argv.slice(2));
  if (flags.help) {
    printHelp();
    process.exit(0);
  }

  try {
    const result = await runPipeline({
      task: flags.task,
      symbol: flags.symbol,
      mock: flags.mock,
      artifactsDir: flags.artifacts,
    });

    if (!result.ok) {
      logPipeline("exiting with code 1");
      process.exit(1);
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    console.error(message);
    process.exit(1);
  }
}

main();
