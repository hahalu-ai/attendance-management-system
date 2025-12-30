# Database Learning Guide - Attendance Management System

This guide will help you understand how databases work, specifically focusing on this project's MySQL implementation and Python Flask backend.

---

## Table of Contents

1. [SQL Toolchain for Mac](#sql-toolchain-for-mac)
2. [Database Structure Deep Dive](#database-structure-deep-dive)
3. [Backend-Database Interaction](#backend-database-interaction)
4. [Key Concepts for Database Jobs](#key-concepts-for-database-jobs)
5. [Hands-On Learning Path](#hands-on-learning-path)
6. [Interview Preparation](#interview-preparation)

---

## SQL Toolchain for Mac

Here are the essential tools you need for working with MySQL on Mac:

### 1. MySQL Server (The Database Engine)

**What it does**: This is the actual database that stores your data.

**Installation**:
```bash
brew install mysql
```

**How to use**:
```bash
# Start MySQL server
brew services start mysql

# Stop MySQL server
brew services stop mysql

# Check if it's running
brew services list
```

**Why it matters**: Without this, you have no database. This is the core engine that processes SQL commands and stores data.

---

### 2. MySQL Command Line Client (Included with MySQL)

**What it does**: A terminal-based interface to interact with your database.

**How to use**:
```bash
# Connect to MySQL
mysql -u root -p

# Once connected, you can run SQL commands
mysql> SHOW DATABASES;
mysql> USE practice_db;
mysql> SHOW TABLES;
mysql> SELECT * FROM users;
mysql> exit;
```

**Common commands you'll use daily**:
```sql
-- See all databases
SHOW DATABASES;

-- Create a database
CREATE DATABASE practice_db;

-- Use a specific database
USE practice_db;

-- See all tables
SHOW TABLES;

-- See table structure
DESCRIBE users;

-- Run your init script
SOURCE /path/to/init_database.sql;
```

**Why it matters**: This is your main interface for running SQL commands, testing queries, and managing your database.

---

### 3. MySQL Workbench (Visual Database Tool)

**What it does**: A graphical interface (GUI) for MySQL - much easier for beginners than command line.

**Installation**:
```bash
brew install --cask mysql-workbench
```

**Features**:
- Visual database designer
- Query editor with syntax highlighting
- Table data viewer/editor
- Database diagram creator
- Query execution and results

**Why it matters**: Makes database work visual and intuitive. You can see tables, run queries, and view results in a nice interface. Great for learning!

---

### 4. mycli (Better Command Line Experience)

**What it does**: Enhanced MySQL command line with auto-completion and syntax highlighting.

**Installation**:
```bash
brew install mycli
```

**How to use**:
```bash
# Connect to MySQL (better than regular mysql client)
mycli -u root -p

# It has auto-completion - just start typing and press TAB
mycli> SELECT * FROM u[TAB]  # autocompletes to 'users'
```

**Why it matters**: If you prefer terminal work, this makes it much more pleasant with auto-complete and colored output.

---

### 5. TablePlus (Modern Database Client - Optional but Recommended)

**What it does**: Modern, beautiful database GUI - easier to use than MySQL Workbench.

**Installation**:
- Download from https://tableplus.com (has free version)

**Why it matters**: Cleaner interface, faster, supports multiple databases (PostgreSQL, SQLite, etc.). Great for day-to-day work.

---

### 6. DBeaver (Free Alternative to TablePlus)

**What it does**: Another excellent free database management tool.

**Installation**:
```bash
brew install --cask dbeaver-community
```

**Why it matters**: Completely free, powerful, and supports many database types.

---

### Quick Setup Workflow for This Project

```bash
# 1. Install MySQL
brew install mysql

# 2. Start MySQL
brew services start mysql

# 3. Secure your installation (set root password)
mysql_secure_installation

# 4. Login to MySQL
mysql -u root -p

# 5. Create your database
CREATE DATABASE practice_db;

# 6. Exit and run your init script
exit;
mysql -u root -p practice_db < /path/to/attendance-management-system/backend/database/init_database.sql

# 7. Verify it worked
mysql -u root -p
USE practice_db;
SHOW TABLES;
```

---

## Database Structure Deep Dive

### Overview

The database has **4 tables** that work together to manage attendance:
1. **users** - Who is in the system
2. **manager_assignments** - Who manages whom
3. **time_entries** - Clock in/out records
4. **qr_requests** - QR code tokens for check-in/out

Reference: `database/init_database.sql`

---

### Table 1: Users Table

**File reference**: `database/init_database.sql:10-21`

```sql
CREATE TABLE users (
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
);
```

**Breaking it down**:

- **`id INT AUTO_INCREMENT PRIMARY KEY`**
  - `INT`: Integer number
  - `AUTO_INCREMENT`: Database automatically generates 1, 2, 3, etc.
  - `PRIMARY KEY`: Unique identifier for each row. No two rows can have same ID
  - Why: Every row needs a unique identifier

- **`username VARCHAR(50) NOT NULL UNIQUE`**
  - `VARCHAR(50)`: Text up to 50 characters
  - `NOT NULL`: Must have a value, can't be empty
  - `UNIQUE`: No two users can have the same username
  - Why: Usernames are used to identify users throughout the system

- **`user_level ENUM('Manager', 'Contractor') NOT NULL`**
  - `ENUM`: Can only be one of the listed values
  - Why: Enforces data consistency - can't accidentally put "worker" or "admin"

- **`created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`**
  - `TIMESTAMP`: Stores date and time
  - `DEFAULT CURRENT_TIMESTAMP`: Automatically sets to current time when row is created
  - Why: Track when accounts were created

- **`updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`**
  - `ON UPDATE CURRENT_TIMESTAMP`: Automatically updates to current time whenever row is modified
  - Why: Track when account info was last changed

- **`INDEX idx_username (username)`**
  - `INDEX`: Creates a fast lookup structure (like a book index)
  - Why: Makes searches by username much faster (important for logins)
  - Technical: Without index, database scans every row. With index, it's instant.

---

### Table 2: Manager Assignments

**File reference**: `database/init_database.sql:27-43`

```sql
CREATE TABLE manager_assignments (
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
);
```

**Key concepts**:

- **`UNIQUE KEY unique_assignment (manager_username, contractor_username)`**
  - `UNIQUE KEY`: Prevents duplicate manager-contractor pairs
  - Why: Can't assign the same contractor to the same manager twice

- **`FOREIGN KEY (manager_username) REFERENCES users(username)`**
  - `FOREIGN KEY`: Links this table to the users table
  - `REFERENCES users(username)`: manager_username must exist in users.username
  - Why: Can't assign a manager who doesn't exist

- **`ON DELETE CASCADE`**
  - What it does: If a user is deleted from users table, all their assignments are automatically deleted
  - Example: Delete user "ylin" → all rows where manager_username='ylin' are deleted
  - Why: Prevents orphaned data (assignments to non-existent users)

- **`ON UPDATE CASCADE`**
  - What it does: If username changes in users table, it automatically updates here too
  - Example: Rename "ylin" to "ylin2" → all manager_username='ylin' become 'ylin2'
  - Why: Keeps data consistent across tables

**Real-world example**:
```sql
-- This works:
INSERT INTO manager_assignments (manager_username, contractor_username)
VALUES ('ylin', 'xlu');

-- This FAILS because 'nonexistent' is not in users table:
INSERT INTO manager_assignments (manager_username, contractor_username)
VALUES ('nonexistent', 'xlu');
```

---

### Table 3: Time Entries

**File reference**: `database/init_database.sql:49-71`

```sql
CREATE TABLE time_entries (
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
);
```

**Important concepts**:

- **`out_time DATETIME NULL`**
  - `NULL`: Can be empty
  - Why: When you clock in, there's no clock out time yet
  - Database logic: NULL out_time means "currently clocked in"

- **`status ENUM('Pending', 'Approved', 'Rejected') NOT NULL DEFAULT 'Pending'`**
  - `DEFAULT 'Pending'`: If not specified, automatically set to 'Pending'
  - Why: New time entries need manager approval

- **`approved_by VARCHAR(50) NULL`**
  - Why NULL: Not approved yet when first created

- **`CONSTRAINT fk_approver ... ON DELETE SET NULL`**
  - `ON DELETE SET NULL`: If approver user is deleted, this becomes NULL (not CASCADE!)
  - Why: Keep time entry record even if manager account is deleted
  - Result: You still see the time entry, but don't know who approved it

**Indexes explained**:
- **`INDEX idx_username_date (username, in_time)`**
  - Composite index: Optimized for searching by username AND sorting by date
  - Used in queries like: "Get all time entries for user X in December"
  - Performance: Makes this query instant instead of slow

---

### Table 4: QR Requests

**File reference**: `database/init_database.sql:77-98`

```sql
CREATE TABLE qr_requests (
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
);
```

**Purpose**: QR code workflow
1. Manager generates QR code with token
2. Worker scans QR code
3. System validates token and records check-in/out

**Important index**:
- **`INDEX idx_status_expires (status, expires_at)`**
  - Purpose: Quickly find expired QR codes to clean up
  - Query: "Find all pending QR codes that expired"
  - Why composite: Filters by status AND date together

---

### Sample Data Section

**File reference**: `database/init_database.sql:105-118`

```sql
INSERT INTO users (username, display_name, email, password, user_level) VALUES
('ylin', 'Yuchen Lin', 'yuchen.lin@example.com', '$2y$10$example_hashed_password', 'Manager'),
('xlu', 'Xuanyu Lu', 'xuanyu.lu@example.com', '$2y$10$example_hashed_password', 'Contractor'),
('jsmith', 'John Smith', 'john.smith@example.com', '$2y$10$example_hashed_password', 'Contractor');
```

**Security note**:
- `'$2y$10$example_hashed_password'` - This is bcrypt hash format
- **Never store plain passwords** - always hash them
- The `$2y$10$` prefix indicates bcrypt algorithm with cost factor 10

---

### Understanding JOINs with Example Queries

**File reference**: `database/init_database.sql:128-135`

**Query: View manager-contractor relationships**
```sql
SELECT
    ma.manager_username,
    u1.display_name AS manager_name,
    ma.contractor_username,
    u2.display_name AS contractor_name
FROM manager_assignments ma
JOIN users u1 ON ma.manager_username = u1.username
JOIN users u2 ON ma.contractor_username = u2.username;
```

**Breaking down JOINs**:
- `FROM manager_assignments ma` - Start with assignments table, alias as 'ma'
- `JOIN users u1 ON ma.manager_username = u1.username` - Get manager's full info
- `JOIN users u2 ON ma.contractor_username = u2.username` - Get contractor's full info
- **Result**: Instead of just usernames, you get display names too

**Visualization**:
```
manager_assignments:    users (u1):           users (u2):
manager_username   →    username='ylin'       username='xlu'
contractor_username →                         display_name='Xuanyu Lu'

Result:
manager_username='ylin', manager_name='Yuchen Lin',
contractor_username='xlu', contractor_name='Xuanyu Lu'
```

---

## Backend-Database Interaction

Your backend is built with **Python Flask** and uses **MySQL**.

### Architecture Overview

```
User Request → Flask API → database.py → MySQL Database → Response
```

### 1. Database Connection Layer

**File reference**: `app/models/database.py:5-12`

```python
def get_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**Config.get_db_config())
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise
```

**What this does**:
- `mysql.connector.connect()` - Opens a connection to MySQL
- `**Config.get_db_config()` - Gets credentials from environment variables
- **Why it matters**: Every database operation needs a connection

**Configuration** - `app/config.py:26-34`:
```python
@staticmethod
def get_db_config():
    return {
        'host': Config.DB_HOST,      # localhost
        'port': Config.DB_PORT,      # 3306
        'user': Config.DB_USER,      # root
        'password': Config.DB_PASSWORD,
        'database': Config.DB_NAME   # practice_db
    }
```

**Where credentials come from**:
- Stored in `.env` file (not committed to Git)
- Loaded by `python-dotenv` package
- **Security best practice**: Never hardcode passwords

---

### 2. Query Execution Helper

**File reference**: `app/models/database.py:14-52`

```python
def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)  # Returns rows as dictionaries

    try:
        cursor.execute(query, params or ())

        if commit:
            conn.commit()
            return cursor.lastrowid

        if fetch_one:
            result = cursor.fetchone()
            return result

        if fetch_all:
            result = cursor.fetchall()
            return result

    except Error as e:
        if commit:
            conn.rollback()  # Undo changes if error
        raise e
    finally:
        cursor.close()
        conn.close()
```

**Key concepts for database jobs**:

- **cursor**: Think of it as a pointer that executes SQL and retrieves results
- **dictionary=True**: Returns `{'username': 'ylin', 'email': '...'}` instead of `('ylin', '...')`
- **params**: SQL injection prevention
- **commit()**: Saves changes to database (INSERT, UPDATE, DELETE need this)
- **rollback()**: Undoes changes if error occurs
- **lastrowid**: Returns ID of newly inserted row

**SQL Injection Prevention Example**:
```python
# DANGEROUS (SQL injection vulnerable):
query = f"SELECT * FROM users WHERE username = '{username}'"

# SAFE (parameterized query):
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))
```

---

### 3. Real Example: Check-in Endpoint

**File reference**: `app/api/attendance.py:36-101`

Let me show you a complete flow from HTTP request to database:

**Step 1: User sends request**
```http
POST /attendance/check-in
Content-Type: application/json

{
  "username": "xlu"
}
```

**Step 2: Flask receives it** (Line 36-43)
```python
@attendance_bp.route('/check-in', methods=['POST'])
def check_in():
    data = request.get_json() or {}
    username = data.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400
```

**Step 3: Query database for user** (Line 46-51)
```python
user_query = "SELECT username, user_level FROM users WHERE username = %s"
user = execute_query(user_query, (username,), fetch_one=True)

if not user:
    return jsonify({"error": "User not found"}), 404
```

**What happens in database**:
```sql
-- This SQL is executed:
SELECT username, user_level FROM users WHERE username = 'xlu'

-- Returns:
{'username': 'xlu', 'user_level': 'Contractor'}
```

**Step 4: Check for existing check-in** (Line 54-62)
```python
open_query = """
    SELECT id FROM time_entries
    WHERE username = %s AND out_time IS NULL
    ORDER BY in_time DESC LIMIT 1
"""
open_entry = execute_query(open_query, (username,), fetch_one=True)

if open_entry:
    return jsonify({"error": "You have an open time entry"}), 400
```

**Database logic**:
- `out_time IS NULL` - Find records where user hasn't clocked out
- If found, can't clock in again

**Step 5A: If Manager - Auto-approve** (Line 64-75)
```python
if user['user_level'] == 'Manager':
    insert_query = """
        INSERT INTO time_entries
        (username, in_time, status, approved_by, approved_at)
        VALUES (%s, NOW(), 'Approved', %s, NOW())
    """
    entry_id = execute_query(insert_query, (username, username), commit=True)
    return jsonify({
        "message": "Check-in successful (auto-approved)",
        "entry_id": entry_id
    }), 201
```

**Database transaction**:
```sql
-- This SQL is executed:
INSERT INTO time_entries
(username, in_time, status, approved_by, approved_at)
VALUES ('ylin', '2025-12-20 15:30:00', 'Approved', 'ylin', '2025-12-20 15:30:00')

-- commit=True saves it to database
-- Returns: entry_id (e.g., 15)
```

**Step 5B: If Contractor - Needs approval** (Line 78-98)
```python
# Verify contractor has a manager
manager_query = """
    SELECT manager_username FROM manager_assignments
    WHERE contractor_username = %s
"""
manager = execute_query(manager_query, (username,), fetch_one=True)

if not manager:
    return jsonify({"error": "No manager assigned"}), 403

# Create pending entry
insert_query = """
    INSERT INTO time_entries
    (username, in_time, status)
    VALUES (%s, NOW(), 'Pending')
"""
entry_id = execute_query(insert_query, (username,), commit=True)
return jsonify({
    "message": "Check-in submitted. Waiting for manager approval.",
    "entry_id": entry_id
}), 201
```

**Database flow**:
1. Check `manager_assignments` table
2. If contractor has manager, create time entry with `status='Pending'`
3. Manager sees this in their "pending approvals" list

---

### 4. Complex Query Example: Monthly Summary

**File reference**: `app/api/attendance.py:261-276`

This is an advanced example showing data aggregation:

```python
query = """
    SELECT
        DATE(in_time) AS work_date,
        MIN(in_time) AS first_check_in,
        MAX(out_time) AS last_check_out,
        SUM(TIMESTAMPDIFF(MINUTE, in_time, out_time)) / 60.0 AS hours_worked
    FROM time_entries
    WHERE username = %s
      AND status = 'Approved'
      AND out_time IS NOT NULL
      AND in_time >= %s
      AND in_time < %s
    GROUP BY work_date
    ORDER BY work_date
"""
entries = execute_query(query, (username, month_start, next_month_start), fetch_all=True)
```

**Breaking down the SQL**:

1. `DATE(in_time) AS work_date` - Convert timestamp to date (2025-12-20)
2. `MIN(in_time)` - Earliest check-in of the day
3. `MAX(out_time)` - Latest check-out of the day
4. `TIMESTAMPDIFF(MINUTE, in_time, out_time)` - Calculate minutes worked
5. `SUM(...) / 60.0` - Total hours for that day
6. `GROUP BY work_date` - One row per day
7. `status = 'Approved'` - Only count approved time
8. `out_time IS NOT NULL` - Only count completed shifts

**Result example**:
```python
[
    {
        'work_date': datetime.date(2025, 12, 15),
        'first_check_in': datetime(2025, 12, 15, 9, 0, 0),
        'last_check_out': datetime(2025, 12, 15, 17, 30, 0),
        'hours_worked': 8.5
    },
    {
        'work_date': datetime.date(2025, 12, 16),
        'first_check_in': datetime(2025, 12, 16, 8, 45, 0),
        'last_check_out': datetime(2025, 12, 16, 17, 0, 0),
        'hours_worked': 8.25
    }
]
```

---

### 5. Transaction Safety Example: Approval Endpoint

**File reference**: `app/api/attendance.py:196-245`

This shows how database transactions prevent data corruption:

```python
try:
    # Verify manager exists
    user = execute_query(user_query, (manager_username,), fetch_one=True)

    # Verify manager has authority over this entry
    entry = execute_query(entry_query, (entry_id, manager_username), fetch_one=True)

    # Update the entry
    update_query = """
        UPDATE time_entries
        SET status = %s, approved_by = %s, approved_at = NOW(), notes = %s
        WHERE id = %s
    """
    execute_query(update_query, (status, manager_username, notes, entry_id), commit=True)

    return jsonify({"message": f"Entry {status.lower()} successfully"}), 200

except Exception as e:
    return jsonify({"error": str(e)}), 500
```

**Transaction flow**:
1. All checks happen first (verify manager, verify authority)
2. Only if all checks pass, UPDATE is executed
3. If ANY step fails, exception is raised
4. `conn.rollback()` in execute_query undoes partial changes
5. **Result**: Database is never left in inconsistent state

**Why this matters for database jobs**:
- **ACID properties**: Atomicity, Consistency, Isolation, Durability
- **Atomicity**: All-or-nothing - either everything succeeds or nothing changes
- **Consistency**: Database rules (foreign keys, constraints) are always enforced
- **Real-world impact**: Prevents data corruption

---

## Key Concepts for Database Jobs

### 1. Database Design Principles Demonstrated

- **Normalization**: User info in one table, relationships in another (no duplication)
- **Primary Keys**: Every table has unique identifier
- **Foreign Keys**: Maintain relationships between tables
- **Indexes**: Speed up common queries
- **Data Types**: ENUM for fixed choices, TIMESTAMP for dates, VARCHAR for text

### 2. Important SQL Concepts in This Project

- **Joins**: Combine data from multiple tables
- **Aggregation**: SUM, COUNT, MIN, MAX for statistics
- **Filtering**: WHERE, AND, OR conditions
- **Grouping**: GROUP BY for summaries
- **Transactions**: COMMIT/ROLLBACK for data safety

### 3. Backend-Database Interaction Pattern

```
Request → Validation → Query Database → Process Results → Response
```

### 4. Database Security

- Parameterized queries (prevent SQL injection)
- Password hashing (bcrypt)
- Foreign key constraints (prevent bad data)
- Transaction rollback (prevent corruption)

### 5. Important Database Concepts Demonstrated

**1. Indexes improve performance**
```sql
INDEX idx_username_date (username, in_time)
```
- Used in: "Get all time entries for user X in December"
- Without index: Scans ALL rows (slow)
- With index: Direct lookup (instant)

**2. Foreign keys enforce data integrity**
```sql
FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
```
- Can't create time entry for non-existent user
- If user deleted, their time entries auto-delete
- **Interview answer**: "Foreign keys maintain referential integrity"

**3. NULL handling**
```sql
out_time IS NULL  -- Find people currently clocked in
```
- NULL means "no value" (different from empty string or 0)
- Used for: optional fields, pending data

**4. Parameterized queries prevent SQL injection**
```python
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
```
- **Never** concatenate user input into SQL
- Database escapes special characters automatically

---

## Hands-On Learning Path

### Week 1: Basics

```bash
# 1. Set up MySQL
brew install mysql
brew services start mysql
mysql_secure_installation

# 2. Create the database
mysql -u root -p
CREATE DATABASE practice_db;
SOURCE /path/to/init_database.sql;

# 3. Practice basic queries
USE practice_db;
SELECT * FROM users;
DESCRIBE users;
SHOW TABLES;
```

### Week 2: Queries

```sql
-- Join practice
SELECT u.display_name, te.in_time, te.status
FROM users u
JOIN time_entries te ON u.username = te.username;

-- Aggregation practice
SELECT username, COUNT(*) as total_entries
FROM time_entries
GROUP BY username;

-- Complex filtering
SELECT * FROM time_entries
WHERE status = 'Pending'
  AND in_time >= '2025-12-01'
ORDER BY in_time DESC;
```

### Week 3: Modifications

```sql
-- Insert new contractor
INSERT INTO users (username, display_name, email, password, user_level)
VALUES ('jdoe', 'Jane Doe', 'jane@example.com', 'hashed_password', 'Contractor');

-- Assign to manager
INSERT INTO manager_assignments (manager_username, contractor_username)
VALUES ('ylin', 'jdoe');

-- Update status
UPDATE time_entries
SET status = 'Approved', approved_by = 'ylin', approved_at = NOW()
WHERE id = 5;
```

### Week 4: Advanced

```sql
-- Subqueries
SELECT * FROM users
WHERE username IN (
    SELECT contractor_username
    FROM manager_assignments
    WHERE manager_username = 'ylin'
);

-- Date functions
SELECT
    DATE_FORMAT(in_time, '%Y-%m') as month,
    COUNT(*) as entries
FROM time_entries
GROUP BY month;

-- Stored procedures (for efficiency)
DELIMITER //
CREATE PROCEDURE GetUserStats(IN user_name VARCHAR(50))
BEGIN
    SELECT
        COUNT(*) as total_entries,
        SUM(CASE WHEN status='Approved' THEN 1 ELSE 0 END) as approved
    FROM time_entries
    WHERE username = user_name;
END //
DELIMITER ;

-- Use the procedure
CALL GetUserStats('xlu');
```

---

## Interview Preparation

### Topics to Master Based on This Project

1. **Explain this database schema** - Practice describing the 4 tables and their relationships
2. **What are foreign keys?** - Referential integrity, CASCADE vs SET NULL behavior
3. **Why use indexes?** - Query performance, when to use composite indexes
4. **ACID properties** - Atomicity, Consistency, Isolation, Durability
5. **Normalization** - Why separate users from time_entries
6. **JOIN types** - INNER, LEFT, RIGHT (this project uses INNER and LEFT)
7. **Aggregation functions** - SUM, COUNT, AVG, MIN, MAX
8. **Transaction management** - COMMIT, ROLLBACK, why they matter
9. **SQL injection** - How parameterized queries prevent it
10. **Database optimization** - Indexes, query analysis, EXPLAIN

### Practice Questions You Can Answer Now

1. **"How would you find all contractors managed by 'ylin'?"**
```sql
SELECT contractor_username
FROM manager_assignments
WHERE manager_username = 'ylin';
```

2. **"How do you prevent the same contractor from clocking in twice?"**
```sql
SELECT id FROM time_entries
WHERE username = 'xlu' AND out_time IS NULL;
-- If this returns a row, they're already clocked in
```

3. **"What happens if you delete a manager who has approved time entries?"**
- Answer: The `approved_by` field uses `ON DELETE SET NULL`, so the time entry remains but `approved_by` becomes NULL. The time entry itself is preserved.

4. **"How would you calculate total hours worked this month?"**
```sql
SELECT
    username,
    SUM(TIMESTAMPDIFF(HOUR, in_time, out_time)) as total_hours
FROM time_entries
WHERE status = 'Approved'
  AND in_time >= '2025-12-01'
  AND in_time < '2026-01-01'
GROUP BY username;
```

5. **"Why use ENUM for status instead of VARCHAR?"**
- Answer: ENUM enforces data integrity - only allows predefined values ('Pending', 'Approved', 'Rejected'). Prevents typos like 'Approvd' or inconsistent values like 'approved' vs 'Approved'. Also more storage-efficient.

### Common Interview Scenarios

**Scenario: "Design a database for an attendance system"**
- Walk through the 4 tables in this project
- Explain relationships: Users → Manager Assignments (many-to-many), Users → Time Entries (one-to-many)
- Discuss normalization: Why not put manager info directly in time_entries table?
- Mention indexes: Why index on (username, in_time) for time_entries

**Scenario: "Optimize this slow query"**
```sql
-- Slow:
SELECT * FROM time_entries WHERE username = 'xlu' ORDER BY in_time DESC;

-- Fast (uses index):
-- Already optimized! The idx_username_date (username, in_time) index makes this instant
```

**Scenario: "Handle concurrent check-ins"**
- Use transactions with proper isolation levels
- Check for existing open entry within the same transaction
- Consider database-level locks if needed

---

## Additional Resources

### Documentation
- [MySQL Official Documentation](https://dev.mysql.com/doc/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Python MySQL Connector](https://dev.mysql.com/doc/connector-python/en/)

### Learning Platforms
- [SQLBolt](https://sqlbolt.com/) - Interactive SQL tutorial
- [Mode SQL Tutorial](https://mode.com/sql-tutorial/) - Advanced SQL concepts
- [LeetCode Database Problems](https://leetcode.com/problemset/database/) - Practice SQL problems

### Books
- "Learning SQL" by Alan Beaulieu
- "Database Design for Mere Mortals" by Michael J. Hernandez
- "High Performance MySQL" by Baron Schwartz

---

## Next Steps

1. Set up MySQL on your Mac using the toolchain guide above
2. Load the database schema and sample data
3. Practice the queries in the "Useful Queries" section (database/init_database.sql:122-149)
4. Try writing your own queries to answer questions like:
   - "Who checked in today?"
   - "How many pending approvals does manager 'ylin' have?"
   - "What's the average hours worked per day for contractor 'xlu'?"
5. Modify the Python code to add a new endpoint
6. Read about database indexing, normalization, and ACID properties

---

## Project File Reference

- **Database Schema**: `backend/database/init_database.sql`
- **Database Connection**: `backend/app/models/database.py`
- **API Endpoints**: `backend/app/api/attendance.py`
- **Configuration**: `backend/app/config.py`
- **Environment Variables**: `backend/.env`

---

**Good luck with your database learning journey!** Feel free to experiment with the code and database - that's the best way to learn.
