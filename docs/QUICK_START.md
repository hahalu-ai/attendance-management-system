# Quick Start Guide - Manager Portal

## What's Been Created

I've set up a complete database and web portal system with:
- **Manager**: Boss (ID: 1)
- **Employees**: Employee A (ID: 2), Employee B (ID: 3), Employee C (ID: 4), Employee D (ID: 5)
- **Web Portal**: Interactive interface with clickable employee banners

## Setup Steps

### 1. Start MySQL Server

First, you need to start your MySQL server. The exact command depends on your system:

```bash
# For Ubuntu/Debian
sudo service mysql start

# Or using systemctl
sudo systemctl start mysql
```

### 2. Initialize the Database

Run the setup script to populate the database with test data:

```bash
cd /home/yuchen/codespace/attendance-management-system
python3 setup_database.py
```

This will:
- Clear existing data
- Create manager "Boss" with ID 1
- Create employees A, B, C, D with IDs 2, 3, 4, 5
- Link all employees to Boss as their manager

### 3. Start the Flask Server

```bash
python3 app.py
```

The server will start on `http://localhost:5001`

### 4. Access the Manager Portal

Open your browser and navigate to:
```
http://localhost:5001/portal
```

## Portal Features

### Manager Display
- Shows "Boss" as the manager at the top in a prominent banner

### Employee Banners
- All employees (A, B, C, D) are displayed in card/banner format
- Each employee card shows:
  - Avatar with their initial letter (A, B, C, D)
  - Employee name
  - Employee ID

### Interactive Features
- **Click any employee card** to view their details in a modal popup
- **Generate QR Code**: Create a QR code with embedded hyperlink to employee info
- **View Attendance**: See attendance records for that employee
- **View Reports**: Access reports for that employee

## API Endpoints

The system also provides a REST API:

### Get Manager and Employees
```
GET http://localhost:5001/manager/1/employees
```

Returns:
```json
{
  "manager": {
    "id": 1,
    "name": "Boss",
    "role": "manager"
  },
  "employees": [
    {"id": 2, "name": "Employee A", "role": "employee"},
    {"id": 3, "name": "Employee B", "role": "employee"},
    {"id": 4, "name": "Employee C", "role": "employee"},
    {"id": 5, "name": "Employee D", "role": "employee"}
  ]
}
```

### Get Employee Info (QR Code Endpoint)
```
GET http://localhost:5001/employee/{employee_id}/info
```

Returns employee details, manager info, and recent attendance records.
This endpoint is embedded in the QR codes generated for each employee.

## Next Steps

The current implementation shows a modal with employee details and three action buttons:
- **Generate QR Code**: Creates a scannable QR code with embedded URL to employee info
- **View Attendance**: Placeholder for viewing attendance records
- **View Reports**: Placeholder for viewing employee reports

The QR code feature is fully functional! See `QR_CODE_FEATURE.md` for detailed documentation.

Please let me know what specific actions you'd like the View Attendance and View Reports buttons to perform!

## Files Created

1. `init_database.sql` - SQL script to initialize the database
2. `setup_database.py` - Python script to set up the database
3. `create_database.py` - Script to create database and tables
4. `static/manager_portal.html` - Web portal interface with QR code feature
5. `app.py` - Updated with API endpoints (manager/employees and employee/info)
6. `QR_CODE_FEATURE.md` - Complete documentation for QR code functionality
7. Helper scripts: `start_server.sh`, `fix_mysql_auth.sh`, `create_mysql_user.sh`

## Troubleshooting

If you see "Error loading data" in the portal:
1. Make sure MySQL is running
2. Run the setup_database.py script
3. Ensure the Flask server is running on port 5001
