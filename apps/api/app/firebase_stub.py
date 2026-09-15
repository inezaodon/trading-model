"""Optional Firebase run-history stub. Local demo never requires Firebase."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

_MEMORY: list[dict[str, Any]] = []
_ENABLED = False


def is_enabled() -> bool:
    return _ENABLED


def record_run(slug: str, params: dict[str, Any], result_meta: dict[str, Any]) -> dict[str, Any]:
    """Store a run in memory. Swap for Firestore when credentials exist."""
    entry = {
        "id": str(uuid4()),
        "slug": slug,
        "params": params,
        "meta": result_meta,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "backend": "memory-stub",
    }
    if _ENABLED:
        _MEMORY.append(entry)
    return entry


def list_runs(limit: int = 50) -> list[dict[str, Any]]:
    return list(reversed(_MEMORY[-limit:]))
