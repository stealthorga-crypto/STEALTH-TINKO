#!/usr/bin/env bash
# Start Frontend Server (portable)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR/tinko-console"

# Default backend URL for dev unless already set
export NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL:-http://127.0.0.1:8010}"

[ -d node_modules ] || npm install
npm run dev
