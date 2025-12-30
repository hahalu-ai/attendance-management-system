#!/usr/bin/env python3
"""
Database Initialization Script for Railway
Run this script to automatically set up the database
"""

import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection(include_db=False):
    """Get database connection"""
    config = {
        'host': os.getenv('DB_HOST') or os.getenv('MYSQLHOST') or os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT') or os.getenv('MYSQLPORT') or os.getenv('MYSQL_PORT', '3306')),
        'user': os.getenv('DB_USER') or os.getenv('MYSQLUSER') or os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('DB_PASSWORD') or os.getenv('MYSQLPASSWORD') or os.getenv('MYSQL_PASSWORD', ''),
    }

    if include_db:
        config['database'] = os.getenv('DB_NAME') or os.getenv('MYSQLDATABASE') or os.getenv('MYSQL_DATABASE', 'attendance_system')

    return mysql.connector.connect(**config)

def create_database():
    """Create database if it doesn't exist"""
    print("Step 1: Creating database...")
    conn = get_db_connection(include_db=False)
    cursor = conn.cursor()

    db_name = os.getenv('DB_NAME') or os.getenv('MYSQLDATABASE') or os.getenv('MYSQL_DATABASE', 'attendance_system')
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    print(f"✓ Database '{db_name}' created/verified")

    cursor.close()
    conn.close()

def create_tables():
    """Create all tables"""
    print("\nStep 2: Creating tables...")
    conn = get_db_connection(include_db=True)
    cursor = conn.cursor()

    # Table 1: Users
    print("  - Creating users table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            display_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            user_level ENUM('Manager', 'Contractor') NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_username (username),
            INDEX idx_email (email)
        )
    """)
    print("    ✓ users table created")

    # Table 2: Manager Assignments
    print("  - Creating manager_assignments table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manager_assignments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            manager_username VARCHAR(50) NOT NULL,
            contractor_username VARCHAR(50) NOT NULL,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_assignment (manager_username, contractor_username),
            CONSTRAINT fk_manager_username
                FOREIGN KEY (manager_username) REFERENCES users(username)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            CONSTRAINT fk_contractor_username
                FOREIGN KEY (contractor_username) REFERENCES users(username)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            INDEX idx_manager (manager_username),
            INDEX idx_contractor (contractor_username)
        )
    """)
    print("    ✓ manager_assignments table created")

    # Table 3: Time Entries
    print("  - Creating time_entries table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS time_entries (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            in_time DATETIME NOT NULL,
            out_time DATETIME NULL,
            status ENUM('Pending', 'Approved', 'Rejected') NOT NULL DEFAULT 'Pending',
            approved_by VARCHAR(50) NULL,
            approved_at DATETIME NULL,
            notes TEXT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            CONSTRAINT fk_time_entry_user
                FOREIGN KEY (username) REFERENCES users(username)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            CONSTRAINT fk_approver
                FOREIGN KEY (approved_by) REFERENCES users(username)
                ON DELETE SET NULL
                ON UPDATE CASCADE,
            INDEX idx_username_date (username, in_time),
            INDEX idx_status (status),
            INDEX idx_approved_by (approved_by)
        )
    """)
    print("    ✓ time_entries table created")

    # Table 4: QR Requests
    print("  - Creating qr_requests table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS qr_requests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            token VARCHAR(255) NOT NULL UNIQUE,
            manager_username VARCHAR(50) NOT NULL,
            worker_username VARCHAR(50) NOT NULL,
            action_type ENUM('check-in', 'check-out') NOT NULL,
            status ENUM('pending', 'used', 'failed', 'expired') NOT NULL DEFAULT 'pending',
            created_at DATETIME NOT NULL,
            expires_at DATETIME NOT NULL,
            used_at DATETIME NULL,
            CONSTRAINT fk_qr_manager
                FOREIGN KEY (manager_username) REFERENCES users(username)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            CONSTRAINT fk_qr_worker
                FOREIGN KEY (worker_username) REFERENCES users(username)
                ON DELETE CASCADE
                ON UPDATE CASCADE,
            INDEX idx_token (token),
            INDEX idx_status_expires (status, expires_at),
            INDEX idx_worker (worker_username)
        )
    """)
    print("    ✓ qr_requests table created")

    conn.commit()
    cursor.close()
    conn.close()

def insert_sample_data():
    """Insert sample data"""
    print("\nStep 3: Inserting sample data...")
    conn = get_db_connection(include_db=True)
    cursor = conn.cursor()

    # Insert users
    print("  - Inserting sample users...")
    try:
        cursor.execute("""
            INSERT IGNORE INTO users (username, display_name, email, password, user_level) VALUES
            ('ylin', 'Yuchen Lin', 'yuchen.lin@example.com', 'f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7', 'Manager'),
            ('xlu', 'Xuanyu Lu', 'xuanyu.lu@example.com', 'f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7', 'Contractor'),
            ('jsmith', 'John Smith', 'john.smith@example.com', 'f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7', 'Contractor')
        """)
        print("    ✓ Sample users inserted")
    except Exception as e:
        print(f"    ⚠ Warning: {e}")

    # Insert manager assignments
    print("  - Assigning contractors to manager...")
    try:
        cursor.execute("""
            INSERT IGNORE INTO manager_assignments (manager_username, contractor_username) VALUES
            ('ylin', 'xlu'),
            ('ylin', 'jsmith')
        """)
        print("    ✓ Manager assignments created")
    except Exception as e:
        print(f"    ⚠ Warning: {e}")

    # Insert sample time entries
    print("  - Inserting sample time entries...")
    try:
        cursor.execute("""
            INSERT IGNORE INTO time_entries (id, username, in_time, out_time, status, approved_by, approved_at) VALUES
            (1, 'xlu', '2025-12-15 09:00:00', '2025-12-15 17:30:00', 'Approved', 'ylin', '2025-12-15 18:00:00'),
            (2, 'jsmith', '2025-12-15 08:45:00', '2025-12-15 17:00:00', 'Pending', NULL, NULL)
        """)
        print("    ✓ Sample time entries inserted")
    except Exception as e:
        print(f"    ⚠ Warning: {e}")

    conn.commit()
    cursor.close()
    conn.close()

def verify_setup():
    """Verify the database setup"""
    print("\nStep 4: Verifying setup...")
    conn = get_db_connection(include_db=True)
    cursor = conn.cursor()

    # Check tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"  ✓ Found {len(tables)} tables: {', '.join([t[0] for t in tables])}")

    # Check users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"  ✓ Found {user_count} users")

    cursor.execute("SELECT username, display_name, user_level FROM users")
    users = cursor.fetchall()
    for username, name, level in users:
        print(f"    - {username} ({name}) - {level}")

    cursor.close()
    conn.close()

def main():
    """Main initialization function"""
    print("=" * 60)
    print("Attendance Management System - Database Initialization")
    print("=" * 60)

    try:
        # Show connection info (without password)
        print("\nConnection Info:")
        print(f"  Host: {os.getenv('DB_HOST') or os.getenv('MYSQLHOST') or os.getenv('MYSQL_HOST', 'localhost')}")
        print(f"  Port: {os.getenv('DB_PORT') or os.getenv('MYSQLPORT') or os.getenv('MYSQL_PORT', '3306')}")
        print(f"  User: {os.getenv('DB_USER') or os.getenv('MYSQLUSER') or os.getenv('MYSQL_USER', 'root')}")
        print(f"  Database: {os.getenv('DB_NAME') or os.getenv('MYSQLDATABASE') or os.getenv('MYSQL_DATABASE', 'attendance_system')}")
        print()

        create_database()
        create_tables()
        insert_sample_data()
        verify_setup()

        print("\n" + "=" * 60)
        print("✓ Database initialization completed successfully!")
        print("=" * 60)
        print("\nTest Credentials:")
        print("  Manager:    ylin / password!")
        print("  Contractor: xlu / password!")
        print("  Contractor: jsmith / password!")
        print()

    except mysql.connector.Error as err:
        print(f"\n✗ Error: {err}")
        print("\nPlease check:")
        print("  1. MySQL service is running")
        print("  2. Environment variables are set correctly")
        print("  3. Database credentials are valid")
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
