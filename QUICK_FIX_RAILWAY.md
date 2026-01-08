# Quick Fix: Railway Database Connection

## The Problem

You're seeing: `ERROR 2005: Unknown MySQL server host '$MYSQLHOST'`

This means Railway environment variables **are not set** in your web service.

---

## The Solution (3 Steps)

### Step 1: Push the Updated Code

```bash
cd /home/yuchen/codespace/attendance-management-system
git add backend/app/__init__.py backend/app/config.py
git commit -m "Add Railway MySQL support and debug endpoints"
git push
```

**Wait** for Railway to finish deploying (check Deployments tab, wait for green checkmark).

---

### Step 2: Check What Variables Railway Sees

Visit this URL (replace `your-app` with your Railway app URL):

```
https://your-app.railway.app/debug-config
```

**You'll see something like this:**

**GOOD (Variables are set):**
```json
{
  "variables_found": {
    "MYSQLHOST": "viaduct-fra1-abc123.railway.app",
    "MYSQLPORT": "3306",
    "MYSQLUSER": "root",
    "MYSQLPASSWORD": "***"
  },
  "config_values_used": {
    "DB_HOST": "viaduct-fra1-abc123.railway.app",
    "DB_PORT": 3306
  }
}
```
✅ **You're good!** Go to Step 3.

**BAD (Variables NOT set):**
```json
{
  "variables_found": {
    "MYSQLHOST": "NOT SET",
    "DB_HOST": "NOT SET"
  },
  "config_values_used": {
    "DB_HOST": "localhost"
  }
}
```
❌ **Need to fix** - Follow "How to Fix" below.

---

### Step 3: Test Database Connection

Visit:
```
https://your-app.railway.app/test-db
```

**Success:**
```json
{
  "status": "success",
  "message": "Database connection successful!"
}
```
✅ **Done!** Connection works. Now initialize the database.

**Still Failing:**
```json
{
  "status": "error",
  "message": "Unknown database 'attendance_system'"
}
```
👉 Database doesn't exist. Create it:
- Go to Railway MySQL service → Data tab
- Run: `CREATE DATABASE attendance_system;`
- OR use Railway's default: Set `MYSQLDATABASE=railway` in variables

---

## How to Fix: Add MySQL Variables to Web Service

If `/debug-config` showed "NOT SET", you need to add the MySQL variables:

### In Railway Dashboard:

1. **Go to MySQL Service**
   - Click your MySQL database service
   - Go to "Variables" or "Connect" tab
   - You'll see: `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`
   - **Copy these values** (write them down)

2. **Go to Web Service**
   - Click your Python web service
   - Go to "Variables" tab

3. **Add Variables Using Reference** (Recommended):
   - Click "New Variable" → "Add a Reference"
   - Select your MySQL service
   - Railway will automatically link the variables

   **OR Add Manually:**
   - Click "New Variable"
   - Add each one from step 1:
     ```
     Name: MYSQLHOST
     Value: <paste from MySQL service>

     Name: MYSQLPORT
     Value: 3306

     Name: MYSQLUSER
     Value: <paste from MySQL service>

     Name: MYSQLPASSWORD
     Value: <paste from MySQL service>

     Name: MYSQLDATABASE
     Value: attendance_system
     ```

4. **Also add these application variables:**
   ```
   SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_hex(32))">
   DEBUG=False
   CORS_ORIGINS=*
   ```

5. **Save and wait** for Railway to redeploy

6. **Test again** - visit `/debug-config` and `/test-db`

---

## Visual Guide: What Should Happen

```
┌─────────────────────────────────────────┐
│  Railway MySQL Service                  │
│  ┌───────────────────────────────────┐  │
│  │ MYSQLHOST: viaduct-fra1.railway   │  │
│  │ MYSQLPORT: 3306                   │  │
│  │ MYSQLUSER: root                   │  │
│  │ MYSQLPASSWORD: xyz123             │  │
│  │ MYSQLDATABASE: railway            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
                    ↓
         (Link/Reference or Copy)
                    ↓
┌─────────────────────────────────────────┐
│  Railway Web Service (Python App)       │
│  ┌───────────────────────────────────┐  │
│  │ Variables:                        │  │
│  │   MYSQLHOST=viaduct-fra1.railway  │  │  ← Should appear here
│  │   MYSQLPORT=3306                  │  │
│  │   MYSQLUSER=root                  │  │
│  │   MYSQLPASSWORD=xyz123            │  │
│  │   MYSQLDATABASE=attendance_system │  │
│  │   SECRET_KEY=abc...               │  │
│  │   DEBUG=False                     │  │
│  └───────────────────────────────────┘  │
│                                          │
│  Code reads these variables:             │
│  config.py uses MYSQLHOST → DB_HOST     │
│  App connects to MySQL ✅                │
└─────────────────────────────────────────┘
```

---

## After Connection Works

1. **Create the database** (if using `attendance_system`):
   ```sql
   CREATE DATABASE IF NOT EXISTS attendance_system;
   ```

2. **Initialize tables**:
   - Use `backend/database/init_database_railway.sql`
   - Copy-paste into Railway MySQL Data tab

3. **Test the app**:
   - Go to `https://your-app.railway.app/`
   - Login: `ylin` / `password!`

---

## TL;DR - Just Do This

1. ✅ Push updated code
2. ✅ Check `/debug-config` - are variables set?
3. ❌ **NO** → Add MySQL variables to web service (use Reference)
4. ✅ **YES** → Check `/test-db` - does it connect?
5. ❌ **NO** → Create database or fix database name
6. ✅ **YES** → Initialize database with SQL file
7. 🎉 **Done** → Test login page

---

## Debug Endpoints Reference

| Endpoint | Purpose | What It Shows |
|----------|---------|---------------|
| `/health` | Check app is running | `{"status": "ok"}` |
| `/debug-config` | Check environment variables | All MYSQL* and DB_* variables |
| `/test-db` | Test database connection | Success or error with details |

---

## Still Stuck?

Share these outputs:
1. `/debug-config` JSON
2. `/test-db` JSON
3. Screenshot of Railway web service Variables tab

This will show exactly what's wrong!
