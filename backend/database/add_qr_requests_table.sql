-- Migration: Add QR Requests Table
-- Run this if you already have the database set up and need to add QR functionality
-- Date: 2025-12-15

USE practice_db;

-- Create QR Code Requests table
CREATE TABLE IF NOT EXISTS qr_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token VARCHAR(255) NOT NULL UNIQUE,
    manager_username VARCHAR(50) NOT NULL,
    worker_username VARCHAR(50) NOT NULL,
    action_type ENUM('check-in', 'check-out') NOT NULL,
    status ENUM('pending', 'used', 'failed', 'expired') NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL,
    expires_at DATETIME NOT NULL,
    used_at DATETIME NULL,
    CONSTRAINT fk_qr_manager
        FOREIGN KEY (manager_username) REFERENCES users(username)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_qr_worker
        FOREIGN KEY (worker_username) REFERENCES users(username)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_token (token),
    INDEX idx_status_expires (status, expires_at),
    INDEX idx_worker (worker_username)
);

-- Verify the table was created
SHOW TABLES LIKE 'qr_requests';

-- Check the structure
DESCRIBE qr_requests;

SELECT 'QR Requests table created successfully!' AS message;
