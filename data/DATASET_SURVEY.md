# Dataset Survey — Trading Model Umbrella

**Generated (UTC):** 2026-09-15 01:11:49
**Candidates evaluated:** 201
**OK / failed:** 199 / 2
**Sources:** Yahoo Finance (`yfinance`), Treasury.gov daily yield CSV, derived pairs spreads

> Educational / research datasets only — not investment advice.

## Scoring rubric (reiterated)

| Component | Weight | Definition |
| --- | --- | --- |
| Liquidity | 0.35 | `log10(avg_volume)` scaled to 0–100; FX/rates/Treasury use category baselines when volume is absent |
| History length | 0.40 | `min(100, history_years / 10 * 100)` — 10+ years full marks |
| Completeness | 0.25 | `max(0, 100 - missing_pct * 5)` — penalizes NaNs |
| **Total** | 1.00 | Weighted sum |

**Suitability tags** (multi-label):

- `gbm` / `heston` / `rough-vol` / `mc-options` — liquid equities & ETFs with ≥5y clean history
- `ou` — rates, Treasury curve, FX, SOFR-proxy ETFs, pairs log-spreads
- `var` — diversified liquid ETFs for portfolio VaR
- `brownian` — synthetic Wiener primary; optional real residual paths

## Top picks per project

### `gbm` — Geometric Brownian Motion Stock Price Simulator

| Rank | Ticker | Score | Years | Avg volume | Missing % | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `QQQ` | 98.32 | 27.51 | 64,578,586 | 0.014 | Liquid equity/ETF with long clean history for μ,σ calibration |
| 2 | `AAPL` | 99.99 | 45.75 | 305,788,463 | 0.009 | Liquid equity/ETF with long clean history for μ,σ calibration |
| 3 | `MSFT` | 97.73 | 40.5 | 55,186,924 | 0.01 | Liquid equity/ETF with long clean history for μ,σ calibration |
| 4 | `NVDA` | 99.98 | 27.64 | 575,778,940 | 0.014 | Liquid equity/ETF with long clean history for μ,σ calibration |
| 5 | `AMZN` | 99.98 | 29.33 | 131,316,911 | 0.014 | Liquid equity/ETF with long clean history for μ,σ calibration |
| 6 | `META` | 95.1 | 14.32 | 27,779,519 | 0.028 | Liquid equity/ETF with long clean history for μ,σ calibration |
| 7 | `GOOGL` | 99.98 | 22.07 | 109,373,084 | 0.018 | Liquid equity/ETF with long clean history for μ,σ calibration |
| 8 | `TSLA` | 99.77 | 16.21 | 94,863,031 | 0.025 | Liquid equity/ETF with long clean history for μ,σ calibration |

### `mc-options` — Monte Carlo Option Pricing

| Rank | Ticker | Score | Years | Avg volume | Missing % | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `QQQ` | 98.32 | 27.51 | 64,578,586 | 0.014 | Liquid underlying for EU call/put Monte Carlo; use risk-free from Treasury/SOFR proxy |
| 2 | `AAPL` | 99.99 | 45.75 | 305,788,463 | 0.009 | Liquid underlying for EU call/put Monte Carlo; use risk-free from Treasury/SOFR proxy |
| 3 | `MSFT` | 97.73 | 40.5 | 55,186,924 | 0.01 | Liquid underlying for EU call/put Monte Carlo; use risk-free from Treasury/SOFR proxy |
| 4 | `NVDA` | 99.98 | 27.64 | 575,778,940 | 0.014 | Liquid underlying for EU call/put Monte Carlo; use risk-free from Treasury/SOFR proxy |
| 5 | `AMZN` | 99.98 | 29.33 | 131,316,911 | 0.014 | Liquid underlying for EU call/put Monte Carlo; use risk-free from Treasury/SOFR proxy |
| 6 | `META` | 95.1 | 14.32 | 27,779,519 | 0.028 | Liquid underlying for EU call/put Monte Carlo; use risk-free from Treasury/SOFR proxy |

### `brownian` — Brownian Motion & Random Walk Visualizer

| Rank | Ticker | Score | Years | Avg volume | Missing % | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `SYNTHETIC_WIENER` | 100.0 | — | — | — | Visualizer core path; market residuals optional for comparison |
| 2 | `QQQ` | 98.32 | 27.51 | 64,578,586 | 0.014 | Optional real residual / return path for comparison to Wiener |
| 3 | `SPY` | 99.27 | 33.62 | 82,888,984 | 0.012 | Optional real residual / return path for comparison to Wiener |
| 4 | `AAPL` | 99.99 | 45.75 | 305,788,463 | 0.009 | Optional real residual / return path for comparison to Wiener |

### `ou` — Ornstein–Uhlenbeck Mean Reversion

| Rank | Ticker | Score | Years | Avg volume | Missing % | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `KO-PEP` | 77.25 | 54.28 | — | 0.0 | Mean-reverting candidate (rates, FX, or pairs log-spread) for OU κ,θ,σ estimation |
| 2 | `XOM-CVX` | 77.25 | 64.69 | — | 0.0 | Mean-reverting candidate (rates, FX, or pairs log-spread) for OU κ,θ,σ estimation |
| 3 | `MSFT-AAPL` | 77.25 | 40.5 | — | 0.0 | Mean-reverting candidate (rates, FX, or pairs log-spread) for OU κ,θ,σ estimation |
| 4 | `GDX-GLD` | 77.25 | 20.31 | — | 0.0 | Mean-reverting candidate (rates, FX, or pairs log-spread) for OU κ,θ,σ estimation |
| 5 | `UST_YIELD_CURVE` | 93.0 | 11.7 | — | 0.0 | Mean-reverting candidate (rates, FX, or pairs log-spread) for OU κ,θ,σ estimation |
| 6 | `^TNX` | 65.0 | 64.7 | 405 | 0.0 | Mean-reverting candidate (rates, FX, or pairs log-spread) for OU κ,θ,σ estimation |
| 7 | `HYG-LQD` | 77.25 | 19.42 | — | 0.0 | Mean-reverting candidate (rates, FX, or pairs log-spread) for OU κ,θ,σ estimation |
| 8 | `IWM-SPY` | 77.25 | 26.29 | — | 0.0 | Mean-reverting candidate (rates, FX, or pairs log-spread) for OU κ,θ,σ estimation |

### `heston` — Heston Stochastic Volatility Simulator

| Rank | Ticker | Score | Years | Avg volume | Missing % | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `QQQ` | 98.32 | 27.51 | 64,578,586 | 0.014 | Equity with leverage/vol clustering for Heston v0,κ,θ,ξ,ρ calibration |
| 2 | `AAPL` | 99.99 | 45.75 | 305,788,463 | 0.009 | Equity with leverage/vol clustering for Heston v0,κ,θ,ξ,ρ calibration |
| 3 | `MSFT` | 97.73 | 40.5 | 55,186,924 | 0.01 | Equity with leverage/vol clustering for Heston v0,κ,θ,ξ,ρ calibration |
| 4 | `NVDA` | 99.98 | 27.64 | 575,778,940 | 0.014 | Equity with leverage/vol clustering for Heston v0,κ,θ,ξ,ρ calibration |
| 5 | `AMZN` | 99.98 | 29.33 | 131,316,911 | 0.014 | Equity with leverage/vol clustering for Heston v0,κ,θ,ξ,ρ calibration |
| 6 | `META` | 95.1 | 14.32 | 27,779,519 | 0.028 | Equity with leverage/vol clustering for Heston v0,κ,θ,ξ,ρ calibration |

### `var` — Monte Carlo Value-at-Risk Engine

| Rank | Ticker | Score | Years | Avg volume | Missing % | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `QQQ` | 98.32 | 27.51 | 64,578,586 | 0.014 | Diversified liquid ETF sleeve for multi-asset Monte Carlo VaR portfolio |
| 2 | `SPY` | 99.27 | 33.62 | 82,888,984 | 0.012 | Diversified liquid ETF sleeve for multi-asset Monte Carlo VaR portfolio |
| 3 | `IWM` | 96.03 | 26.3 | 35,323,069 | 0.015 | Diversified liquid ETF sleeve for multi-asset Monte Carlo VaR portfolio |
| 4 | `TLT` | 91.73 | 24.13 | 11,392,823 | 0.016 | Diversified liquid ETF sleeve for multi-asset Monte Carlo VaR portfolio |
| 5 | `GLD` | 91.07 | 21.82 | 9,592,478 | 0.018 | Diversified liquid ETF sleeve for multi-asset Monte Carlo VaR portfolio |
| 6 | `HYG` | 93.17 | 19.43 | 16,675,131 | 0.02 | Diversified liquid ETF sleeve for multi-asset Monte Carlo VaR portfolio |
| 7 | `IEF` | 86.73 | 24.13 | 3,060,792 | 0.016 | Diversified liquid ETF sleeve for multi-asset Monte Carlo VaR portfolio |
| 8 | `EEM` | 97.08 | 23.42 | 46,652,766 | 0.017 | Diversified liquid ETF sleeve for multi-asset Monte Carlo VaR portfolio |

### `rough-vol` — Rough Volatility (Rough Bergomi) Simulator

| Rank | Ticker | Score | Years | Avg volume | Missing % | Why |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `QQQ` | 98.32 | 27.51 | 64,578,586 | 0.014 | High-liquidity equity/ETF for realized-vol roughness / Hurst estimation |
| 2 | `AAPL` | 99.99 | 45.75 | 305,788,463 | 0.009 | High-liquidity equity/ETF for realized-vol roughness / Hurst estimation |
| 3 | `MSFT` | 97.73 | 40.5 | 55,186,924 | 0.01 | High-liquidity equity/ETF for realized-vol roughness / Hurst estimation |
| 4 | `NVDA` | 99.98 | 27.64 | 575,778,940 | 0.014 | High-liquidity equity/ETF for realized-vol roughness / Hurst estimation |
| 5 | `AMZN` | 99.98 | 29.33 | 131,316,911 | 0.014 | High-liquidity equity/ETF for realized-vol roughness / Hurst estimation |
| 6 | `META` | 95.1 | 14.32 | 27,779,519 | 0.028 | High-liquidity equity/ETF for realized-vol roughness / Hurst estimation |

## Category coverage

| Category | Count |
| --- | --- |
| commodity_crypto | 14 |
| commodity_etf | 2 |
| etf | 46 |
| fx | 11 |
| liquid_equity | 28 |
| nasdaq100_equity | 81 |
| pairs_spread | 8 |
| rates | 10 |
| rates_treasury | 1 |

## Full ranked table (OK only)

| Rank | Ticker | Category | Score | Liq | Hist | Comp | Years | Avg vol | Miss% | N | Tags | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `BTC-USD` | commodity_crypto | 100.0 | 100.0 | 100.0 | 100.0 | 11.99 | 22,418,011,230 | 0.0 | 4381 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 2 | `AAPL` | nasdaq100_equity | 99.99 | 100.0 | 100.0 | 99.95 | 45.75 | 305,788,463 | 0.009 | 11529 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 3 | `NVDA` | nasdaq100_equity | 99.98 | 100.0 | 100.0 | 99.93 | 27.64 | 575,778,940 | 0.014 | 6952 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 4 | `AMZN` | nasdaq100_equity | 99.98 | 100.0 | 100.0 | 99.93 | 29.33 | 131,316,911 | 0.014 | 7377 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 5 | `GOOGL` | nasdaq100_equity | 99.98 | 100.0 | 100.0 | 99.91 | 22.07 | 109,373,084 | 0.018 | 5551 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 6 | `GOOG` | nasdaq100_equity | 99.98 | 100.0 | 100.0 | 99.91 | 22.07 | 106,734,511 | 0.018 | 5551 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 7 | `NFLX` | nasdaq100_equity | 99.98 | 100.0 | 100.0 | 99.92 | 24.31 | 145,822,678 | 0.016 | 6115 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 8 | `TSLA` | nasdaq100_equity | 99.77 | 99.43 | 100.0 | 99.88 | 16.21 | 94,863,031 | 0.025 | 4076 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 9 | `SPY` | etf | 99.27 | 97.96 | 100.0 | 99.94 | 33.62 | 82,888,984 | 0.012 | 8462 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 10 | `QQQ` | etf | 98.32 | 95.25 | 100.0 | 99.93 | 27.51 | 64,578,586 | 0.014 | 6920 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 11 | `MSFT` | nasdaq100_equity | 97.73 | 93.55 | 100.0 | 99.95 | 40.5 | 55,186,924 | 0.01 | 10203 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 12 | `XLF` | etf | 97.7 | 93.47 | 100.0 | 99.93 | 27.73 | 54,799,061 | 0.014 | 6972 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 13 | `INTC` | nasdaq100_equity | 97.55 | 93.04 | 100.0 | 99.95 | 46.49 | 52,683,889 | 0.009 | 11717 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 14 | `CSCO` | nasdaq100_equity | 97.38 | 92.57 | 100.0 | 99.94 | 36.57 | 50,423,670 | 0.011 | 9208 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 15 | `EEM` | etf | 97.08 | 91.72 | 100.0 | 99.92 | 23.42 | 46,652,766 | 0.017 | 5891 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 16 | `BAC` | liquid_equity | 96.38 | 89.69 | 100.0 | 99.97 | 53.56 | 38,695,541 | 0.007 | 13503 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 17 | `IWM` | etf | 96.03 | 88.7 | 100.0 | 99.92 | 26.3 | 35,323,069 | 0.015 | 6612 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 18 | `XLE` | etf | 95.65 | 87.63 | 100.0 | 99.93 | 27.73 | 32,011,716 | 0.014 | 6972 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 19 | `ETH-USD` | commodity_crypto | 95.4 | 100.0 | 88.5 | 100.0 | 8.85 | 15,108,160,711 | 0.0 | 3232 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 20 | `GDX` | commodity_etf | 95.12 | 86.13 | 100.0 | 99.9 | 20.31 | 27,882,369 | 0.02 | 5109 | brownian | ok |
| 21 | `META` | nasdaq100_equity | 95.1 | 86.09 | 100.0 | 99.86 | 14.32 | 27,779,519 | 0.028 | 3599 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 22 | `KLAC` | nasdaq100_equity | 94.91 | 85.49 | 100.0 | 99.95 | 45.93 | 26,268,595 | 0.009 | 11574 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 23 | `AVGO` | nasdaq100_equity | 94.8 | 85.21 | 100.0 | 99.89 | 17.11 | 25,598,180 | 0.023 | 4301 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 24 | `WMT` | liquid_equity | 94.31 | 83.77 | 100.0 | 99.97 | 54.05 | 22,425,847 | 0.007 | 13623 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 25 | `T` | liquid_equity | 94.14 | 83.3 | 100.0 | 99.95 | 42.81 | 21,482,761 | 0.009 | 10785 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 26 | `LRCX` | nasdaq100_equity | 94.07 | 83.09 | 100.0 | 99.95 | 42.36 | 21,067,733 | 0.009 | 10671 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 27 | `AMD` | nasdaq100_equity | 93.96 | 82.79 | 100.0 | 99.95 | 46.49 | 20,486,613 | 0.009 | 11717 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 28 | `CSX` | nasdaq100_equity | 93.59 | 81.73 | 100.0 | 99.95 | 45.86 | 18,580,664 | 0.009 | 11556 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 29 | `AMAT` | nasdaq100_equity | 93.33 | 80.97 | 100.0 | 99.95 | 46.49 | 17,327,659 | 0.009 | 11717 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 30 | `BKNG` | nasdaq100_equity | 93.33 | 81.0 | 100.0 | 99.93 | 27.46 | 17,379,563 | 0.014 | 6905 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 31 | `XLU` | etf | 93.29 | 80.88 | 100.0 | 99.93 | 27.73 | 17,186,651 | 0.014 | 6972 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 32 | `QCOM` | nasdaq100_equity | 93.26 | 80.79 | 100.0 | 99.94 | 34.75 | 17,039,864 | 0.011 | 8747 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 33 | `SLV` | etf | 93.25 | 80.78 | 100.0 | 99.9 | 20.38 | 17,021,956 | 0.02 | 5125 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 34 | `HYG` | etf | 93.17 | 80.55 | 100.0 | 99.9 | 19.43 | 16,675,131 | 0.02 | 4887 | brownian,gbm,heston,mc-options,ou,rough-vol,var | ok |
| 35 | `MU` | nasdaq100_equity | 93.16 | 80.48 | 100.0 | 99.95 | 42.29 | 16,565,296 | 0.009 | 10652 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 36 | `EFA` | etf | 93.13 | 80.44 | 100.0 | 99.92 | 25.05 | 16,498,459 | 0.016 | 6297 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 37 | `CMCSA` | nasdaq100_equity | 93.12 | 80.39 | 100.0 | 99.95 | 46.49 | 16,432,870 | 0.009 | 11717 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 38 | `UST_YIELD_CURVE` | rates_treasury | 93.0 | 80.0 | 100.0 | 100.0 | 11.7 | — | 0.0 | 2926 | brownian,ou | ok |
| 39 | `SHOP` | liquid_equity | 92.92 | 79.89 | 100.0 | 99.83 | 11.32 | 15,692,213 | 0.035 | 2845 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 40 | `SMH` | etf | 92.73 | 79.29 | 100.0 | 99.92 | 26.28 | 14,851,127 | 0.015 | 6607 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 41 | `SBUX` | nasdaq100_equity | 92.61 | 78.94 | 100.0 | 99.94 | 34.22 | 14,372,970 | 0.012 | 8612 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 42 | `GILD` | nasdaq100_equity | 92.47 | 78.54 | 100.0 | 99.94 | 34.64 | 13,849,416 | 0.011 | 8721 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 43 | `V` | liquid_equity | 92.45 | 78.5 | 100.0 | 99.89 | 18.49 | 13,800,365 | 0.022 | 4650 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 44 | `XLK` | etf | 92.37 | 78.24 | 100.0 | 99.93 | 27.73 | 13,475,515 | 0.014 | 6972 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 45 | `NKE` | liquid_equity | 91.91 | 76.91 | 100.0 | 99.95 | 45.78 | 11,920,385 | 0.009 | 11537 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 46 | `JPM` | liquid_equity | 91.88 | 76.83 | 100.0 | 99.95 | 46.49 | 11,833,094 | 0.009 | 11717 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 47 | `VWO` | etf | 91.86 | 76.82 | 100.0 | 99.91 | 21.51 | 11,825,644 | 0.018 | 5411 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 48 | `TLT` | etf | 91.73 | 76.42 | 100.0 | 99.92 | 24.13 | 11,392,823 | 0.016 | 6069 | brownian,gbm,heston,mc-options,ou,rough-vol,var | ok |
| 49 | `XLB` | etf | 91.71 | 76.37 | 100.0 | 99.93 | 27.73 | 11,347,073 | 0.014 | 6972 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 50 | `PYPL` | nasdaq100_equity | 91.66 | 76.3 | 100.0 | 99.82 | 11.19 | 11,269,403 | 0.036 | 2814 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 51 | `MRVL` | nasdaq100_equity | 91.63 | 76.13 | 100.0 | 99.92 | 26.21 | 11,101,222 | 0.015 | 6588 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 52 | `ORLY` | nasdaq100_equity | 91.57 | 75.96 | 100.0 | 99.94 | 33.39 | 10,922,739 | 0.012 | 8404 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 53 | `VZ` | liquid_equity | 91.27 | 75.09 | 100.0 | 99.95 | 42.81 | 10,085,693 | 0.009 | 10785 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 54 | `MA` | liquid_equity | 91.25 | 75.08 | 100.0 | 99.9 | 20.31 | 10,074,362 | 0.02 | 5106 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 55 | `TTD` | nasdaq100_equity | 91.18 | 75.16 | 99.8 | 99.8 | 9.98 | 10,151,565 | 0.04 | 2507 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 56 | `XOM` | liquid_equity | 91.13 | 74.67 | 100.0 | 99.97 | 64.7 | 9,701,541 | 0.006 | 16282 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 57 | `GLD` | etf | 91.07 | 74.55 | 100.0 | 99.91 | 21.82 | 9,592,478 | 0.018 | 5487 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 58 | `KO` | liquid_equity | 91.05 | 74.44 | 100.0 | 99.97 | 64.7 | 9,493,820 | 0.006 | 16282 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 59 | `FAST` | nasdaq100_equity | 90.58 | 73.13 | 100.0 | 99.95 | 39.07 | 8,417,205 | 0.01 | 9839 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 60 | `FTNT` | nasdaq100_equity | 90.55 | 73.08 | 100.0 | 99.88 | 16.82 | 8,377,854 | 0.024 | 4228 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 61 | `XLY` | etf | 90.54 | 73.01 | 100.0 | 99.93 | 27.73 | 8,325,320 | 0.014 | 6972 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 62 | `TXN` | nasdaq100_equity | 90.53 | 72.97 | 100.0 | 99.97 | 54.29 | 8,293,615 | 0.007 | 13683 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 63 | `PANW` | nasdaq100_equity | 90.52 | 73.02 | 100.0 | 99.86 | 14.15 | 8,334,512 | 0.028 | 3556 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 64 | `XLI` | etf | 90.52 | 72.97 | 100.0 | 99.93 | 27.73 | 8,292,895 | 0.014 | 6972 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 65 | `GDXJ` | commodity_etf | 90.29 | 72.35 | 100.0 | 99.88 | 16.84 | 7,834,458 | 0.024 | 4233 | brownian | ok |
| 66 | `LQD` | etf | 90.26 | 72.24 | 100.0 | 99.92 | 24.13 | 7,754,959 | 0.016 | 6069 | brownian,gbm,heston,mc-options,ou,rough-vol,var | ok |
| 67 | `VEA` | etf | 90.21 | 72.1 | 100.0 | 99.89 | 19.14 | 7,657,475 | 0.021 | 4813 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 68 | `AMGN` | nasdaq100_equity | 90.2 | 72.03 | 100.0 | 99.95 | 43.24 | 7,605,177 | 0.009 | 10894 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 69 | `MDLZ` | nasdaq100_equity | 90.18 | 72.01 | 100.0 | 99.92 | 25.25 | 7,594,482 | 0.016 | 6349 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 70 | `XLP` | etf | 90.02 | 71.53 | 100.0 | 99.93 | 27.73 | 7,262,138 | 0.014 | 6972 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 71 | `HD` | liquid_equity | 90.01 | 71.5 | 100.0 | 99.95 | 44.98 | 7,243,885 | 0.009 | 11334 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 72 | `CRM` | liquid_equity | 89.96 | 71.37 | 100.0 | 99.91 | 22.23 | 7,155,615 | 0.018 | 5591 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 73 | `IWF` | etf | 89.91 | 71.24 | 100.0 | 99.92 | 26.3 | 7,071,283 | 0.015 | 6612 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 74 | `KRE` | etf | 89.91 | 71.24 | 100.0 | 99.9 | 20.23 | 7,072,253 | 0.02 | 5087 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 75 | `ARKK` | etf | 89.89 | 71.24 | 100.0 | 99.83 | 11.87 | 7,072,089 | 0.034 | 2982 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 76 | `CPRT` | nasdaq100_equity | 89.87 | 71.09 | 100.0 | 99.94 | 32.49 | 6,978,208 | 0.012 | 8176 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 77 | `DIS` | liquid_equity | 89.64 | 70.43 | 100.0 | 99.97 | 64.7 | 6,561,809 | 0.006 | 16282 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 78 | `UNH` | liquid_equity | 89.63 | 70.4 | 100.0 | 99.95 | 41.91 | 6,543,979 | 0.009 | 10556 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 79 | `DIA` | etf | 89.55 | 70.2 | 100.0 | 99.93 | 28.65 | 6,424,887 | 0.014 | 7206 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 80 | `EURUSD=X` | fx | 89.5 | 70.0 | 100.0 | 100.0 | 22.79 | — | 0.0 | 5913 | brownian,ou | ok |
| 81 | `GBPUSD=X` | fx | 89.5 | 70.0 | 100.0 | 100.0 | 22.79 | — | 0.0 | 5925 | brownian,ou | ok |
| 82 | `USDJPY=X` | fx | 89.5 | 70.0 | 100.0 | 100.0 | 29.87 | — | 0.0 | 7747 | brownian,ou | ok |
| 83 | `AUDUSD=X` | fx | 89.5 | 70.0 | 100.0 | 100.0 | 20.33 | — | 0.0 | 5289 | brownian,ou | ok |
| 84 | `USDCAD=X` | fx | 89.5 | 70.0 | 100.0 | 100.0 | 23.0 | — | 0.0 | 5981 | brownian,ou | ok |
| 85 | `USDCHF=X` | fx | 89.5 | 70.0 | 100.0 | 100.0 | 23.0 | — | 0.0 | 5979 | brownian,ou | ok |
| 86 | `NZDUSD=X` | fx | 89.5 | 70.0 | 100.0 | 100.0 | 22.79 | — | 0.0 | 5914 | brownian,ou | ok |
| 87 | `EURGBP=X` | fx | 89.5 | 70.0 | 100.0 | 100.0 | 27.69 | — | 0.0 | 7213 | brownian,ou | ok |
| 88 | `EURJPY=X` | fx | 89.5 | 70.0 | 100.0 | 100.0 | 23.64 | — | 0.0 | 6138 | brownian,ou | ok |
| 89 | `GBPJPY=X` | fx | 89.5 | 70.0 | 100.0 | 100.0 | 22.79 | — | 0.0 | 5929 | brownian,ou | ok |
| 90 | `ADBE` | nasdaq100_equity | 89.46 | 69.91 | 100.0 | 99.95 | 40.09 | 6,257,893 | 0.01 | 10097 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 91 | `XLV` | etf | 89.42 | 69.81 | 100.0 | 99.93 | 27.73 | 6,199,361 | 0.014 | 6972 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 92 | `ON` | nasdaq100_equity | 89.32 | 69.54 | 100.0 | 99.92 | 26.37 | 6,049,671 | 0.015 | 6630 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 93 | `JNJ` | liquid_equity | 89.14 | 68.99 | 100.0 | 99.97 | 64.7 | 5,750,446 | 0.006 | 16282 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 94 | `CTSH` | nasdaq100_equity | 89.05 | 68.77 | 100.0 | 99.93 | 28.24 | 5,634,652 | 0.014 | 7101 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 95 | `ROST` | nasdaq100_equity | 89.03 | 68.7 | 100.0 | 99.95 | 41.1 | 5,599,704 | 0.01 | 10352 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 96 | `PG` | liquid_equity | 88.76 | 67.9 | 100.0 | 99.97 | 64.7 | 5,198,148 | 0.006 | 16282 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 97 | `IBM` | liquid_equity | 88.68 | 67.68 | 100.0 | 99.97 | 64.7 | 5,097,827 | 0.006 | 16282 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 98 | `GS` | liquid_equity | 88.42 | 66.98 | 100.0 | 99.92 | 27.36 | 4,779,477 | 0.015 | 6882 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 99 | `XLRE` | etf | 88.39 | 66.97 | 100.0 | 99.82 | 10.93 | 4,774,177 | 0.036 | 2747 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 100 | `KDP` | nasdaq100_equity | 88.14 | 66.19 | 100.0 | 99.89 | 18.35 | 4,443,697 | 0.022 | 4616 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 101 | `XBI` | etf | 88.12 | 66.11 | 100.0 | 99.91 | 20.6 | 4,409,522 | 0.019 | 5182 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 102 | `PEP` | nasdaq100_equity | 88.03 | 65.82 | 100.0 | 99.97 | 54.29 | 4,291,966 | 0.007 | 13683 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 103 | `MCD` | liquid_equity | 87.99 | 65.71 | 100.0 | 99.97 | 60.19 | 4,249,023 | 0.007 | 15147 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 104 | `CVX` | liquid_equity | 87.94 | 65.57 | 100.0 | 99.97 | 64.7 | 4,194,195 | 0.006 | 16282 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 105 | `TMUS` | nasdaq100_equity | 87.77 | 65.14 | 100.0 | 99.9 | 19.41 | 4,032,121 | 0.02 | 4881 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 106 | `JNK` | etf | 87.77 | 65.14 | 100.0 | 99.89 | 18.78 | 4,032,205 | 0.021 | 4722 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 107 | `EXC` | nasdaq100_equity | 87.62 | 64.66 | 100.0 | 99.97 | 53.37 | 3,859,883 | 0.007 | 13454 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 108 | `BA` | liquid_equity | 87.55 | 64.45 | 100.0 | 99.97 | 64.7 | 3,783,617 | 0.006 | 16282 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 109 | `ISRG` | nasdaq100_equity | 87.51 | 64.38 | 100.0 | 99.92 | 26.25 | 3,759,756 | 0.015 | 6598 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 110 | `BKR` | nasdaq100_equity | 87.49 | 64.28 | 100.0 | 99.95 | 39.44 | 3,724,327 | 0.01 | 9934 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 111 | `USO` | etf | 87.25 | 63.63 | 100.0 | 99.91 | 20.43 | 3,508,382 | 0.019 | 5138 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 112 | `VNQ` | etf | 87.13 | 63.3 | 100.0 | 99.91 | 21.96 | 3,405,410 | 0.018 | 5523 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 113 | `XOP` | etf | 87.05 | 63.08 | 100.0 | 99.9 | 20.23 | 3,336,866 | 0.02 | 5087 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 114 | `VOO` | etf | 87.04 | 63.06 | 100.0 | 99.88 | 16.01 | 3,329,580 | 0.025 | 4026 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 115 | `INTU` | nasdaq100_equity | 87.03 | 63.0 | 100.0 | 99.94 | 33.51 | 3,310,855 | 0.012 | 8433 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 116 | `AGG` | etf | 87.02 | 62.96 | 100.0 | 99.92 | 22.96 | 3,299,134 | 0.017 | 5775 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 117 | `BND` | etf | 86.92 | 62.71 | 100.0 | 99.9 | 19.43 | 3,222,799 | 0.02 | 4888 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 118 | `CAT` | liquid_equity | 86.78 | 62.24 | 100.0 | 99.97 | 64.7 | 3,086,608 | 0.006 | 16282 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 119 | `IEF` | etf | 86.73 | 62.15 | 100.0 | 99.92 | 24.13 | 3,060,792 | 0.016 | 6069 | brownian,gbm,heston,mc-options,ou,rough-vol,var | ok |
| 120 | `DXCM` | nasdaq100_equity | 86.68 | 62.02 | 100.0 | 99.91 | 21.42 | 3,026,104 | 0.019 | 5387 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 121 | `NXPI` | nasdaq100_equity | 86.66 | 61.98 | 100.0 | 99.88 | 16.11 | 3,013,622 | 0.025 | 4049 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 122 | `EMB` | etf | 86.63 | 61.88 | 100.0 | 99.89 | 18.74 | 2,987,951 | 0.021 | 4711 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 123 | `COST` | nasdaq100_equity | 86.47 | 61.38 | 100.0 | 99.95 | 40.18 | 2,851,209 | 0.01 | 10122 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 124 | `IBB` | etf | 86.35 | 61.05 | 100.0 | 99.92 | 25.58 | 2,766,685 | 0.016 | 6433 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 125 | `ADSK` | nasdaq100_equity | 86.25 | 60.74 | 100.0 | 99.95 | 41.21 | 2,688,961 | 0.01 | 10380 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 126 | `PCAR` | nasdaq100_equity | 86.2 | 60.61 | 100.0 | 99.95 | 46.49 | 2,656,799 | 0.009 | 11717 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 127 | `MAR` | nasdaq100_equity | 86.17 | 60.53 | 100.0 | 99.93 | 28.48 | 2,637,572 | 0.014 | 7163 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 128 | `BIL` | rates | 86.02 | 60.15 | 100.0 | 99.89 | 19.29 | 2,547,000 | 0.021 | 4853 | brownian,ou | ok |
| 129 | `CTAS` | nasdaq100_equity | 85.92 | 59.8 | 100.0 | 99.95 | 43.07 | 2,465,801 | 0.009 | 10850 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 130 | `VTI` | etf | 85.87 | 59.68 | 100.0 | 99.92 | 25.25 | 2,439,973 | 0.016 | 6347 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 131 | `ADI` | nasdaq100_equity | 85.75 | 59.32 | 100.0 | 99.95 | 46.49 | 2,360,232 | 0.009 | 11717 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 132 | `BIIB` | nasdaq100_equity | 85.58 | 58.85 | 100.0 | 99.94 | 34.99 | 2,259,870 | 0.011 | 8809 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 133 | `PAYX` | nasdaq100_equity | 85.38 | 58.26 | 100.0 | 99.95 | 43.05 | 2,139,248 | 0.009 | 10845 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 134 | `HON` | nasdaq100_equity | 85.34 | 58.15 | 100.0 | 99.97 | 64.7 | 2,117,421 | 0.006 | 16282 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 135 | `UNG` | etf | 85.32 | 58.12 | 100.0 | 99.9 | 19.41 | 2,111,920 | 0.02 | 4882 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 136 | `WDAY` | nasdaq100_equity | 85.24 | 57.93 | 100.0 | 99.86 | 13.92 | 2,075,498 | 0.029 | 3497 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 137 | `ADP` | nasdaq100_equity | 85.23 | 57.83 | 100.0 | 99.95 | 46.49 | 2,055,901 | 0.009 | 11717 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 138 | `SHY` | etf | 85.21 | 57.8 | 100.0 | 99.92 | 24.13 | 2,050,298 | 0.016 | 6069 | brownian,gbm,heston,mc-options,ou,rough-vol,var | ok |
| 139 | `CDNS` | nasdaq100_equity | 85.18 | 57.69 | 100.0 | 99.95 | 39.26 | 2,030,512 | 0.01 | 9889 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 140 | `TEAM` | nasdaq100_equity | 84.9 | 57.0 | 100.0 | 99.81 | 10.76 | 1,905,812 | 0.037 | 2704 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 141 | `FANG` | nasdaq100_equity | 84.88 | 56.9 | 100.0 | 99.86 | 13.92 | 1,888,307 | 0.029 | 3497 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 142 | `DBC` | etf | 84.8 | 56.63 | 100.0 | 99.91 | 20.6 | 1,841,552 | 0.019 | 5182 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 143 | `IWD` | etf | 84.78 | 56.57 | 100.0 | 99.92 | 26.3 | 1,830,659 | 0.015 | 6612 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 144 | `SOXX` | etf | 84.63 | 56.13 | 100.0 | 99.92 | 25.17 | 1,757,956 | 0.016 | 6328 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 145 | `ASML` | nasdaq100_equity | 84.38 | 55.42 | 100.0 | 99.94 | 31.5 | 1,648,145 | 0.013 | 7926 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 146 | `USFR` | rates | 84.28 | 55.21 | 100.0 | 99.84 | 12.61 | 1,615,521 | 0.032 | 3170 | brownian,ou | ok |
| 147 | `CCEP` | nasdaq100_equity | 84.21 | 54.91 | 100.0 | 99.95 | 39.8 | 1,571,625 | 0.01 | 10025 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 148 | `SHV` | rates | 84.11 | 54.66 | 100.0 | 99.9 | 19.67 | 1,536,014 | 0.02 | 4948 | brownian,ou | ok |
| 149 | `ODFL` | nasdaq100_equity | 83.98 | 54.26 | 100.0 | 99.94 | 34.89 | 1,480,793 | 0.011 | 8782 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 150 | `XEL` | nasdaq100_equity | 83.91 | 54.06 | 100.0 | 99.97 | 53.56 | 1,452,858 | 0.007 | 13503 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 151 | `TIP` | etf | 83.88 | 53.99 | 100.0 | 99.92 | 22.77 | 1,444,763 | 0.017 | 5727 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 152 | `UBER` | liquid_equity | 83.79 | 84.17 | 73.5 | 99.73 | 7.35 | 23,269,291 | 0.054 | 1845 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 153 | `ES=F` | commodity_crypto | 83.75 | 53.58 | 100.0 | 100.0 | 25.99 | 1,389,974 | 0.0 | 6561 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 154 | `SNPS` | nasdaq100_equity | 83.55 | 53.05 | 100.0 | 99.94 | 34.55 | 1,324,091 | 0.011 | 8697 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 155 | `VRTX` | nasdaq100_equity | 83.54 | 53.02 | 100.0 | 99.94 | 35.14 | 1,320,104 | 0.011 | 8847 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 156 | `AEP` | nasdaq100_equity | 83.26 | 52.2 | 100.0 | 99.97 | 64.7 | 1,224,530 | 0.006 | 16282 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 157 | `CDW` | nasdaq100_equity | 82.31 | 49.55 | 100.0 | 99.85 | 13.22 | 959,124 | 0.03 | 3322 | brownian | ok |
| 158 | `VRSK` | nasdaq100_equity | 82.18 | 49.17 | 100.0 | 99.89 | 16.94 | 926,315 | 0.023 | 4258 | brownian | ok |
| 159 | `CRWD` | nasdaq100_equity | 82.13 | 80.46 | 72.6 | 99.72 | 7.26 | 16,540,030 | 0.055 | 1823 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 160 | `IDXX` | nasdaq100_equity | 81.9 | 48.34 | 100.0 | 99.94 | 35.23 | 858,413 | 0.011 | 8869 | brownian | ok |
| 161 | `PLTR` | liquid_equity | 81.63 | 94.04 | 59.5 | 99.67 | 5.95 | 57,732,451 | 0.067 | 1494 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 162 | `XLC` | etf | 81.44 | 67.26 | 82.4 | 99.76 | 8.24 | 4,903,424 | 0.048 | 2069 | brownian,gbm,heston,mc-options,rough-vol,var | ok |
| 163 | `ICSH` | rates | 80.81 | 45.28 | 100.0 | 99.84 | 12.74 | 647,301 | 0.031 | 3203 | brownian,ou | ok |
| 164 | `TFLO` | rates | 80.78 | 45.21 | 100.0 | 99.84 | 12.61 | 643,157 | 0.032 | 3170 | brownian,ou | ok |
| 165 | `MELI` | nasdaq100_equity | 80.53 | 44.45 | 100.0 | 99.89 | 19.1 | 599,731 | 0.021 | 4802 | brownian | ok |
| 166 | `REGN` | nasdaq100_equity | 80.37 | 43.95 | 100.0 | 99.94 | 35.45 | 572,550 | 0.011 | 8926 | brownian | ok |
| 167 | `SOFI` | liquid_equity | 79.73 | 91.6 | 56.9 | 99.65 | 5.69 | 46,120,620 | 0.07 | 1429 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 168 | `ZS` | nasdaq100_equity | 79.67 | 59.22 | 85.0 | 99.77 | 8.5 | 2,338,473 | 0.047 | 2134 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 169 | `NQ=F` | commodity_crypto | 78.52 | 38.62 | 100.0 | 100.0 | 25.99 | 350,609 | 0.0 | 6561 | brownian | ok |
| 170 | `CL=F` | commodity_crypto | 77.96 | 37.03 | 100.0 | 100.0 | 26.06 | 302,966 | 0.0 | 6542 | brownian | ok |
| 171 | `KO-PEP` | pairs_spread | 77.25 | 35.0 | 100.0 | 100.0 | 54.28 | — | 0.0 | 13683 | brownian,ou | ok |
| 172 | `XOM-CVX` | pairs_spread | 77.25 | 35.0 | 100.0 | 100.0 | 64.69 | — | 0.0 | 16282 | brownian,ou | ok |
| 173 | `MSFT-AAPL` | pairs_spread | 77.25 | 35.0 | 100.0 | 100.0 | 40.5 | — | 0.0 | 10203 | brownian,ou | ok |
| 174 | `GDX-GLD` | pairs_spread | 77.25 | 35.0 | 100.0 | 100.0 | 20.31 | — | 0.0 | 5109 | brownian,ou | ok |
| 175 | `HYG-LQD` | pairs_spread | 77.25 | 35.0 | 100.0 | 100.0 | 19.42 | — | 0.0 | 4887 | brownian,ou | ok |
| 176 | `IWM-SPY` | pairs_spread | 77.25 | 35.0 | 100.0 | 100.0 | 26.29 | — | 0.0 | 6612 | brownian,ou | ok |
| 177 | `XLK-XLF` | pairs_spread | 77.25 | 35.0 | 100.0 | 100.0 | 27.72 | — | 0.0 | 6972 | brownian,ou | ok |
| 178 | `EEM-EFA` | pairs_spread | 77.25 | 35.0 | 100.0 | 100.0 | 23.41 | — | 0.0 | 5891 | brownian,ou | ok |
| 179 | `YM=F` | commodity_crypto | 74.85 | 28.13 | 100.0 | 100.0 | 24.44 | 133,475 | 0.0 | 6152 | brownian | ok |
| 180 | `NG=F` | commodity_crypto | 74.03 | 25.81 | 100.0 | 100.0 | 26.04 | 107,737 | 0.0 | 6539 | brownian | ok |
| 181 | `SGOV` | rates | 73.99 | 68.32 | 62.9 | 99.69 | 6.29 | 5,402,982 | 0.063 | 1579 | brownian,ou | ok |
| 182 | `ZC=F` | commodity_crypto | 73.48 | 24.24 | 100.0 | 100.0 | 26.16 | 93,218 | 0.0 | 6545 | brownian | ok |
| 183 | `COIN` | liquid_equity | 73.15 | 75.89 | 54.2 | 99.64 | 5.42 | 10,852,775 | 0.073 | 1360 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 184 | `RTY=F` | commodity_crypto | 72.56 | 30.97 | 91.8 | 100.0 | 9.18 | 173,281 | 0.0 | 2311 | brownian | ok |
| 185 | `ABNB` | nasdaq100_equity | 72.05 | 68.85 | 57.6 | 99.66 | 5.76 | 5,674,137 | 0.069 | 1444 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 186 | `ZS=F` | commodity_crypto | 71.36 | 18.18 | 100.0 | 100.0 | 26.0 | 53,379 | 0.0 | 6537 | brownian | ok |
| 187 | `DASH` | nasdaq100_equity | 71.02 | 65.89 | 57.6 | 99.66 | 5.76 | 4,321,577 | 0.069 | 1445 | brownian,gbm,heston,mc-options,rough-vol | ok |
| 188 | `ZW=F` | commodity_crypto | 69.69 | 13.4 | 100.0 | 100.0 | 26.16 | 34,341 | 0.0 | 6557 | brownian | ok |
| 189 | `GFS` | nasdaq100_equity | 65.19 | 59.35 | 48.8 | 99.59 | 4.88 | 2,366,399 | 0.082 | 1222 | brownian | ok |
| 190 | `^TNX` | rates | 65.0 | 0.0 | 100.0 | 100.0 | 64.7 | 405 | 0.0 | 16162 | brownian,ou | ok |
| 191 | `^IRX` | rates | 65.0 | 0.0 | 100.0 | 100.0 | 66.69 | 421 | 0.0 | 16659 | brownian,ou | ok |
| 192 | `^TYX` | rates | 65.0 | 0.0 | 100.0 | 100.0 | 49.57 | 553 | 0.0 | 12420 | brownian,ou | ok |
| 193 | `^FVX` | rates | 65.0 | 0.0 | 100.0 | 100.0 | 64.7 | 419 | 0.0 | 16162 | brownian,ou | ok |
| 194 | `DX-Y.NYB` | fx | 65.0 | 0.0 | 100.0 | 100.0 | 55.69 | 1,647 | 0.0 | 14142 | brownian,ou | ok |
| 195 | `GC=F` | commodity_crypto | 65.0 | 0.0 | 100.0 | 100.0 | 26.04 | 4,284 | 0.0 | 6533 | brownian | ok |
| 196 | `SI=F` | commodity_crypto | 65.0 | 0.0 | 100.0 | 100.0 | 26.04 | 1,442 | 0.0 | 6535 | brownian | ok |
| 197 | `HG=F` | commodity_crypto | 65.0 | 0.0 | 100.0 | 100.0 | 26.04 | 1,301 | 0.0 | 6538 | brownian | ok |
| 198 | `GEHC` | nasdaq100_equity | 62.06 | 63.41 | 37.5 | 99.47 | 3.75 | 3,439,282 | 0.107 | 937 | brownian | ok |
| 199 | `EA` | nasdaq100_equity | 51.03 | 73.57 | 0.7 | 100.0 | 0.07 | 8,766,120 | 0.0 | 6 | — | ok |

## Failures / incomplete

| Ticker | Category | Status | Error |
| --- | --- | --- | --- |
| `ANSS` | nasdaq100_equity | empty | no rows |
| `SQ` | liquid_equity | empty | no rows |

## Method notes

1. Built ~150 tickers across NASDAQ-100 names, broad ETFs, Treasury/SOFR proxies, FX, commodities/crypto, plus derived pairs spreads.
2. Fetched `period=max` via `yfinance` (fallback `10y`); Treasury.gov CSV for the full par yield curve.
3. Pair spreads: `log(A) - log(B)` on intersecting calendars.
4. Winners favor PROGRESS.md hypotheses, then fill by total score + tag fit.
5. Small CSV tails (60 rows) cached under `data/selected/` for offline demos.

## Manifest

Machine-readable winners: [`data/selected/manifest.json`](selected/manifest.json)

