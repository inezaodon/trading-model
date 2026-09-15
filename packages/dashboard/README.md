# Dashboard

Static research terminal for orchestrator artifacts (`surface`, `paths`, `backtest`, `report`).

## Run

```bash
# from repo root — generate artifacts first
npm run demo

npm run build -w packages/dashboard
npm run start -w packages/dashboard
# → http://127.0.0.1:4173
```

The tiny server exposes `artifacts/` at `/artifacts/*.json` so the browser can load them without a bundler.
