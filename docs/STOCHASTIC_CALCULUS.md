# Modern Stochastic Calculus for Trading Models

This document captures the mathematical foundations used in this repository and why each layer exists.

## 1. Classical Itô calculus (baseline)

Asset prices under Black–Scholes / GBM:

\[
dS_t = \mu S_t\,dt + \sigma S_t\,dW_t
\]

Itô's lemma for \(f(t,S)\):

\[
df = \bigl(f_t + \mu S f_S + \tfrac12\sigma^2 S^2 f_{SS}\bigr)dt + \sigma S f_S\,dW
\]

**Trading use:** delta-hedging, log-return simulation, Monte Carlo baselines.

**Limitation:** constant \(\sigma\) cannot produce realistic equity smiles or clustered volatility.

## 2. Markov stochastic volatility (Heston / SABR family)

Heston:

\[
\begin{aligned}
dS_t &= \mu S_t\,dt + \sqrt{v_t}\,S_t\,dW^S_t \\
dv_t &= \kappa(\theta - v_t)\,dt + \xi\sqrt{v_t}\,dW^v_t \\
d\langle W^S, W^v\rangle_t &= \rho\,dt
\end{aligned}
\]

SABR / local-stochastic volatility add local vol factors for smile shape.

**Trading use:** option pricing via Fourier / PDE, vol-of-vol risk, correlation (leverage) \(\rho < 0\) common for equities and Nasdaq-100 constituents.

**Limitation:** Markovian variance paths are typically too smooth (\(H = 1/2\)) to match the **steep short-maturity skew** seen on equity index options.

## 3. Rough volatility (current research standard)

Empirical realized volatility behaves like fractional Brownian motion with Hurst \(H \approx 0.1\) (Gatheral–Jaisson–Rosenbaum). Rough models replace Markov variance with Volterra / fractional kernels.

### Rough Bergomi (sketch)

\[
v_t = \xi_0(t)\exp\Bigl(\eta\sqrt{2H}\,Z_t - \tfrac12\eta^2 t^{2H}\Bigr)
\]

where \(Z\) is a Riemann–Liouville / Mandelbrot–Van Ness type fractional Gaussian noise and \(\xi_0\) is the forward variance curve.

### Rough Heston

Variance driven by a fractional kernel (Mittag–Leffler / power-law), with characteristic function via a **fractional Riccati ODE** — Fourier pricing remains available.

### Why traders care

- Fits short-tenor implied vol skew with few parameters
- Consistent with high-frequency microstructure (Hawkes → rough Heston limit)
- Better alignment with surfaces like SPX / Nasdaq-linked options than classical Heston alone

### Numerical caveats

- Non-Markovian → classical PDEs fail; use Monte Carlo (hybrid / Cholesky schemes), Markovian lifts, or rough PDEs
- Stock price often lacks a clean Stratonovich form when \([V,\log S]=\infty\)
- Hybrid Euler + fractional kernel schemes are the practical workhorse here

## 4. Signature / path-dependent models

Path signatures (iterated integrals) provide universal features of price/vol paths. Signature volatility models nest Stein–Stein, Bergomi, Heston and enable Fourier pricing/hedging research.

**Trading use in this repo:** feature hooks for ML-assisted regimes and path-dependent hedges (research layer).

## 5. What we implement

| Module | Implemented | Notes |
| --- | --- | --- |
| GBM + Itô helpers | yes | Exact / Euler |
| Heston (QE / Euler) | yes | Correlated Brownian |
| Rough Bergomi (hybrid approx) | yes | Practical discrete kernel |
| Forward variance curve from IV | yes | From NASDAQ-style IV30/60/90 |
| Signature features | light | Truncated level-2/3 |
| Live order execution | no | Research only |

## 6. Primary references

1. Gatheral, Jaisson, Rosenbaum (2018) — Volatility is rough  
2. Bayer, Friz, Gatheral (2016) — Pricing under rough volatility  
3. El Euch & Rosenbaum — Rough Heston characteristic function  
4. Friz et al. / Bank–Bayer–Friz–Pelizzari — Rough PDEs for LSV  
5. Cuchiero et al. — Signature volatility models  
6. arXiv:2412.21192 — Rough differential equations for volatility  

Market calibration inputs: see [`NASDAQ_DATA.md`](NASDAQ_DATA.md).
