## QR Code Check-in/Check-out Workflow

## Overview

The system uses a QR code-based workflow for worker check-in and check-out. This ensures that:
1. Managers have control over when workers can check in/out
2. Workers confirm their attendance by scanning the QR code
3. The system maintains accurate time tracking with manager oversight

## Workflow Steps

### 1. Manager Initiates Check-in/Check-out

**Manager Actions:**
1. Log into the Manager Portal (`/manager/portal.html`)
2. Select a worker from the dropdown list
3. View the worker's current status (Clocked In / Clocked Out)
4. Click either "Generate Check-In QR" or "Generate Check-Out QR"

**System Actions:**
- Validates manager has authority over the worker
- Checks worker's current clock status
- Generates a secure SHA-256 token with:
  - Manager username
  - Worker username
  - Action type (check-in or check-out)
  - Timestamp
  - Random salt
- Stores the QR request in database with 5-minute expiration
- Displays QR code on screen

### 2. Worker Scans QR Code

**Worker Actions:**
1. Open Worker QR Scanner page (`/worker/scan.html`) on their phone
2. Choose either:
   - **Camera Scan**: Point camera at QR code
   - **Manual Entry**: Enter token manually if camera doesn't work
3. System automatically submits when QR code is detected

**System Actions:**
- Validates the token exists and hasn't expired
- Verifies the token is for the correct worker
- Performs the requested action:
  - **Check-in**: Creates new time entry with status "Pending"
  - **Check-out**: Updates existing open time entry with out_time
- Marks QR request as "used"
- Returns confirmation to worker

### 3. Manager Reviews Confirmation

**Manager Actions:**
- Manager portal automatically detects when QR code is scanned
- Shows success message
- Worker status updates automatically

**System Actions:**
- Polls QR request status every 5 seconds
- Updates UI when status changes to "used"
- Refreshes worker clock status

## Database Schema

### `qr_requests` Table

| Column | Type | Description |
|--------|------|-------------|
| id | INT | Primary key |
| token | VARCHAR(255) | Unique SHA-256 hash |
| manager_username | VARCHAR(50) | Manager who generated QR |
| worker_username | VARCHAR(50) | Worker who should scan |
| action_type | ENUM | 'check-in' or 'check-out' |
| status | ENUM | 'pending', 'used', 'failed', 'expired' |
| created_at | DATETIME | When QR was generated |
| expires_at | DATETIME | When QR expires (5 min after creation) |
| used_at | DATETIME | When worker scanned QR |

## API Endpoints

### Generate QR Request

```http
POST /api/attendance/qr/generate
Content-Type: application/json

{
  "manager_username": "ylin",
  "worker_username": "xlu",
  "action": "check-in"  // or "check-out"
}
```

**Response:**
```json
{
  "message": "QR code generated successfully",
  "token": "a1b2c3d4e5f6...",
  "worker_username": "xlu",
  "worker_name": "Xuanyu Lu",
  "action": "check-in",
  "expires_in_seconds": 300,
  "timestamp": "2025-12-15T10:30:00"
}
```

### Verify QR Code

```http
POST /api/attendance/qr/verify
Content-Type: application/json

{
  "token": "a1b2c3d4e5f6...",
  "worker_username": "xlu"  // Optional
}
```

**Response (Success):**
```json
{
  "message": "Check-in successful",
  "action": "check-in",
  "worker_username": "xlu",
  "entry_id": 123,
  "timestamp": "2025-12-15T10:30:15"
}
```

**Response (Error):**
```json
{
  "error": "Invalid or expired QR code"
}
```

### Check QR Status

```http
GET /api/attendance/qr/status/{token}
```

**Response:**
```json
{
  "token": "a1b2c3d4e5f6...",
  "worker_username": "xlu",
  "action": "check-in",
  "status": "used",
  "created_at": "2025-12-15T10:30:00",
  "expires_at": "2025-12-15T10:35:00",
  "used_at": "2025-12-15T10:30:15",
  "is_expired": false
}
```

## Security Features

1. **Token Expiration**: QR codes expire after 5 minutes
2. **One-time Use**: Each QR code can only be used once
3. **Worker Verification**: System verifies QR is for the correct worker
4. **Manager Authorization**: Only assigned managers can generate QR for workers
5. **Secure Hashing**: Uses SHA-256 with random salt
6. **Status Tracking**: Tracks pending, used, failed, and expired states

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "QR code expired" | More than 5 minutes passed | Generate new QR code |
| "Invalid or expired QR code" | Token not found or already used | Generate new QR code |
| "Worker already has an open time entry" | Trying to check-in when already clocked in | Use check-out instead |
| "No open time entry found" | Trying to check-out when not clocked in | Use check-in instead |
| "Worker is not assigned to this manager" | Manager-worker relationship missing | Update manager assignments |

## Mobile Optimization

The worker scanning page is optimized for mobile devices:

- Responsive design for all screen sizes
- Camera access for QR scanning (with permission)
- Fallback to manual token entry
- Touch-friendly buttons
- Clear visual feedback

## Setup Instructions

### For New Installations

The `qr_requests` table is included in `init_database.sql`. Just run the setup normally.

### For Existing Databases

Run the migration script:

```bash
mysql -u root -p practice_db < backend/database/add_qr_requests_table.sql
```

## Workflow Diagram

```
Manager                          System                           Worker
   |                                |                                |
   |--Login--------------------------->|                                |
   |<--Show Worker List---------------|                                |
   |                                |                                |
   |--Select Worker----------------->|                                |
   |--Click "Generate Check-In QR"-->|                                |
   |                                |                                |
   |                                |--Create Token                  |
   |                                |--Store in qr_requests          |
   |<--Display QR Code---------------|                                |
   |                                |                                |
   |                                |                                |--Open Scanner
   |                                |                                |--Scan QR Code
   |                                |<--Send Token------------------|
   |                                |                                |
   |                                |--Verify Token                  |
   |                                |--Check Permissions             |
   |                                |--Create Time Entry             |
   |                                |--Mark QR as 'used'            |
   |                                |                                |
   |                                |--Confirmation----------------->|
   |<--Success Notification----------|                                |
```

## Best Practices

1. **Generate QR just before needed**: QR codes expire in 5 minutes
2. **Verify worker status**: Check if worker is clocked in/out before generating QR
3. **Use camera scanning**: Faster and more reliable than manual entry
4. **Monitor expiration**: Watch the countdown timer on manager portal
5. **Handle camera permissions**: Workers must allow camera access for scanning

## Troubleshooting

### QR Code Won't Scan

1. Ensure good lighting
2. Hold camera steady
3. Try manual entry option
4. Check QR code hasn't expired

### Camera Not Working

1. Check browser camera permissions
2. Use HTTPS (required for camera access)
3. Try different browser
4. Use manual entry as fallback

### Token Expired

1. Generate new QR code
2. Worker should scan within 5 minutes
3. Check system time is synchronized

## Future Enhancements

- Geolocation verification
- Facial recognition
- Push notifications
- Offline mode with sync
- Bulk QR generation
- Custom expiration times
- QR code history/audit trail
