// Manager Portal JavaScript with QR Code Functionality

// Auto-detect environment: use Railway in production, localhost for development
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5001/api'
    : 'https://attendance-management-system-production-1f1a.up.railway.app/api';

let currentUser = null;
let workers = [];
let qrTimer = null;
let qrCode = null;

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
            showMessage('访问被拒绝。仅限管理员。', 'error');
        }
    }
}

function setupEventListeners() {
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    document.getElementById('worker-select').addEventListener('change', handleWorkerSelection);
    document.getElementById('generate-checkin-btn').addEventListener('click', () => generateQR('check-in'));
    document.getElementById('generate-checkout-btn').addEventListener('click', () => generateQR('check-out'));
    document.getElementById('cancel-qr-btn').addEventListener('click', cancelQR);
    document.getElementById('refresh-workers-btn').addEventListener('click', loadWorkers);
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
                showMessage('访问被拒绝。仅限管理员。', 'error');
                return;
            }

            sessionStorage.setItem('user', JSON.stringify(currentUser));
            showDashboard();
            showMessage('登录成功！', 'success');
        } else {
            showMessage(data.error || '登录失败', 'error');
        }
    } catch (error) {
        showMessage('连接错误：' + error.message, 'error');
    }
}

function showDashboard() {
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('dashboard-section').style.display = 'block';
    document.getElementById('user-info').innerHTML = `
        已登录为：<strong>${currentUser.display_name}</strong> (${currentUser.username})
    `;
    loadWorkers();
    loadPendingApprovals();
}

async function loadWorkers() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/users/${currentUser.username}/contractors`
        );
        const data = await response.json();

        if (response.ok) {
            workers = data.contractors || [];
            populateWorkerSelect();
        } else {
            showMessage(data.error || '加载员工列表失败', 'error');
        }
    } catch (error) {
        showMessage('连接错误：' + error.message, 'error');
    }
}

function populateWorkerSelect() {
    const select = document.getElementById('worker-select');
    select.innerHTML = '<option value="">-- 选择一名员工 --</option>';

    workers.forEach(worker => {
        const option = document.createElement('option');
        option.value = worker.username;
        option.textContent = `${worker.display_name} (${worker.username})`;
        select.appendChild(option);
    });
}

async function handleWorkerSelection() {
    const workerUsername = document.getElementById('worker-select').value;

    if (!workerUsername) {
        document.getElementById('worker-status').style.display = 'none';
        document.getElementById('action-buttons').style.display = 'none';
        return;
    }

    const worker = workers.find(w => w.username === workerUsername);

    try {
        // Check if worker has open time entry
        const response = await fetch(
            `${API_BASE_URL}/attendance/my-entries?username=${workerUsername}`
        );
        const data = await response.json();

        if (response.ok) {
            const entries = data.entries || [];
            const openEntry = entries.find(e => e.out_time === null);

            // Show worker status
            document.getElementById('selected-worker-name').textContent = worker.display_name;

            if (openEntry) {
                document.getElementById('worker-clock-status').innerHTML =
                    '<span class="status-clocked-in">已签到</span>';
                document.getElementById('generate-checkin-btn').disabled = true;
                document.getElementById('generate-checkout-btn').disabled = false;
            } else {
                document.getElementById('worker-clock-status').innerHTML =
                    '<span class="status-clocked-out">已签退</span>';
                document.getElementById('generate-checkin-btn').disabled = false;
                document.getElementById('generate-checkout-btn').disabled = true;
            }

            document.getElementById('worker-status').style.display = 'block';
            document.getElementById('action-buttons').style.display = 'flex';
        }
    } catch (error) {
        showMessage('检查员工状态时出错：' + error.message, 'error');
    }
}

async function generateQR(action) {
    const workerUsername = document.getElementById('worker-select').value;

    if (!workerUsername) {
        showMessage('请先选择一名员工', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/attendance/qr/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                manager_username: currentUser.username,
                worker_username: workerUsername,
                action: action
            })
        });

        const data = await response.json();

        if (response.ok) {
            displayQRCode(data);
            showMessage(`已为 ${action} 生成二维码`, 'success');
        } else {
            showMessage(data.error || '生成二维码失败', 'error');
        }
    } catch (error) {
        showMessage('连接错误：' + error.message, 'error');
    }
}

function displayQRCode(data) {
    // Clear existing QR code
    document.getElementById('qrcode').innerHTML = '';

    // Create new QR code
    qrCode = new QRCode(document.getElementById('qrcode'), {
        text: data.token,
        width: 256,
        height: 256,
        colorDark: '#000000',
        colorLight: '#ffffff',
        correctLevel: QRCode.CorrectLevel.H
    });

    // Update display
    document.getElementById('qr-worker-name').textContent = data.worker_name || data.worker_username;
    document.getElementById('qr-action').textContent = data.action.toUpperCase();
    document.getElementById('qr-action-type').textContent = data.action;

    // Show QR section, hide action buttons
    document.getElementById('qr-display').style.display = 'block';
    document.getElementById('action-buttons').style.display = 'none';

    // Start countdown timer
    startQRTimer(data.expires_in_seconds || 300);

    // Poll for QR code status
    pollQRStatus(data.token);
}

function startQRTimer(seconds) {
    let remaining = seconds;

    // Clear existing timer
    if (qrTimer) {
        clearInterval(qrTimer);
    }

    updateTimerDisplay(remaining);

    qrTimer = setInterval(() => {
        remaining--;
        updateTimerDisplay(remaining);

        if (remaining <= 0) {
            clearInterval(qrTimer);
            showMessage('二维码已过期。请生成新码。', 'error');
            cancelQR();
        }
    }, 1000);
}

function updateTimerDisplay(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    document.getElementById('qr-timer').textContent =
        `${minutes}:${secs.toString().padStart(2, '0')}`;
}

async function pollQRStatus(token) {
    const maxAttempts = 60; // Poll for 5 minutes (60 * 5 seconds)
    let attempts = 0;

    const pollInterval = setInterval(async () => {
        attempts++;

        try {
            const response = await fetch(`${API_BASE_URL}/attendance/qr/status/${token}`);
            const data = await response.json();

            if (response.ok) {
                if (data.status === 'used') {
                    clearInterval(pollInterval);
                    showMessage(`${data.action} 成功完成！`, 'success');
                    cancelQR();
                    handleWorkerSelection(); // Refresh worker status
                } else if (data.status === 'failed' || data.status === 'expired') {
                    clearInterval(pollInterval);
                    showMessage(`二维码 ${data.status}`, 'error');
                    cancelQR();
                }
            }
        } catch (error) {
            console.error('Error polling QR status:', error);
        }

        if (attempts >= maxAttempts) {
            clearInterval(pollInterval);
        }
    }, 5000); // Poll every 5 seconds
}

function cancelQR() {
    if (qrTimer) {
        clearInterval(qrTimer);
        qrTimer = null;
    }

    document.getElementById('qr-display').style.display = 'none';
    document.getElementById('action-buttons').style.display = 'flex';
    document.getElementById('qrcode').innerHTML = '';
}

async function loadPendingApprovals() {
    try {
        const response = await fetch(
            `${API_BASE_URL}/attendance/pending-approvals?manager_username=${currentUser.username}`
        );
        const data = await response.json();

        if (response.ok) {
            displayPendingApprovals(data.pending_entries || []);
        } else {
            showMessage(data.error || '加载待审批失败', 'error');
        }
    } catch (error) {
        showMessage('连接错误：' + error.message, 'error');
    }
}

function displayPendingApprovals(entries) {
    const container = document.getElementById('pending-content');

    if (!entries || entries.length === 0) {
        container.innerHTML = '<p>无待审批</p>';
        return;
    }

    let html = `
        <table>
            <thead>
                <tr>
                    <th>员工</th>
                    <th>签到</th>
                    <th>签退</th>
                    <th>操作</th>
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
                    <button onclick="approveEntry(${entry.id}, 'Approved')" class="btn btn-success btn-sm">批准</button>
                    <button onclick="approveEntry(${entry.id}, 'Rejected')" class="btn btn-danger btn-sm">拒绝</button>
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
                manager_username: currentUser.username,
                entry_id: entryId,
                status: status
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(data.message, 'success');
            loadPendingApprovals();
        } else {
            showMessage(data.error || '审批失败', 'error');
        }
    } catch (error) {
        showMessage('连接错误：' + error.message, 'error');
    }
}

function handleLogout() {
    sessionStorage.removeItem('user');
    currentUser = null;
    workers = [];
    document.getElementById('dashboard-section').style.display = 'none';
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('login-form').reset();
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

function formatDateTime(dateTimeString) {
    if (!dateTimeString) return '无';
    const date = new Date(dateTimeString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Make approveEntry globally accessible
window.approveEntry = approveEntry;
