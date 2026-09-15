# PROGRESS.md — Trading Model Umbrella (read this first)

> **Mandatory handoff file.** Every agent working on this repo MUST read this file before coding and update the Status section when finishing a task. If a context window ends, the next agent continues from here.

**Updated:** 2026-09-15  
**Repo root (merge worktree):** `/agent/trading-model-merge`  
**Primary checkout:** `/agent/trading-model`  
**Final integration branch (do NOT push to `main` yet):** `dev`  
**Cloud run:** https://cursor.com/agents/bc-01a0a28e-c96a-7657-bc33-727817b3dedd

---

## Vision

One **umbrella website + backend** that hosts **7 stochastic-calculus Python projects** as first-class apps. Individual feature branches are built by specialist “devs”; an umbrella agent merges them into branch **`dev`**.

Educational / research only — **not** investment advice, **no** live order routing.

---

## The 7 projects

| # | Slug | Title | Branch | Owns path | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | `gbm` | Geometric Brownian Motion Stock Price Simulator | `cursor/p1-gbm-dedd` | `projects/01-gbm-simulator/` | done |
| 2 | `mc-options` | Monte Carlo Option Pricing (EU call/put) | `cursor/p2-mc-options-dedd` | `projects/02-mc-option-pricing/` | done |
| 3 | `brownian` | Brownian Motion & Random Walk Visualizer | `cursor/p3-brownian-dedd` | `projects/03-brownian-visualizer/` | pending |
| 4 | `ou` | Ornstein–Uhlenbeck Mean Reversion | `cursor/p4-ou-dedd` | `projects/04-ornstein-uhlenbeck/` | done |
| 5 | `heston` | Heston Stochastic Volatility Simulator | `cursor/p5-heston-dedd` | `projects/05-heston-simulator/` | done |
| 6 | `var` | Monte Carlo Value-at-Risk Engine | `cursor/p6-var-dedd` | `projects/06-monte-carlo-var/` | done |
| 7 | `rough-vol` | Rough Volatility (Rough Bergomi) Simulator | `cursor/p7-rough-vol-dedd` | `projects/07-rough-volatility/` | done |

> Project 7 fills the “7 projects” list (user listed 1–6 explicitly; #7 continues modern stochastic calculus from earlier research: rough vol / fractional kernels).

### Umbrella

| Piece | Branch | Path | Status |
| --- | --- | --- | --- |
| API backend | `cursor/umbrella-api-dedd` → merges to `dev` | `apps/api/` | pending |
| Website frontend | `cursor/umbrella-web-dedd` → merges to `dev` | `apps/web/` | pending |
| Combined | **`dev`** | whole monorepo | pending |
| `main` | — | — | **do not push until user asks** |

---

## Already completed (prior orchestration)

- Scaffold + stochastic calculus docs (`docs/STOCHASTIC_CALCULUS.md`, `NASDAQ_DATA.md`, `ARCHITECTURE.md`)
- `packages/core-math` — GBM, Itô, Heston, rough Bergomi, signatures, calibrate CLI
- `packages/market-data` — NASDAQ Data Link mock/live + Greeks & Vols schema
- `packages/strategies` — delta-hedge + vol signal backtest
- `packages/orchestrator` + `packages/dashboard` — Node multi-agent runner

Reuse `packages/core-math` where possible; each `projects/0N-*` should be a **self-contained demo app** (CLI + library + tests + README) that the umbrella API can invoke.

---

## Architecture (umbrella)

```
Browser (apps/web)
    │  REST / JSON
    ▼
Backend (apps/api)  Express or FastAPI
    │  spawns / imports
    ▼
projects/01..07  (Python engines)
    │
    ▼
data/selected/   (curated datasets from survey)
```

API contract (each project):

- `POST /api/v1/{slug}/run` — body: params JSON → returns series / metrics / chart-ready arrays
- `GET /api/v1/projects` — catalog of the 7 apps
- `GET /api/v1/datasets` — selected datasets metadata

Website: one shell with nav for all 7; each page has params form + Plotly/Chart.js viz + short math blurb.

---

## Datasets

Survey lives in `data/DATASET_SURVEY.md` (target: evaluate ~150 candidate series).

**Preferred fits (working hypothesis):**

| Project | Best data |
| --- | --- |
| GBM / Heston / Rough / MC options | Liquid NASDAQ names + ETF: `QQQ`, `AAPL`, `MSFT`, `NVDA`, `AMZN`, `META`, `GOOGL`, `TSLA`, `AMD`, `NFLX` |
| OU mean reversion | Spreads / rates: `TNX`/^TNX, Treasury 2s10s, `SOFR`, pairs like `KO-PEP`, sector ETFs |
| Brownian visualizer | Synthetic Wiener (no market data required); optional real residual paths |
| VaR | Multi-asset portfolio from selected liquid ETFs: `QQQ,SPY,IWM,TLT,GLD,HYG` |

Sources to probe: Yahoo Finance (`yfinance`), Treasury.gov CSV archives, FRED (if key), NASDAQ Data Link mock from `packages/market-data`, HuggingFace yahoo parquet samples.

---

## Firebase

- MCP namespace **Firebase** reports `namespaceStatus: ready`
- Backend can optionally persist run history / auth via Firebase (Firestore + Hosting)
- **Action for human:** if deploy/auth is required, run Firebase login when the orchestrator asks — do not block Python project builds on Firebase

---

## Agent rules

1. **Read this file first.** Update your row’s Status → `in_progress` / `done` / `blocked`.
2. Work **only** in your owned path + your branch. Use a dedicated git worktree when possible.
3. Every project needs: `README.md`, `pyproject.toml` or `requirements.txt`, `src/`, `tests/` (pytest), CLI entry, deterministic `seed`.
4. No live trading. Cite NASDAQ / FRED / Treasury where data is used.
5. When done: commit on your branch, append a short note under **Agent notes** below.
6. Umbrella merger only: merge into **`dev`**, never `main`, until the user explicitly requests `main`.

---

## Agent notes

### Project 1 — GBM (`cursor/p1-gbm-dedd`, 2026-09-15)

- Built standalone `projects/01-gbm-simulator/`: NumPy exact log-Euler GBM, μ/σ CSV calibration, Matplotlib + Plotly JSON export, CLI `gbm-sim`, umbrella JSON `{times, paths, params, stats}`, bundled synthetic `data/qqq_sample.csv`.
- Tests: **17 passed** (`python3 -m pytest -q`).
- Runnable via `pip install -e ".[dev]"` then `gbm-sim simulate|calibrate`.

### Orchestrator (2026-09-15)

- Created this PROGRESS.md and launched 7 project agents + dataset survey + umbrella plan.
- Prior packages already merged on `cursor/trading-model-merge-dedd`.
- Final target: branch `dev` with all projects + `apps/web` + `apps/api`.
- Firebase MCP: **not logged in** — human must complete login (session shown in chat) before Hosting/Firestore deploy.
- Worktrees under `/agent/wt/{p1-gbm,p2-mc-options,p3-brownian,p4-ou,p5-heston,p6-var,p7-rough-vol,umbrella}`.
- Live agents:
  - p1 GBM: `bc-a787331d-43d7-566d-a999-87bb9ccfcd9d`
  - p2 MC options: `bc-64dbb699-b09f-5677-aaf5-c29c641c2f96`
  - p3 Brownian: `bc-d83363be-6095-5e3a-ba62-e19a49bb27dc`
  - p4 OU: `bc-73d26277-90e0-5585-bbe7-bb3aa3b4c56c`
  - p5 Heston: `bc-04e702cc-8d8b-5f4b-93c1-75ff8f872bc6`
  - p6 VaR: `bc-f73eb3ce-df78-515a-bcff-4a9edc1c0e1e`
  - p7 Rough vol: `bc-29003dcd-a4d4-5719-b349-755a4ce6d16a`
  - Dataset survey: `bc-0f266286-43b5-51f7-9890-092979da60e4`
  - Umbrella web/API: `bc-43eb4849-f464-55fe-952d-751b30a6f9c8`
- After all succeed: merge into branch **`dev`** (never `main` until user asks).

### p7 rough-vol (2026-09-15)

- Shipped `projects/07-rough-volatility/`: hybrid RL kernel (H≈0.1), ξ₀ knots, NASDAQ IV calibrate CLI, JSON + pytest.
- Branch `cursor/p7-rough-vol-dedd`. Standalone polish of `packages/core-math` rough Bergomi.

### p6 VaR (2026-09-15)

- Built `projects/06-monte-carlo-var/`: GBM + empirical bootstrap MC VaR/ES, equal/custom weights, 95/99, bundled synthetic QQQ/SPY/IWM/TLT/GLD returns, JSON CLI (`python -m monte_carlo_var run`), pytest (12 passed), seed=42.
- Branch: `cursor/p6-var-dedd`.

---


### Orchestrator dashboard agent (merged)
- Merged `cursor/orchestrator-dashboard-4c38` tip into `cursor/trading-model-merge-dedd` (registry, demo pipeline, dashboard UI).

### p5 Heston merged
- Merged `cursor/p5-heston-dedd` (`20b4d8a`) into merge branch; 14 pytest passed upstream.

### p7 Rough vol merged
- Merged `cursor/p7-rough-vol-dedd` (`8b8600d`) into merge branch; 10 pytest passed upstream.

### p6 VaR merged
- Merged `cursor/p6-var-dedd` (`f946722`) into merge branch; 12 pytest passed upstream.

### p1 GBM merged
- Merged `cursor/p1-gbm-dedd` (`d973245`) into merge branch; 17 pytest passed upstream.

### p2 MC options merged
- Merged `cursor/p2-mc-options-dedd` (`5a90f23`) into merge branch; 19 pytest passed upstream.

### p4 OU merged
- Merged `cursor/p4-ou-dedd` (`ad20f8c`) into merge branch; 19 pytest passed upstream.

## Merge checklist → `dev`

- [x] p1 GBM done
- [x] p2 MC options done
- [ ] p3 Brownian done
- [x] p4 OU done
- [x] p5 Heston done
- [x] p6 VaR done
- [x] p7 Rough vol done
- [ ] Dataset survey written + selected datasets vendored/cached
- [ ] `apps/api` serves all 7
- [ ] `apps/web` shows all 7
- [ ] All merged to `dev`
- [ ] Smoke tests pass
- [ ] `main` untouched
