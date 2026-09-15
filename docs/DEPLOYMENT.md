# Deployment readiness

Last verified: 2026-09-15

## Live surfaces

| Surface | URL | Status |
| --- | --- | --- |
| Firebase Hosting (static UI) | https://trading-model-oineza-8280d.web.app | live |
| Firebase Console | https://console.firebase.google.com/project/trading-model-oineza-8280d/overview | live |
| Local umbrella API + UI | http://127.0.0.1:8000/ | start with `make demo` |
| GitHub | https://github.com/inezaodon/trading-model | branch `dev` |

Firebase Project ID: **`trading-model-oineza-8280d`** (display name `trading-model-oineza`)

## What is already wired

- 7 Python projects under `projects/01`…`07` with CLIs + pytest
- FastAPI umbrella `apps/api` — `GET /api/v1/projects`, `POST /api/v1/{slug}/run`, `GET /api/v1/runs`
- Static site `apps/web` (also served by Firebase Hosting)
- Firestore `runs` collection rules
- Web SDK config at `apps/web/firebase-config.json`
- Dataset survey + selected CSVs under `data/selected/`
- Node packages: market-data, strategies, orchestrator, dashboard

## Commands for the next projects you ship

```bash
cd /agent/trading-model-merge   # or clone from GitHub on branch dev

# local full stack
make demo
# → http://127.0.0.1:8000/

# smoke all engines
make smoke
# or:
./scripts/smoke-api.sh

# deploy static UI + Firestore rules
npx firebase-tools deploy --only hosting,firestore --project trading-model-oineza-8280d

# add a new project (pattern)
# 1. create projects/08-your-project/ with pyproject + CLI + tests
# 2. register slug in apps/api/app/catalog.py
# 3. add engine loader / fallback in apps/api/app/engines/
# 4. add apps/web/projects/<slug>.html + rewrite in firebase.json
# 5. make smoke && firebase deploy --only hosting
```

## Auth already completed in this environment

- GitHub CLI: `inezaodon`
- Firebase CLI/MCP: `oineza@nd.edu`
- Active Firebase project: `trading-model-oineza-8280d`

## Health checklist (run anytime)

- [ ] `curl http://127.0.0.1:8000/api/v1/health`
- [ ] `curl -X POST http://127.0.0.1:8000/api/v1/gbm/run -H 'content-type: application/json' -d '{"params":{"seed":1}}'`
- [ ] Open https://trading-model-oineza-8280d.web.app/
- [ ] `git checkout dev && git pull`
