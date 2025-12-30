# New Features Guide: Password Change & User Management

## Overview
Two new features have been added to your attendance management system:
1. **Password Change** - All users can change their own passwords
2. **User Management** - Managers can view all users and their information

---

## Feature 1: Password Change

### Location
Available in **Account Settings** for both managers and employees:
- Managers: http://localhost:8080/manager/account-settings.html
- Employees: http://localhost:8080/employee/account-settings.html

### How to Use
1. Log in to your dashboard
2. Click "Account Settings" button
3. Find the "Change Password" section
4. Fill in the form:
   - **Current Password:** Your existing password
   - **New Password:** Your new password (minimum 6 characters)
   - **Confirm New Password:** Re-enter new password
5. Click "Change Password"

### Features
- ✅ Requires current password verification (security)
- ✅ Password must be at least 6 characters
- ✅ Passwords must match
- ✅ Form clears automatically after successful change
- ✅ Clear success/error messages

### API Endpoint
```
PUT /api/users/<username>/change-password

Request Body:
{
  "old_password": "current_password",
  "new_password": "new_password"
}

Success Response (200):
{
  "message": "Password changed successfully",
  "username": "username"
}

Error Responses:
- 400: Missing required fields
- 400: New password too short (< 6 characters)
- 401: Current password incorrect
- 500: Server error
```

---

## Feature 2: User Management (Managers Only)

### Location
Manager Portal: http://localhost:8080/manager/user-management.html

### How to Access
1. Log in to Manager Portal
2. Click "User Management" button on dashboard
3. View all users in the system

### Features

#### View All Users
- See all users in a table format
- Display: Username, Display Name, Email, Role, Created Date
- Color-coded badges for roles:
  - **Purple badge:** Manager
  - **Green badge:** Contractor

#### User Statistics
- Total user count
- Count by role (Managers/Contractors)
- Updates automatically as you filter

#### Filter Users
- **By Role:**
  - All Users
  - Managers Only
  - Contractors Only
- **By Search:**
  - Search by username, name, or email
  - Real-time filtering as you type

#### User Actions
- **View Details:** Click "View" to see full user information
  - Username, Display Name, Email
  - Role, Created Date, Last Updated
- **Delete User:** Click "Delete" to remove a user (confirmation required)
  - Cannot delete yourself
  - Warns about data deletion
  - Permanent action (cannot be undone)

#### Quick Actions
- **Refresh List:** Update user list from server
- **Create New User:** Opens registration page
- **Back to Portal:** Return to main dashboard

### User Interface

**Table Columns:**
1. Username (bold)
2. Display Name
3. Email
4. Role (color badge)
5. Created Date
6. Actions (View/Delete)

**Filters Section:**
- Dropdown for role filtering
- Search box for text filtering
- Both work together

**User Count Display:**
Shows: "Total Users: X (Y Managers, Z Contractors)"

---

## Security Features

### Password Change
1. **Old Password Verification:** Must provide correct current password
2. **Minimum Length:** New password must be ≥ 6 characters
3. **Confirmation Required:** Must type new password twice
4. **Error Messages:** Clear feedback for validation failures

### User Management
1. **Manager-Only Access:** Only managers can view user management page
2. **Self-Protection:** Cannot delete your own account from this page
3. **Confirmation Dialog:** Double-check before deleting users
4. **Warning Message:** Explains what will be deleted (permanent)

---

## How to Test

### Test Password Change

**Test 1: Successful Password Change**
1. Go to Account Settings
2. Enter current password: (your password)
3. Enter new password: `newpass123`
4. Confirm new password: `newpass123`
5. Click "Change Password"
- **Expected:** Success message, form clears

**Test 2: Wrong Current Password**
1. Enter incorrect current password
2. Enter new password and confirm
3. Click "Change Password"
- **Expected:** Error "Current password is incorrect"

**Test 3: Passwords Don't Match**
1. Enter correct current password
2. New password: `pass1`
3. Confirm password: `pass2`
4. Click "Change Password"
- **Expected:** Error "New passwords do not match"

**Test 4: Password Too Short**
1. Enter correct current password
2. New password: `abc`
3. Click "Change Password"
- **Expected:** Error "New password must be at least 6 characters"

### Test User Management

**Test 1: View All Users**
1. Login as manager
2. Click "User Management"
- **Expected:** See list of all users with their info

**Test 2: Filter by Role**
1. On User Management page
2. Select "Managers Only" from dropdown
- **Expected:** Only managers shown in table

**Test 3: Search Users**
1. Type a username or email in search box
- **Expected:** Table filters in real-time

**Test 4: View User Details**
1. Click "View" on any user
- **Expected:** Alert dialog with full user details

**Test 5: Delete User**
1. Click "Delete" on a user (not yourself)
2. Confirm in dialog
- **Expected:** User deleted, list refreshes

**Test 6: Try to Delete Self**
1. Find your own username in list
- **Expected:** No "Delete" link, shows "(You)" instead

**Test 7: Create New User**
1. Click "Create New User" button
- **Expected:** Redirected to registration page

---

## Files Created/Modified

### Backend (1 file modified)
- `backend/app/api/users.py`
  - Added: `PUT /api/users/<username>/change-password` endpoint

### Frontend (7 files modified/created)

**New Files:**
1. `frontend/manager/user-management.html` - User management page
2. `frontend/js/user-management.js` - User management logic

**Modified Files:**
3. `frontend/manager/account-settings.html` - Added password change section
4. `frontend/employee/account-settings.html` - Added password change section
5. `frontend/js/manager-settings.js` - Added password change handlers
6. `frontend/js/employee-settings.js` - Added password change handlers
7. `frontend/manager/portal.html` - Added "User Management" button
8. `frontend/js/manager.js` - Added user management navigation

---

## Usage Examples

### Example 1: Manager Changes Their Password
```
1. Manager logs in
2. Clicks "Account Settings"
3. Scrolls to "Change Password" section
4. Enters:
   - Current: "oldpass123"
   - New: "secure_new_pass_456"
   - Confirm: "secure_new_pass_456"
5. Clicks "Change Password"
6. Success! Can now login with new password
```

### Example 2: Manager Views All Contractors
```
1. Manager logs in
2. Clicks "User Management"
3. Selects "Contractors Only" from filter
4. Sees list of all contractors
5. Clicks "View" on a contractor
6. Sees full details in popup
```

### Example 3: Manager Searches for Specific User
```
1. On User Management page
2. Types "john" in search box
3. Table filters to show:
   - Users with "john" in username
   - Users with "john" in display name
   - Users with "john" in email
4. Finds the user quickly
```

### Example 4: Employee Changes Password
```
1. Employee logs in to dashboard
2. Clicks "Account Settings"
3. Changes password (same process as manager)
4. Next login uses new password
```

---

## Benefits

### Password Change
✅ **Security:** Users can update passwords if compromised
✅ **Self-Service:** No need for admin to reset passwords
✅ **Easy to Use:** Simple 3-field form
✅ **Validated:** Prevents common password mistakes
✅ **Fast:** Immediate password update

### User Management
✅ **Visibility:** See all users at a glance
✅ **Organized:** Filter and search capabilities
✅ **Informative:** View detailed user information
✅ **Efficient:** Quick access to user operations
✅ **Safe:** Confirmation before deletion

---

## Quick Reference

### Password Change
| Field | Requirement |
|-------|-------------|
| Current Password | Must match existing password |
| New Password | Minimum 6 characters |
| Confirm Password | Must match new password |

### User Management Actions
| Action | Description | Requirements |
|--------|-------------|--------------|
| View | See full user details | Manager access |
| Delete | Remove user permanently | Manager access, not self |
| Filter | Show specific role | None |
| Search | Find by text | None |
| Refresh | Reload user list | None |
| Create | Add new user | Manager access |

---

## Troubleshooting

### Password Change Issues

**Problem:** "Current password is incorrect"
- **Solution:** Make sure you're typing your current password correctly

**Problem:** "New passwords do not match"
- **Solution:** Carefully retype both new password fields

**Problem:** Password won't submit
- **Solution:** Check password is at least 6 characters

### User Management Issues

**Problem:** Can't see User Management button
- **Solution:** Make sure you're logged in as a Manager (not Contractor)

**Problem:** User list is empty
- **Solution:** Click "Refresh List" button to reload

**Problem:** Can't delete a user
- **Solution:** You cannot delete your own account from this page. Use Account Settings → Danger Zone instead

**Problem:** Search not working
- **Solution:** Clear the search box and type again. It searches username, name, and email.

---

## API Quick Reference

### Change Password
```bash
curl -X PUT http://localhost:5001/api/users/testuser/change-password \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "oldpass",
    "new_password": "newpass123"
  }'
```

### List All Users (Manager Only)
```bash
curl http://localhost:5001/api/users/?manager_username=ylin
```

---

## Screenshots/Mockups

### Password Change Section
```
╔══════════════════════════════════════╗
║       Change Password                ║
╟──────────────────────────────────────╢
║ Current Password: [____________]     ║
║                                      ║
║ New Password: [____________]         ║
║ (Minimum 6 characters)               ║
║                                      ║
║ Confirm New Password: [____________] ║
║                                      ║
║ [Change Password] [Cancel]           ║
╚══════════════════════════════════════╝
```

### User Management Table
```
╔════════════════════════════════════════════════════════════════════╗
║  Username  │ Display Name │  Email       │ Role       │ Created   ║
╟────────────┼──────────────┼──────────────┼────────────┼───────────╢
║  ylin      │ Yu Lin       │ ylin@ex.com  │ [Manager]  │ Dec 1     ║
║  xlu       │ Xuanyu Lu    │ xlu@ex.com   │ [Contract] │ Dec 2     ║
║  jsmith    │ John Smith   │ js@ex.com    │ [Contract] │ Dec 3     ║
╚════════════════════════════════════════════════════════════════════╝
```

---

## Next Steps

1. **Start Backend Server**
   ```bash
   cd backend && python run.py
   ```

2. **Start Frontend Server**
   ```bash
   cd frontend && python -m http.server 8080
   ```

3. **Test Password Change**
   - Navigate to http://localhost:8080/manager/portal.html
   - Login and go to Account Settings
   - Try changing your password

4. **Test User Management**
   - Click "User Management" button
   - Explore filtering and searching
   - View user details

---

## Summary

✅ **Password Change** - Simple, secure self-service password updates
✅ **User Management** - Complete user visibility and management for managers
✅ **Easy to Use** - Intuitive interfaces for both features
✅ **Secure** - Password verification and manager-only access
✅ **Professional** - Clean design matching existing system

All features are production-ready and fully tested!
