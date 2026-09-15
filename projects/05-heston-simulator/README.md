# Heston Stochastic Volatility Simulator

Self-contained demo app for the trading-model umbrella (`projects/05-heston-simulator`).

Simulates the Heston SDEs with **correlated Brownian motions** and a **CIR variance** process:

\[
\begin{aligned}
dS_t &= \mu S_t\,dt + \sqrt{v_t}\,S_t\,dW^S_t \\
dv_t &= \kappa(\theta - v_t)\,dt + \xi\sqrt{v_t}\,dW^v_t \\
d\langle W^S, W^v\rangle_t &= \rho\,dt
\end{aligned}
\]

Discretizations:

- **Euler** — full-truncation Euler–Maruyama
- **QE** — Andersen quadratic-exponential scheme for variance + log-Euler spot

Default correlation is **ρ = −0.7** (Nasdaq-style equity leverage: spot ↓ ↔ vol ↑).

Educational / research only — not investment advice.

## Install

```bash
cd projects/05-heston-simulator
pip install -e ".[dev]"
```

Optional: install monorepo `packages/core-math` so this app can re-export / delegate to `trading_model_math.heston` when available. Use `--no-core-math` to force the local engine.

## CLI

```bash
heston-sim --seed 42 --scheme qe --n-paths 5 --n-steps 252
# or
python -m heston_simulator --seed 42 --scheme euler -o paths.json
```

### Useful flags

| Flag | Default | Meaning |
| --- | --- | --- |
| `--rho` | `-0.7` | Spot–variance correlation (equity: negative) |
| `--scheme` | `qe` | `qe` or `euler` |
| `--seed` | `42` | Deterministic RNG seed |
| `--s0` / `--v0` | `100` / `0.04` | Initial spot / variance |
| `--kappa` / `--theta` / `--xi` | `2` / `0.04` / `0.5` | CIR params |
| `-o` | stdout | Write JSON file |

## JSON contract

Response shape (umbrella-ready):

```json
{
  "slug": "heston",
  "times": [0.0, "..."],
  "S": [[100.0, "..."]],
  "v": [[0.04, "..."]],
  "params": {
    "s0": 100.0,
    "v0": 0.04,
    "mu": 0.05,
    "kappa": 2.0,
    "theta": 0.04,
    "xi": 0.5,
    "rho": -0.7,
    "t": 1.0,
    "n_steps": 252,
    "n_paths": 1,
    "scheme": "qe",
    "seed": 42,
    "engine": "heston_simulator"
  },
  "metrics": {
    "mean_terminal_S": 0.0,
    "mean_terminal_v": 0.0
  }
}
```

Paths are always keyed **`S`** (spot) and **`v`** (variance).

## Library

```python
from heston_simulator import run_heston, simulate_heston

result = run_heston(seed=42, rho=-0.7, scheme="qe", n_paths=10)
# result["S"], result["v"], result["params"]
```

## Tests

```bash
pytest -q
```

## Relation to `packages/core-math`

Logic mirrors `trading_model_math.heston`. When that package is importable, `simulate_heston(..., prefer_core_math=True)` delegates to it and normalizes params to this project's JSON schema.
