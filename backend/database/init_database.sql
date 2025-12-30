-- Attendance Management System Database Schema
-- Database: attendance_system

USE attendance_system;

-- =============================================
-- Table 1: Users
-- Stores user credentials and profile information
-- =============================================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    display_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL, -- Should store hashed passwords
    user_level ENUM('Manager', 'Contractor') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- =============================================
-- Table 2: Manager-Employee Relationships
-- Shows which managers oversee which contractors
-- =============================================
CREATE TABLE manager_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    manager_username VARCHAR(50) NOT NULL,
    contractor_username VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_assignment (manager_username, contractor_username),
    CONSTRAINT fk_manager_username
        FOREIGN KEY (manager_username) REFERENCES users(username)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_contractor_username
        FOREIGN KEY (contractor_username) REFERENCES users(username)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_manager (manager_username),
    INDEX idx_contractor (contractor_username)
);

-- =============================================
-- Table 3: Time Entries (Attendance Records)
-- Tracks check-in/check-out times and approval status
-- =============================================
CREATE TABLE time_entries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    in_time DATETIME NOT NULL,
    out_time DATETIME NULL,
    status ENUM('Pending', 'Approved', 'Rejected') NOT NULL DEFAULT 'Pending',
    approved_by VARCHAR(50) NULL,
    approved_at DATETIME NULL,
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_time_entry_user
        FOREIGN KEY (username) REFERENCES users(username)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_approver
        FOREIGN KEY (approved_by) REFERENCES users(username)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    INDEX idx_username_date (username, in_time),
    INDEX idx_status (status),
    INDEX idx_approved_by (approved_by)
);

-- =============================================
-- Table 4: QR Code Requests
-- Stores QR code tokens for check-in/check-out workflow
-- =============================================
CREATE TABLE qr_requests (
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

-- =============================================
-- Sample Data (Optional - for testing)
-- =============================================

-- Insert sample users (default password: "password!" for all users)
-- Password hash: SHA256 of "password!"
INSERT INTO users (username, display_name, email, password, user_level) VALUES
('ylin', 'Yuchen Lin', 'yuchen.lin@example.com', 'f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7', 'Manager'),
('xlu', 'Xuanyu Lu', 'xuanyu.lu@example.com', 'f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7', 'Contractor'),
('jsmith', 'John Smith', 'john.smith@example.com', 'f82a7d02e8f0a728b7c3e958c278745cb224d3d7b2e3b84c0ecafc5511fdbdb7', 'Contractor');

-- Assign contractors to manager
INSERT INTO manager_assignments (manager_username, contractor_username) VALUES
('ylin', 'xlu'),
('ylin', 'jsmith');

-- Insert sample time entries
INSERT INTO time_entries (username, in_time, out_time, status, approved_by, approved_at) VALUES
('xlu', '2025-12-15 09:00:00', '2025-12-15 17:30:00', 'Approved', 'ylin', '2025-12-15 18:00:00'),
('jsmith', '2025-12-15 08:45:00', '2025-12-15 17:00:00', 'Pending', NULL, NULL);

-- =============================================
-- Useful Queries
-- =============================================

-- View all users
-- SELECT * FROM users;

-- View manager-contractor relationships
-- SELECT
--     ma.manager_username,
--     u1.display_name AS manager_name,
--     ma.contractor_username,
--     u2.display_name AS contractor_name
-- FROM manager_assignments ma
-- JOIN users u1 ON ma.manager_username = u1.username
-- JOIN users u2 ON ma.contractor_username = u2.username;

-- View time entries with approval details
-- SELECT
--     te.id,
--     u.display_name,
--     te.in_time,
--     te.out_time,
--     te.status,
--     approver.display_name AS approved_by_name,
--     te.approved_at
-- FROM time_entries te
-- JOIN users u ON te.username = u.username
-- LEFT JOIN users approver ON te.approved_by = approver.username
-- ORDER BY te.in_time DESC;
