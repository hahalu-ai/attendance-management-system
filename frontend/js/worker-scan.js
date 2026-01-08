// Worker QR Scanner JavaScript

const API_BASE_URL = 'http://localhost:5001/api';
let html5QrCode = null;
let isScanning = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('start-scan-btn').addEventListener('click', startScanning);
    document.getElementById('stop-scan-btn').addEventListener('click', stopScanning);
    document.getElementById('submit-token-btn').addEventListener('click', submitManualToken);
    document.getElementById('scan-another-btn').addEventListener('click', resetScanner);
}

function switchTab(tab) {
    // Update tab buttons
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');

    // Update tab content
    document.getElementById('camera-tab').classList.remove('active');
    document.getElementById('manual-tab').classList.remove('active');

    if (tab === 'camera') {
        document.getElementById('camera-tab').classList.add('active');
    } else {
        document.getElementById('manual-tab').classList.add('active');
        stopScanning(); // Stop camera if switching away
    }
}

async function startScanning() {
    try {
        // Show QR reader
        document.getElementById('qr-reader').style.display = 'block';
        document.getElementById('start-scan-btn').style.display = 'none';
        document.getElementById('stop-scan-btn').style.display = 'inline-block';

        // Initialize scanner
        html5QrCode = new Html5Qrcode("qr-reader");

        // Start scanning
        await html5QrCode.start(
            { facingMode: "environment" }, // Use back camera
            {
                fps: 10,
                qrbox: { width: 250, height: 250 }
            },
            onScanSuccess,
            onScanError
        );

        isScanning = true;
        showMessage('相机已启动。将其对准二维码进行扫描。', 'success');
    } catch (error) {
        showMessage('启动相机时出错：' + error.message, 'error');
        console.error('Camera error:', error);

        // Fallback to manual entry
        document.getElementById('qr-reader').style.display = 'none';
        document.getElementById('start-scan-btn').style.display = 'inline-block';
        document.getElementById('stop-scan-btn').style.display = 'none';

        showMessage('相机不可用。请使用手动输入。', 'error');
        switchTab('manual');
    }
}

async function stopScanning() {
    if (html5QrCode && isScanning) {
        try {
            await html5QrCode.stop();
            html5QrCode.clear();
            isScanning = false;
        } catch (error) {
            console.error('Error stopping scanner:', error);
        }
    }

    document.getElementById('qr-reader').style.display = 'none';
    document.getElementById('start-scan-btn').style.display = 'inline-block';
    document.getElementById('stop-scan-btn').style.display = 'none';
}

function onScanSuccess(decodedText, decodedResult) {
    console.log('QR Code scanned:', decodedText);

    // Stop scanning
    stopScanning();

    // Verify the QR code
    verifyQRCode(decodedText);
}

function onScanError(errorMessage) {
    // Ignore scan errors (they happen frequently when camera is finding QR code)
}

async function submitManualToken() {
    const token = document.getElementById('manual-token').value.trim();

    if (!token) {
        showMessage('请输入令牌', 'error');
        return;
    }

    verifyQRCode(token);
}

async function verifyQRCode(token) {
    showMessage('正在验证二维码...', 'success');

    try {
        const response = await fetch(`${API_BASE_URL}/attendance/qr/verify`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: token })
        });

        const data = await response.json();

        if (response.ok) {
            showResult(true, data);
        } else {
            showResult(false, data);
        }
    } catch (error) {
        showResult(false, { error: '连接错误：' + error.message });
    }
}

function showResult(success, data) {
    // Hide scanner sections
    document.getElementById('camera-tab').style.display = 'none';
    document.getElementById('manual-tab').style.display = 'none';

    // Show result
    const resultDisplay = document.getElementById('result-display');
    const resultIcon = document.getElementById('result-icon');
    const resultTitle = document.getElementById('result-title');
    const resultMessage = document.getElementById('result-message');
    const resultDetails = document.getElementById('result-details');

    if (success) {
        resultIcon.innerHTML = '<div class="success-icon">✓</div>';
        resultTitle.textContent = '成功！';
        resultMessage.textContent = data.message || '操作成功完成';
        resultDetails.innerHTML = `
            <p><strong>员工：</strong> ${data.worker_username}</p>
            <p><strong>操作：</strong> ${data.action}</p>
            <p><strong>时间：</strong> ${formatDateTime(data.timestamp)}</p>
        `;
        showMessage('操作成功完成！', 'success');
    } else {
        resultIcon.innerHTML = '<div class="error-icon">✗</div>';
        resultTitle.textContent = '错误';
        resultMessage.textContent = data.error || '验证二维码失败';
        resultDetails.innerHTML = `
            <p>请重试或联系您的管理员。</p>
        `;
        showMessage(data.error || '验证失败', 'error');
    }

    resultDisplay.style.display = 'block';
}

function resetScanner() {
    // Hide result
    document.getElementById('result-display').style.display = 'none';

    // Show scanner sections
    document.getElementById('camera-tab').style.display = 'block';
    document.getElementById('manual-tab').style.display = 'block';

    // Reset to camera tab
    switchTab('camera');
    document.querySelector('.tab').click();

    // Clear manual input
    document.getElementById('manual-token').value = '';
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
        minute: '2-digit',
        second: '2-digit'
    });
}

// Make switchTab globally accessible
window.switchTab = switchTab;
