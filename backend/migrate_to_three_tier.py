#!/usr/bin/env python3
"""
Railway-Friendly Migration Script: Two-Tier to Three-Tier User System

This script migrates the database from (Manager, Contractor) to (Manager, Lead, Member).
It's idempotent - safe to run multiple times.

Usage:
    python migrate_to_three_tier.py
"""

import mysql.connector
from mysql.connector import Error
import sys
import os
from datetime import datetime

# Import config
try:
    from app.config import Config
except ImportError:
    # Fallback for Railway environment
    class Config:
        @staticmethod
        def get_db_config():
            return {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 3306)),
                'user': os.getenv('DB_USER', 'root'),
                'password': os.getenv('DB_PASSWORD', ''),
                'database': os.getenv('DB_NAME', 'attendance_system')
            }

def get_connection():
    """Create and return a database connection"""
    try:
        config = Config.get_db_config()
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        sys.exit(1)

def check_migration_status(cursor):
    """Check if migration has already been run"""
    try:
        # Check if new tables exist
        cursor.execute("SHOW TABLES LIKE 'lead_assignments'")
        lead_table_exists = cursor.fetchone() is not None

        cursor.execute("SHOW TABLES LIKE 'manager_lead_assignments'")
        manager_lead_table_exists = cursor.fetchone() is not None

        # Check if user_level enum has 'Lead' and 'Member'
        cursor.execute("""
            SELECT COLUMN_TYPE FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME = 'user_level'
        """)
        result = cursor.fetchone()
        if result:
            enum_values = result[0]
            has_three_tiers = 'Lead' in enum_values and 'Member' in enum_values
        else:
            has_three_tiers = False

        return {
            'lead_assignments_exists': lead_table_exists,
            'manager_lead_assignments_exists': manager_lead_table_exists,
            'has_three_tier_enum': has_three_tiers,
            'is_migrated': lead_table_exists and manager_lead_table_exists and has_three_tiers
        }
    except Error as e:
        print(f"❌ Error checking migration status: {e}")
        return {'is_migrated': False}

def backup_tables(cursor, connection):
    """Create backup tables"""
    print("📦 Creating backup tables...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    try:
        # Backup users table
        cursor.execute(f"DROP TABLE IF EXISTS users_backup_{timestamp}")
        cursor.execute(f"CREATE TABLE users_backup_{timestamp} AS SELECT * FROM users")
        print(f"   ✓ Created users_backup_{timestamp}")

        # Backup manager_assignments if it exists
        cursor.execute("SHOW TABLES LIKE 'manager_assignments'")
        if cursor.fetchone():
            cursor.execute(f"DROP TABLE IF EXISTS manager_assignments_backup_{timestamp}")
            cursor.execute(f"CREATE TABLE manager_assignments_backup_{timestamp} AS SELECT * FROM manager_assignments")
            print(f"   ✓ Created manager_assignments_backup_{timestamp}")

        connection.commit()
        print("✅ Backup completed successfully")
        return True
    except Error as e:
        print(f"⚠️  Backup failed (continuing anyway): {e}")
        return False

def modify_users_table(cursor, connection):
    """Modify users table to support three user types"""
    print("🔧 Modifying users table...")

    try:
        # Check current enum values
        cursor.execute("""
            SELECT COLUMN_TYPE FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'users'
            AND COLUMN_NAME = 'user_level'
        """)
        result = cursor.fetchone()

        if result and 'Lead' in result[0] and 'Member' in result[0]:
            print("   ℹ️  Users table already has three-tier enum, skipping...")
            return True

        # Modify the enum to include Lead and Member
        cursor.execute("""
            ALTER TABLE users
            MODIFY COLUMN user_level ENUM('Manager', 'Lead', 'Member', 'Contractor') NOT NULL
        """)
        connection.commit()
        print("   ✓ Updated user_level enum to include Lead and Member")
        return True
    except Error as e:
        print(f"❌ Error modifying users table: {e}")
        connection.rollback()
        return False

def update_contractors_to_leads(cursor, connection):
    """Convert all Contractors to Leads"""
    print("🔄 Converting Contractors to Leads...")

    try:
        cursor.execute("SELECT COUNT(*) FROM users WHERE user_level = 'Contractor'")
        count = cursor.fetchone()[0]

        if count == 0:
            print("   ℹ️  No Contractors found, skipping...")
            return True

        cursor.execute("UPDATE users SET user_level = 'Lead' WHERE user_level = 'Contractor'")
        connection.commit()
        print(f"   ✓ Converted {count} Contractor(s) to Lead(s)")
        return True
    except Error as e:
        print(f"❌ Error converting Contractors: {e}")
        connection.rollback()
        return False

def create_lead_assignments_table(cursor, connection):
    """Create lead_assignments table"""
    print("📋 Creating lead_assignments table...")

    try:
        # Check if table already exists
        cursor.execute("SHOW TABLES LIKE 'lead_assignments'")
        if cursor.fetchone():
            print("   ℹ️  Table already exists, skipping...")
            return True

        cursor.execute("""
            CREATE TABLE lead_assignments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                lead_username VARCHAR(50) NOT NULL,
                member_username VARCHAR(50) NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_assignment (lead_username, member_username),
                CONSTRAINT fk_lead_username
                    FOREIGN KEY (lead_username) REFERENCES users(username)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                CONSTRAINT fk_member_username
                    FOREIGN KEY (member_username) REFERENCES users(username)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                INDEX idx_lead (lead_username),
                INDEX idx_member (member_username)
            )
        """)
        connection.commit()
        print("   ✓ Created lead_assignments table")
        return True
    except Error as e:
        print(f"❌ Error creating lead_assignments table: {e}")
        connection.rollback()
        return False

def create_manager_lead_assignments_table(cursor, connection):
    """Create manager_lead_assignments table"""
    print("📋 Creating manager_lead_assignments table...")

    try:
        # Check if table already exists
        cursor.execute("SHOW TABLES LIKE 'manager_lead_assignments'")
        if cursor.fetchone():
            print("   ℹ️  Table already exists, skipping...")
            return True

        cursor.execute("""
            CREATE TABLE manager_lead_assignments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                manager_username VARCHAR(50) NOT NULL,
                lead_username VARCHAR(50) NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_manager_lead (manager_username, lead_username),
                CONSTRAINT fk_manager_lead_manager
                    FOREIGN KEY (manager_username) REFERENCES users(username)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                CONSTRAINT fk_manager_lead_lead
                    FOREIGN KEY (lead_username) REFERENCES users(username)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                INDEX idx_manager_lead (manager_username),
                INDEX idx_lead_manager (lead_username)
            )
        """)
        connection.commit()
        print("   ✓ Created manager_lead_assignments table")
        return True
    except Error as e:
        print(f"❌ Error creating manager_lead_assignments table: {e}")
        connection.rollback()
        return False

def migrate_manager_assignments(cursor, connection):
    """Migrate data from manager_assignments to manager_lead_assignments"""
    print("🔄 Migrating manager assignments...")

    try:
        # Check if old table exists
        cursor.execute("SHOW TABLES LIKE 'manager_assignments'")
        if not cursor.fetchone():
            print("   ℹ️  No manager_assignments table found, skipping...")
            return True

        # Check if data already migrated
        cursor.execute("SELECT COUNT(*) FROM manager_lead_assignments")
        if cursor.fetchone()[0] > 0:
            print("   ℹ️  Data already migrated, skipping...")
            return True

        # Migrate data
        cursor.execute("""
            INSERT INTO manager_lead_assignments (manager_username, lead_username, assigned_at)
            SELECT manager_username, contractor_username, assigned_at
            FROM manager_assignments
        """)
        rows_migrated = cursor.rowcount
        connection.commit()
        print(f"   ✓ Migrated {rows_migrated} assignment(s)")
        return True
    except Error as e:
        print(f"❌ Error migrating assignments: {e}")
        connection.rollback()
        return False

def update_qr_requests_table(cursor, connection):
    """Update qr_requests table column names"""
    print("🔧 Updating qr_requests table...")

    try:
        # Check if columns already updated
        cursor.execute("""
            SELECT COLUMN_NAME FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'qr_requests'
            AND COLUMN_NAME = 'lead_username'
        """)
        if cursor.fetchone():
            print("   ℹ️  Columns already updated, skipping...")
            return True

        # Drop old foreign keys
        print("   → Dropping old foreign keys...")
        try:
            cursor.execute("ALTER TABLE qr_requests DROP FOREIGN KEY fk_qr_manager")
        except Error:
            pass  # May not exist

        try:
            cursor.execute("ALTER TABLE qr_requests DROP FOREIGN KEY fk_qr_worker")
        except Error:
            pass  # May not exist

        # Rename columns
        print("   → Renaming columns...")
        cursor.execute("""
            ALTER TABLE qr_requests
            CHANGE COLUMN manager_username lead_username VARCHAR(50) NOT NULL
        """)
        cursor.execute("""
            ALTER TABLE qr_requests
            CHANGE COLUMN worker_username member_username VARCHAR(50) NOT NULL
        """)

        # Add new foreign keys
        print("   → Adding new foreign keys...")
        cursor.execute("""
            ALTER TABLE qr_requests
            ADD CONSTRAINT fk_qr_lead
                FOREIGN KEY (lead_username) REFERENCES users(username)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        """)
        cursor.execute("""
            ALTER TABLE qr_requests
            ADD CONSTRAINT fk_qr_member
                FOREIGN KEY (member_username) REFERENCES users(username)
                ON DELETE CASCADE
                ON UPDATE CASCADE
        """)

        # Update index
        print("   → Updating indexes...")
        try:
            cursor.execute("DROP INDEX idx_worker ON qr_requests")
        except Error:
            pass  # May not exist

        cursor.execute("ALTER TABLE qr_requests ADD INDEX idx_member (member_username)")

        connection.commit()
        print("   ✓ Updated qr_requests table")
        return True
    except Error as e:
        print(f"❌ Error updating qr_requests table: {e}")
        connection.rollback()
        return False

def remove_contractor_enum(cursor, connection):
    """Remove 'Contractor' from user_level enum"""
    print("🧹 Cleaning up old enum value...")

    try:
        cursor.execute("""
            ALTER TABLE users
            MODIFY COLUMN user_level ENUM('Manager', 'Lead', 'Member') NOT NULL
        """)
        connection.commit()
        print("   ✓ Removed 'Contractor' from enum")
        return True
    except Error as e:
        print(f"❌ Error removing Contractor enum: {e}")
        connection.rollback()
        return False

def verify_migration(cursor):
    """Verify the migration was successful"""
    print("\n🔍 Verifying migration...")

    try:
        # Count users by type
        cursor.execute("SELECT user_level, COUNT(*) as count FROM users GROUP BY user_level")
        user_counts = cursor.fetchall()

        print("   User counts by type:")
        for user_level, count in user_counts:
            print(f"   - {user_level}: {count}")

        # Count assignments
        cursor.execute("SELECT COUNT(*) FROM manager_lead_assignments")
        manager_lead_count = cursor.fetchone()[0]
        print(f"   - Manager-Lead assignments: {manager_lead_count}")

        cursor.execute("SELECT COUNT(*) FROM lead_assignments")
        lead_member_count = cursor.fetchone()[0]
        print(f"   - Lead-Member assignments: {lead_member_count}")

        print("\n✅ Migration verification complete!")
        return True
    except Error as e:
        print(f"⚠️  Verification warning: {e}")
        return False

def main():
    """Main migration function"""
    print("\n" + "="*60)
    print("  Three-Tier User System Migration")
    print("  Database: attendance_system")
    print("="*60 + "\n")

    connection = None
    try:
        # Connect to database
        print("🔌 Connecting to database...")
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        print("✅ Connected successfully\n")

        # Check migration status
        print("🔍 Checking migration status...")
        status = check_migration_status(cursor)

        if status.get('is_migrated'):
            print("✅ Migration already completed! Nothing to do.\n")
            verify_migration(cursor)
            return 0

        print("📝 Migration needed, proceeding...\n")

        # Run migration steps
        steps = [
            ("Backup tables", lambda: backup_tables(cursor, connection)),
            ("Modify users table", lambda: modify_users_table(cursor, connection)),
            ("Update Contractors to Leads", lambda: update_contractors_to_leads(cursor, connection)),
            ("Create lead_assignments table", lambda: create_lead_assignments_table(cursor, connection)),
            ("Create manager_lead_assignments table", lambda: create_manager_lead_assignments_table(cursor, connection)),
            ("Migrate manager assignments", lambda: migrate_manager_assignments(cursor, connection)),
            ("Update qr_requests table", lambda: update_qr_requests_table(cursor, connection)),
            ("Remove old enum value", lambda: remove_contractor_enum(cursor, connection)),
        ]

        for step_name, step_func in steps:
            if not step_func():
                print(f"\n❌ Migration failed at step: {step_name}")
                return 1

        # Verify migration
        verify_migration(cursor)

        print("\n" + "="*60)
        print("  ✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("="*60 + "\n")

        print("Next steps:")
        print("1. Restart your backend server")
        print("2. Test the new API endpoints")
        print("3. Update your frontend")
        print()

        return 0

    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if connection:
            connection.rollback()
        return 1
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Database connection closed\n")

if __name__ == "__main__":
    sys.exit(main())
