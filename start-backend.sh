#!/usr/bin/env bash
# Start Backend Server (portable)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

PORT_BACKEND="${PORT_BACKEND:-8010}"

# Use project venv and ensure .env is loaded so DATABASE_URL (Neon) and other vars are visible
PY=./.venv/Scripts/python.exe
if [ ! -f "$PY" ]; then
	echo "Virtualenv Python not found at $PY. Falling back to system python."
	PY=python
fi

"$PY" -m dotenv run -- "$PY" -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT_BACKEND" --reload
