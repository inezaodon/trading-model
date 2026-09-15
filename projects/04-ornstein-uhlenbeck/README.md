# Ornstein–Uhlenbeck Mean Reversion
# Project slug: `ou` — umbrella API: POST /api/v1/ou/run
#
# Educational / research only. Not investment advice. No live trading.

## SDE

\[
dX_t = \kappa(\theta - X_t)\,dt + \sigma\,dW_t
\]

- **κ** — mean-reversion speed  
- **θ** — long-run mean  
- **σ** — diffusion  
- Half-life: \(\ln 2 / \kappa\)  
- Stationary std: \(\sigma / \sqrt{2\kappa}\)

Exact transition (default scheme) and Euler–Maruyama are both available.

## Layout

```
projects/04-ornstein-uhlenbeck/
  data/synthetic_rates.csv   # bundled synthetic daily rates + 2s10s-like spread
  src/ornstein_uhlenbeck/
    simulate.py              # OU path simulator
    fit.py                   # AR(1) / OLS calibration
    signals.py               # z-score spread signals (demo)
    sample_data.py           # synthetic rates + FRED/Treasury notes
    api.py                   # run(params) → JSON for umbrella API
    cli.py                   # CLI entry
  tests/
  pyproject.toml
```

## Install & test

```bash
cd projects/04-ornstein-uhlenbeck
pip install -e ".[dev]"
pytest -q
```

## CLI

```bash
python -m ornstein_uhlenbeck simulate --kappa 3 --theta 0 --sigma 0.5 --seed 42
python -m ornstein_uhlenbeck fit --series rate --seed 42
python -m ornstein_uhlenbeck signals --series spread_2s10s --entry 1.5 --exit 0.25
python -m ornstein_uhlenbeck demo --seed 42 --out /tmp/ou-demo.json
```

Deterministic **seed** (default `42`) controls all RNG paths.

## JSON API (`run`)

```python
from ornstein_uhlenbeck import run

run({"mode": "simulate", "kappa": 3.0, "theta": 0.0, "sigma": 0.5, "seed": 42})
run({"mode": "fit", "series": "rate", "seed": 42})
run({"mode": "signals", "series": "spread_2s10s", "entry": 1.5, "exit": 0.25})
run({"mode": "demo", "seed": 42})
```

Modes: `simulate` | `fit` | `signals` | `demo`.

## Sample data & live Treasury / FRED fit

Bundled `data/synthetic_rates.csv` is a **synthetic** OU rate path (seed 42) plus a synthetic 2s10s-like spread — for offline demos and tests.

To fit real series:

1. Download from **FRED** (`DGS2`, `DGS10`, `T10Y2Y`, `SOFR`) or **Treasury.gov** constant-maturity CSVs (optional: Yahoo `^TNX`).
2. Pass the level or spread column:

```python
from ornstein_uhlenbeck import fit_ou, run
import numpy as np

obs = np.loadtxt("T10Y2Y.csv", delimiter=",", skiprows=1, usecols=1)
print(fit_ou(obs, dt=1 / 252))
# or
run({"mode": "fit", "observations": obs.tolist(), "dt": 1 / 252})
```

## Spread trading / z-score (research only)

Model z-score \(z_t = (X_t - \theta) / \sigma_\infty\) with entry / exit bands, or a rolling empirical z-score. Positions are −1 / 0 / +1 for charting — **not** executable orders.

## License

MIT — part of the trading-model umbrella.
