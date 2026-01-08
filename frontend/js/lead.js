// Lead Portal JavaScript

// Auto-detect environment
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5001/api'
    : 'https://attendance-management-system-production-1f1a.up.railway.app/api';

let currentUser = null;
let members = [];
let qrTimer = null;
let qrCode = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkSession();
    setupEventListeners();
    setupTabs();
});

function checkSession() {
    const user = sessionStorage.getItem('user');
    if (user) {
        currentUser = JSON.parse(user);
        if (currentUser.user_level === 'Lead') {
            showDashboard();
        } else {
            showMessage('Access denied. Leads only.', 'error');
        }
    }
}

function setupEventListeners() {
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    document.getElementById('member-select').addEventListener('change', handleMemberSelection);
    document.getElementById('generate-checkin-btn').addEventListener('click', () => generateQR('check-in'));
    document.getElementById('generate-checkout-btn').addEventListener('click', () => generateQR('check-out'));
    document.getElementById('cancel-qr-btn').addEventListener('click', cancelQR);
    document.getElementById('refresh-members-btn').addEventListener('click', loadMembers);
    document.getElementById('refresh-pending-btn').addEventListener('click', loadPendingApprovals);
    document.getElementById('add-member-btn').addEventListener('click', showAddMemberForm);
    document.getElementById('cancel-add-member-btn').addEventListener('click', hideAddMemberForm);
    document.getElementById('add-member-form').addEventListener('submit', handleAddMember);
    document.getElementById('account-settings-btn').addEventListener('click', () => {
        window.location.href = 'account-settings.html';
    });
}

function setupTabs() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and contents
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            // Add active class to clicked tab and its content
            tab.classList.add('active');
            const tabId = tab.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');

            // Load data when switching tabs
            if (tabId === 'members-tab') {
                loadMembers();
            } else if (tabId === 'approvals-tab') {
                loadPendingApprovals();
            }
        });
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

            if (currentUser.user_level !== 'Lead') {
                showMessage('Access denied. Leads only.', 'error');
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
    loadMembers();
}

async function loadMembers() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/users/lead/${currentUser.username}/members`
        );
        const data = await response.json();

        if (response.ok) {
            members = data.members || [];
            populateMemberSelect();
            displayMembersList();
        } else {
            showMessage(data.error || 'Failed to load members', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function populateMemberSelect() {
    const select = document.getElementById('member-select');
    select.innerHTML = '<option value="">-- Select a Member --</option>';

    members.forEach(member => {
        const option = document.createElement('option');
        option.value = member.username;
        option.textContent = `${member.display_name} (${member.username})`;
        select.appendChild(option);
    });
}

function displayMembersList() {
    const container = document.getElementById('members-list');

    if (members.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">No members yet. Click "Add New Member" to get started.</p>';
        return;
    }

    container.innerHTML = members.map(member => `
        <div class="member-card">
            <h4>${member.display_name}</h4>
            <p><strong>Username:</strong> ${member.username}</p>
            <p><strong>Email:</strong> ${member.email}</p>
            <p><strong>Added:</strong> ${new Date(member.assigned_at).toLocaleDateString()}</p>
            <button class="btn btn-danger btn-sm" onclick="removeMember('${member.username}', '${member.display_name}')">
                Remove Member
            </button>
        </div>
    `).join('');
}

function showAddMemberForm() {
    document.getElementById('add-member-modal').style.display = 'block';
}

function hideAddMemberForm() {
    document.getElementById('add-member-modal').style.display = 'none';
    document.getElementById('add-member-form').reset();
}

async function handleAddMember(e) {
    e.preventDefault();

    const memberUsername = document.getElementById('new-member-username').value;
    const displayName = document.getElementById('new-member-name').value;
    const email = document.getElementById('new-member-email').value;

    try {
        const response = await fetch(
            `${API_BASE_URL}/users/lead/${currentUser.username}/members`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    member_username: memberUsername,
                    display_name: displayName,
                    email: email
                })
            }
        );

        const data = await response.json();

        if (response.ok) {
            showMessage('Member created successfully!', 'success');
            hideAddMemberForm();
            loadMembers();
        } else {
            showMessage(data.error || 'Failed to create member', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

async function removeMember(memberUsername, memberName) {
    if (!confirm(`Are you sure you want to remove ${memberName} from your team?`)) {
        return;
    }

    try {
        const response = await fetch(
            `${API_BASE_URL}/users/lead/${currentUser.username}/members/${memberUsername}`,
            {
                method: 'DELETE'
            }
        );

        const data = await response.json();

        if (response.ok) {
            showMessage('Member removed successfully', 'success');
            loadMembers();
        } else {
            showMessage(data.error || 'Failed to remove member', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

async function handleMemberSelection() {
    const memberUsername = document.getElementById('member-select').value;

    if (!memberUsername) {
        document.getElementById('member-status').style.display = 'none';
        document.getElementById('action-buttons').style.display = 'none';
        return;
    }

    const member = members.find(m => m.username === memberUsername);

    try {
        // Check if member has open time entry
        const response = await fetch(
            `${API_BASE_URL}/attendance/my-entries?username=${memberUsername}`
        );
        const data = await response.json();

        if (response.ok) {
            const entries = data.entries || [];
            const openEntry = entries.find(e => e.out_time === null);

            // Show member status
            document.getElementById('selected-member-name').textContent = member.display_name;

            if (openEntry) {
                document.getElementById('member-clock-status').innerHTML =
                    '<span class="status-clocked-in">Clocked In</span>';
                document.getElementById('last-checkin-time').textContent =
                    `Checked in at: ${new Date(openEntry.in_time).toLocaleString()}`;
                document.getElementById('generate-checkin-btn').disabled = true;
                document.getElementById('generate-checkout-btn').disabled = false;
            } else {
                document.getElementById('member-clock-status').innerHTML =
                    '<span class="status-clocked-out">Clocked Out</span>';
                document.getElementById('last-checkin-time').textContent = '';
                document.getElementById('generate-checkin-btn').disabled = false;
                document.getElementById('generate-checkout-btn').disabled = true;
            }

            document.getElementById('member-status').style.display = 'block';
            document.getElementById('action-buttons').style.display = 'flex';
        }
    } catch (error) {
        showMessage('Error loading member status: ' + error.message, 'error');
    }
}

async function generateQR(action) {
    const memberUsername = document.getElementById('member-select').value;

    if (!memberUsername) {
        showMessage('Please select a member first', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/attendance/qr/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lead_username: currentUser.username,
                member_username: memberUsername,
                action: action
            })
        });

        const data = await response.json();

        if (response.ok) {
            displayQRCode(data.token, data.action, data.member_name);
        } else {
            showMessage(data.error || 'Failed to generate QR code', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function displayQRCode(token, action, memberName) {
    // Clear previous QR code
    const container = document.getElementById('qr-code-container');
    container.innerHTML = '';

    // Generate QR code
    qrCode = new QRCode(container, {
        text: token,
        width: 256,
        height: 256,
        colorDark: '#000000',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H
    });

    // Show QR display
    document.getElementById('qr-display').style.display = 'block';
    document.getElementById('action-buttons').style.display = 'none';

    // Start countdown timer (5 minutes)
    let timeLeft = 300;
    updateTimer(timeLeft);

    qrTimer = setInterval(() => {
        timeLeft--;
        updateTimer(timeLeft);

        if (timeLeft <= 0) {
            cancelQR();
            showMessage('QR code expired. Please generate a new one.', 'warning');
        }
    }, 1000);
}

function updateTimer(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    document.getElementById('qr-timer').textContent =
        `${minutes}:${secs.toString().padStart(2, '0')}`;
}

function cancelQR() {
    if (qrTimer) {
        clearInterval(qrTimer);
        qrTimer = null;
    }

    document.getElementById('qr-display').style.display = 'none';
    document.getElementById('action-buttons').style.display = 'flex';
    document.getElementById('qr-code-container').innerHTML = '';
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
    const container = document.getElementById('pending-approvals-list');

    if (entries.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">No pending approvals.</p>';
        return;
    }

    container.innerHTML = entries.map(entry => {
        const inTime = new Date(entry.in_time).toLocaleString();
        const outTime = entry.out_time ? new Date(entry.out_time).toLocaleString() : 'Not checked out';

        return `
            <div class="card" style="margin-bottom: 15px; background: #f8f9fa;">
                <h4>${entry.display_name} (${entry.username})</h4>
                <p><strong>Check-in:</strong> ${inTime}</p>
                <p><strong>Check-out:</strong> ${outTime}</p>
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <button class="btn btn-success btn-sm" onclick="approveEntry(${entry.id}, 'Approved')">
                        Approve
                    </button>
                    <button class="btn btn-danger btn-sm" onclick="approveEntry(${entry.id}, 'Rejected')">
                        Reject
                    </button>
                </div>
            </div>
        `;
    }).join('');
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
            showMessage(`Entry ${status.toLowerCase()} successfully`, 'success');
            loadPendingApprovals();
        } else {
            showMessage(data.error || 'Failed to process approval', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function handleLogout() {
    sessionStorage.removeItem('user');
    currentUser = null;
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('login-form').reset();
    showMessage('Logged out successfully', 'success');
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('message');
    messageDiv.textContent = message;
    messageDiv.className = `message ${type}`;
    messageDiv.style.display = 'block';

    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}
