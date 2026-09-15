# Trading Model

A quantitative trading research stack built on **modern stochastic calculus** — classical Itô SDEs, Heston/SABR, and rough volatility — with NASDAQ-oriented market data adapters and a Node.js multi-agent orchestrator.

> Educational / research software. Not investment advice. No live order routing.

## Why this stack

Modern equity and index markets (including NASDAQ-100 names and options surfaces) show:

- Fat-tailed returns, volatility clustering, and leverage effects
- Steep short-maturity implied-vol skews that classical Brownian SV models struggle to fit
- Path-dependent / non-Markovian volatility dynamics

This repo implements the practical toolkit used in industry research today:

| Layer | Models / tools | Role |
| --- | --- | --- |
| Classical SDEs | GBM, Itô lemma utilities | Baseline price paths & hedging |
| Markov SV | Heston, SABR-style local-stochastic vol | Smile, mean-reverting variance |
| Rough vol | Rough Bergomi / fractional kernels (H ≈ 0.1) | Short-tenor skew realism |
| Signatures | Path signatures (research hooks) | Path-dependent features |
| Market data | NASDAQ Data Link / Greeks & Vols schema | Calibration inputs |
| Agents | Node orchestrator + worker agents | Parallel simulate / calibrate / backtest |

## Packages

```
packages/
  core-math/       # SDE simulators, Itô helpers, Heston, rough Bergomi
  market-data/     # NASDAQ Data Link client + mock surfaces
  strategies/      # Delta-hedge, vol-arb, model-based signals
  orchestrator/    # Node multi-agent runner (spawn & delegate)
  dashboard/       # Lightweight viz of paths, vol, PnL
apps/
  api/             # FastAPI umbrella backend (7 project engines)
  web/             # Single website for all 7 demos
projects/          # Self-contained demo apps (merged by orchestrator)
```

## Umbrella website + API

```bash
# install + serve API and static web on :8000
make demo
# or
npm run demo:umbrella

# smoke-test all 7 run endpoints
make smoke
```

Open http://127.0.0.1:8000/ — brand **Trading Model**, nav to all seven projects.
Integration handoff: [`docs/PROGRESS.md`](docs/PROGRESS.md).

## Quick start (Node orchestrator)

```bash
# from repo root
npm install
npm run build
npm run demo          # orchestrator runs math + mock NASDAQ agents
npm test
```

Python math engine (used by Node agents via CLI):

```bash
cd packages/core-math
python3 -m pip install -e ".[dev]"
pytest
```

## References

See [`docs/STOCHASTIC_CALCULUS.md`](docs/STOCHASTIC_CALCULUS.md) and [`docs/NASDAQ_DATA.md`](docs/NASDAQ_DATA.md).

Key external sources:

- Gatheral, Jaisson, Rosenbaum — rough volatility
- Bayer, Friz, Gatheral — pricing under rough volatility
- [NASDAQ Data Link – Option Volatility Surfaces](https://data.nasdaq.com/databases/OPT)
- [NASDAQ Greeks and Vols](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/GreeksandVols_Specification.pdf)
- Asymmetric SV on Nasdaq-100 (MDPI Risks, 2024)

## Agent orchestration

```bash
npm run agents -- --task full-pipeline --symbol QQQ
```

The orchestrator starts worker agents:

1. **market-agent** — fetch / mock NASDAQ-style IV surface
2. **math-agent** — simulate Heston + rough Bergomi paths
3. **strategy-agent** — delta-hedge / vol signals + backtest
4. **report-agent** — summarize paths, skew fit, PnL

## License

MIT
