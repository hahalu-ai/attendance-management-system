#!/bin/bash

echo "========================================="
echo "Railway Database Initialization Script"
echo "========================================="
echo ""

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found"
    echo ""
    echo "Please install Railway CLI first:"
    echo ""
    echo "Option 1 - Using npm:"
    echo "  npm i -g @railway/cli"
    echo ""
    echo "Option 2 - Using Homebrew (macOS):"
    echo "  brew install railway"
    echo ""
    echo "Option 3 - Using curl:"
    echo "  curl -fsSL https://railway.app/install.sh | sh"
    echo ""
    exit 1
fi

echo "✓ Railway CLI found"
echo ""

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Not logged in to Railway"
    echo "Logging in..."
    railway login
    echo ""
fi

echo "✓ Logged in to Railway"
echo ""

# Check if linked to project
if ! railway status &> /dev/null; then
    echo "🔗 Not linked to a Railway project"
    echo "Linking to project..."
    railway link
    echo ""
fi

echo "✓ Linked to Railway project"
echo ""

# Find SQL file
SQL_FILE="backend/database/init_database.sql"

if [ ! -f "$SQL_FILE" ]; then
    echo "❌ Error: SQL file not found at $SQL_FILE"
    exit 1
fi

echo "✓ Found SQL file: $SQL_FILE"
echo ""

# Import database
echo "📊 Importing database schema..."
echo "This may take a few seconds..."
echo ""

railway run mysql -h \$MYSQLHOST -u \$MYSQLUSER -p\$MYSQLPASSWORD \$MYSQLDATABASE < "$SQL_FILE"

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✅ Database initialized successfully!"
    echo "========================================="
    echo ""
    echo "Created tables:"
    echo "  - users"
    echo "  - manager_assignments"
    echo "  - time_entries"
    echo "  - qr_requests"
    echo ""
    echo "Default users created:"
    echo "  - ylin (Manager) - password: password!"
    echo "  - xlu (Contractor) - password: password!"
    echo "  - jsmith (Contractor) - password: password!"
    echo ""
    echo "Next steps:"
    echo "1. Visit your Railway URL"
    echo "2. Login with username: ylin, password: password!"
    echo ""
else
    echo ""
    echo "❌ Database initialization failed"
    echo "Please check the error message above"
    echo ""
    echo "Common issues:"
    echo "- MySQL service not running on Railway"
    echo "- Wrong project linked"
    echo "- SQL file has errors"
    echo ""
fi
