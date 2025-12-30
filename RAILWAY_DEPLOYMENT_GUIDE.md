# Railway Deployment Guide

## Fix Applied

Created `railway.json` in the root directory to tell Railway where to find your Dockerfile.

## Steps to Deploy on Railway

### 1. Add MySQL Database

Your application requires a MySQL database. In Railway:

1. Open your project
2. Click **"New"** → **"Database"** → **"Add MySQL"**
3. Railway will create a MySQL instance and provide connection details

### 2. Configure Environment Variables

**IMPORTANT**: The app now automatically detects Railway's MySQL variables, so you have two options:

#### Option A: Let Railway Auto-Configure (Recommended)

Simply ensure your MySQL database is **linked** to your web service:
1. In Railway, go to your web service
2. Click "Settings" → "Service Variables"
3. Look for variables from your MySQL service (they should appear automatically if linked)
4. The app will automatically use: `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, `MYSQLDATABASE`

Then manually add ONLY these variables to your web service:
```
SECRET_KEY=<generate-a-random-secret-key>
DEBUG=False
CORS_ORIGINS=*
```

#### Option B: Manual Configuration (Reference Variables)

If auto-linking doesn't work, manually reference MySQL service variables:

1. In your **web service**, click "Variables" → "New Variable"
2. For each variable, use "Reference" to link to MySQL service:
   - Variable name: `DB_HOST` → Reference → MySQL service → `MYSQLHOST`
   - Variable name: `DB_PORT` → Reference → MySQL service → `MYSQLPORT`
   - Variable name: `DB_USER` → Reference → MySQL service → `MYSQLUSER`
   - Variable name: `DB_PASSWORD` → Reference → MySQL service → `MYSQLPASSWORD`
   - Variable name: `DB_NAME` → Type manually: `attendance_system`

3. Add application variables:
   - `SECRET_KEY` → `<generate-a-random-secret-key>`
   - `DEBUG` → `False`
   - `CORS_ORIGINS` → `*`

To generate a secure SECRET_KEY, run:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Note**: Railway uses variable names like `MYSQLHOST` (no underscore) or `MYSQL_HOST` (with underscore) depending on how the database was created. The app supports both formats.

### 3. Initialize Database

After deployment, you need to initialize your database schema.

#### Step 1: Create the Database
In Railway's MySQL service:
1. Click on your MySQL service
2. Go to "Data" tab or connect via MySQL client
3. Create the database:
   ```sql
   CREATE DATABASE attendance_system;
   ```

#### Step 2: Run Schema and Sample Data
Run the SQL file located at `backend/database/init_database.sql`:

1. **Via Railway Console**:
   - Copy contents of `init_database.sql`
   - Paste into Railway's Query tab
   - Execute

2. **Via MySQL Client**:
   ```bash
   mysql -h <MYSQL_HOST> -u <MYSQL_USER> -p<MYSQL_PASSWORD> < backend/database/init_database.sql
   ```

This will create:
- `users` table (with sample users)
- `manager_assignments` table
- `time_entries` table
- `qr_requests` table

**Default test credentials** (password: "password!" for all):
- Manager: `ylin` / password: `password!`
- Contractor: `xlu` / password: `password!`
- Contractor: `jsmith` / password: `password!`

### 4. Redeploy

After adding environment variables:
1. Commit the `railway.json` file
2. Push to your repository
3. Railway will automatically redeploy
4. Or manually trigger redeploy in Railway dashboard

### 5. Verify Deployment

Once deployed, check:
- Health endpoint: `https://your-app.railway.app/health`
- Config endpoint: `https://your-app.railway.app/debug-config`
- Main page: `https://your-app.railway.app/`

### 6. Check Logs

If still getting errors:
1. Go to Railway dashboard
2. Click on your service
3. View "Deployments" tab
4. Click latest deployment
5. Check build logs and runtime logs

## Common Issues

### "ERROR 2005: Unknown MySQL server host '$MYSQLHOST'"
- **Cause**: Environment variables not properly configured or MySQL service not linked
- **Solution**:
  1. ✅ **Update your code** - Already fixed! The app now auto-detects Railway's MySQL variables
  2. **Commit and push the updated config.py**:
     ```bash
     git add backend/app/config.py
     git commit -m "Support Railway MySQL environment variables"
     git push
     ```
  3. **Check MySQL service is linked**:
     - In Railway, go to your web service
     - Click "Settings" tab
     - Scroll to "Service Variables" - you should see `MYSQLHOST`, `MYSQLPORT`, etc.
     - If not visible, manually add them using "Reference" (see Option B above)
  4. **Verify variable names**: Check your MySQL service variables tab - Railway might use:
     - `MYSQLHOST` (no underscore) OR
     - `MYSQL_HOST` (with underscore)
     - The app now supports BOTH formats

### "Application failed to respond"
- **Cause**: App not binding to `0.0.0.0:$PORT`
- **Solution**: ✅ Already configured in your Dockerfile
- Verify with logs that gunicorn starts successfully

### Database Connection Errors (Other)
- **Cause**: Database not configured or wrong credentials
- **Solution**:
  - Check `/debug-config` endpoint to see what values the app is reading
  - Verify MySQL service is running in Railway
  - Check that `DB_NAME` is set to `attendance_system` (or MYSQLDATABASE)
  - Ensure database was created: `CREATE DATABASE attendance_system;`

### Build Fails
- **Cause**: Missing dependencies or wrong Python version
- **Solution**: Check `requirements.txt` and `runtime.txt`
- Current: Python 3.10.12 (configured in runtime.txt)

### Frontend Not Loading
- **Cause**: Static files path issue
- **Solution**: Verify frontend files are in `/home/yuchen/codespace/attendance-management-system/frontend/`
- Check Dockerfile copies everything: `COPY . .`

## Current Configuration

### Dockerfile Location
`backend/Dockerfile` - Railway will find it via `railway.json`

### Port Configuration
Railway provides `$PORT` environment variable → Dockerfile uses it:
```dockerfile
CMD gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
```

### Build Context
Root directory (`/attendance-management-system/`) with Dockerfile in `backend/`

## Testing Locally with Docker

To test the Docker build locally:

```bash
cd /home/yuchen/codespace/attendance-management-system/backend
docker build -t attendance-app .
docker run -p 5001:5001 -e PORT=5001 attendance-app
```

## Need More Help?

If issues persist:
1. Share the Railway deployment logs (build + runtime)
2. Share the error message from Railway dashboard
3. Verify database is created and accessible
