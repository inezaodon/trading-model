#!/usr/bin/env bash
# Quick API smoke test (requires server OR starts one-shot TestClient)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="${HOME}/.local/bin:${PATH}"
export PYTHONPATH="${ROOT}/apps/api:${ROOT}/packages/core-math/src${PYTHONPATH:+:${PYTHONPATH}}"
cd "$ROOT"
python3 << 'PY'
from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)
r = c.get("/api/v1/health")
assert r.status_code == 200, r.text
r = c.get("/api/v1/projects")
assert r.status_code == 200
assert r.json()["count"] == 7
r = c.get("/api/v1/datasets")
assert r.status_code == 200
slugs = [p["slug"] for p in r.json().get("projects", [])] if False else None
projects = c.get("/api/v1/projects").json()["projects"]
for p in projects:
    slug = p["slug"]
    body = {"params": dict(p.get("default_params") or {})}
    # Keep MC / VaR fast in smoke
    if slug == "mc-options":
        body["params"]["n_paths"] = 2000
    if slug == "var":
        body["params"]["n_sims"] = 2000
    if slug == "rough-vol":
        body["params"]["n_steps"] = 64
        body["params"]["n_paths"] = 2
    resp = c.post(f"/api/v1/{slug}/run", json=body)
    assert resp.status_code == 200, (slug, resp.text)
    data = resp.json()
    assert "metrics" in data and "series" in data, slug
    print(f"OK  {slug:12} engine={data.get('engine')}")
r = c.get("/")
assert r.status_code == 200
print("OK  landing page")
print("smoke passed")
PY
