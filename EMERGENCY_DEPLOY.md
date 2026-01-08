# 🚨 Emergency Deployment Guide

## If Deployment is Failing - Try These in Order

### METHOD 1: Deploy Without Migration First ⚡ (Fastest)

1. **Update Dockerfile to skip migration**:
   ```bash
   # Replace line 26 in Dockerfile with:
   CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5001", "--workers", "2", "--timeout", "60"]
   ```

2. **Push and Deploy**:
   ```bash
   git add Dockerfile
   git commit -m "Deploy without migration first"
   git push
   ```

3. **Run migration separately** (after server is running):
   ```bash
   # Install Railway CLI
   npm i -g @railway/cli

   # Login and link
   railway login
   railway link

   # Run migration
   railway run python migrate_to_three_tier.py
   ```

4. **Add migration back to Dockerfile** (for future deployments):
   ```bash
   # Restore line 26:
   CMD python migrate_to_three_tier.py && gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60

   git commit -am "Re-add migration to deployment"
   git push
   ```

---

### METHOD 2: Use Simplified Dockerfile 🔧

1. **Copy Dockerfile.simple to Dockerfile**:
   ```bash
   cp Dockerfile.simple Dockerfile
   git add Dockerfile
   git commit -m "Use simplified Dockerfile"
   git push
   ```

2. **Deploy succeeds** ✅

3. **Run migration via Railway CLI**:
   ```bash
   railway run python backend/migrate_to_three_tier.py
   ```

---

### METHOD 3: Manual SQL Migration 💾

Skip Python migration, use SQL directly:

1. **Deploy app normally** (without migration)

2. **Get SQL file content**:
   ```bash
   cat backend/database/migration_to_three_tiers.sql
   ```

3. **Run in Railway MySQL**:

   **Option A - Via Railway CLI**:
   ```bash
   railway link
   railway run bash
   # Inside Railway container:
   mysql -h $MYSQLHOST -u $MYSQLUSER -p$MYSQLPASSWORD $MYSQLDATABASE < /app/backend/database/migration_to_three_tiers.sql
   ```

   **Option B - Via Railway Web UI**:
   - Go to your MySQL database in Railway
   - Click "Query" tab
   - Copy/paste entire contents of `migration_to_three_tiers.sql`
   - Click "Execute"

---

### METHOD 4: Fresh Start 🔄

If nothing works, completely reset:

1. **Delete Railway Service**:
   - Railway Dashboard → Your Service → Settings → Delete

2. **Create New Service**:
   - Railway → New Service
   - Deploy from GitHub → Your Repo
   - Wait for build to complete

3. **Add MySQL Database**:
   - Railway → Add Database → MySQL
   - Link to your service

4. **Set Environment Variables**:
   Go to Service → Variables, add these exactly:
   ```
   DB_HOST=${{MYSQLHOST}}
   DB_PORT=${{MYSQLPORT}}
   DB_NAME=${{MYSQLDATABASE}}
   DB_USER=${{MYSQLUSER}}
   DB_PASSWORD=${{MYSQLPASSWORD}}
   PORT=5001
   ```

5. **Deploy**:
   - Railway will auto-deploy
   - Should work now!

---

## 🔍 What Information I Need

To help you debug, please share:

### 1. Railway Build Logs
```
Railway → Deployments → Click failed deployment → View Build Logs
```

Copy from "Building..." to the error message.

### 2. Railway Deploy Logs
```
Railway → Deployments → Click failed deployment → View Deploy Logs
```

Copy the last 50 lines.

### 3. Git Status
```bash
git status
git log --oneline -5
```

### 4. Environment Variables
```bash
railway variables
# Or screenshot from Railway dashboard (hide passwords)
```

### 5. Which Step Failed?
- [ ] Building Docker image
- [ ] Installing dependencies
- [ ] Running migration
- [ ] Starting server
- [ ] Other: ___________

---

## 🎯 Quick Checks

Run these locally to catch issues before deploying:

```bash
# 1. All files committed?
git status

# 2. Python files have no syntax errors?
python3 -m py_compile backend/migrate_to_three_tier.py
python3 -m py_compile backend/run.py

# 3. Requirements.txt complete?
cat backend/requirements.txt
# Must have: Flask, Flask-CORS, mysql-connector-python, gunicorn

# 4. Dockerfile valid?
cat Dockerfile

# 5. No .env or secrets accidentally committed?
git log -1 --stat | grep -E ".env|secret|password"
```

---

## 📊 Expected Railway Log Output (Success)

When deployment works, you should see:

```
Building...
 => [1/6] FROM python:3.10-slim
 => [2/6] WORKDIR /app
 => [3/6] COPY backend/requirements.txt .
 => [4/6] RUN pip install...
Successfully installed Flask-3.0.0 gunicorn-21.2.0...
 => [5/6] COPY backend/ ./backend/
 => [6/6] COPY frontend/ ./frontend/
Successfully built

Deploying...
Starting container...

============================================================
  Three-Tier User System Migration
  Database: attendance_system
============================================================

🔌 Connecting to database...
✅ Connected successfully

🔍 Checking migration status...
📝 Migration needed, proceeding...

✅ MIGRATION COMPLETED SUCCESSFULLY!

[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:5001
```

---

## ⚡ Fastest Solution Right Now

**If you just want it working ASAP**:

1. Use Dockerfile WITHOUT migration:
   ```bash
   # Edit Dockerfile line 26 to:
   CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5001", "--workers", "2"]

   git commit -am "Temporary: skip migration"
   git push
   ```

2. Wait for deployment ✅

3. Run migration separately:
   ```bash
   railway run python migrate_to_three_tier.py
   ```

4. Your app is now live with the three-tier system! 🎉

---

**Now share your error logs and I'll give you the exact fix!** 📋
