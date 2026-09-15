# Trading Model Web (`apps/web`)

Single static website hosting all **7** stochastic-calculus project demos. Served by the FastAPI app via `StaticFiles` / route handlers (no Vite required).

See [`docs/PROGRESS.md`](../../docs/PROGRESS.md) for integration status and slug map.

## Brand & UI

- Brand: **Trading Model** (hero-level on landing)
- Look: charcoal / teal financial research aesthetic
- Charting: Chart.js CDN
- Responsive nav + param forms + Run → API

## Pages

| Path | Project |
| --- | --- |
| `/` | Landing |
| `/projects/gbm` | GBM simulator |
| `/projects/mc-options` | Monte Carlo options |
| `/projects/brownian` | Brownian visualizer |
| `/projects/ou` | Ornstein–Uhlenbeck |
| `/projects/heston` | Heston SV |
| `/projects/var` | Monte Carlo VaR |
| `/projects/rough-vol` | Rough Bergomi |

## Local run

Prefer the API server (serves this folder):

```bash
./scripts/run-demo.sh
```

Or open files only after starting API on port 8000 so `/api/v1/...` calls succeed.
