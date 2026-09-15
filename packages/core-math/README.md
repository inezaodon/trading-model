# core-math (`trading_model_math`)

NumPy-based stochastic calculus for the trading-model research stack.

## Models

| Module | Role |
| --- | --- |
| `gbm` | Geometric Brownian Motion path simulation |
| `ito` | Itô lemma helpers and log-return transforms |
| `heston` | Heston SV with correlated Brownian motions (Euler / QE) |
| `rough_bergomi` | Hybrid discrete approximation of rough Bergomi (\(H \approx 0.1\)) |
| `signatures` | Truncated path-signature features (level 2–3) |
| `calibrate` | Heuristic map from IV30/60/90 + slope → model params |

## Install

```bash
cd packages/core-math
python3 -m pip install -e ".[dev]"
pytest -q
```

## CLI

Spawned by the Node orchestrator:

```bash
python -m trading_model_math simulate-heston --symbol QQQ --seed 42 --n-paths 4 --n-steps 64
python -m trading_model_math simulate-rbergomi --symbol QQQ --seed 7 --out paths.json
python -m trading_model_math calibrate --iv30 0.22 --iv60 0.21 --iv90 0.20 --slope -1.5
python -m trading_model_math signatures --path-json paths.json --level 2
```

Path JSON schema:

```json
{
  "model": "heston",
  "symbol": "QQQ",
  "params": {},
  "times": [0.0, 0.01, "..."],
  "paths": [{"S": [], "v": []}]
}
```

## Math notes

See repo docs: `docs/STOCHASTIC_CALCULUS.md`. Equity / Nasdaq calibrations default to leverage \(\rho < 0\).
