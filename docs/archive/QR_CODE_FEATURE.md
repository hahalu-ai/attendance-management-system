# QR Code Feature Documentation

## Overview

The manager portal now includes a QR code generation feature for each employee. When you click on an employee and press "Generate QR Code", a unique QR code is created with an embedded hyperlink to that employee's information.

## How It Works

### 1. Generate QR Code
- Click on any employee card in the portal
- In the modal that appears, click the **"Generate QR Code"** button
- A QR code will be generated and displayed

### 2. QR Code Contents
Each QR code contains an embedded URL in this format:
```
http://localhost:5001/employee/{employee_id}/info
```

For example:
- Employee A (ID: 2) → `http://localhost:5001/employee/2/info`
- Employee B (ID: 3) → `http://localhost:5001/employee/3/info`
- Employee C (ID: 4) → `http://localhost:5001/employee/4/info`
- Employee D (ID: 5) → `http://localhost:5001/employee/5/info`

### 3. Scanning the QR Code
When someone scans the QR code with their phone:
1. The QR code scanner will detect the embedded URL
2. The phone will open the link in a browser
3. The API will return employee information including:
   - Employee ID, name, and role
   - Manager information
   - Recent attendance records (last 5 entries)

## API Endpoint

### GET /employee/{employee_id}/info

Returns comprehensive employee information.

**Example Request:**
```bash
curl http://localhost:5001/employee/2/info
```

**Example Response:**
```json
{
  "employee": {
    "id": 2,
    "name": "Employee A",
    "role": "employee"
  },
  "manager": {
    "id": 1,
    "name": "Boss",
    "role": "manager"
  },
  "recent_attendance": [
    {
      "id": 1,
      "check_in_time": "2025-12-07T09:00:00",
      "check_out_time": "2025-12-07T17:00:00",
      "status": "approved"
    }
  ],
  "qr_generated_at": "QR Code Access"
}
```

## Features

### Visual Design
- QR code is displayed in a styled container with a light background
- The embedded URL is shown below the QR code for reference
- QR code uses your brand colors (purple gradient: #667eea)
- High error correction level for better scanning reliability

### Customization Options

You can customize the QR code in `manager_portal.html`:

```javascript
new QRCode(qrcodeDiv, {
    text: employeeUrl,          // The URL to embed
    width: 200,                 // QR code width in pixels
    height: 200,                // QR code height in pixels
    colorDark: "#667eea",       // Dark color (your brand color)
    colorLight: "#ffffff",      // Light/background color
    correctLevel: QRCode.CorrectLevel.H  // Error correction level (L, M, Q, H)
});
```

### Use Cases

1. **Employee ID Cards**: Print QR codes on employee badges
2. **Quick Access**: Scan to quickly view employee info without logging in
3. **Mobile Access**: Easy mobile access to employee data
4. **Attendance Tracking**: QR codes could be used for check-in/check-out (future feature)
5. **Visitor Management**: Share employee contact info via QR code

## Future Enhancements

You can extend this feature to:
- Generate printable employee badges with QR codes
- Use QR codes for attendance check-in/check-out
- Add authentication to the QR code URL
- Include additional employee data (contact info, department, etc.)
- Generate downloadable QR code images (PNG/SVG)
- Add expiration time to QR code links for security

## Technical Details

**Library Used:** QRCode.js (v1.0.0)
- CDN: `https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js`
- Documentation: https://davidshimjs.github.io/qrcodejs/

**Browser Support:** Works in all modern browsers with JavaScript enabled

**Mobile Scanning:** Compatible with all standard QR code scanner apps
