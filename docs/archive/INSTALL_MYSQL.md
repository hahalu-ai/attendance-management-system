# MySQL Installation and Setup Guide for WSL2

## Option 1: Install MySQL on WSL2 (Recommended)

### Step 1: Install MySQL Server
```bash
sudo apt update
sudo apt install mysql-server -y
```

### Step 2: Start MySQL Service
```bash
sudo service mysql start
```

### Step 3: Secure MySQL Installation (Optional but Recommended)
```bash
sudo mysql_secure_installation
```
- You can set a root password or press Enter to skip
- Answer Y/N to security questions as needed

### Step 4: Create the Database
```bash
sudo mysql -u root
```

Then in the MySQL prompt:
```sql
CREATE DATABASE IF NOT EXISTS practice_db;
EXIT;
```

### Step 5: Update Database Connection (if you set a root password)
If you set a root password, update the password in `db.py`:
```python
password="your_new_password"
```

### Step 6: Initialize the Database
```bash
python3 setup_database.py
```

### Step 7: Start the Flask Server
```bash
python3 app.py
```

## Option 2: Use SQLite Instead (Quick Alternative)

If you want to avoid MySQL installation, I can convert the system to use SQLite, which requires no server setup.

### Advantages:
- No installation needed
- Lightweight
- Perfect for development/testing
- No service to start

### Disadvantages:
- Less suitable for production
- Simpler feature set than MySQL

Let me know if you'd like me to convert to SQLite!

## Option 3: Use MySQL on Windows (WSL2 Integration)

If you have MySQL running on Windows, you can connect to it from WSL:

1. Find your Windows IP from WSL:
```bash
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'
```

2. Update `db.py` with the Windows IP:
```python
host="172.x.x.x"  # Replace with your Windows IP
```

3. Ensure MySQL on Windows allows remote connections

## Troubleshooting

### MySQL won't start on WSL2
```bash
# Check MySQL status
sudo service mysql status

# Try restarting
sudo service mysql restart

# Check error logs
sudo tail -50 /var/log/mysql/error.log
```

### Permission denied
```bash
sudo usermod -d /var/lib/mysql/ mysql
sudo service mysql restart
```

### Can't connect after installation
```bash
# Connect without password (fresh install)
sudo mysql -u root

# Or with password
mysql -u root -p
```
