"""Every catalog slug must run with default params on the real project engine.

A response with HTTP 200 but ``engine`` like ``fallback-after-project-error:...``
means the project engine silently failed; that must fail this test.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

_API = Path(__file__).resolve().parents[1]
_CORE = Path(__file__).resolve().parents[3] / "packages" / "core-math" / "src"
for _p in (str(_API), str(_CORE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app.catalog import PROJECTS  # noqa: E402
from app.main import app  # noqa: E402

SLUGS = [p["slug"] for p in PROJECTS]


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(app)


def test_catalog_has_seven_projects() -> None:
    assert len(SLUGS) == 7


@pytest.mark.parametrize("slug", SLUGS)
def test_default_params_use_project_engine(client: TestClient, slug: str) -> None:
    defaults = dict(next(p for p in PROJECTS if p["slug"] == slug).get("default_params") or {})
    resp = client.post(f"/api/v1/{slug}/run", json={"params": defaults})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get("engine") == "project", f"{slug}: engine={data.get('engine')!r}"
