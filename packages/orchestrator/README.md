# @trading-model/orchestrator

Node/TypeScript multi-agent runner for the trading-model research stack. The orchestrator owns lifecycle: it spawns worker agents sequentially, passes JSON artifact contracts under `artifacts/`, and aggregates a final report.

## How agents are delegated

Agents are registered in an **agent registry** (`AgentRegistry`). Each agent is a named unit with a single `run(ctx)` function. The default pipeline for `full-pipeline` is:

```
market-agent → math-agent → strategy-agent → report-agent
```

| Agent | Responsibility | Prefer CLI | Fallback |
| --- | --- | --- | --- |
| **market-agent** | IV surface → `artifacts/surface.json` | `node packages/market-data/dist/cli.js surface --symbol … --out …` | Inline deterministic mock surface |
| **math-agent** | Paths → `artifacts/paths.json` | `python3 -m trading_model_math simulate-heston …` (cwd `packages/core-math`; optional `calibrate` first) | Placeholder path bundle with clear warning |
| **strategy-agent** | Backtest → `artifacts/backtest.json` | `node packages/strategies/dist/cli.js --paths … --surface … --out …` | Placeholder PnL / equity curve |
| **report-agent** | Rollup → `artifacts/report.json` | (in-process) | Always aggregates whatever artifacts exist |

Delegation rules:

1. **Repo root** is detected by walking up for `package.json` (`name: trading-model` or workspaces).
2. CLIs are invoked with **absolute paths** under that root via `child_process.spawn`.
3. If a sibling package/CLI is missing (common during parallel package builds), the agent logs a **warning** and writes a usable mock/placeholder so the pipeline can continue.
4. `--mock` / `npm run demo` forces placeholders regardless of CLI availability.
5. Failures are labeled `[agent-name]` in logs; by default the pipeline **stops on first hard failure**.

### Adding an agent

```ts
import { createOrchestratorRegistry, runPipeline } from "@trading-model/orchestrator";

const registry = createOrchestratorRegistry([
  {
    name: "risk-agent",
    description: "Compute risk metrics",
    run: async (ctx) => ({
      agent: "risk-agent",
      ok: true,
      outputs: { risk: `${ctx.artifactsDir}/risk.json` },
      durationMs: 0,
    }),
  },
]);

await runPipeline({
  task: "full-pipeline",
  agentNames: ["market-agent", "math-agent", "risk-agent", "report-agent"],
  registry,
});
```

## Commands

From repo root:

```bash
npm install
npm run build -w packages/orchestrator

# Full pipeline (uses real CLIs when present)
npm run agents -- --task full-pipeline --symbol QQQ

# Offline demo with mock data
npm run demo
```

From this package:

```bash
npm run build
npm run demo
npm test
```

## Artifact contracts

See [`docs/ARCHITECTURE.md`](../../docs/ARCHITECTURE.md):

- `artifacts/surface.json`
- `artifacts/paths.json`
- `artifacts/backtest.json`
- `artifacts/report.json`
