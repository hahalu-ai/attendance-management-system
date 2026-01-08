# Railway Deployment Guide

## Quick Start - Running Migration on Railway

### Option 1: Automatic Migration (Recommended)

**The Dockerfile now handles this automatically!** No manual start command needed.

If you want to manually set it in Railway Settings → Deploy → Start Command:

```bash
python migrate_to_three_tier.py && gunicorn run:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60
```

Note: Since the Dockerfile sets WORKDIR to `/app/backend`, don't include `backend/` prefix.

### Option 2: Manual Migration via Railway CLI

```bash
# Install Railway CLI if not already installed
npm i -g @railway/cli

# Login to Railway
railway login

# Link to your project
railway link

# Run migration
railway run python backend/migrate_to_three_tier.py

# Check if successful
railway run python -c "from backend.app.models.database import execute_query; print(execute_query('SELECT user_level, COUNT(*) FROM users GROUP BY user_level', fetch_all=True))"
```

### Option 3: One-Time Migration Script

Create a one-off service in Railway:

1. Go to your Railway project
2. Click "New" → "Empty Service"
3. Name it "migration-runner"
4. Connect your GitHub repo
5. Set the start command to: `python backend/migrate_to_three_tier.py`
6. Add the same environment variables as your main service
7. Deploy and let it run once
8. Remove the service after successful migration

## Environment Variables

Make sure these are set in Railway:

```bash
DB_HOST=<your-railway-mysql-host>
DB_PORT=3306
DB_USER=root
DB_PASSWORD=<your-railway-mysql-password>
DB_NAME=attendance_system
PORT=5001
SECRET_KEY=<your-secret-key>
```

## Testing the Migration

After migration, test with Railway CLI:

```bash
# Check user types
railway run python -c "
from backend.app.models.database import execute_query
users = execute_query('SELECT user_level, COUNT(*) as count FROM users GROUP BY user_level', fetch_all=True)
for user in users:
    print(f'{user[\"user_level\"]}: {user[\"count\"]}')
"

# Check tables exist
railway run python -c "
from backend.app.models.database import execute_query
tables = execute_query('SHOW TABLES', fetch_all=True)
print('Tables:', [list(t.values())[0] for t in tables])
"
```

## Rollback (If Needed)

The migration script creates backup tables. To rollback:

```bash
railway run mysql -h <host> -u root -p<password> attendance_system

# In MySQL shell:
# Find backup tables
SHOW TABLES LIKE '%backup%';

# Restore from backup (replace timestamp)
DROP TABLE users;
CREATE TABLE users AS SELECT * FROM users_backup_YYYYMMDD_HHMMSS;

# Etc for other tables...
```

## Troubleshooting

### Migration fails with "Table already exists"

This is safe - the script is idempotent. It will skip already-migrated tables.

### Foreign key constraint errors

Check that all old data is valid:
```bash
railway run python -c "
from backend.app.models.database import execute_query
# Check for orphaned records
result = execute_query('SELECT * FROM manager_assignments ma WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = ma.manager_username)', fetch_all=True)
print('Orphaned manager assignments:', result)
"
```

### Connection timeout

Increase Railway's timeout or run migration locally:
```bash
# Set your Railway MySQL credentials locally
export DB_HOST=<railway-host>
export DB_PASSWORD=<railway-password>
export DB_NAME=attendance_system

# Run migration
python backend/migrate_to_three_tier.py
```

## Post-Migration Checklist

- [ ] Migration script completed successfully
- [ ] Backend server starts without errors
- [ ] Can create a new Lead (test with Manager account)
- [ ] Lead can create Members
- [ ] QR code generation works
- [ ] Frontend displays correctly

## Support

Check logs in Railway dashboard:
- Go to your service
- Click "Deployments"
- Click on latest deployment
- View "Deploy Logs" and "Service Logs"
