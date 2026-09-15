"""Trading Model umbrella FastAPI backend.

Serves REST endpoints for the 7 stochastic-calculus projects and the static web UI.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Ensure packages/core-math is importable when installed editable or via path
REPO_ROOT = Path(__file__).resolve().parents[3]
CORE_MATH_SRC = REPO_ROOT / "packages" / "core-math" / "src"
if CORE_MATH_SRC.is_dir() and str(CORE_MATH_SRC) not in sys.path:
    sys.path.insert(0, str(CORE_MATH_SRC))

from .catalog import PROJECTS, SLUG_INDEX  # noqa: E402
from .engines.loader import run_engine  # noqa: E402
from . import firebase_stub  # noqa: E402

WEB_ROOT = REPO_ROOT / "apps" / "web"
DATA_MANIFEST = REPO_ROOT / "data" / "selected" / "manifest.json"

app = FastAPI(
    title="Trading Model API",
    description="Umbrella backend for 7 stochastic calculus research projects.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "null",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RunBody(BaseModel):
    params: dict = Field(default_factory=dict)


@app.get("/api/v1/health")
def health() -> dict:
    return {"ok": True, "service": "trading-model-api"}


@app.get("/api/v1/projects")
def list_projects() -> dict:
    return {"projects": PROJECTS, "count": len(PROJECTS)}


@app.get("/api/v1/projects/{slug}")
def get_project(slug: str) -> dict:
    project = SLUG_INDEX.get(slug)
    if not project:
        raise HTTPException(status_code=404, detail=f"Unknown project: {slug}")
    return project


@app.get("/api/v1/datasets")
def list_datasets() -> dict:
    if DATA_MANIFEST.is_file():
        try:
            data = json.loads(DATA_MANIFEST.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("source", str(DATA_MANIFEST.relative_to(REPO_ROOT)))
                return data
            return {"datasets": data, "source": str(DATA_MANIFEST.relative_to(REPO_ROOT))}
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Failed to read manifest: {exc}") from exc

    # Stub until dataset survey agent vendors selected series
    return {
        "source": "stub",
        "note": "data/selected/manifest.json not present yet — using research stubs.",
        "datasets": [
            {
                "id": "nasdaq-liquid-equities",
                "tickers": [
                    "QQQ",
                    "AAPL",
                    "MSFT",
                    "NVDA",
                    "AMZN",
                    "META",
                    "GOOGL",
                    "TSLA",
                    "AMD",
                    "NFLX",
                ],
                "use_for": ["gbm", "heston", "rough-vol", "mc-options"],
            },
            {
                "id": "mean-reversion-spreads",
                "tickers": ["TNX", "SOFR", "KO", "PEP"],
                "use_for": ["ou"],
            },
            {
                "id": "var-etf-basket",
                "tickers": ["QQQ", "SPY", "IWM", "TLT", "GLD", "HYG"],
                "use_for": ["var"],
            },
            {
                "id": "synthetic-wiener",
                "tickers": [],
                "use_for": ["brownian"],
                "note": "No market data required",
            },
        ],
    }


@app.post("/api/v1/{slug}/run")
def run_project(slug: str, body: RunBody | None = None) -> dict:
    if slug not in SLUG_INDEX:
        raise HTTPException(status_code=404, detail=f"Unknown project: {slug}")
    project = SLUG_INDEX[slug]
    params = dict(project.get("default_params") or {})
    if body and body.params:
        params.update(body.params)
    try:
        result = run_engine(slug, params)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    firebase_stub.record_run(
        slug,
        params,
        {"engine": result.get("engine"), "metrics": result.get("metrics", {})},
    )
    return result


@app.get("/api/v1/runs")
def list_runs() -> dict:
    return {
        "enabled": firebase_stub.is_enabled(),
        "backend": "memory-stub",
        "runs": firebase_stub.list_runs(),
    }


# Static website (served by same process for simplest demo)
if WEB_ROOT.is_dir():
    app.mount("/assets", StaticFiles(directory=str(WEB_ROOT)), name="assets")

    @app.get("/")
    def index() -> FileResponse:
        return FileResponse(WEB_ROOT / "index.html")

    @app.get("/projects/{slug}")
    def project_page(slug: str) -> FileResponse:
        page = WEB_ROOT / "projects" / f"{slug}.html"
        if not page.is_file():
            raise HTTPException(status_code=404, detail="Project page not found")
        return FileResponse(page)

    # Also allow direct file paths under /web for relative asset links
    @app.get("/css/{path:path}")
    def css(path: str) -> FileResponse:
        f = WEB_ROOT / "css" / path
        if not f.is_file():
            raise HTTPException(status_code=404)
        return FileResponse(f)

    @app.get("/js/{path:path}")
    def js(path: str) -> FileResponse:
        f = WEB_ROOT / "js" / path
        if not f.is_file():
            raise HTTPException(status_code=404)
        return FileResponse(f)
