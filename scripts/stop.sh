#!/bin/bash

echo "========================================"
echo "Attendance Management System - Stopping"
echo "========================================"
echo ""

# Stop backend
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    echo "Stopping backend server (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null
    rm backend.pid
    echo "✓ Backend stopped"
else
    echo "⚠️  Backend PID file not found"
fi

# Stop frontend
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    echo "Stopping frontend server (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null
    rm frontend.pid
    echo "✓ Frontend stopped"
else
    echo "⚠️  Frontend PID file not found"
fi

# Kill any remaining Python processes for the app (optional)
# Uncomment if needed:
# pkill -f "python.*run.py"
# pkill -f "python.*http.server.*8080"

echo ""
echo "All servers stopped"
echo ""
