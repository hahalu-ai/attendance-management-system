#!/bin/bash

echo "========================================="
echo "  Attendance Management System Starter  "
echo "========================================="
echo ""

# Check if MySQL is running
echo "Checking MySQL status..."
if ! pgrep -x "mysqld" > /dev/null; then
    echo "⚠️  MySQL is not running!"
    echo "Please start MySQL first:"
    echo "  sudo service mysql start"
    echo ""
    read -p "Press Enter to continue anyway or Ctrl+C to exit..."
else
    echo "✓ MySQL is running"
fi

echo ""
echo "Starting Flask server on http://localhost:5001"
echo ""
echo "Portal will be available at: http://localhost:5001/portal"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================="
echo ""

python3 app.py
