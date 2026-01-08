// Manager Portal JavaScript - Manages Leads (Super User)

<<<<<<< HEAD
// Auto-detect environment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5001/api'
    : 'https://attendance-management-system-production-1f1a.up.railway.app/api';

=======
const API_BASE_URL = 'http://localhost:5001/api';
>>>>>>> parent of dd9b182 (f)
let currentUser = null;
let leads = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkSession();
    setupEventListeners();
});

function checkSession() {
    const user = sessionStorage.getItem('user');
    if (user) {
        currentUser = JSON.parse(user);
        if (currentUser.user_level === 'Manager') {
            showDashboard();
        } else {
            showMessage('Access denied. Managers only.', 'error');
        }
    }
}

function setupEventListeners() {
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    document.getElementById('refresh-leads-btn')?.addEventListener('click', loadLeads);
    document.getElementById('view-pending-btn').addEventListener('click', loadPendingApprovals);
    document.getElementById('refresh-pending-btn').addEventListener('click', loadPendingApprovals);
    document.getElementById('user-management-btn').addEventListener('click', () => {
        window.location.href = 'user-management.html';
    });
    document.getElementById('account-settings-btn').addEventListener('click', () => {
        window.location.href = 'account-settings.html';
    });
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

            if (currentUser.user_level !== 'Manager') {
                showMessage('Access denied. Managers only.', 'error');
                return;
            }

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
    loadLeads();
    loadPendingApprovals();
}

async function loadLeads() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/users/manager/${currentUser.username}/leads`
        );
        const data = await response.json();

        if (response.ok) {
            leads = data.leads || [];
            displayLeads();
        } else {
            showMessage(data.error || 'Failed to load leads', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

async function displayLeads() {
    const container = document.getElementById('leads-list');

    if (leads.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">No leads found. Create new leads in User Management.</p>';
        return;
    }

    let html = '<div class="leads-grid">';

    for (const lead of leads) {
        // Get members for this lead
        const members = await getLeadMembers(lead.username);

        html += `
            <div class="lead-card">
                <h3>${lead.display_name}</h3>
                <p><strong>Username:</strong> ${lead.username}</p>
                <p><strong>Email:</strong> ${lead.email}</p>
                <p><strong>Members:</strong> ${members.length}</p>
                <button class="btn btn-primary btn-sm" onclick="viewLeadDetails('${lead.username}')">
                    View Details
                </button>
            </div>
        `;
    }

    html += '</div>';
    container.innerHTML = html;
}

async function getLeadMembers(leadUsername) {
    try {
        const response = await fetch(
            `${API_BASE_URL}/users/lead/${leadUsername}/members`
        );
        const data = await response.json();

        if (response.ok) {
            return data.members || [];
        }
        return [];
    } catch (error) {
        console.error('Error loading members:', error);
        return [];
    }
}

async function viewLeadDetails(leadUsername) {
    const lead = leads.find(l => l.username === leadUsername);
    if (!lead) return;

    const members = await getLeadMembers(leadUsername);

    let membersHtml = members.length > 0
        ? members.map(m => `
            <li>
                <strong>${m.display_name}</strong> (${m.username})
                <br><small>${m.email}</small>
            </li>
          `).join('')
        : '<li style="color: #666;">No members yet</li>';

    const detailsHtml = `
        <div class="card" style="background: #f8f9fa; margin-top: 20px; border: 2px solid #007bff;">
            <h3>Lead Details: ${lead.display_name}</h3>
            <div style="margin: 15px 0;">
                <p><strong>Username:</strong> ${lead.username}</p>
                <p><strong>Email:</strong> ${lead.email}</p>
                <p><strong>Created:</strong> ${new Date(lead.created_at).toLocaleDateString()}</p>
            </div>
            <h4>Members (${members.length})</h4>
            <ul style="list-style: none; padding: 0;">
                ${membersHtml}
            </ul>
            <button class="btn btn-secondary" onclick="closeLeadDetails()">Close</button>
        </div>
    `;

    const detailsContainer = document.getElementById('lead-details');
    detailsContainer.innerHTML = detailsHtml;
    detailsContainer.style.display = 'block';
}

function closeLeadDetails() {
    document.getElementById('lead-details').style.display = 'none';
    document.getElementById('lead-details').innerHTML = '';
}

async function loadPendingApprovals() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/attendance/pending-approvals?username=${currentUser.username}`
        );
        const data = await response.json();

        if (response.ok) {
            displayPendingApprovals(data.pending_entries || []);
        } else {
            showMessage(data.error || 'Failed to load pending approvals', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function displayPendingApprovals(entries) {
    const container = document.getElementById('pending-content');

    if (!entries || entries.length === 0) {
        container.innerHTML = '<p>No pending approvals</p>';
        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>User</th>
                    <th>Check-in</th>
                    <th>Check-out</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
    `;

    entries.forEach(entry => {
        html += `
            <tr>
                <td>${entry.display_name || entry.username}</td>
                <td>${formatDateTime(entry.in_time)}</td>
                <td>${formatDateTime(entry.out_time)}</td>
                <td>
                    <button onclick="approveEntry(${entry.id}, 'Approved')" class="btn btn-success btn-sm">Approve</button>
                    <button onclick="approveEntry(${entry.id}, 'Rejected')" class="btn btn-danger btn-sm">Reject</button>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

async function approveEntry(entryId, status) {
    try {
        const response = await fetch(`${API_BASE_URL}/attendance/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                approver_username: currentUser.username,
                entry_id: entryId,
                status: status
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message, 'success');
            loadPendingApprovals();
        } else {
            showMessage(data.error || 'Approval failed', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function handleLogout() {
    sessionStorage.removeItem('user');
    currentUser = null;
    leads = [];
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

// Make functions globally accessible
window.approveEntry = approveEntry;
window.viewLeadDetails = viewLeadDetails;
window.closeLeadDetails = closeLeadDetails;
