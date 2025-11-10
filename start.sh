#!/bin/bash

# Start the FastAPI backend
echo "Starting FastAPI backend on http://localhost:8000..."
cd api && python3 main.py &
API_PID=$!

# Wait for API to start
sleep 2

# Start the Next.js frontend
echo "Starting Next.js frontend on http://localhost:3000..."
cd ../frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "================================"
echo "Servers running:"
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:3000"
echo "================================"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $API_PID $FRONTEND_PID; exit" INT
wait
