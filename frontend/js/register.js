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
            showMessage('访问被拒绝。只有管理员可以创建账户。', 'error');
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
                showMessage('访问被拒绝。只有管理员可以创建账户。', 'error');
                return;
            }

            sessionStorage.setItem('user', JSON.stringify(currentManager));
            showRegistrationForm();
            showMessage('管理员身份验证成功', 'success');
        } else {
            showMessage(data.error || '登录失败', 'error');
        }
    } catch (error) {
        showMessage('连接错误：' + error.message, 'error');
    }
}

function showRegistrationForm() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('registration-section').style.display = 'block';
    document.getElementById('user-info').innerHTML = `
        管理员：<strong>${currentManager.display_name}</strong> (${currentManager.username})
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
        showMessage('密码不匹配', 'error');
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
            showMessage(`成功为 ${username} 创建账户！`, 'success');
            document.getElementById('registration-form').reset();

            // Ask if manager wants to assign contractor
            if (userLevel === 'Contractor') {
                setTimeout(() => {
                    if (confirm(`您要将 ${username} 分配给自己作为其管理员吗？`)) {
                        assignContractorToSelf(username);
                    }
                }, 1000);
            }
        } else {
            showMessage(data.error || '注册失败', 'error');
        }
    } catch (error) {
        showMessage('连接错误：' + error.message, 'error');
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
            showMessage(`${contractorUsername} 已成功分配给您`, 'success');
        } else {
            showMessage(`注意：${data.error || '分配失败'}`, 'error');
        }
    } catch (error) {
        console.error('Assignment error:', error);
    }
}

function resetForm() {
    document.getElementById('registration-form').reset();
    showMessage('表单已清除', 'success');
}

function handleLogout() {
    sessionStorage.removeItem('user');
    currentManager = null;
    document.getElementById('registration-section').style.display = 'none';
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('manager-login-form').reset();
    showMessage('登出成功', 'success');
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
