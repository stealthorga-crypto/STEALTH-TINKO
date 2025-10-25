#!/usr/bin/env bash
# Start Backend Server (portable)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

PORT_BACKEND="${PORT_BACKEND:-8010}"
/c/Python313/python -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT_BACKEND" --reload
