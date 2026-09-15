# @trading-model/strategies

Delta-hedge simulator, volatility signal, and backtest engine for the trading-model stack.

## Inputs

- `artifacts/paths.json` — `{ times, paths: [{ S, v }] }` from core-math
- `artifacts/surface.json` — `{ symbol, iv30, spot, ... }` from market-data

## Output

- `artifacts/backtest.json` — `{ symbol, strategy, pnl, equityCurve, metrics }`

## CLI

```bash
npx strategy-agent --paths artifacts/paths.json --surface artifacts/surface.json --out artifacts/backtest.json
```

Fixtures under `fixtures/` are used when sibling packages are unavailable.
