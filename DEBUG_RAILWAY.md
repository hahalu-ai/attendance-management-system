# 🔍 Railway Deployment Debugging Guide

## Step 1: Get the Full Error Logs

Please share your Railway deployment logs by:

1. Go to Railway Dashboard → Your Project → Your Service
2. Click on the latest deployment (red failed icon)
3. Click "View Logs"
4. Copy the **ENTIRE log output** (especially the error at the end)
5. Share it with me

## Step 2: Common Issues & Quick Fixes

### Issue A: Build Failed (During Docker Build)

**Symptoms**: Error during `pip install` or `COPY` commands

**Quick Fix**:
```bash
# Check if all files are committed
git status

# Add any missing files
git add .
git commit -m "Add missing files"
git push
```

### Issue B: Runtime Failed (Migration Error)

**Symptoms**: "python: can't open file" or "No module named..."

**Quick Fix**:
Try this simpler Dockerfile:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy everything
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Set working directory
WORKDIR /app/backend

# Run migration and start server
CMD python migrate_to_three_tier.py && gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
```

Save this as `Dockerfile.simple` then use it in Railway.

### Issue C: Database Connection Failed

**Symptoms**: "Can't connect to MySQL" or "Access denied"

**Check**:
1. Railway → Your MySQL service → Is it running?
2. Railway → Your app service → Variables tab → Are DB variables set?

**Auto-set variables**:
Railway automatically sets these when you link MySQL:
- `MYSQLHOST`
- `MYSQLPORT`
- `MYSQLDATABASE`
- `MYSQLUSER`
- `MYSQLPASSWORD`

But your app needs:
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`

**Fix**: Add these to your app's environment variables in Railway:
```
DB_HOST=${{MYSQLHOST}}
DB_PORT=${{MYSQLPORT}}
DB_NAME=${{MYSQLDATABASE}}
DB_USER=${{MYSQLUSER}}
DB_PASSWORD=${{MYSQLPASSWORD}}
```

### Issue D: Port Binding Failed

**Symptoms**: "Address already in use" or port errors

**Check**:
- Railway → Variables → Make sure `PORT` variable exists
- It should be automatically set by Railway

### Issue E: Gunicorn Not Found

**Symptoms**: "gunicorn: command not found"

**Fix**:
Check `backend/requirements.txt` includes:
```
gunicorn==21.2.0
```

## Step 3: Alternative Deployment (Skip Migration)

If migration keeps failing, deploy without it first:

### Option 1: Use Simplified Dockerfile

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r backend/requirements.txt
WORKDIR /app/backend
CMD gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
```

Then run migration manually via Railway CLI:
```bash
railway run python backend/migrate_to_three_tier.py
```

### Option 2: Use Old System First

Deploy without migration, then migrate later:

1. Remove migration from Dockerfile CMD
2. Deploy successfully
3. Run migration via Railway CLI
4. Redeploy with migration in CMD

## Step 4: Railway CLI Debugging

Install Railway CLI for better debugging:

```bash
# Install
npm i -g @railway/cli

# Login
railway login

# Link to project
railway link

# View logs in real-time
railway logs

# Run commands directly on Railway
railway run python backend/migrate_to_three_tier.py

# Check environment variables
railway variables

# SSH into container (if needed)
railway shell
```

## Step 5: Verify Files Are Correct

Run these checks locally:

```bash
# 1. Check all files exist
ls -la backend/migrate_to_three_tier.py
ls -la backend/run.py
ls -la backend/requirements.txt
ls -la Dockerfile

# 2. Check Python syntax
python3 -m py_compile backend/migrate_to_three_tier.py
python3 -m py_compile backend/run.py

# 3. Check requirements.txt has all dependencies
cat backend/requirements.txt
# Should have: Flask, Flask-CORS, mysql-connector-python, python-dotenv, gunicorn

# 4. Check no syntax errors in Dockerfile
docker build -t test . --no-cache
```

## Step 6: Manual SQL Migration (Last Resort)

If Python migration fails, use SQL directly:

```bash
# Via Railway CLI
railway run mysql -u root -p$MYSQLPASSWORD $MYSQLDATABASE < backend/database/migration_to_three_tiers.sql
```

Or via Railway web interface:
1. Open MySQL database in Railway
2. Click "Query" tab
3. Paste contents of `backend/database/migration_to_three_tiers.sql`
4. Execute

## Common Error Messages Decoded

### "No such file or directory"
- File path is wrong
- File wasn't copied to Docker container
- Working directory is incorrect

**Fix**: Check Dockerfile COPY commands and WORKDIR

### "Can't connect to MySQL server"
- Database service not running
- Wrong credentials
- Network issue

**Fix**: Check database service status and environment variables

### "Module not found"
- Dependency not installed
- Wrong Python version
- requirements.txt missing package

**Fix**: Check requirements.txt and pip install logs

### "Permission denied"
- File permissions issue (rare on Railway)

**Fix**: Make sure script is readable, no need for chmod on Railway

### "SyntaxError" or "IndentationError"
- Python code has errors

**Fix**: Check the file locally with `python3 -m py_compile`

## What to Share for Help

When asking for help, include:

1. **Full Railway deployment logs** (from start to error)
2. **Screenshot of error** (if it's clearer)
3. **Environment variables** (redact passwords):
   ```bash
   railway variables | grep -v PASSWORD
   ```
4. **Git status**:
   ```bash
   git status
   git log -1
   ```
5. **Which step failed**: Build, Migration, or Server Start?

## Quick Reset

If nothing works, try a clean reset:

```bash
# 1. Remove Railway service
# Railway Dashboard → Service → Settings → Delete Service

# 2. Clean local files
git clean -fdx
git reset --hard HEAD

# 3. Create fresh Railway service
# Railway Dashboard → New Service → Deploy from GitHub

# 4. Link MySQL database
# Railway → Add MySQL → Link to Service

# 5. Set environment variables
# Add DB_HOST, DB_PORT, etc. pointing to MySQL variables

# 6. Deploy
git push
```

---

**Share your Railway logs and I'll help you debug the specific issue!** 🔍
