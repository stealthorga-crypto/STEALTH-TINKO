#!/usr/bin/env bash
# Cross-platform start script for Tinko Recovery Platform (Git Bash, WSL, Linux, macOS)
set -euo pipefail

echo "🚀 Starting Tinko Recovery Platform..."

# Project root
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# Config
PORT_BACKEND="${PORT_BACKEND:-8010}"
API_URL="${NEXT_PUBLIC_API_URL:-http://127.0.0.1:${PORT_BACKEND}}"

# Optional: Start Redis via Docker if available
if command -v docker >/dev/null 2>&1 && docker ps >/dev/null 2>&1; then
    if ! docker ps --format '{{.Names}}' | grep -q '^tinko-redis$'; then
        echo "🐳 Starting Redis container..."
        docker run -d --name tinko-redis -p 6379:6379 redis:alpine >/dev/null 2>&1 || docker start tinko-redis >/dev/null
    else
        echo "✅ Redis already running"
    fi
else
    echo "ℹ️  Docker not available or not running — skipping Redis (Celery optional in dev)"
fi

echo "\n▶️  Backend (FastAPI) on :$PORT_BACKEND"
(
    cd "$ROOT_DIR"
    /c/Python313/python -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT_BACKEND" --reload
) &
BACKEND_PID=$!

# Wait for backend warmup
sleep 3 || true

echo "\n▶️  Frontend (Next.js) on :3000"
(
    cd "$ROOT_DIR/tinko-console"
    [ -d node_modules ] || npm install
    # Inline env for Git Bash/Linux; Next will read NEXT_PUBLIC_API_URL
    NEXT_PUBLIC_API_URL="$API_URL" npm run dev
) &
FRONTEND_PID=$!

echo "\n=========================================="
echo "✅ Tinko Recovery Platform is starting"
echo "=========================================="
echo "🌐 Backend:  $API_URL/docs"
echo "🎨 Frontend: http://localhost:3000"
echo "💚 Health:   $API_URL/healthz"
echo "(Press Ctrl+C to stop)"

wait $BACKEND_PID $FRONTEND_PID
