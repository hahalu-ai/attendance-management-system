const API_BASE_URL = 'http://localhost:5001/api';
let currentUser = null;
let allUsers = [];
let filteredUsers = [];

document.addEventListener('DOMContentLoaded', () => {
    checkSession();
    setupEventListeners();
});

function checkSession() {
    const user = sessionStorage.getItem('user');
    if (user) {
        currentUser = JSON.parse(user);
        if (currentUser.user_level === 'Manager') {
            displayUserInfo();
            loadAllUsers();
        } else {
            showMessage('Access denied. Managers only.', 'error');
            setTimeout(() => window.location.href = '../index.html', 2000);
        }
    } else {
        window.location.href = 'portal.html';
    }
}

function setupEventListeners() {
    document.getElementById('refresh-btn').addEventListener('click', loadAllUsers);
    document.getElementById('role-filter').addEventListener('change', applyFilters);
    document.getElementById('search-input').addEventListener('input', applyFilters);
}

function displayUserInfo() {
    document.getElementById('user-info').innerHTML = `
        Logged in as: <strong>${currentUser.display_name}</strong> (${currentUser.username})
    `;
}

async function loadAllUsers() {
    try {
        showMessage('Loading users...', 'success');

        const response = await fetch(`${API_BASE_URL}/users/?manager_username=${currentUser.username}`);
        const data = await response.json();

        if (response.ok) {
            allUsers = data.users || [];
            filteredUsers = [...allUsers];
            applyFilters();
            showMessage(`Loaded ${allUsers.length} users successfully`, 'success');
        } else {
            showMessage(data.error || 'Failed to load users', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function applyFilters() {
    const roleFilter = document.getElementById('role-filter').value;
    const searchText = document.getElementById('search-input').value.toLowerCase();

    filteredUsers = allUsers.filter(user => {
        // Role filter
        const roleMatch = roleFilter === 'all' || user.user_level === roleFilter;

        // Search filter
        const searchMatch = searchText === '' ||
            user.username.toLowerCase().includes(searchText) ||
            user.display_name.toLowerCase().includes(searchText) ||
            user.email.toLowerCase().includes(searchText);

        return roleMatch && searchMatch;
    });

    displayUsers();
}

function displayUsers() {
    const tbody = document.getElementById('users-table-body');
    const userCount = document.getElementById('user-count');

    // Update count
    const managerCount = filteredUsers.filter(u => u.user_level === 'Manager').length;
    const contractorCount = filteredUsers.filter(u => u.user_level === 'Contractor').length;

    userCount.innerHTML = `
        <strong>Total Users:</strong> ${filteredUsers.length}
        (${managerCount} Manager${managerCount !== 1 ? 's' : ''},
        ${contractorCount} Contractor${contractorCount !== 1 ? 's' : ''})
    `;

    // Display users
    if (filteredUsers.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" style="text-align: center;">No users found</td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = filteredUsers.map(user => `
        <tr>
            <td><strong>${user.username}</strong></td>
            <td>${user.display_name}</td>
            <td>${user.email}</td>
            <td>
                <span class="badge badge-${user.user_level.toLowerCase()}">
                    ${user.user_level}
                </span>
            </td>
            <td>${formatDate(user.created_at)}</td>
            <td>
                <div class="action-links">
                    <a href="#" class="action-link" onclick="viewUserDetails('${user.username}'); return false;">View</a>
                    ${user.username !== currentUser.username ?
                        `<a href="#" class="action-link danger" onclick="confirmDeleteUser('${user.username}'); return false;">Delete</a>` :
                        '<span style="color: #999; font-size: 13px;">(You)</span>'}
                </div>
            </td>
        </tr>
    `).join('');
}

async function viewUserDetails(username) {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${username}`);
        const data = await response.json();

        if (response.ok) {
            const user = data;
            alert(`User Details:\n\n` +
                `Username: ${user.username}\n` +
                `Display Name: ${user.display_name}\n` +
                `Email: ${user.email}\n` +
                `Role: ${user.user_level}\n` +
                `Created: ${formatDateTime(user.created_at)}\n` +
                `Last Updated: ${formatDateTime(user.updated_at)}`
            );
        } else {
            showMessage('Failed to load user details', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

async function confirmDeleteUser(username) {
    const user = allUsers.find(u => u.username === username);
    if (!user) return;

    const confirmMsg = `Are you sure you want to delete user "${user.display_name}" (${username})?\n\n` +
        `This will permanently delete:\n` +
        `- The user account\n` +
        `- All their time entries\n` +
        `- All manager/contractor assignments\n` +
        `- All QR requests\n\n` +
        `This action cannot be undone!`;

    if (confirm(confirmMsg)) {
        await deleteUser(username);
    }
}

async function deleteUser(username) {
    try {
        const response = await fetch(`${API_BASE_URL}/users/${username}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                manager_username: currentUser.username
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(`User ${username} deleted successfully`, 'success');
            loadAllUsers(); // Refresh the list
        } else {
            showMessage(data.error || 'Failed to delete user', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function formatDate(dateTimeString) {
    if (!dateTimeString) return 'N/A';
    const date = new Date(dateTimeString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
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
