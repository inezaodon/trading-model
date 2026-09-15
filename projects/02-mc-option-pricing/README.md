# Monte Carlo Option Pricing (European call/put)

Risk-neutral **Monte Carlo** pricing of European calls and puts under geometric Brownian motion (GBM), with **Black–Scholes** closed-form comparison, standard errors / confidence intervals, and chart-ready convergence data.

Educational / research only — **not** investment advice.

## Math

Under the risk-neutral measure the spot follows

$$
dS_t = r S_t\,dt + \sigma S_t\,dW_t^\mathbb{Q}
$$

Terminal value is exact lognormal. The Monte Carlo estimator discounts the payoff mean:

$$
\hat V = e^{-rT}\frac{1}{N}\sum_{i=1}^{N} \bigl(S_T^{(i)}-K\bigr)^+
\quad\text{(call; put analogous)}
$$

with sample standard error \(\widehat{\mathrm{SE}} = s/\sqrt{N}\) and a normal CI.

## Install

```bash
cd projects/02-mc-option-pricing
pip install -e ".[dev]"
```

## CLI

JSON on stdout (umbrella API friendly):

```bash
# Price with QQQ-style sample params
mc-option-pricing price --sample QQQ --n-paths 50000 --seed 42

# Explicit market params
mc-option-pricing price --spot 230 --strike 230 --rate 0.045 --vol 0.24 \
  --maturity 0.25 --option-type call --n-paths 100000 --seed 7

# Convergence grid for plots
mc-option-pricing converge --sample NVDA --path-counts 1000,5000,25000,100000

# List NASDAQ-style sample parameter sets
mc-option-pricing samples
```

Or: `python -m mc_option_pricing …`

### `price` response shape

```json
{
  "price": 12.34,
  "stderr": 0.05,
  "ci_low": 12.24,
  "ci_high": 12.44,
  "bs_price": 12.31,
  "paths_used": 50000,
  "params": { "spot": 480.0, "strike": 480.0, "...": "..." }
}
```

### `converge` response shape

Arrays aligned for Plotly / Chart.js: `n_paths`, `mc_price`, `stderr`, `ci_low`, `ci_high`, `abs_error`, plus `bs_price` and `params`.

## Library

```python
from mc_option_pricing import price_european_mc, convergence_study, get_sample

out = price_european_mc(spot=480, strike=480, rate=0.045, vol=0.22, maturity=0.25, seed=42)
grid = convergence_study(**{k: get_sample("AAPL")[k] for k in
    ("spot", "strike", "rate", "vol", "maturity", "option_type")}, seed=1)
```

## Sample underlyings

Illustrative mid-2020s levels (not live quotes): `QQQ`, `AAPL`, `MSFT`, `NVDA`, `AMZN`, `META`, `GOOGL`, `TSLA`, `AMD`, `NFLX`.

## Tests

```bash
pytest
```

## Seed control

Pass `--seed` (CLI) or `seed=` (library). Same seed → identical MC prices and stderr.
