# Agent Delegation Log

Orchestrator run for **trading-model** — modern stochastic calculus stack.

## Research verdict (orchestrator)

Modern quantitative trading no longer stops at Black–Scholes. Production research stacks typically layer:

1. **Itô / GBM** — baseline paths and delta hedges  
2. **Heston / SABR** — Markov stochastic vol with leverage \(\rho < 0\) (Nasdaq-100 style)  
3. **Rough volatility** (Bergomi / Heston, \(H \approx 0.1\)) — short-tenor skew realism via fractional kernels  
4. **Signatures / rough paths** — path-dependent pricing & features  
5. **Market surfaces** — NASDAQ Data Link ORATS IV summaries + Greeks & Vols schema for calibration  

Primary references are linked from `docs/STOCHASTIC_CALCULUS.md` and `docs/NASDAQ_DATA.md`.

## Live agent assignments

| Agent | Role | Owns | Cursor agent id |
| --- | --- | --- | --- |
| A | core-math (Python SDEs) | `packages/core-math/**` | bc-aef2dbff-84bf-5bb4-8bab-eb2212e963fd |
| B | market-data (NASDAQ adapters) | `packages/market-data/**` | bc-a3b5d8ec-9258-5640-89fe-fbdc8efde78e |
| C | strategies (hedge / backtest) | `packages/strategies/**` | bc-b683ac61-155a-5532-bb64-c470879c442c |
| D | orchestrator + dashboard | `packages/orchestrator/**`, `packages/dashboard/**` | bc-b9787670-86d2-51ee-9727-a9bc8c144c38 |

## Pipeline contract

```
surface.json → calibrate/simulate → paths.json → backtest.json → report.json
```

## Local branch

`cursor/trading-model-scaffold-dedd` under `/agent/trading-model`
