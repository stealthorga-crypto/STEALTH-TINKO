#!/bin/bash
# Start script for Tinko Recovery Platform - Backend + Frontend

echo "🚀 Starting Tinko Recovery Platform..."
echo ""

# Navigate to project root
cd "$(dirname "$0")"

# Check if Docker is running for Redis (optional)
if docker ps &>/dev/null; then
    echo "✅ Docker is running"
    # Start Redis if not running
    if ! docker ps | grep -q tinko-redis; then
        echo "Starting Redis container..."
        docker run -d --name tinko-redis -p 6379:6379 redis:alpine 2>/dev/null || docker start tinko-redis
    fi
else
    echo "⚠️  Docker not running - Celery workers will not be available"
fi

echo ""
echo "Starting Backend (FastAPI)..."
cd Stealth-Reecovery
/c/Python313/python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID) - http://127.0.0.1:8000"

echo ""
echo "Waiting for backend to initialize..."
sleep 5

echo ""
echo "Starting Frontend (Next.js)..."
cd ../tinko-console

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies (this may take a few minutes)..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID) - http://localhost:3000"

echo ""
echo "=========================================="
echo "✅ Tinko Recovery Platform is running!"
echo "=========================================="
echo ""
echo "🌐 Backend API:  http://127.0.0.1:8000/docs"
echo "🎨 Frontend UI:  http://localhost:3000"
echo "💚 Health Check: http://127.0.0.1:8000/healthz"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
