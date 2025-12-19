const API_BASE_URL = 'http://localhost:5001/api';
let currentManager = null;

document.addEventListener('DOMContentLoaded', () => {
    checkSession();
    setupEventListeners();
});

function checkSession() {
    const user = sessionStorage.getItem('user');
    if (user) {
        currentManager = JSON.parse(user);
        if (currentManager.user_level === 'Manager') {
            showRegistrationForm();
        } else {
            showMessage('Access denied. Only managers can create accounts.', 'error');
        }
    }
}

function setupEventListeners() {
    document.getElementById('manager-login-form').addEventListener('submit', handleManagerLogin);
    document.getElementById('registration-form').addEventListener('submit', handleRegistration);
    document.getElementById('cancel-btn').addEventListener('click', resetForm);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
}

async function handleManagerLogin(e) {
    e.preventDefault();

    const username = document.getElementById('manager-username').value;
    const password = document.getElementById('manager-password').value;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            currentManager = data.user;

            if (currentManager.user_level !== 'Manager') {
                showMessage('Access denied. Only managers can create accounts.', 'error');
                return;
            }

            sessionStorage.setItem('user', JSON.stringify(currentManager));
            showRegistrationForm();
            showMessage('Manager authenticated successfully', 'success');
        } else {
            showMessage(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

function showRegistrationForm() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('registration-section').style.display = 'block';
    document.getElementById('user-info').innerHTML = `
        Manager: <strong>${currentManager.display_name}</strong> (${currentManager.username})
    `;
}

async function handleRegistration(e) {
    e.preventDefault();

    const username = document.getElementById('username').value;
    const displayName = document.getElementById('display-name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const userLevel = document.getElementById('user-level').value;

    // Validate passwords match
    if (password !== confirmPassword) {
        showMessage('Passwords do not match', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/users/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                manager_username: currentManager.username,
                username: username,
                display_name: displayName,
                email: email,
                password: password,
                user_level: userLevel
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(`Account created successfully for ${username}!`, 'success');
            document.getElementById('registration-form').reset();

            // Ask if manager wants to assign contractor
            if (userLevel === 'Contractor') {
                setTimeout(() => {
                    if (confirm(`Would you like to assign ${username} to yourself as their manager?`)) {
                        assignContractorToSelf(username);
                    }
                }, 1000);
            }
        } else {
            showMessage(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showMessage('Connection error: ' + error.message, 'error');
    }
}

async function assignContractorToSelf(contractorUsername) {
    try {
        const response = await fetch(`${API_BASE_URL}/users/assign-manager`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                manager_username: currentManager.username,
                contractor_username: contractorUsername
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(`${contractorUsername} assigned to you successfully`, 'success');
        } else {
            showMessage(`Note: ${data.error || 'Assignment failed'}`, 'error');
        }
    } catch (error) {
        console.error('Assignment error:', error);
    }
}

function resetForm() {
    document.getElementById('registration-form').reset();
    showMessage('Form cleared', 'success');
}

function handleLogout() {
    sessionStorage.removeItem('user');
    currentManager = null;
    document.getElementById('registration-section').style.display = 'none';
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('manager-login-form').reset();
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
