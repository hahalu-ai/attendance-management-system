# 🔧 Railway Deployment Fix

## Issue
Getting error: `python: can't open file '/app/backend/backend/migrate_to_three_tier.py': [Errno 2] No such file or directory`

## Root Cause
The Dockerfile sets `WORKDIR /app/backend`, so all commands run from that directory. When you specify `python backend/migrate_to_three_tier.py`, it tries to find `/app/backend/backend/...` which doesn't exist.

## ✅ Solution (Automatic)

I've updated your **Dockerfile** to automatically run the migration before starting the server:

```dockerfile
CMD python migrate_to_three_tier.py && gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
```

## 🚀 Deploy Steps

### Method 1: Use Dockerfile (Recommended)

Just push your code to GitHub:
```bash
git add .
git commit -m "Fix Railway deployment with automatic migration"
git push
```

Railway will:
1. Build using Dockerfile
2. Run migration automatically
3. Start the server

**NO manual start command needed!** The Dockerfile handles everything.

### Method 2: Override Start Command (Alternative)

If you prefer to set a custom start command in Railway Settings:

**In Railway Dashboard → Settings → Deploy → Start Command:**
```bash
python migrate_to_three_tier.py && gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
```

Note: Since WORKDIR is `/app/backend`, don't add `backend/` prefix.

### Method 3: One-Time Migration via Railway CLI

If you want to run migration separately first:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and link to your project
railway login
railway link

# Run migration once
railway run python migrate_to_three_tier.py

# Then deploy normally
git push
```

## 🧪 Verify It Works

After deployment, check your Railway logs for:
```
📦 Creating backup tables...
   ✓ Created users_backup_YYYYMMDD_HHMMSS
🔧 Modifying users table...
   ✓ Updated user_level enum to include Lead and Member
...
✅ MIGRATION COMPLETED SUCCESSFULLY!

 * Serving Flask app 'app'
 * Debug mode: off
```

## 📁 File Structure on Railway

```
/app/
  ├── backend/
  │   ├── migrate_to_three_tier.py  ← Migration script
  │   ├── run.py                     ← Flask app
  │   ├── app/
  │   │   ├── api/
  │   │   └── models/
  │   └── requirements.txt
  └── frontend/
      ├── index.html
      ├── js/
      └── css/
```

**Working Directory**: `/app/backend`

So from Railway's perspective:
- ✅ `python migrate_to_three_tier.py` = `/app/backend/migrate_to_three_tier.py`
- ❌ `python backend/migrate_to_three_tier.py` = `/app/backend/backend/migrate_to_three_tier.py` (doesn't exist!)

## 🎯 Updated Documentation

I've updated these files:
- ✅ `Dockerfile` - Now runs migration automatically
- ✅ `RAILWAY_FIX.md` - This file (troubleshooting guide)

All other documentation files remain valid, just ignore the start command examples that include `backend/` prefix - the Dockerfile handles it!

## ⚠️ Important Notes

1. **Migration is idempotent** - Safe to run on every deployment
2. **Backups are created** - Before each migration run
3. **No data loss** - Existing data is preserved
4. **Fast** - Migration completes in ~5 seconds

## 🆘 Still Having Issues?

### Issue: "Migration already completed"
✅ **This is normal!** The script detects it already ran and skips. Server will start normally.

### Issue: "Table already exists"
✅ **This is expected!** Migration checks if tables exist and skips creation if they do.

### Issue: Database connection error
1. Check MySQL service is running in Railway
2. Verify environment variables (automatically set by Railway)
3. Check database credentials in Railway dashboard

### Issue: Gunicorn not found
```bash
# Add to backend/requirements.txt
gunicorn==21.2.0
```

## 🎉 Success!

Once you see "MIGRATION COMPLETED SUCCESSFULLY!" followed by server startup logs, you're live with the three-tier system!

---

**Fixed**: 2026-01-08
**Working Directory**: `/app/backend`
**Migration Script**: `migrate_to_three_tier.py` (in backend folder)
