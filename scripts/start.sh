#!/bin/bash

echo "========================================"
echo "Attendance Management System - Starting"
echo "========================================"
echo ""

# Check if running from project root
if [ ! -d "backend" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "Error: backend/.env file not found"
    echo "Please run ./scripts/setup.sh first"
    exit 1
fi

# Start backend server
echo "Starting backend server..."
cd backend

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start Flask server in background
python3 run.py &
BACKEND_PID=$!

echo "Backend server started (PID: $BACKEND_PID)"
echo $BACKEND_PID > ../backend.pid

cd ..

# Start frontend (simple HTTP server)
echo ""
echo "Starting frontend server..."
cd frontend

# Use Python's built-in HTTP server
python3 -m http.server 8080 &
FRONTEND_PID=$!

echo "Frontend server started (PID: $FRONTEND_PID)"
echo $FRONTEND_PID > ../frontend.pid

cd ..

echo ""
echo "========================================"
echo "Servers Started Successfully!"
echo "========================================"
echo ""
echo "Backend API:  http://localhost:5001"
echo "Frontend:     http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop, or run ./scripts/stop.sh"
echo ""

# Wait for user interrupt
trap 'echo ""; echo "Use ./scripts/stop.sh to stop the servers"; exit 0' INT

# Keep script running
wait
