#!/usr/bin/env python3
"""
Initialize Railway MySQL Database
This script reads Railway MySQL credentials and initializes the database.
"""

import os
import sys
import subprocess
import json

def run_command(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("=" * 60)
    print("Railway Database Initialization (Python)")
    print("=" * 60)
    print()

    # Check if railway CLI is installed
    success, _, _ = run_command("railway --version")
    if not success:
        print("❌ Railway CLI not found")
        print()
        print("Please install Railway CLI first:")
        print("  npm i -g @railway/cli")
        print()
        sys.exit(1)

    print("✓ Railway CLI found")

    # Check if logged in
    success, output, _ = run_command("railway whoami")
    if not success:
        print("🔐 Please login to Railway first:")
        print("  railway login")
        print()
        sys.exit(1)

    print(f"✓ Logged in as: {output.strip()}")

    # Check if linked
    success, _, _ = run_command("railway status")
    if not success:
        print("🔗 Please link to your project first:")
        print("  railway link")
        print()
        sys.exit(1)

    print("✓ Linked to Railway project")

    # Get MySQL variables
    print()
    print("📊 Fetching MySQL credentials...")

    success, output, error = run_command("railway variables --json")
    if not success:
        print(f"❌ Failed to get variables: {error}")
        sys.exit(1)

    try:
        variables = json.loads(output)

        # Find MySQL credentials
        mysql_host = None
        mysql_port = None
        mysql_user = None
        mysql_password = None
        mysql_database = None

        for var in variables:
            name = var.get('name', '')
            value = var.get('value', '')

            if 'MYSQLHOST' in name:
                mysql_host = value
            elif 'MYSQLPORT' in name:
                mysql_port = value
            elif 'MYSQLUSER' in name:
                mysql_user = value
            elif 'MYSQLPASSWORD' in name:
                mysql_password = value
            elif 'MYSQLDATABASE' in name:
                mysql_database = value

        if not all([mysql_host, mysql_port, mysql_user, mysql_password, mysql_database]):
            print("❌ Missing MySQL credentials")
            print("Please ensure MySQL service is added to your Railway project")
            sys.exit(1)

        print(f"✓ MySQL Host: {mysql_host}")
        print(f"✓ MySQL Port: {mysql_port}")
        print(f"✓ MySQL Database: {mysql_database}")
        print()

    except json.JSONDecodeError:
        print("❌ Failed to parse variables")
        sys.exit(1)

    # Check if SQL file exists
    sql_file = "backend/database/init_database.sql"
    if not os.path.exists(sql_file):
        print(f"❌ SQL file not found: {sql_file}")
        sys.exit(1)

    print(f"✓ Found SQL file: {sql_file}")
    print()

    # Import database
    print("📊 Importing database schema...")
    print("This may take a few seconds...")
    print()

    cmd = f'railway run mysql -h $MYSQLHOST -u $MYSQLUSER -p$MYSQLPASSWORD $MYSQLDATABASE < {sql_file}'
    success, output, error = run_command(cmd)

    if success:
        print()
        print("=" * 60)
        print("✅ Database initialized successfully!")
        print("=" * 60)
        print()
        print("Created tables:")
        print("  - users")
        print("  - manager_assignments")
        print("  - time_entries")
        print("  - qr_requests")
        print()
        print("Default users created:")
        print("  - ylin (Manager) - password: password!")
        print("  - xlu (Contractor) - password: password!")
        print("  - jsmith (Contractor) - password: password!")
        print()
        print("Next steps:")
        print("1. Visit your Railway URL")
        print("2. Login with username: ylin, password: password!")
        print()
    else:
        print()
        print("❌ Database initialization failed")
        print(f"Error: {error}")
        print()
        sys.exit(1)

if __name__ == "__main__":
    main()
