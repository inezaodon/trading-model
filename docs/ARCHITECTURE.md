# Architecture — Orchestrator View

```
                 ┌─────────────────────────────┐
                 │   Node Orchestrator (root)  │
                 │  packages/orchestrator      │
                 └─────────────┬───────────────┘
           ┌───────────────────┼───────────────────┐
           ▼                   ▼                   ▼
   market-agent          math-agent          strategy-agent
   market-data/          core-math/          strategies/
   (NASDAQ mock/API)     (Python SDEs)       (hedge/backtest)
           │                   │                   │
           └───────────────────┴───────────────────┘
                               ▼
                         report-agent
                         dashboard/
```

## Design rules

1. **Orchestrator owns lifecycle** — spawns agents, passes JSON contracts, aggregates results.
2. **Agents own one job** — no cross-package imports of private internals.
3. **Contracts are JSON files** under `artifacts/` for replay and tests.
4. **Math stays in Python** for NumPy speed; Node wraps via `child_process`.
5. **No live trading** — research PnL only.

## Artifact contracts

- `artifacts/surface.json` — IV surface summary  
- `artifacts/paths.json` — simulated \(S_t, v_t\)  
- `artifacts/backtest.json` — strategy PnL  
- `artifacts/report.json` — final rollup  

## Parallel build ownership (agent teams)

| Agent | Owns |
| --- | --- |
| A — core-math | `packages/core-math/**` |
| B — market-data | `packages/market-data/**` |
| C — strategies | `packages/strategies/**` |
| D — orchestrator + dashboard | `packages/orchestrator/**`, `packages/dashboard/**`, root `package.json` |
