# NASDAQ Data Integration

Grounding market inputs in public NASDAQ documentation and Data Link products.

## Products referenced

### 1. NASDAQ Data Link — Option Volatility Surfaces (ORATS)

- Portal: https://data.nasdaq.com/databases/OPT  
- Delivery: Tables API  
- Useful fields for this model:
  - `iv30`, `iv60`, `iv90` — constant-maturity implied vols
  - `m1atmiv` … month ATM IVs
  - `slope`, `deriv` — skew slope & curvature
  - Historical volatility windows (10–252d)

Strike IV reconstruction (ORATS-style summary):

```
IV(strike) ≈ ATMIV * (1 + (slope/1000 + (deriv/1000 * (delta*100-50)/2)) * (delta*100-50))
```

These summaries feed our **forward variance curve** \(\xi_0(t)\) for rough Bergomi and Heston \(\theta\) / initial \(v_0\).

### 2. NASDAQ Greeks and Vols

- Spec: https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/GreeksandVols_Specification.pdf  
- Streaming Greeks (Δ, Γ, ν, Θ, ρ), implied volatility, theoretical price  
- Update cadence ~60s during regular + extended sessions  

Schema fields used by our mock/live adapters:

```json
{
  "timestamp": 0,
  "option": "QQQ240920C00450000",
  "underlying": "QQQ",
  "delta": 0.5,
  "gamma": 0.02,
  "vega": 0.12,
  "theta": -0.03,
  "rho": 0.01,
  "impliedVolatility": 0.22,
  "theoreticalPrice": 4.55
}
```

### 3. Empirical NASDAQ-100 SV evidence

Asymmetric stochastic volatility / leverage effects are documented on Nasdaq-100 returns (e.g. MDPI *Risks* 2024 study). We default equity \(\rho\) negative (≈ −0.6 to −0.7) when calibrating Heston-style models to NDX/QQQ-like underlyings.

## Auth & demo mode

Set `NASDAQ_DATA_LINK_API_KEY` for live Tables API pulls.

Without a key, `packages/market-data` serves a **deterministic mock surface** shaped like QQQ / mega-cap tech skew so agents can run offline.

## Mapping surface → model

| Market field | Model parameter |
| --- | --- |
| spot / `stockpx` | \(S_0\) |
| `iv30`² | near-term variance / \(\xi_0(30d)\) |
| `iv60`, `iv90` | forward variance curve knots |
| skew `slope` | rough Bergomi \(\eta,\rho\) / Heston \(\rho,\xi\) |
| hist vol | realized vol target / Hurst estimation input |

Hurst \(H\) is estimated from log realized-vol increments when history is available; otherwise default \(H = 0.1\).
