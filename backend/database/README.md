# Database Initialization Files

## Quick Start - Which File Should I Use?

### For Railway Deployment:
👉 **Use `init_database_railway.sql`** - Copy and paste into Railway's MySQL console

### For Local Development:
👉 **Run `python ../init_db.py`** - Automatic setup with progress messages

### If Having Trouble:
👉 **Follow `init_step_by_step.md`** - Run commands one at a time

---

## Files in This Directory

### 1. `init_database.sql` ❌ DO NOT USE
- **Status**: BROKEN for Railway
- **Issues**:
  - Missing `IF NOT EXISTS` clauses
  - Assumes database already exists
  - Cannot be run multiple times
  - Fails in Railway console
- **Keep for**: Reference only

### 2. `init_database_railway.sql` ✅ RECOMMENDED
- **Status**: Fixed and Railway-compatible
- **Features**:
  - Creates database automatically
  - Safe to run multiple times
  - Works in Railway console
  - Includes verification queries
- **Use for**: Railway deployment

### 3. `init_step_by_step.md` ✅ ALTERNATIVE
- **Type**: Documentation with individual SQL commands
- **Use when**: Railway SQL file doesn't work
- **How**: Copy-paste each command individually
- **Good for**: Debugging, understanding the schema

### 4. `add_qr_requests_table.sql`
- **Purpose**: Adds QR requests table to existing database
- **Note**: This table is already included in the main init files
- **Use**: Only if you already have a database and need to add this table

### 5. `../init_db.py` ✅ PYTHON SCRIPT
- **Type**: Python script for automatic initialization
- **Features**:
  - Auto-detects Railway environment variables
  - Shows progress messages
  - Verifies setup at the end
  - Error handling
- **Use for**: Local development, automation

---

## How to Initialize Database

### Option A: Railway Console (Easiest)

1. Open Railway project
2. Click on MySQL service
3. Go to "Data" or "Query" tab
4. Open `init_database_railway.sql` in your editor
5. Copy entire contents
6. Paste into Railway console
7. Execute
8. Done! ✅

### Option B: Python Script (Local)

```bash
# From the backend directory
cd backend
python init_db.py
```

This will:
- ✅ Create database
- ✅ Create all tables
- ✅ Insert sample data
- ✅ Show verification

### Option C: Step-by-Step (For Troubleshooting)

1. Open `init_step_by_step.md`
2. Follow the instructions
3. Run each SQL command individually
4. Verify each step completes

---

## Database Schema Overview

The initialization creates these tables:

### 1. `users`
- Stores user credentials and profile information
- Fields: username, display_name, email, password, user_level
- User levels: Manager, Contractor

### 2. `manager_assignments`
- Links managers to their contractors
- Foreign keys to users table
- Unique constraint on manager-contractor pairs

### 3. `time_entries`
- Attendance records with check-in/out times
- Status: Pending, Approved, Rejected
- Links to users for employee and approver

### 4. `qr_requests`
- QR code tokens for check-in/out workflow
- Expires after certain time
- Status: pending, used, failed, expired

---

## Sample Data Included

All init files include sample data for testing:

### Users:
| Username | Display Name | Role | Password |
|----------|--------------|------|----------|
| ylin | Yuchen Lin | Manager | password! |
| xlu | Xuanyu Lu | Contractor | password! |
| jsmith | John Smith | Contractor | password! |

### Manager Assignments:
- ylin manages xlu
- ylin manages jsmith

### Sample Time Entries:
- xlu: Dec 15, 9:00 AM - 5:30 PM (Approved)
- jsmith: Dec 15, 8:45 AM - 5:00 PM (Pending)

---

## Troubleshooting

### "Database already exists" error
✅ This is fine! The script will use the existing database.

### "Table already exists" error
❌ You're using the old `init_database.sql` file.
✅ Use `init_database_railway.sql` instead (has `IF NOT EXISTS`).

### "Duplicate entry" error on INSERT
❌ You're using the old file.
✅ Use the Railway version (has `INSERT IGNORE`).

### "Unknown database" error
❌ Database wasn't created.
✅ Make sure you run `CREATE DATABASE` first, or use the Railway SQL file.

### Connection refused / Access denied
❌ Wrong credentials or MySQL not running.
✅ Check environment variables and MySQL service status.

---

## Verification

After initialization, verify with:

```sql
-- List all tables
SHOW TABLES;

-- Count users
SELECT COUNT(*) FROM users;

-- View all users
SELECT username, display_name, user_level FROM users;

-- Check manager assignments
SELECT * FROM manager_assignments;
```

Expected results:
- 4 tables created
- 3 users inserted
- 2 manager assignments
- 2 sample time entries

---

## Need Help?

See the parent directory for:
- `DATABASE_INIT_FIX.md` - Detailed explanation of fixes
- `RAILWAY_TROUBLESHOOTING.md` - Railway-specific issues
- `RAILWAY_DEPLOYMENT_GUIDE.md` - Complete deployment guide
