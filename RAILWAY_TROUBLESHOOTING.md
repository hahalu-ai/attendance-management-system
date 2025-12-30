# Railway Deployment Troubleshooting

## Quick Fix for "Unknown MySQL server host" Error

### What I Fixed:

Updated `backend/app/config.py` to automatically detect Railway's MySQL environment variables.

### What You Need to Do:

#### Step 1: Commit and Push the Fix

```bash
cd /home/yuchen/codespace/attendance-management-system
git add backend/app/config.py RAILWAY_DEPLOYMENT_GUIDE.md RAILWAY_TROUBLESHOOTING.md
git commit -m "Fix Railway MySQL environment variable detection"
git push
```

#### Step 2: Verify MySQL Service in Railway

1. Open your Railway project
2. You should see TWO services:
   - Your web app (Python/Flask)
   - MySQL database
3. If you DON'T see MySQL service, add it:
   - Click "New" → "Database" → "Add MySQL"

#### Step 3: Check Variable Linking

**In your WEB SERVICE** (not MySQL service):

1. Click on your web service
2. Go to "Variables" tab
3. Look for these variables (they should appear automatically if MySQL is linked):
   - `MYSQLHOST` or `MYSQL_HOST`
   - `MYSQLPORT` or `MYSQL_PORT`
   - `MYSQLUSER` or `MYSQL_USER`
   - `MYSQLPASSWORD` or `MYSQL_PASSWORD`
   - `MYSQLDATABASE` or `MYSQL_DATABASE`

**If you DON'T see these variables:**

The MySQL service is not linked. Click "New Variable" → "Add a Reference" → Select your MySQL service

**OR manually add them:**

1. Go to your **MySQL service** → "Variables" tab
2. Copy the values (host, port, user, password)
3. Go to your **web service** → "Variables" tab
4. Click "New Variable" and add each one:
   - Name: `MYSQLHOST`, Value: `<paste host>`
   - Name: `MYSQLPORT`, Value: `<paste port>`
   - Name: `MYSQLUSER`, Value: `<paste user>`
   - Name: `MYSQLPASSWORD`, Value: `<paste password>`
   - Name: `MYSQLDATABASE`, Value: `attendance_system` (type this manually)

#### Step 4: Add Required Application Variables

Still in your **web service** Variables tab, add:

```
SECRET_KEY=<generate-random-key>
DEBUG=False
CORS_ORIGINS=*
```

To generate SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and use it as SECRET_KEY value.

#### Step 5: Initialize the Database

**IMPORTANT**: The original `init_database.sql` file has issues that cause failures in Railway. Use the fixed version instead!

**Option A: Use the Railway-Compatible SQL File (Recommended)**

1. Click on your **MySQL service** (not web service)
2. Go to "Data" or "Query" tab
3. Copy the contents of `backend/database/init_database_railway.sql`
4. Paste and execute in the MySQL console

**Option B: Use Step-by-Step Commands**

If Option A fails, follow the step-by-step guide in `backend/database/init_step_by_step.md`

**Option C: Use Python Script (If Railway provides shell access)**

```bash
cd backend
python init_db.py
```

This will automatically:
- Create the database
- Create all tables
- Insert sample data
- Verify everything worked

**Why the original file fails:**
- Missing `CREATE DATABASE IF NOT EXISTS`
- No `IF NOT EXISTS` on CREATE TABLE statements
- Uses regular `INSERT` instead of `INSERT IGNORE`
- Railway console may not support `USE database;` statement

#### Step 6: Wait for Redeploy

Railway should automatically redeploy your app after you pushed the code changes.

1. Go to your web service
2. Click "Deployments" tab
3. Wait for the latest deployment to complete (green checkmark)

#### Step 7: Verify It Works

Once deployed, test these URLs (replace `your-app` with your actual Railway URL):

1. **Health check**: `https://your-app.railway.app/health`
   - Should return: `{"status": "ok", "message": "Application is running"}`

2. **Config check**: `https://your-app.railway.app/debug-config`
   - Should show your database configuration (password will be hidden as ***)

3. **Main page**: `https://your-app.railway.app/`
   - Should load the login page

---

## Still Not Working?

### Check the Logs

1. Go to your web service in Railway
2. Click "Deployments" tab
3. Click on the latest deployment
4. Check both:
   - **Build Logs** - Should show successful Docker build
   - **Deploy Logs** - Should show gunicorn starting

### Common Log Errors and Fixes:

#### "Can't connect to MySQL server"
- MySQL service is not running or not accessible
- Check MySQL service status in Railway
- Verify firewall/network settings (Railway usually handles this automatically)

#### "Access denied for user"
- Wrong username or password
- Double-check the `MYSQLUSER` and `MYSQLPASSWORD` values
- They should match what's in your MySQL service

#### "Unknown database 'attendance_system'"
- Database not created yet
- Run `CREATE DATABASE attendance_system;` in MySQL console

#### "gunicorn: command not found"
- Missing dependency
- Check that `gunicorn==21.2.0` is in `backend/requirements.txt`

---

## Debug Checklist

Use this checklist to verify everything:

- [ ] MySQL service exists in Railway project
- [ ] Web service exists in Railway project
- [ ] MySQL variables visible in web service (MYSQLHOST, MYSQLPORT, etc.)
- [ ] SECRET_KEY added to web service variables
- [ ] Database `attendance_system` created in MySQL
- [ ] Tables created (users, time_entries, manager_assignments, qr_requests)
- [ ] Latest code pushed to git repository
- [ ] Railway deployment completed successfully (green checkmark)
- [ ] Health endpoint returns OK: `/health`
- [ ] Config endpoint shows correct values: `/debug-config`
- [ ] Main page loads: `/`

---

## Need More Help?

If you're still stuck, provide:
1. Screenshot of Railway variables tab (web service)
2. Build logs from Railway
3. Deploy logs from Railway (last 50 lines)
4. What URL you're accessing and what error you see
