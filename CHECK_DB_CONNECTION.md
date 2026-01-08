# How to Check Database Connection

You're getting `ERROR 2005 (HY000): Unknown MySQL server host '$MYSQLHOST'` - this means Railway environment variables aren't set properly.

## Step-by-Step Diagnosis

### Step 1: Commit and Deploy the New Debug Endpoints

First, make sure the updated code is deployed:

```bash
git add backend/app/__init__.py backend/app/config.py
git commit -m "Add database connection debug endpoints"
git push
```

Wait for Railway to redeploy (check Deployments tab).

---

### Step 2: Check Environment Variables in Railway

In **Railway Dashboard**:

#### A. Check Your Web Service Variables

1. Click on your **web service** (Python app)
2. Go to **"Variables"** tab
3. Look for these variables:

**You should see ONE of these sets:**

**Option 1: Railway MySQL variables (linked automatically)**
```
MYSQLHOST=<some-host>.railway.app
MYSQLPORT=3306
MYSQLUSER=root
MYSQLPASSWORD=<password>
MYSQLDATABASE=railway
```

**Option 2: Custom DB_ variables (manually set)**
```
DB_HOST=<host>
DB_PORT=3306
DB_USER=root
DB_PASSWORD=<password>
DB_NAME=attendance_system
```

**❌ If you see NOTHING or only some variables:**
- MySQL service is NOT linked to your web service
- You need to add them manually (see Step 3 below)

---

### Step 3: Access Debug Endpoints

Once deployed, visit these URLs (replace `your-app` with your Railway app URL):

#### **A. Health Check**
```
https://your-app.railway.app/health
```

**Expected**: `{"status": "ok", "message": "Application is running"}`

**If this fails**: Your app isn't running at all. Check Railway deployment logs.

---

#### **B. Config Check**
```
https://your-app.railway.app/debug-config
```

This shows you **exactly** what environment variables are set and what values the app is using.

**What to look for:**

```json
{
  "variables_found": {
    "DB_HOST": "NOT SET",           // ❌ Bad
    "MYSQLHOST": "viaduct-...",     // ✅ Good!
    "MYSQL_HOST": "NOT SET",
    ...
  },
  "config_values_used": {
    "DB_HOST": "viaduct-...",       // ✅ Should match one of the variables above
    "DB_PORT": 3306,
    "DB_NAME": "railway",           // ⚠️ Should be "attendance_system" eventually
    "DB_USER": "root"
  }
}
```

**Analysis:**
- ✅ **GOOD**: At least one of `MYSQLHOST`, `MYSQL_HOST`, or `DB_HOST` shows a real hostname
- ✅ **GOOD**: `config_values_used` shows real values (not "localhost" or "NOT SET")
- ❌ **BAD**: All variables show "NOT SET"
- ❌ **BAD**: `config_values_used` shows "localhost" or default values

---

#### **C. Database Connection Test**
```
https://your-app.railway.app/test-db
```

**If successful:**
```json
{
  "status": "success",
  "message": "Database connection successful!",
  "database": "attendance_system",
  "mysql_version": "8.0.x"
}
```

**If failed:**
```json
{
  "status": "error",
  "message": "2005 (HY000): Unknown MySQL server host...",
  "connection_info": {
    "host": "$MYSQLHOST",  // ❌ Literal string means variable not set
    "port": 3306,
    "user": "root"
  }
}
```

---

### Step 4: Fix Missing Variables

If Step 3 showed variables are NOT SET, you need to link MySQL service:

#### Option A: Link MySQL Service (Automatic)

1. In Railway, go to your **web service**
2. Click **"Settings"**
3. Scroll to **"Service Variables"** or **"Shared Variables"**
4. Look for **"Add Reference"** or **"Link Service"**
5. Select your **MySQL database service**
6. This should automatically expose MYSQL* variables

#### Option B: Manually Add Variables (If linking doesn't work)

1. Go to your **MySQL service** in Railway
2. Go to **"Variables"** or **"Connect"** tab
3. Copy the values you see (host, port, user, password)
4. Go back to your **web service**
5. Click **"Variables"** → **"New Variable"**
6. Add each one:

```
Variable Name: MYSQLHOST
Value: <paste the host from MySQL service>

Variable Name: MYSQLPORT
Value: <paste the port, usually 3306>

Variable Name: MYSQLUSER
Value: <paste the user, usually root>

Variable Name: MYSQLPASSWORD
Value: <paste the password>

Variable Name: MYSQLDATABASE
Value: attendance_system
```

**OR** use the Reference feature:
- Click **"New Variable"** → **"Add a Reference"**
- Select your MySQL service
- Map each variable

---

### Step 5: Verify the Fix

After adding variables:

1. Railway will automatically redeploy
2. Wait for deployment to complete (green checkmark)
3. Visit `/debug-config` again
4. You should now see real values instead of "NOT SET"
5. Visit `/test-db`
6. Should show "success"

---

## Common Issues and Solutions

### Issue 1: All variables show "NOT SET"

**Problem**: MySQL service not linked or variables not added

**Solution**:
- Follow Step 4 above to add variables
- Make sure you're in the **web service**, not MySQL service

---

### Issue 2: Variables show but connection still fails

**Problem**: Wrong database name or database doesn't exist

**Check `/test-db` error message**:
```
"Unknown database 'attendance_system'"
```

**Solution**:
1. Go to Railway MySQL service → Data tab
2. Run: `CREATE DATABASE IF NOT EXISTS attendance_system;`
3. Or set `MYSQLDATABASE=railway` to use Railway's default database
4. Or set `DB_NAME=railway`

---

### Issue 3: "config_values_used" shows "localhost"

**Problem**: Updated config.py not deployed

**Solution**:
```bash
git add backend/app/config.py
git commit -m "Update config to support Railway variables"
git push
```

Wait for Railway to redeploy.

---

### Issue 4: Deployment fails / App won't start

**Check Railway Logs**:
1. Go to web service → Deployments
2. Click latest deployment
3. Check **Build Logs** and **Deploy Logs**
4. Look for errors related to:
   - Missing dependencies
   - Import errors
   - Port binding issues

---

## Quick Checklist

Use this to verify everything:

- [ ] MySQL service exists in Railway
- [ ] Web service exists in Railway
- [ ] `/health` endpoint returns OK
- [ ] `/debug-config` shows at least one set of MySQL variables (not "NOT SET")
- [ ] `/debug-config` "config_values_used" shows real values (not "localhost")
- [ ] `config_values_used.DB_NAME` is "attendance_system" (or "railway" if using default)
- [ ] `/test-db` returns "success"
- [ ] Database `attendance_system` exists (or using Railway default `railway`)
- [ ] Database tables created (run init_database_railway.sql)

---

## Next Steps After Connection Works

Once `/test-db` returns success:

1. **Initialize the database** (if not done):
   - Use `backend/database/init_database_railway.sql`
   - Follow `DATABASE_INIT_FIX.md`

2. **Test the login page**:
   - Go to `https://your-app.railway.app/`
   - Try logging in with: `ylin` / `password!`

3. **Check logs for any runtime errors**

---

## Still Not Working?

Provide these for further help:

1. **Screenshot** of Railway web service Variables tab
2. **Output** from `/debug-config` endpoint (full JSON)
3. **Output** from `/test-db` endpoint (full JSON)
4. **Railway deployment logs** (last 50 lines)

This will show exactly where the issue is!
