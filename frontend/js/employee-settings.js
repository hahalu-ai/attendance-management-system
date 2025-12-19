const API_BASE_URL = 'http://localhost:5001/api';
let currentUser = null;

document.addEventListener('DOMContentLoaded', () => {
    checkSession();
    setupEventListeners();
});

function checkSession() {
    const user = sessionStorage.getItem('user');
    if (user) {
        currentUser = JSON.parse(user);
        loadUserProfile();
        checkDeletionEligibility();
    } else {
        window.location.href = 'dashboard.html';
    }
}

function setupEventListeners() {
    document.getElementById('password-form').addEventListener('submit', handlePasswordChange);
    document.getElementById('cancel-password-btn').addEventListener('click', resetPasswordForm);
    document.getElementById('show-delete-btn').addEventListener('click', showDeleteForm);
    document.getElementById('cancel-delete-btn').addEventListener('click', hideDeleteForm);
    document.getElementById('confirm-delete-btn').addEventListener('click', confirmDeleteAccount);
}

async function loadUserProfile() {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${currentUser.username}`);
        const data = await response.json();

        if (response.ok) {
            displayProfile(data);
        } else {
            showMessage('Failed to load profile', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function displayProfile(user) {
    document.getElementById('user-info').innerHTML = `
        Logged in as: <strong>${user.display_name}</strong> (${user.username})
    `;

    document.getElementById('profile-info').innerHTML = `
        <p><strong>Username:</strong> ${user.username}</p>
        <p><strong>Display Name:</strong> ${user.display_name}</p>
        <p><strong>Email:</strong> ${user.email}</p>
        <p><strong>User Level:</strong> ${user.user_level}</p>
        <p><strong>Account Created:</strong> ${formatDateTime(user.created_at)}</p>
    `;
}

async function checkDeletionEligibility() {
    try {
        // Check for pending time entries
        const response = await fetch(`${API_BASE_URL}/attendance/my-entries?username=${currentUser.username}`);
        const data = await response.json();

        if (response.ok) {
            const entries = data.entries || [];
            const pendingEntries = entries.filter(e => e.status === 'Pending');
            const checkDiv = document.getElementById('deletion-check');

            if (pendingEntries.length > 0) {
                checkDiv.innerHTML = `
                    <div class="warning-box">
                        <p><strong>⚠ Cannot Delete Account:</strong></p>
                        <p>You have ${pendingEntries.length} pending time entry/entries.</p>
                        <p>Please wait for manager approval or contact your manager before deleting your account.</p>
                    </div>
                `;
                document.getElementById('show-delete-btn').disabled = true;
            }
        }
    } catch (error) {
        console.error('Error checking deletion eligibility:', error);
    }
}

async function handlePasswordChange(e) {
    e.preventDefault();

    const currentPassword = document.getElementById('current-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-new-password').value;

    // Validate passwords match
    if (newPassword !== confirmPassword) {
        showMessage('New passwords do not match', 'error');
        return;
    }

    if (newPassword.length < 6) {
        showMessage('New password must be at least 6 characters', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/${currentUser.username}/change-password`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                old_password: currentPassword,
                new_password: newPassword
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('Password changed successfully!', 'success');
            resetPasswordForm();
        } else {
            showMessage(data.error || 'Failed to change password', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function resetPasswordForm() {
    document.getElementById('password-form').reset();
}

function showDeleteForm() {
    document.getElementById('delete-form').style.display = 'block';
    document.getElementById('show-delete-btn').style.display = 'none';
}

function hideDeleteForm() {
    document.getElementById('delete-form').style.display = 'none';
    document.getElementById('show-delete-btn').style.display = 'inline-block';
    document.getElementById('delete-password').value = '';
    document.getElementById('confirm-checkbox').checked = false;
}

async function confirmDeleteAccount() {
    const password = document.getElementById('delete-password').value;
    const confirmed = document.getElementById('confirm-checkbox').checked;

    if (!password) {
        showMessage('Please enter your password', 'error');
        return;
    }

    if (!confirmed) {
        showMessage('Please confirm that you understand this action is permanent', 'error');
        return;
    }

    if (!confirm('Are you absolutely sure? This cannot be undone!')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/${currentUser.username}/self-delete`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password: password })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('Account deleted successfully. Redirecting...', 'success');
            sessionStorage.removeItem('user');
            setTimeout(() => {
                window.location.href = '../index.html';
            }, 2000);
        } else {
            showMessage(data.error || 'Deletion failed', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function formatDateTime(dateTimeString) {
    if (!dateTimeString) return 'N/A';
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function showMessage(message, type = 'success') {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';

    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}
