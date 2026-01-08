from db import get_connection

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Clear existing data
        print("Clearing existing data...")
        cursor.execute("DELETE FROM attendance_record")
        cursor.execute("DELETE FROM manager_employee")
        cursor.execute("DELETE FROM user")

        # Reset auto increment
        cursor.execute("ALTER TABLE user AUTO_INCREMENT = 1")

        # Insert Manager
        print("Inserting Manager 'Boss'...")
        cursor.execute("INSERT INTO user (name, role) VALUES ('Boss', 'manager')")

        # Insert Employees A, B, C, D
        print("Inserting Employees A, B, C, D...")
        cursor.execute("""
            INSERT INTO user (name, role) VALUES
            ('Employee A', 'employee'),
            ('Employee B', 'employee'),
            ('Employee C', 'employee'),
            ('Employee D', 'employee')
        """)

        # Link Boss (id=1) to all employees (ids 2,3,4,5)
        print("Linking Boss to all employees...")
        cursor.execute("""
            INSERT INTO manager_employee (manager_id, employee_id) VALUES
            (1, 2),
            (1, 3),
            (1, 4),
            (1, 5)
        """)

        conn.commit()

        # Verify the data
        print("\n=== Users ===")
        cursor.execute("SELECT * FROM user")
        for row in cursor.fetchall():
            print(row)

        print("\n=== Manager-Employee Relationships ===")
        cursor.execute("SELECT * FROM manager_employee")
        for row in cursor.fetchall():
            print(row)

        print("\nDatabase setup completed successfully!")

    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    setup_database()
