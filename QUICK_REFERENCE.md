# Quick Reference Guide

## Project Structure

```
attendance-management-system/
├── backend/           # Flask API server
├── frontend/          # Web interface
├── scripts/           # Launch and setup scripts
├── docs/              # Additional documentation
├── old_files/         # Legacy files (can be deleted)
└── README.md          # Main documentation
```

## Getting Started (3 Steps)

### 1. Setup
```bash
./scripts/setup.sh
```
- Installs Python dependencies
- Creates `.env` configuration file
- Initializes database schema

### 2. Configure
Edit `backend/.env` with your MySQL credentials:
```env
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=practice_db
```

### 3. Launch
```bash
./scripts/start.sh
```
- Backend: http://localhost:5001
- Frontend: http://localhost:8080

## Stop Servers
```bash
./scripts/stop.sh
```

## Database Schema (Renamed from Old Version)

| Old Table Name      | New Table Name       | Purpose                          |
|---------------------|----------------------|----------------------------------|
| `user`              | `users`              | User accounts (username, email)  |
| `manager_employee`  | `manager_assignments`| Manager-contractor relationships |
| `attendance_record` | `time_entries`       | Clock in/out records            |

## API Endpoints

### Quick Test
```bash
# Test backend is running
curl http://localhost:5001

# Register a user
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test",
    "display_name": "Test User",
    "email": "test@example.com",
    "password": "password123",
    "user_level": "Contractor"
  }'

# Login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "password123"}'

# Check in
curl -X POST http://localhost:5001/api/attendance/check-in \
  -H "Content-Type: application/json" \
  -d '{"username": "test"}'
```

## Common Tasks

### View Logs
```bash
# Backend logs (if running in background)
tail -f backend.log

# Check database
mysql -u root -p practice_db
```

### Reset Database
```bash
mysql -u root -p practice_db < backend/database/init_database.sql
```

### Update Dependencies
```bash
cd backend
pip install -r requirements.txt
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port 5001 in use | `lsof -i :5001` then `kill <PID>` |
| Can't connect to MySQL | Check MySQL service: `sudo systemctl status mysql` |
| Frontend not loading | Open `frontend/index.html` directly in browser |
| Backend crashes | Check `backend/.env` is configured correctly |

## File Locations

- **Database Schema**: `backend/database/init_database.sql`
- **API Routes**: `backend/app/api/`
- **Configuration**: `backend/.env`
- **Frontend Pages**: `frontend/*.html`
- **Logs**: Check terminal output

## Default Sample Users

After running init_database.sql, you'll have:
- **ylin** (Manager)
- **xlu** (Contractor)
- **jsmith** (Contractor)

**Note**: You'll need to add passwords via registration or update the SQL file.

## Development Workflow

1. **Backend changes**: Edit files in `backend/app/`, restart server
2. **Frontend changes**: Edit HTML/CSS/JS, refresh browser (no restart needed)
3. **Database changes**: Edit `backend/database/init_database.sql`, re-import
4. **New dependencies**: Add to `backend/requirements.txt`, run `pip install -r requirements.txt`

## Clean Up Old Files

```bash
# After verifying everything works, you can remove:
rm -rf old_files/
rm -rf __pycache__/
```

---

**Need more details?** See [README.md](README.md)
