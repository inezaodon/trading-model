# Brownian Motion & Random Walk Visualizer

Educational simulator of **Wiener processes** (standard Brownian motion) in 1D and 2D, plus the classical **simple random walk → Brownian motion** limit (Donsker). Exports **chart-ready JSON** for the trading-model umbrella web UI; optional matplotlib `savefig` for static demos.

**Not investment advice.** Synthetic paths only — no market data required.

## Wiener process (quick math)

A standard Brownian motion \(W = (W_t)_{t \ge 0}\) satisfies:

1. \(W_0 = 0\) almost surely  
2. Independent increments  
3. \(W_t - W_s \sim \mathcal{N}(0, t-s)\) for \(t > s\)  
4. Continuous sample paths a.s.

On a uniform grid with \(\Delta t = T/n\):

\[
W_{k\Delta t} = W_{(k-1)\Delta t} + \sqrt{\Delta t}\, Z_k,\quad Z_k \sim N(0,1).
\]

**Scaled BM with drift:** \(X_t = x_0 + \mu t + \sigma W_t\).

**2D BM:** two (possibly correlated) Wiener components \((W^x, W^y)\); trajectories are plotted in the plane.

### Random walk → BM (Donsker)

For i.i.d. steps \(\xi_i = \pm 1\) with equal probability and \(S_k = \sum_{i=1}^k \xi_i\),

\[
X^{(n)}_t = n^{-1/2} S_{\lfloor n t \rfloor}
\]

converges in law to a Wiener process as \(n \to \infty\). The CLI command `random-walk-limit` builds this scaled embedding for teaching.

## Install

```bash
cd projects/03-brownian-visualizer
pip install -e ".[dev]"          # pytest + matplotlib
# or: pip install -e ".[plot]"   # matplotlib only
```

## Library usage

```python
from brownian_visualizer import (
    simulate_brownian_1d,
    simulate_brownian_2d,
    simulate_scaled_brownian,
    random_walk_to_bm_limit,
    result_to_chart_json,
)

bm = simulate_brownian_1d(t=1.0, n_steps=252, n_paths=5, seed=42)
chart = result_to_chart_json(bm)  # → {"model":"brownian","series":[...], ...}

traj = simulate_brownian_2d(n_steps=500, n_paths=1, seed=7, rho=0.3)
rw = random_walk_to_bm_limit(n_steps=5000, n_paths=3, seed=1)
```

## CLI

```bash
python -m brownian_visualizer simulate-1d --seed 42 --n-paths 3 --n-steps 252
python -m brownian_visualizer simulate-scaled --mu 0.2 --sigma 0.5 --seed 1 --out scaled.json
python -m brownian_visualizer simulate-2d --n-paths 2 --rho 0 --seed 7 --savefig demo_2d.png
python -m brownian_visualizer random-walk --n-steps 1000 --seed 42
python -m brownian_visualizer random-walk-limit --n-steps 4000 --n-paths 4 --seed 42
python -m brownian_visualizer random-walk-2d --n-steps 2000 --seed 3
```

Global flags: `--seed` (default **42**), `--out PATH`, `--savefig PATH`.

## JSON schema (web)

| Field | Use |
| --- | --- |
| `model` | Always `"brownian"` |
| `kind` | Simulator variant (`standard_bm_1d`, `scaled_bm_1d`, `standard_bm_2d`, `random_walk_bm_limit`, …) |
| `params` | Inputs including `seed` |
| `times` / `steps` | Abscissa |
| `series` | 1D chart series `{label, y}` |
| `trajectories` | 2D paths `{label, x, y}` |

Umbrella API slug: **`brownian`** → `POST /api/v1/brownian/run`.

## Tests

```bash
pytest -q
```

## Layout

```
projects/03-brownian-visualizer/
  pyproject.toml
  README.md
  src/brownian_visualizer/
    brownian.py      # 1D / 2D / scaled Wiener
    random_walk.py   # simple RW + Donsker scaling
    export.py        # chart-ready JSON
    plot.py          # optional matplotlib
    cli.py
  tests/
```
