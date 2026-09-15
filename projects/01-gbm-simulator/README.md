# GBM Stock Price Simulator

Geometric Brownian Motion (GBM) Monte Carlo simulator for educational / research use in the **trading-model** umbrella (`slug: gbm`).

**Not investment advice. No live order routing.**

## Math

Asset price \(S_t\) follows the Itô SDE

\[
dS_t = \mu S_t\,dt + \sigma S_t\,dW_t
\]

where \(\mu\) is the drift, \(\sigma\) is volatility, and \(W_t\) is a Wiener process.

By Itô's formula, \(\log S_t\) is arithmetic Brownian motion. The exact discrete step used here is

\[
S_{t+\Delta t} = S_t \exp\Bigl(\bigl(\mu - \tfrac12\sigma^2\bigr)\Delta t + \sigma\sqrt{\Delta t}\,Z\Bigr),
\quad Z\sim\mathcal{N}(0,1).
\]

Terminal moments under GBM:

\[
\mathbb{E}[S_T] = S_0 e^{\mu T},
\qquad
\mathrm{Var}(S_T) = S_0^2 e^{2\mu T}\bigl(e^{\sigma^2 T}-1\bigr).
\]

Given historical closes, annualized parameters are recovered from log returns
\(r_i = \log(S_i/S_{i-1})\) with step \(\Delta t\) (default \(1/252\)):

\[
\hat\sigma = \sqrt{\widehat{\mathrm{Var}}(r)/\Delta t},
\qquad
\hat\mu = \bar r/\Delta t + \tfrac12\hat\sigma^2.
\]

## Install

From this directory:

```bash
pip install -e ".[dev]"
```

Requires Python ≥ 3.10, NumPy, Matplotlib. Optional: `pip install -e ".[plotly]"` if you want the Plotly Python package (figure JSON export works without it).

## CLI

```bash
# Simulate paths (deterministic seed)
gbm-sim simulate --s0 100 --mu 0.05 --sigma 0.2 --t 1 --n-steps 252 --n-paths 200 --seed 42

# Export umbrella API JSON + Plotly figure JSON + PNG
gbm-sim simulate --n-paths 100 --seed 42 \
  --json-out /tmp/gbm.json \
  --plotly-out /tmp/gbm_plotly.json \
  --plot-out /tmp/gbm.png

# Print JSON to stdout (for umbrella API subprocess)
gbm-sim simulate --n-paths 50 --seed 1 --stdout-json

# Estimate μ, σ from bundled QQQ-like sample (or your CSV)
gbm-sim calibrate
gbm-sim calibrate --csv data/qqq_sample.csv --simulate --json-out /tmp/calibrated.json
```

## Library

```python
from gbm_simulator import simulate_gbm, estimate_mu_sigma, load_price_csv, simulation_to_json

result = simulate_gbm(s0=100, mu=0.05, sigma=0.2, t=1.0, n_steps=252, n_paths=100, seed=42)
payload = simulation_to_json(result)  # {times, paths, params, stats}

prices = load_price_csv("data/qqq_sample.csv")
est = estimate_mu_sigma(prices)  # mu, sigma, s0, ...
```

## Umbrella API JSON contract

```json
{
  "times": [0.0, 0.004, "..."],
  "paths": [[100.0, "..."], ["..."]],
  "params": {"s0": 100.0, "mu": 0.05, "sigma": 0.2, "t": 1.0, "n_steps": 252, "n_paths": 100, "seed": 42, "model": "gbm"},
  "stats": {"mean_terminal": 105.1, "theoretical_mean": 105.1, "...": "..."}
}
```

Slug for the umbrella router: **`gbm`** → `POST /api/v1/gbm/run`.

## Data

`data/qqq_sample.csv` is a **synthetic** daily close series (~2 years) with QQQ-like level and volatility (seeded GBM). For live NASDAQ series see the monorepo `docs/NASDAQ_DATA.md` / `packages/market-data`.

## Tests

```bash
pytest -q
```

## Relation to `packages/core-math`

This project is **standalone** (own GBM implementation + CLI + export). The monorepo `trading_model_math.gbm.simulate_gbm` exposes a compatible core routine; this demo adds calibration, Matplotlib/Plotly export, and the umbrella `{times, paths, params, stats}` contract.
