# Rough Volatility (Rough Bergomi) Simulator

Standalone **project 07** in the trading-model umbrella: Monte Carlo paths under
the **rough Bergomi** model with Hurst \(H \approx 0.1\), a hybrid fractional
kernel scheme, and forward-variance curve input tied to **NASDAQ-style IV**
summaries (IV30/60/90 + skew slope).

> Educational / research only — not investment advice.

## Model

Instantaneous variance (Bayer–Friz–Gatheral):

\[
v_t = \xi_0(t)\exp\Bigl(\eta\sqrt{2H}\,Z_t - \tfrac12\eta^2 t^{2H}\Bigr)
\]

where \(Z\) is a Riemann–Liouville-type Volterra Gaussian field with kernel
\(K(t,s)\propto (t-s)^{H-1/2}\), and \(\xi_0(t)\) is the forward variance curve.

**Hybrid scheme:** discrete RL kernel matrix + local Euler diagonal weights,
correlated spot Brownian (leverage \(\rho\)), deterministic seed for reproducibility.

## Install

```bash
cd projects/07-rough-volatility
python3 -m pip install -e ".[dev]"
```

## CLI

```bash
# Simulate with flat ξ₀ and H=0.1
rough-vol simulate --s0 100 --hurst 0.1 --eta 1.5 --rho -0.7 --n-steps 64 --n-paths 4 --seed 42

# Or: python -m rough_volatility simulate ...

# Calibrate from NASDAQ-style IV surface (QQQ mock defaults)
rough-vol calibrate --iv30 0.22 --iv60 0.21 --iv90 0.20 --slope -1.5 --s0 450

# Calibrate + simulate → combined JSON
rough-vol run --from-iv --iv30 0.22 --iv60 0.21 --iv90 0.20 --slope -1.5 --seed 42 --out paths.json
```

JSON output includes `times`, `paths[].S`, `paths[].v`, `forward_variance_curve`,
`params` (incl. `seed`), and `metrics`.

## Library

```python
from rough_volatility import simulate_rough_bergomi, calibrate_from_nasdaq_iv

cal = calibrate_from_nasdaq_iv(0.22, 0.21, 0.20, slope=-1.5, s0=450.0)
knots = [tuple(k) for k in cal["params"]["forward_variance_knots"]]
out = simulate_rough_bergomi(
    s0=450.0,
    hurst=0.1,
    eta=cal["params"]["eta"],
    rho=cal["params"]["rho"],
    forward_variance_knots=knots,
    n_steps=90,
    n_paths=8,
    seed=42,
)
```

## NASDAQ IV mapping

See [`docs/NASDAQ_IV.md`](docs/NASDAQ_IV.md). Constant-maturity IVs feed
\(\xi_0\) knots; skew `slope` maps to \(\eta,\rho\). Defaults target QQQ /
Nasdaq-100-like leverage (\(\rho < 0\)).

## Tests

```bash
pytest
```

## References

1. Gatheral, Jaisson, Rosenbaum (2018) — *Volatility is rough*
2. Bayer, Friz, Gatheral (2016) — *Pricing under rough volatility*
3. [NASDAQ Data Link – Option Volatility Surfaces](https://data.nasdaq.com/databases/OPT)
4. Umbrella: `packages/core-math` (`trading_model_math.rough_bergomi`) — this project
   ships a polished standalone copy for the umbrella API (`slug: rough-vol`).

## API contract (umbrella)

`POST /api/v1/rough-vol/run` — body: simulation / IV params → JSON series above.
