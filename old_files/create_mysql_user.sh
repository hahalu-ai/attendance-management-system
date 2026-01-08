#!/bin/bash

echo "========================================="
echo "  Create New MySQL User (Alternative)"
echo "========================================="
echo ""

DB_USER="attendance_user"
DB_PASS="6luxuanyu6"
DB_NAME="practice_db"

echo "Creating user: $DB_USER"
echo "Database: $DB_NAME"
echo ""

sudo mysql <<EOF
-- Create user if not exists
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS $DB_NAME;

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';

-- Flush privileges
FLUSH PRIVILEGES;

-- Show confirmation
SELECT user, host FROM mysql.user WHERE user='$DB_USER';
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✓ User created successfully!"
    echo "========================================="
    echo ""
    echo "Now update db.py with these credentials:"
    echo "  user='$DB_USER'"
    echo "  password='$DB_PASS'"
    echo ""
    echo "Would you like me to update db.py automatically? (y/n)"
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        # Backup original
        cp db.py db.py.backup

        # Update db.py
        cat > db.py <<PYEOF
import mysql.connector

def get_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="$DB_USER",
        password="$DB_PASS",
        database="$DB_NAME"
    )
    return conn
PYEOF

        echo "✓ db.py has been updated!"
        echo "✓ Original saved as db.py.backup"
        echo ""
        echo "You can now run: python3 setup_database.py"
    else
        echo "Please manually update db.py"
    fi
else
    echo "✗ Failed to create user"
fi
