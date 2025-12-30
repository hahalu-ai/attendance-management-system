# Database Initialization - Step by Step

If the full SQL file fails, run these commands **one at a time** in Railway's MySQL console.

## Why the original file fails:

1. **`USE attendance_system;` fails** if database doesn't exist
2. **`CREATE TABLE` fails** if tables already exist (no `IF NOT EXISTS`)
3. **`INSERT` fails** if data already exists (duplicate key errors)
4. **Railway console limitations** - some consoles don't allow large multi-statement files

---

## Solution: Run These Commands One at a Time

### Step 1: Create Database
```sql
CREATE DATABASE IF NOT EXISTS attendance_system;
```

### Step 2: Select Database
```sql
USE attendance_system;
```

### Step 3: Create Users Table
```sql
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
);
```

### Step 4: Create Manager Assignments Table
```sql
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
);
```

### Step 5: Create Time Entries Table
```sql
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
);
```

### Step 6: Create QR Requests Table
```sql
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
);
```

### Step 7: Insert Sample Users
```sql
INSERT IGNORE INTO users (username, display_name, email, password, user_level) VALUES
('ylin', 'Yuchen Lin', 'yuchen.lin@example.com', 'f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7', 'Manager'),
('xlu', 'Xuanyu Lu', 'xuanyu.lu@example.com', 'f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7', 'Contractor'),
('jsmith', 'John Smith', 'john.smith@example.com', 'f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7', 'Contractor');
```

### Step 8: Assign Managers
```sql
INSERT IGNORE INTO manager_assignments (manager_username, contractor_username) VALUES
('ylin', 'xlu'),
('ylin', 'jsmith');
```

### Step 9: Insert Sample Time Entries (Optional)
```sql
INSERT IGNORE INTO time_entries (id, username, in_time, out_time, status, approved_by, approved_at) VALUES
(1, 'xlu', '2025-12-15 09:00:00', '2025-12-15 17:30:00', 'Approved', 'ylin', '2025-12-15 18:00:00'),
(2, 'jsmith', '2025-12-15 08:45:00', '2025-12-15 17:00:00', 'Pending', NULL, NULL);
```

### Step 10: Verify Setup
```sql
SHOW TABLES;
```

```sql
SELECT COUNT(*) as user_count FROM users;
```

```sql
SELECT username, display_name, user_level FROM users;
```

---

## Test Credentials

After initialization, you can login with:

| Username | Password | Role |
|----------|----------|------|
| ylin | password! | Manager |
| xlu | password! | Contractor |
| jsmith | password! | Contractor |

---

## Troubleshooting

### If you get "Table already exists" error:
- This is fine! Just continue to the next step
- Or use the Railway-compatible file which has `CREATE TABLE IF NOT EXISTS`

### If you get "Duplicate entry" error on INSERT:
- This is fine! The data is already there
- The new file uses `INSERT IGNORE` to skip duplicates

### If you need to reset everything:
Run these commands first:
```sql
USE attendance_system;
DROP TABLE IF EXISTS qr_requests;
DROP TABLE IF EXISTS time_entries;
DROP TABLE IF EXISTS manager_assignments;
DROP TABLE IF EXISTS users;
```

Then start from Step 3 again.

---

## Quick Copy-Paste Version

If Railway's console supports it, you can copy-paste this entire block:

```sql
CREATE DATABASE IF NOT EXISTS attendance_system;
USE attendance_system;

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
);

CREATE TABLE IF NOT EXISTS manager_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    manager_username VARCHAR(50) NOT NULL,
    contractor_username VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_assignment (manager_username, contractor_username),
    CONSTRAINT fk_manager_username FOREIGN KEY (manager_username) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_contractor_username FOREIGN KEY (contractor_username) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_manager (manager_username),
    INDEX idx_contractor (contractor_username)
);

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
    CONSTRAINT fk_time_entry_user FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_approver FOREIGN KEY (approved_by) REFERENCES users(username) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_username_date (username, in_time),
    INDEX idx_status (status),
    INDEX idx_approved_by (approved_by)
);

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
    CONSTRAINT fk_qr_manager FOREIGN KEY (manager_username) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_qr_worker FOREIGN KEY (worker_username) REFERENCES users(username) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_token (token),
    INDEX idx_status_expires (status, expires_at),
    INDEX idx_worker (worker_username)
);

INSERT IGNORE INTO users (username, display_name, email, password, user_level) VALUES
('ylin', 'Yuchen Lin', 'yuchen.lin@example.com', 'f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7', 'Manager'),
('xlu', 'Xuanyu Lu', 'xuanyu.lu@example.com', 'f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7', 'Contractor'),
('jsmith', 'John Smith', 'john.smith@example.com', 'f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7', 'Contractor');

INSERT IGNORE INTO manager_assignments (manager_username, contractor_username) VALUES
('ylin', 'xlu'),
('ylin', 'jsmith');

SHOW TABLES;
SELECT username, display_name, user_level FROM users;
```
