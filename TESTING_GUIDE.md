# Testing Guide: User Registration & Account Deletion Features

## Overview
This guide helps you test the newly implemented user registration UI and account deletion features.

## Prerequisites
1. Start the backend server: `cd backend && python run.py`
2. Start the frontend server: `cd frontend && python -m http.server 8080`
3. Ensure MySQL database is running

---

## Feature 1: Manager-Controlled User Registration

### Test 1: Access Registration Page
**Steps:**
1. Navigate to http://localhost:8080/manager/portal.html
2. Look for "Create New Account" link below the login button
3. Click the link

**Expected Result:**
- Redirected to http://localhost:8080/register.html
- See "Manager Login Required" section

### Test 2: Manager Authentication for Registration
**Steps:**
1. On register.html, enter manager credentials (e.g., username: `ylin`)
2. Click "Login"

**Expected Result:**
- Login section hidden
- Registration form displayed
- Header shows "Manager: [Display Name] (username)"

### Test 3: Create New Contractor Account
**Steps:**
1. Fill out the registration form:
   - Username: `testuser`
   - Display Name: `Test User`
   - Email: `test@example.com`
   - Password: `password123`
   - Confirm Password: `password123`
   - User Level: `Contractor`
2. Click "Create Account"

**Expected Result:**
- Success message: "Account created successfully for testuser!"
- Browser prompt: "Would you like to assign testuser to yourself as their manager?"
- Click "OK" to auto-assign
- Form resets
- If assignment succeeds, another success message appears

### Test 4: Create New Manager Account
**Steps:**
1. Fill out form with different username/email
2. Set User Level to "Manager"
3. Click "Create Account"

**Expected Result:**
- Success message
- No assignment prompt (only for contractors)

### Test 5: Validation Tests
**Test password mismatch:**
1. Enter different passwords in "Password" and "Confirm Password"
2. Click "Create Account"
- Expected: Error message "Passwords do not match"

**Test duplicate username:**
1. Try to create user with existing username
- Expected: Error "Username or email already exists"

**Test required fields:**
1. Leave fields blank
- Expected: Browser validation prevents submission

---

## Feature 2: Account Deletion (Self-Service)

### Test 6: Manager Account Settings
**Steps:**
1. Log in to manager portal (http://localhost:8080/manager/portal.html)
2. After login, click "Account Settings" button in dashboard
3. Redirected to account-settings.html

**Expected Result:**
- Profile information displayed (username, display name, email, user level, creation date)
- "Danger Zone" section visible
- "Delete My Account" button present

### Test 7: Manager with Assigned Contractors (Deletion Blocked)
**Steps:**
1. On manager account settings page
2. If you have contractors assigned, see warning box

**Expected Result:**
- Warning box shows: "Cannot Delete Account"
- Lists assigned contractors
- "Delete My Account" button is disabled
- Message: "Please reassign them to another manager before deleting your account"

### Test 8: Manager Self-Deletion (No Contractors)
**Steps:**
1. Ensure manager has no contractors assigned
2. Click "Delete My Account"
3. Delete form appears
4. Enter correct password
5. Check the confirmation checkbox
6. Click "Permanently Delete Account"
7. Confirm in browser dialog

**Expected Result:**
- Account deleted successfully
- Success message: "Account deleted successfully. Redirecting..."
- Session cleared
- Redirected to home page (index.html) after 2 seconds

### Test 9: Employee Account Settings
**Steps:**
1. Log in to employee dashboard (http://localhost:8080/employee/dashboard.html)
2. Click "Account Settings" button
3. Redirected to account-settings.html

**Expected Result:**
- Profile information displayed
- "Danger Zone" section visible

### Test 10: Employee with Pending Time Entries (Deletion Blocked)
**Steps:**
1. Employee account with pending time entries
2. On account settings page

**Expected Result:**
- Warning box shows: "Cannot Delete Account"
- Shows count of pending entries
- "Delete My Account" button is disabled
- Message: "Please wait for manager approval or contact your manager"

### Test 11: Employee Self-Deletion (No Pending Entries)
**Steps:**
1. Ensure employee has no pending time entries
2. Click "Delete My Account"
3. Enter correct password
4. Check confirmation checkbox
5. Click "Permanently Delete Account"
6. Confirm in browser dialog

**Expected Result:**
- Account deleted successfully
- Session cleared
- Redirected to home page

### Test 12: Wrong Password for Deletion
**Steps:**
1. Click "Delete My Account"
2. Enter incorrect password
3. Check checkbox
4. Click "Permanently Delete Account"

**Expected Result:**
- Error message: "Invalid password"
- Account NOT deleted
- User remains on settings page

### Test 13: Cancel Deletion
**Steps:**
1. Click "Delete My Account"
2. Delete form appears
3. Click "Cancel" button

**Expected Result:**
- Delete form hidden
- "Delete My Account" button visible again
- No changes made

---

## API Endpoint Testing

### Test 14: Self-Deletion API (cURL)
```bash
# Test valid deletion
curl -X DELETE http://localhost:5001/api/users/testuser/self-delete \
  -H "Content-Type: application/json" \
  -d '{"password": "password123"}'

# Expected: 200 OK with success message

# Test invalid password
curl -X DELETE http://localhost:5001/api/users/testuser/self-delete \
  -H "Content-Type: application/json" \
  -d '{"password": "wrongpassword"}'

# Expected: 401 Unauthorized
```

### Test 15: Registration API (cURL)
```bash
# Create new contractor
curl -X POST http://localhost:5001/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "manager_username": "ylin",
    "username": "newuser",
    "display_name": "New User",
    "email": "newuser@example.com",
    "password": "password123",
    "user_level": "Contractor"
  }'

# Expected: 201 Created with user info
```

---

## Database Verification

### Test 16: Check CASCADE Deletion
**Steps:**
1. Create test user with time entries
2. Delete user via self-deletion
3. Check database:

```sql
-- Before deletion
SELECT * FROM users WHERE username = 'testuser';
SELECT * FROM time_entries WHERE username = 'testuser';
SELECT * FROM manager_assignments WHERE contractor_username = 'testuser';

-- After deletion (should all be empty)
SELECT * FROM users WHERE username = 'testuser';
SELECT * FROM time_entries WHERE username = 'testuser';
SELECT * FROM manager_assignments WHERE contractor_username = 'testuser';
```

**Expected Result:**
- All related records deleted automatically (CASCADE)

---

## Edge Cases to Test

### Test 17: Session Management
**Test:**
1. Delete account
2. Try to use browser back button
3. Try to access dashboard

**Expected:**
- Session cleared
- Redirected to login page
- No access to deleted account

### Test 18: Concurrent Operations
**Test:**
1. Manager opens registration page
2. Manager logs out from another tab
3. Try to create user

**Expected:**
- Should still work if session was saved
- Or require re-login if session cleared

### Test 19: Network Errors
**Test:**
1. Stop backend server
2. Try to create account or delete account

**Expected:**
- Error message: "Connection error: [error details]"
- User-friendly error display

---

## Checklist Summary

**Registration:**
- [ ] "Create Account" link visible on login pages
- [ ] Manager authentication required
- [ ] Form validation works
- [ ] Contractor creation successful
- [ ] Manager creation successful
- [ ] Auto-assignment option appears for contractors
- [ ] Duplicate username/email blocked
- [ ] Form resets after successful creation

**Account Deletion:**
- [ ] "Account Settings" button visible in both dashboards
- [ ] Profile information loads correctly
- [ ] Contractor blocked if pending entries exist
- [ ] Manager blocked if contractors assigned
- [ ] Password verification works
- [ ] Confirmation checkbox required
- [ ] Browser confirmation dialog appears
- [ ] Account successfully deleted
- [ ] Session cleared after deletion
- [ ] Redirect to home page works
- [ ] CASCADE cleanup verified in database
- [ ] Wrong password rejected
- [ ] Cancel button works

---

## Known Issues / Notes

1. **Security:** Currently uses SHA-256 password hashing. Consider upgrading to bcrypt for production.
2. **Soft Delete:** Current implementation is hard delete (permanent). Consider soft delete for audit trail.
3. **Email Notifications:** No email sent on account creation/deletion. Add if needed.
4. **Undo:** No way to recover deleted accounts. Ensure users understand this is permanent.

---

## Success Criteria

All features working correctly when:
1. Managers can create accounts through the registration page
2. Users can delete their own accounts (with restrictions)
3. Managers can still delete any user account (existing functionality preserved)
4. All validation and business logic rules enforced
5. Database CASCADE cleanup works properly
6. Session management works correctly
7. Error handling provides user-friendly messages

## Questions or Issues?

If any test fails, check:
1. Backend server running on port 5001
2. Frontend server running on port 8080
3. MySQL database accessible
4. Browser console for JavaScript errors
5. Backend console for API errors
