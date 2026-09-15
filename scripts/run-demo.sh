#!/usr/bin/env bash
# Start Trading Model umbrella API + static web on http://127.0.0.1:8000
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export PATH="${HOME}/.local/bin:${PATH}"

if ! python3 -c "import fastapi, uvicorn, numpy" 2>/dev/null; then
  echo "Installing API dependencies..."
  python3 -m pip install -r apps/api/requirements.txt
fi

# Prefer editable core-math when present
if [[ -d packages/core-math/src ]]; then
  export PYTHONPATH="${ROOT}/apps/api:${ROOT}/packages/core-math/src${PYTHONPATH:+:${PYTHONPATH}}"
else
  export PYTHONPATH="${ROOT}/apps/api${PYTHONPATH:+:${PYTHONPATH}}"
fi

HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8000}"

echo "Trading Model → http://${HOST}:${PORT}/"
exec python3 -m uvicorn app.main:app --app-dir "${ROOT}/apps/api" --host "${HOST}" --port "${PORT}" "$@"
