export interface CliFlags {
  task: string;
  symbol: string;
  mock: boolean;
  artifacts?: string;
  help: boolean;
}

export function parseArgs(argv: string[]): CliFlags {
  const flags: CliFlags = {
    task: "full-pipeline",
    symbol: "QQQ",
    mock: false,
    help: false,
  };

  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i]!;
    if (arg === "--help" || arg === "-h") {
      flags.help = true;
    } else if (arg === "--mock" || arg === "--demo") {
      flags.mock = true;
    } else if (arg === "--task" && argv[i + 1]) {
      flags.task = argv[++i]!;
    } else if (arg.startsWith("--task=")) {
      flags.task = arg.slice("--task=".length);
    } else if (arg === "--symbol" && argv[i + 1]) {
      flags.symbol = argv[++i]!;
    } else if (arg.startsWith("--symbol=")) {
      flags.symbol = arg.slice("--symbol=".length);
    } else if (arg === "--artifacts" && argv[i + 1]) {
      flags.artifacts = argv[++i]!;
    } else if (arg.startsWith("--artifacts=")) {
      flags.artifacts = arg.slice("--artifacts=".length);
    }
  }

  return flags;
}

export function printHelp(): void {
  console.log(`Usage: trading-model-agents [options]

Options:
  --task <name>       full-pipeline | market | math | strategy | report
  --symbol <SYM>      Underlying symbol (default: QQQ)
  --mock              Force mock/placeholder data (no sibling CLIs)
  --demo              Alias for --mock
  --artifacts <dir>   Artifacts directory (default: <repo>/artifacts)
  -h, --help          Show help

Examples:
  npm run agents -- --task full-pipeline --symbol QQQ
  npm run demo
`);
}
