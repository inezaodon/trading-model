# Trading Model API (`apps/api`)

FastAPI backend for the umbrella website. Serves the 7 stochastic-calculus project run endpoints and (optionally) the static UI from `apps/web`.

See [`docs/PROGRESS.md`](../../docs/PROGRESS.md) for project slugs, merge status, and agent ownership.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/v1/health` | Liveness |
| GET | `/api/v1/projects` | Catalog of 7 apps |
| GET | `/api/v1/datasets` | `data/selected/manifest.json` or stub |
| POST | `/api/v1/{slug}/run` | Run engine for slug |
| GET | `/api/v1/runs` | In-memory Firebase stub history |

Slugs: `gbm`, `mc-options`, `brownian`, `ou`, `heston`, `var`, `rough-vol`.

## Engines

`app/engines/loader.py` tries to import a `run(params)` from `projects/0N-*` (when sibling agents merge packages). If unavailable, solid inline fallbacks run (GBM/Heston/rough vol also try `packages/core-math`).

Firebase is optional — `app/firebase_stub.py` is memory-only and never required for local demo.

## Setup

```bash
# from repo root
python3 -m pip install -r apps/api/requirements.txt
# optional: editable core-math
python3 -m pip install -e packages/core-math
```

## Run

```bash
# from repo root
./scripts/run-demo.sh
# or
make demo
# or
PYTHONPATH=apps/api:packages/core-math/src \
  python3 -m uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000 --reload
```

Open http://127.0.0.1:8000/
