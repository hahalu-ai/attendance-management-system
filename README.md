# Attendance Management System

A professional time tracking and attendance management system with manager approval workflows. Built with Flask (backend) and vanilla JavaScript (frontend).

## Features

- **User Authentication**: Secure login system with password hashing
- **Role-Based Access**: Manager and Contractor roles with different permissions
- **Time Tracking**: Clock in/out functionality with precise time recording
- **Approval Workflow**: Managers approve contractor time entries
- **Monthly Reports**: Comprehensive attendance summaries and statistics
- **Manager Dashboard**: View and manage team attendance
- **Employee Portal**: Self-service time entry and history viewing

## Project Structure

```
attendance-management-system/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── users.py        # User management endpoints
│   │   │   └── attendance.py   # Attendance/time entry endpoints
│   │   ├── models/
│   │   │   └── database.py     # Database connection and queries
│   │   ├── __init__.py         # Flask app factory
│   │   └── config.py           # Configuration management
│   ├── database/
│   │   └── init_database.sql   # Database schema
│   ├── requirements.txt        # Python dependencies
│   ├── run.py                  # Application entry point
│   └── .env.example            # Environment variables template
├── frontend/
│   ├── manager/
│   │   └── portal.html         # Manager dashboard
│   ├── employee/
│   │   └── dashboard.html      # Employee dashboard
│   ├── css/
│   │   └── main.css            # Stylesheet
│   ├── js/
│   │   ├── main.js             # Common JavaScript
│   │   └── employee.js         # Employee dashboard logic
│   └── index.html              # Landing page
├── scripts/
│   ├── setup.sh                # Setup script
│   ├── start.sh                # Start servers
│   └── stop.sh                 # Stop servers
├── docs/                       # Documentation
└── README.md                   # This file
```

## Database Schema

### Table: `users`
Stores user credentials and profile information.

| Column        | Type          | Description                          |
|---------------|---------------|--------------------------------------|
| id            | INT           | Primary key                          |
| username      | VARCHAR(50)   | Unique username                      |
| display_name  | VARCHAR(100)  | Display name                         |
| email         | VARCHAR(100)  | Unique email address                 |
| password      | VARCHAR(255)  | Hashed password                      |
| user_level    | ENUM          | 'Manager' or 'Contractor'            |
| created_at    | TIMESTAMP     | Account creation time                |
| updated_at    | TIMESTAMP     | Last update time                     |

### Table: `manager_assignments`
Defines manager-contractor relationships.

| Column              | Type         | Description                          |
|---------------------|--------------|--------------------------------------|
| id                  | INT          | Primary key                          |
| manager_username    | VARCHAR(50)  | Manager's username (FK)              |
| contractor_username | VARCHAR(50)  | Contractor's username (FK)           |
| assigned_at         | TIMESTAMP    | Assignment creation time             |

### Table: `time_entries`
Tracks clock in/out times and approval status.

| Column      | Type         | Description                              |
|-------------|--------------|------------------------------------------|
| id          | INT          | Primary key                              |
| username    | VARCHAR(50)  | User's username (FK)                     |
| in_time     | DATETIME     | Clock in time                            |
| out_time    | DATETIME     | Clock out time (NULL if still clocked in)|
| status      | ENUM         | 'Pending', 'Approved', 'Rejected'        |
| approved_by | VARCHAR(50)  | Approver's username (FK)                 |
| approved_at | DATETIME     | Approval timestamp                       |
| notes       | TEXT         | Optional notes (rejection reason, etc.)  |
| created_at  | TIMESTAMP    | Record creation time                     |
| updated_at  | TIMESTAMP    | Last update time                         |

## Prerequisites

- **Python 3.8+**
- **MySQL 5.7+** or **MariaDB 10.3+**
- **pip** (Python package manager)
- **Git** (for cloning the repository)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd attendance-management-system
```

### 2. Run Setup Script

```bash
./scripts/setup.sh
```

The setup script will:
- Create a `.env` file from the template
- Install Python dependencies
- Prompt you to initialize the database
- Import the database schema

### 3. Configure Environment Variables

Edit `backend/.env` with your database credentials:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=practice_db

# Flask Configuration
SECRET_KEY=change-this-to-a-random-secret-key
DEBUG=True
PORT=5001
HOST=0.0.0.0

# CORS Configuration
CORS_ORIGINS=*
```

### 4. Initialize Database (Manual Method)

If you skipped the automated database setup, run:

```bash
# Create database
mysql -u root -p -e "CREATE DATABASE practice_db;"

# Import schema
mysql -u root -p practice_db < backend/database/init_database.sql
```

## Running the Application

### Start All Servers

```bash
./scripts/start.sh
```

This will start:
- **Backend API**: http://localhost:5001
- **Frontend**: http://localhost:8080

### Stop All Servers

```bash
./scripts/stop.sh
```

### Run Backend Only

```bash
cd backend
python3 run.py
```

### Run Frontend Only

```bash
cd frontend
python3 -m http.server 8080
```

## API Documentation

### Authentication

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "ylin",
  "password": "password123"
}
```

#### Register
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "jdoe",
  "display_name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "user_level": "Contractor"
}
```

### Users

#### Get User Info
```http
GET /api/users/<username>
```

#### Get User's Manager
```http
GET /api/users/<username>/manager
```

#### Get Manager's Contractors
```http
GET /api/users/<username>/contractors
```

#### Assign Manager to Contractor
```http
POST /api/users/assign-manager
Content-Type: application/json

{
  "manager_username": "ylin",
  "contractor_username": "jdoe"
}
```

### Attendance

#### Check In
```http
POST /api/attendance/check-in
Content-Type: application/json

{
  "username": "jdoe"
}
```

#### Check Out
```http
POST /api/attendance/check-out
Content-Type: application/json

{
  "username": "jdoe"
}
```

#### Get My Time Entries
```http
GET /api/attendance/my-entries?username=jdoe
```

#### Get Pending Approvals (Manager Only)
```http
GET /api/attendance/pending-approvals?manager_username=ylin
```

#### Approve/Reject Entry (Manager Only)
```http
POST /api/attendance/approve
Content-Type: application/json

{
  "manager_username": "ylin",
  "entry_id": 123,
  "status": "Approved",
  "notes": "Looks good!"
}
```

#### Get Monthly Summary
```http
GET /api/attendance/monthly-summary?username=jdoe&year=2025&month=12
```

## Usage

### For Contractors

1. **Login**: Navigate to http://localhost:8080 and click "Employee Login"
2. **Check In**: Click "Check In" when you start work
3. **Check Out**: Click "Check Out" when you finish work
4. **View History**: See all your time entries in the dashboard
5. **Monthly Report**: Select a month to view your attendance summary

### For Managers

1. **Login**: Navigate to http://localhost:8080 and click "Manager Login"
2. **View Pending**: See all pending approval requests from your team
3. **Approve/Reject**: Review and approve or reject time entries
4. **View Team**: Monitor your contractors' attendance
5. **Reports**: Access team attendance summaries

## Sample Data

The database initialization includes sample users:

| Username | Password (hashed)          | Display Name  | Role       |
|----------|---------------------------|---------------|------------|
| ylin     | (see init_database.sql)   | Yuchen Lin    | Manager    |
| xlu      | (see init_database.sql)   | Xuanyu Lu     | Contractor |
| jsmith   | (see init_database.sql)   | John Smith    | Contractor |

**Note**: Default passwords are hashed. For testing, you'll need to register new users or update the `init_database.sql` file.

## Development

### Backend Development

```bash
cd backend

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in debug mode
python3 run.py
```

### Frontend Development

The frontend uses vanilla JavaScript with no build process required. Simply edit the HTML/CSS/JS files and refresh your browser.

### Adding New API Endpoints

1. Create/edit files in `backend/app/api/`
2. Register blueprints in `backend/app/__init__.py`
3. Restart the backend server

## Security Considerations

⚠️ **Important for Production:**

1. **Password Hashing**: Currently uses SHA-256. Switch to `bcrypt` or `argon2` for production
2. **Secret Key**: Change `SECRET_KEY` in `.env` to a strong random value
3. **CORS**: Restrict `CORS_ORIGINS` to your frontend domain
4. **HTTPS**: Use HTTPS in production
5. **Input Validation**: Add more robust input validation
6. **SQL Injection**: The app uses parameterized queries, but review all database calls
7. **Authentication**: Consider implementing JWT tokens or session management

## Troubleshooting

### Database Connection Issues

```bash
# Check MySQL is running
sudo systemctl status mysql

# Test connection
mysql -u root -p
```

### Port Already in Use

```bash
# Check what's using port 5001
lsof -i :5001

# Kill the process
kill -9 <PID>
```

### Python Dependencies

```bash
# Reinstall dependencies
cd backend
pip install --force-reinstall -r requirements.txt
```

## Future Enhancements

- [ ] JWT authentication
- [ ] Email notifications for approvals
- [ ] QR code check-in/out
- [ ] Mobile app
- [ ] Export reports to PDF/Excel
- [ ] Real-time updates with WebSockets
- [ ] Two-factor authentication
- [ ] Audit logs
- [ ] Multi-language support

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Version**: 2.0
**Last Updated**: December 2025
**Developed with**: Flask, MySQL, Vanilla JavaScript
