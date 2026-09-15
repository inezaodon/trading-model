# Rough Volatility — NASDAQ-style IV surface parameters

This project maps **NASDAQ Data Link / ORATS-style** constant-maturity implied
vol summaries into the rough Bergomi forward variance curve \(\xi_0(t)\).

## Fields used

| Field | Role in rough Bergomi |
| --- | --- |
| `iv30`, `iv60`, `iv90` | Knots for \(\xi_0(t)\) via total variance \(w(T)=\mathrm{IV}(T)^2 T\) |
| `slope` | Skew intensity → \(\eta\) (roughness) and \(\rho\) (leverage) |
| spot / `stockpx` | \(S_0\) |
| hist vol (optional) | realized-vol target; default Hurst \(H = 0.1\) if unavailable |

Year fractions use ACT/365: \(T_{30}=30/365\), \(T_{60}=60/365\), \(T_{90}=90/365\).

## Default mock (QQQ-like)

Offline demos use a deterministic mock surface:

```json
{
  "symbol": "QQQ",
  "iv30": 0.22,
  "iv60": 0.21,
  "iv90": 0.20,
  "slope": -1.5,
  "s0": 450.0
}
```

Negative `slope` → negative \(\rho\) (leverage effect documented on Nasdaq-100
asymmetric SV studies). Default \(H \approx 0.1\) follows Gatheral–Jaisson–Rosenbaum.

## CLI

```bash
rough-vol calibrate --iv30 0.22 --iv60 0.21 --iv90 0.20 --slope -1.5 --s0 450
rough-vol run --from-iv --iv30 0.22 --iv60 0.21 --iv90 0.20 --slope -1.5 --seed 42
```

## External references

- [NASDAQ Data Link – Option Volatility Surfaces](https://data.nasdaq.com/databases/OPT)
- [NASDAQ Greeks and Vols specification](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/GreeksandVols_Specification.pdf)
- Umbrella docs: `docs/NASDAQ_DATA.md`
