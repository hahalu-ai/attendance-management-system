import mysql.connector

print("Creating practice_db database...")

try:
    # Connect without specifying database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="6luxuanyu6"
    )

    cursor = conn.cursor()

    # Create database
    cursor.execute("CREATE DATABASE IF NOT EXISTS practice_db")
    print("✓ Database 'practice_db' created successfully!")

    # Create tables
    cursor.execute("USE practice_db")

    print("\nCreating tables...")

    # Create user table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id   INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            role ENUM('employee', 'manager') NOT NULL DEFAULT 'employee'
        )
    """)
    print("✓ Table 'user' created")

    # Create manager_employee table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS manager_employee (
            manager_id  INT NOT NULL,
            employee_id INT NOT NULL,
            PRIMARY KEY (manager_id, employee_id),
            CONSTRAINT foreign_key_manager
                FOREIGN KEY (manager_id) REFERENCES user(id)
                ON DELETE CASCADE,
            CONSTRAINT  foreign_key_employee
                FOREIGN KEY (employee_id) REFERENCES user(id)
                ON DELETE CASCADE
        )
    """)
    print("✓ Table 'manager_employee' created")

    # Create attendance_record table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_record (
            id             INT AUTO_INCREMENT PRIMARY KEY,
            user_id        INT NOT NULL,
            check_in_time  DATETIME NOT NULL,
            check_out_time DATETIME NULL,
            status         ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
            approved_by    INT NULL,
            approved_at    DATETIME NULL,
            CONSTRAINT foreign_key_user
                FOREIGN KEY (user_id) REFERENCES user(id)
                ON DELETE CASCADE,
            CONSTRAINT foreign_key_approver
                FOREIGN KEY (approved_by) REFERENCES user(id)
                ON DELETE SET NULL
        )
    """)
    print("✓ Table 'attendance_record' created")

    conn.commit()
    cursor.close()
    conn.close()

    print("\n========================================")
    print("✓ Database and tables created successfully!")
    print("========================================")
    print("\nNow run: python3 setup_database.py")

except mysql.connector.Error as e:
    print(f"✗ Error: {e}")
    print("\nIf you see 'Access denied', try running one of the fix scripts:")
    print("  ./fix_mysql_auth.sh")
    print("  or")
    print("  ./create_mysql_user.sh")
