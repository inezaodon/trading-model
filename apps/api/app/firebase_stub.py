"""Firebase run-history: Firestore when configured, otherwise in-memory stub."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

_MEMORY: list[dict[str, Any]] = []
_REPO_ROOT = Path(__file__).resolve().parents[3]
_CONFIG_CANDIDATES = [
    _REPO_ROOT / "apps" / "web" / "firebase-config.json",
    _REPO_ROOT / "firebase-config.json",
]


def _env_enabled() -> bool:
    return os.environ.get("FIREBASE_RUN_HISTORY", "1").strip().lower() not in {
        "0",
        "false",
        "off",
        "no",
    }


def is_enabled() -> bool:
    return _env_enabled()


def _firestore_client():
    """Return a Firestore client if credentials / project are available."""
    project = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCLOUD_PROJECT")
    if not project:
        # Fall back to .firebaserc
        rc = _REPO_ROOT / ".firebaserc"
        if rc.is_file():
            try:
                data = json.loads(rc.read_text(encoding="utf-8"))
                project = (data.get("projects") or {}).get("default")
            except Exception:
                project = None
    if not project:
        return None, None

    try:
        from google.cloud import firestore  # type: ignore
    except ImportError:
        return None, project

    try:
        client = firestore.Client(project=project)
        return client, project
    except Exception:
        return None, project


def record_run(slug: str, params: dict[str, Any], result_meta: dict[str, Any]) -> dict[str, Any]:
    """Store a run in Firestore when possible; otherwise memory stub."""
    entry = {
        "id": str(uuid4()),
        "slug": slug,
        "params": params,
        "meta": result_meta,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "backend": "memory-stub",
    }
    if not _env_enabled():
        return entry

    client, project = _firestore_client()
    if client is not None:
        try:
            doc = {
                "slug": slug,
                "params": params,
                "meta": result_meta,
                "created_at": entry["created_at"],
                "backend": "firestore",
                "project": project,
            }
            client.collection("runs").document(entry["id"]).set(doc)
            entry["backend"] = "firestore"
            entry["project"] = project
            return entry
        except Exception as exc:
            entry["backend"] = "memory-stub"
            entry["firestore_error"] = str(exc)

    _MEMORY.append(entry)
    return entry


def list_runs(limit: int = 50) -> list[dict[str, Any]]:
    client, _project = _firestore_client()
    if client is not None:
        try:
            docs = (
                client.collection("runs")
                .order_by("created_at", direction="DESCENDING")
                .limit(limit)
                .stream()
            )
            out: list[dict[str, Any]] = []
            for d in docs:
                row = d.to_dict() or {}
                row["id"] = d.id
                out.append(row)
            if out:
                return out
        except Exception:
            pass
    return list(reversed(_MEMORY[-limit:]))


def web_config() -> dict[str, Any] | None:
    for path in _CONFIG_CANDIDATES:
        if path.is_file():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                return None
    return None
