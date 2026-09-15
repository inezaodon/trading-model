# Monte Carlo Value-at-Risk Engine

Educational Monte Carlo **VaR** and **Expected Shortfall (ES / CVaR)** for a
multi-asset ETF portfolio. Part of the trading-model umbrella (`slug: var`).

**Not investment advice. No live trading.**

## Features

- Thousands of simulated portfolio P&L scenarios
- **GBM** (multivariate normal horizon log-returns) or **empirical bootstrap**
- Configurable weights, horizon (trading days), confidence levels (95% / 99%)
- Bundled sample daily log-returns for `QQQ, SPY, IWM, TLT, GLD` (synthetic;
  optional `yfinance` download if installed)
- Deterministic `seed` for reproducible JSON
- Library + CLI + pytest; JSON shaped for `POST /api/v1/var/run`

## Install

```bash
cd projects/06-monte-carlo-var
python3 -m pip install -e ".[dev]"
pytest -q
```

Optional live data:

```bash
python3 -m pip install -e ".[data]"
```

## CLI

```bash
# Generate / refresh bundled sample CSV
python -m monte_carlo_var gen-sample --seed 42

# Equal-weight 10-day VaR/ES (GBM, 10k scenarios)
python -m monte_carlo_var run --method gbm --horizon-days 10 --n-scenarios 10000 --seed 42

# Bootstrap with custom weights
python -m monte_carlo_var run --method bootstrap --weights 0.3,0.25,0.15,0.2,0.1 --confidence 0.95,0.99
```

## Library

```python
from monte_carlo_var import run_var

result = run_var(method="gbm", horizon_days=10, n_scenarios=5000, seed=42)
print(result["risk_table"])
```

## Math (brief)

Daily log-returns \(R_t \in \mathbb{R}^N\). Over horizon \(h\):

- **GBM:** \(R_{0\to h} \sim \mathcal{N}(h\mu,\, h\Sigma)\) with \(\mu,\Sigma\) from history.
- **Bootstrap:** sample \(h\) historical days with replacement (joint across assets) and sum.

Portfolio P&L: \(V_0 \cdot w^\top(\mathrm{e}^{R}-1)\).

VaR at confidence \(\alpha\): \(-\,q_{1-\alpha}(\mathrm{PnL})\).  
ES: \(-\mathbb{E}[\mathrm{PnL}\mid \mathrm{PnL}\le -\mathrm{VaR}]\).

## JSON sketch

```json
{
  "project": "var",
  "params": { "method": "gbm", "horizon_days": 10, "seed": 42 },
  "risk_table": [
    { "confidence": 0.95, "var": 12345.0, "es": 16000.0 }
  ],
  "metrics": { "pnl_summary": {}, "by_confidence": [] },
  "chart": { "pnl_histogram": {}, "pnl_sorted": [] }
}
```

## Data note

Bundled returns are **synthetic** correlated Gaussians calibrated to rough ETF
vol/correlation priors so the demo works offline. Cite Yahoo Finance / NASDAQ
if you enable `--download`.
