#!/bin/bash

echo "========================================"
echo "Attendance Management System - Setup"
echo "========================================"
echo ""

# Check if running from project root
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Step 1: Setup backend
echo "[1/4] Setting up backend..."
cd backend

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and configure your database credentials"
    read -p "Press enter to continue after editing .env file..."
fi

# Install Python dependencies
echo "Installing Python dependencies..."
if command -v python3 &> /dev/null; then
    pip3 install -r requirements.txt
elif command -v python &> /dev/null; then
    pip install -r requirements.txt
else
    echo "Error: Python is not installed"
    exit 1
fi

cd ..

# Step 2: Setup database
echo ""
echo "[2/4] Setting up database..."
echo "Please ensure MySQL is running and you have the credentials ready."
read -p "Do you want to initialize the database now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Please enter your MySQL credentials:"
    read -p "MySQL Host (default: localhost): " DB_HOST
    DB_HOST=${DB_HOST:-localhost}

    read -p "MySQL User (default: root): " DB_USER
    DB_USER=${DB_USER:-root}

    read -sp "MySQL Password: " DB_PASSWORD
    echo ""

    read -p "Database Name (default: practice_db): " DB_NAME
    DB_NAME=${DB_NAME:-practice_db}

    # Create database
    echo "Creating database..."
    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"

    # Import schema
    echo "Importing database schema..."
    mysql -h "$DB_HOST" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < backend/database/init_database.sql

    echo "✓ Database setup complete!"
else
    echo "⚠️  Skipping database setup. You can run the SQL file manually:"
    echo "   mysql -u root -p practice_db < backend/database/init_database.sql"
fi

# Step 3: Verify frontend
echo ""
echo "[3/4] Verifying frontend files..."
if [ -f "frontend/index.html" ]; then
    echo "✓ Frontend files found"
else
    echo "⚠️  Frontend files missing"
fi

# Step 4: Final instructions
echo ""
echo "[4/4] Setup complete!"
echo ""
echo "========================================"
echo "Next Steps:"
echo "========================================"
echo "1. Make sure backend/.env is configured correctly"
echo "2. Run './scripts/start.sh' to start the application"
echo "3. Open http://localhost:5001 in your browser"
echo ""
echo "For development:"
echo "  - Backend API: http://localhost:5001/api"
echo "  - Frontend: Open frontend/index.html in browser"
echo ""
