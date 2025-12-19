// Employee Dashboard JavaScript

const API_BASE_URL = 'http://localhost:5001/api';
let currentUser = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkSession();
    setupEventListeners();
    setDefaultMonth();
});

function checkSession() {
    const user = sessionStorage.getItem('user');
    if (user) {
        currentUser = JSON.parse(user);
        showDashboard();
    }
}

function setupEventListeners() {
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('check-in-btn').addEventListener('click', handleCheckIn);
    document.getElementById('check-out-btn').addEventListener('click', handleCheckOut);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    document.getElementById('get-summary-btn').addEventListener('click', getMonthlySummary);
    document.getElementById('account-settings-btn').addEventListener('click', () => {
        window.location.href = 'account-settings.html';
    });
}

function setDefaultMonth() {
    const now = new Date();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const year = now.getFullYear();
    document.getElementById('summary-month').value = `${year}-${month}`;
}

async function handleLogin(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            currentUser = data.user;
            sessionStorage.setItem('user', JSON.stringify(currentUser));
            showDashboard();
            showMessage('Login successful!', 'success');
        } else {
            showMessage(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function showDashboard() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'block';
    document.getElementById('user-info').innerHTML = `
        Logged in as: <strong>${currentUser.display_name}</strong> (${currentUser.username})
    `;
    loadTimeEntries();
}

async function handleCheckIn() {
    try {
        const response = await fetch(`${API_BASE_URL}/attendance/check-in`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser.username })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message, 'success');
            loadTimeEntries();
        } else {
            showMessage(data.error || 'Check-in failed', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

async function handleCheckOut() {
    try {
        const response = await fetch(`${API_BASE_URL}/attendance/check-out`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser.username })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message, 'success');
            loadTimeEntries();
        } else {
            showMessage(data.error || 'Check-out failed', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

async function loadTimeEntries() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/attendance/my-entries?username=${currentUser.username}`
        );
        const data = await response.json();

        if (response.ok) {
            displayTimeEntries(data.entries);
        } else {
            showMessage(data.error || 'Failed to load entries', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function displayTimeEntries(entries) {
    const container = document.getElementById('entries-list');

    if (!entries || entries.length === 0) {
        container.innerHTML = '<p>No time entries found.</p>';
        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>Check In</th>
                    <th>Check Out</th>
                    <th>Status</th>
                    <th>Approved By</th>
                </tr>
            </thead>
            <tbody>
    `;

    entries.forEach(entry => {
        html += `
            <tr>
                <td>${formatDateTime(entry.in_time)}</td>
                <td>${formatDateTime(entry.out_time)}</td>
                <td><span class="status-badge status-${entry.status.toLowerCase()}">${entry.status}</span></td>
                <td>${entry.approved_by || 'N/A'}</td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

async function getMonthlySummary() {
    const monthValue = document.getElementById('summary-month').value;
    if (!monthValue) {
        showMessage('Please select a month', 'error');
        return;
    }

    const [year, month] = monthValue.split('-');

    try {
        const response = await fetch(
            `${API_BASE_URL}/attendance/monthly-summary?username=${currentUser.username}&year=${year}&month=${month}`
        );
        const data = await response.json();

        if (response.ok) {
            displayMonthlySummary(data);
        } else {
            showMessage(data.error || 'Failed to load summary', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function displayMonthlySummary(data) {
    const container = document.getElementById('monthly-summary');
    const summary = data.summary;

    let html = `
        <div class="summary-stats">
            <p><strong>Days Worked:</strong> ${summary.days_worked} / ${summary.expected_workdays}</p>
            <p><strong>Total Hours:</strong> ${summary.total_hours}</p>
            <p><strong>Full Attendance:</strong> ${summary.is_full_attendance ? 'Yes' : 'No'}</p>
        </div>
    `;

    container.innerHTML = html;
}

function handleLogout() {
    sessionStorage.removeItem('user');
    currentUser = null;
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('login-form').reset();
    showMessage('Logged out successfully', 'success');
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
