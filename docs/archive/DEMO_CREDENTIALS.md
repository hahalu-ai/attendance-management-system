# Demo User Credentials

This document contains all user credentials for the Attendance Management System demo project.

**Database:** `practice_db`
**Password Hashing:** SHA-256

---

## Users Overview

| Username | Display Name | Role | Email | Status |
|----------|-------------|------|-------|--------|
| ylin | Yuchen Lin | Manager | yuchen.lin@example.com | Active |
| xlu | Xuanyu Lu | Contractor | xuanyu.lu@example.com | Active |
| jsmith | John Smith | Contractor | john.smith@example.com | Active |

---

## Detailed Credentials

### 1. Manager Account

**Username:** `ylin`
**Display Name:** Yuchen Lin
**Email:** yuchen.lin@example.com
**Role:** Manager
**Password:** *[Hashed - plaintext unknown]*
**Password Hash:** `31b262744de93020a5b39dcc098129ee091f6e209dc3121b9162c3768b2837ac`
**Created:** 2025-12-18 17:29:17

**Assigned Contractors:**
- xlu (Xuanyu Lu)
- jsmith (John Smith)

---

### 2. Contractor Account - Xuanyu Lu

**Username:** `xlu`
**Display Name:** Xuanyu Lu
**Email:** xuanyu.lu@example.com
**Role:** Contractor
**Password:** `password`
**Password Hash:** `5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8`
**Created:** 2025-12-18 17:29:17

**Manager:** ylin (Yuchen Lin)

---

### 3. Contractor Account - John Smith

**Username:** `jsmith`
**Display Name:** John Smith
**Email:** john.smith@example.com
**Role:** Contractor
**Password:** `password`
**Password Hash:** `5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8`
**Created:** 2025-12-18 17:29:17

**Manager:** ylin (Yuchen Lin)

---

## Login Instructions

### For Contractors (xlu or jsmith):
1. Navigate to the login page
2. Enter username: `xlu` or `jsmith`
3. Enter password: `password`
4. Click "Login"

### For Manager (ylin):
1. Navigate to the login page
2. Enter username: `ylin`
3. Enter password: *[Unknown - may need to reset via database or use password recovery]*

---

## Manager-Contractor Relationships

| Manager | Contractor | Assigned Date |
|---------|-----------|---------------|
| ylin | xlu | 2025-12-18 17:29:17 |
| ylin | jsmith | 2025-12-18 17:29:17 |

---

## API Authentication

### Login Endpoint
```bash
POST http://localhost:5001/api/auth/login
Content-Type: application/json

{
  "username": "xlu",
  "password": "password"
}
```

### Registration Endpoint
```bash
POST http://localhost:5001/api/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "display_name": "New User",
  "email": "newuser@example.com",
  "password": "password123",
  "user_level": "Contractor"
}
```

---

## Password Change

Users can change their password via the account settings or API:

```bash
PUT http://localhost:5001/api/users/<username>/change-password
Content-Type: application/json

{
  "old_password": "current_password",
  "new_password": "new_password"
}
```

---

## Security Notes

⚠️ **DEMO PROJECT ONLY** ⚠️

1. **Weak Hashing:** Currently using SHA-256 for password hashing. **NOT RECOMMENDED for production!**
   - Should use bcrypt, argon2, or PBKDF2 for production systems

2. **Simple Passwords:** Demo accounts use simple passwords like "password"
   - Production systems should enforce strong password policies

3. **No Rate Limiting:** No protection against brute force attacks
   - Production should implement rate limiting on login attempts

4. **No Session Management:** Basic authentication without proper session handling
   - Production should use JWT tokens or secure session management

---

## Resetting Manager Password

If you need to reset the manager password to a known value, you can run:

```bash
python3 <<EOF
from app.models.database import execute_query
from app.api.users import hash_password

new_password = "manager123"
hashed = hash_password(new_password)

execute_query(
    "UPDATE users SET password = %s WHERE username = 'ylin'",
    (hashed,),
    commit=True
)

print(f"Manager password reset to: {new_password}")
EOF
```

Or directly via MySQL:

```sql
USE practice_db;

-- Reset manager password to 'manager123'
UPDATE users
SET password = '0b14d501a594442a01c6859541bcb3e8164d183d32937b851835442f69d5c94e'
WHERE username = 'ylin';
```

---

## Database Direct Access

```bash
# Login to MySQL
mysql -u root practice_db

# View all users
SELECT username, display_name, email, user_level, created_at FROM users;

# View all password hashes
SELECT username, password FROM users;
```

---

**Last Updated:** 2025-12-18
**Document Purpose:** Demo/Testing credentials for development use only
