#!/bin/bash

echo "========================================="
echo "  MySQL Authentication Fix"
echo "========================================="
echo ""
echo "This script will fix the MySQL authentication issue"
echo ""

# Get the password from db.py
PASSWORD="6luxuanyu6"

echo "Step 1: Checking current MySQL authentication..."
sudo mysql -e "SELECT user, host, plugin FROM mysql.user WHERE user='root';"

echo ""
echo "Step 2: Setting root password authentication..."
sudo mysql <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$PASSWORD';
FLUSH PRIVILEGES;
EOF

if [ $? -eq 0 ]; then
    echo "✓ MySQL root password has been set successfully!"
else
    echo "✗ Failed to set password. Trying alternative method..."
    sudo mysql <<EOF
UPDATE mysql.user SET plugin='mysql_native_password', authentication_string=PASSWORD('$PASSWORD') WHERE User='root';
FLUSH PRIVILEGES;
EOF
fi

echo ""
echo "Step 3: Creating database if not exists..."
sudo mysql -e "CREATE DATABASE IF NOT EXISTS practice_db;"

echo ""
echo "Step 4: Verifying connection..."
mysql -u root -p$PASSWORD -e "SHOW DATABASES;" 2>&1

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "✓ Success! MySQL is now configured!"
    echo "========================================="
    echo ""
    echo "You can now run: python3 setup_database.py"
else
    echo ""
    echo "========================================="
    echo "⚠️  Authentication still not working"
    echo "========================================="
    echo ""
    echo "Please try creating a new user instead:"
    echo "Run the alternative script: ./create_mysql_user.sh"
fi
