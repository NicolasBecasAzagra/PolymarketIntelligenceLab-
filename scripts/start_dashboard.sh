#!/bin/bash
set -e

# ==============================================================================
# Polymarket Intelligence Lab - Start Dashboard & API
# ==============================================================================

echo "================================================================="
echo "Starting Polymarket Intelligence Lab UI Server..."
echo "================================================================="

cd "$(dirname "$0")/.."

# 1. Start FastAPI Backend in the background
echo "-> Starting FastAPI Backend on port 8000..."
~/.local/bin/poetry run uvicorn src.api.main:app --host 0.0.0.0 --port 8000 &
FASTAPI_PID=$!

# 2. Start Next.js Frontend
echo "-> Starting Next.js Frontend on port 3000..."
cd frontend
npm run build
npm run start -- -H 0.0.0.0 &
NEXTJS_PID=$!

echo "================================================================="
echo "✅ Systems Online!"
echo "API Backend running at:   http://localhost:8000/api/opportunities"
echo "Web Dashboard running at: http://localhost:3000"
echo "Press Ctrl+C to stop both servers."
echo "================================================================="

# Trap Ctrl+C to kill both background processes
trap "echo 'Stopping servers...'; kill $FASTAPI_PID $NEXTJS_PID; exit" INT

# Wait for both processes
wait $FASTAPI_PID $NEXTJS_PID
