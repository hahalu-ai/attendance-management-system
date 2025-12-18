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
        showMessage('Camera started. Point at QR code to scan.', 'success');
    } catch (error) {
        showMessage('Error starting camera: ' + error.message, 'error');
        console.error('Camera error:', error);

        // Fallback to manual entry
        document.getElementById('qr-reader').style.display = 'none';
        document.getElementById('start-scan-btn').style.display = 'inline-block';
        document.getElementById('stop-scan-btn').style.display = 'none';

        showMessage('Camera not available. Please use manual entry.', 'error');
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
        showMessage('Please enter a token', 'error');
        return;
    }

    verifyQRCode(token);
}

async function verifyQRCode(token) {
    showMessage('Verifying QR code...', 'success');

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
        showResult(false, { error: 'Connection error: ' + error.message });
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
        resultTitle.textContent = 'Success!';
        resultMessage.textContent = data.message || 'Action completed successfully';
        resultDetails.innerHTML = `
            <p><strong>Worker:</strong> ${data.worker_username}</p>
            <p><strong>Action:</strong> ${data.action}</p>
            <p><strong>Time:</strong> ${formatDateTime(data.timestamp)}</p>
        `;
        showMessage('Action completed successfully!', 'success');
    } else {
        resultIcon.innerHTML = '<div class="error-icon">✗</div>';
        resultTitle.textContent = 'Error';
        resultMessage.textContent = data.error || 'Failed to verify QR code';
        resultDetails.innerHTML = `
            <p>Please try again or contact your manager.</p>
        `;
        showMessage(data.error || 'Verification failed', 'error');
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
    if (!dateTimeString) return 'N/A';
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
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
