# QR Code Check-in/Check-out - Quick Start Guide

## TL;DR - How It Works

1. **Manager** selects worker → clicks "Generate Check-In/Out QR"
2. **Worker** scans QR code with phone
3. **System** records check-in/out automatically

## Setup (One Time)

### 1. Update Database

If you already have the database running, add the QR table:

```bash
mysql -u root -p practice_db < backend/database/add_qr_requests_table.sql
```

If starting fresh, just run:

```bash
mysql -u root -p practice_db < backend/database/init_database.sql
```

### 2. Start the System

```bash
./scripts/start.sh
```

## Usage

### For Managers

1. **Login**
   - Open: http://localhost:8080/manager/portal.html
   - Use your manager credentials

2. **Generate QR Code**
   - Select a worker from dropdown
   - Check their current status (Clocked In/Out)
   - Click "Generate Check-In QR" or "Generate Check-Out QR"

3. **Show QR to Worker**
   - QR code appears on screen
   - Valid for 5 minutes (countdown shown)
   - Wait for worker to scan

4. **Confirmation**
   - System shows success when scanned
   - Worker status updates automatically

### For Workers

1. **Open Scanner**
   - On your phone, open: http://localhost:8080/worker/scan.html
   - Can also scan from computer

2. **Scan QR Code**
   - Allow camera access when prompted
   - Point camera at manager's QR code
   - Or use "Manual Entry" tab if camera doesn't work

3. **Confirmation**
   - See success message immediately
   - Your check-in/out is recorded

## Testing the System

### Quick Test Flow

```bash
# 1. Open Manager Portal in browser
http://localhost:8080/manager/portal.html

# 2. Login as manager (use sample data)
Username: ylin
Password: (set during registration)

# 3. Open Worker Scanner on phone
http://localhost:8080/worker/scan.html

# 4. In Manager Portal:
- Select worker "Xuanyu Lu"
- Click "Generate Check-In QR"

# 5. On phone:
- Click "Start Camera"
- Point at QR code on manager screen
- See success message
```

## API Quick Test

### Generate QR Code

```bash
curl -X POST http://localhost:5001/api/attendance/qr/generate \
  -H "Content-Type: application/json" \
  -d '{
    "manager_username": "ylin",
    "worker_username": "xlu",
    "action": "check-in"
  }'
```

### Verify QR Code

```bash
# Use token from previous response
curl -X POST http://localhost:5001/api/attendance/qr/verify \
  -H "Content-Type: application/json" \
  -d '{
    "token": "YOUR_TOKEN_HERE"
  }'
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| QR won't scan | Use "Manual Entry" tab, paste token |
| Camera not working | Enable camera permissions in browser settings |
| QR expired | Generate new one (they expire in 5 min) |
| "Worker already clocked in" | Use Check-Out instead of Check-In |
| 404 error on worker scan | Make sure frontend server is running on port 8080 |

## File Locations

- **Manager Portal**: `frontend/manager/portal.html`
- **Worker Scanner**: `frontend/worker/scan.html`
- **QR API**: `backend/app/api/attendance.py` (lines 297-528)
- **Database Schema**: `backend/database/init_database.sql` (table: qr_requests)
- **Full Documentation**: `docs/QR_WORKFLOW.md`

## Important Notes

- QR codes expire after **5 minutes**
- Each QR code can only be used **once**
- Workers must scan **before** QR expires
- Manager must be assigned to worker
- Check-in only works when worker is clocked out
- Check-out only works when worker is clocked in

## Next Steps

1. Test with sample data
2. Register real users
3. Assign managers to workers
4. Start using QR workflow

For detailed information, see [QR_WORKFLOW.md](docs/QR_WORKFLOW.md)
