// Main JavaScript file for common functionality

const API_BASE_URL = 'http://localhost:5001/api';

function showMessage(message, type = 'success') {
    const messageDiv = document.getElementById('message');
    if (!messageDiv) return;

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

function formatDate(dateString) {
    if (!dateString) return '无';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Session management
function saveSession(user) {
    sessionStorage.setItem('user', JSON.stringify(user));
}

function getSession() {
    const user = sessionStorage.getItem('user');
    return user ? JSON.parse(user) : null;
}

function clearSession() {
    sessionStorage.removeItem('user');
}
