-- Migration Script: Two-Tier to Three-Tier User System
-- This script migrates from (Manager, Contractor) to (Manager, Lead, Member)
--
-- Changes:
-- 1. Update users table to support 'Member' user level
-- 2. Rename manager_assignments to lead_assignments (Lead -> Member relationships)
-- 3. Create manager_lead_assignments table (Manager -> Lead relationships)
-- 4. Update existing data: Convert Contractors to Leads
-- 5. Members will be created by Leads (no initial Members)

USE attendance_system;

-- =============================================
-- Step 1: Backup existing tables (optional but recommended)
-- =============================================
-- Uncomment these lines if you want to backup:
-- CREATE TABLE users_backup AS SELECT * FROM users;
-- CREATE TABLE manager_assignments_backup AS SELECT * FROM manager_assignments;
-- CREATE TABLE time_entries_backup AS SELECT * FROM time_entries;
-- CREATE TABLE qr_requests_backup AS SELECT * FROM qr_requests;

-- =============================================
-- Step 2: Modify users table to support three user types
-- =============================================
ALTER TABLE users
MODIFY COLUMN user_level ENUM('Manager', 'Lead', 'Member') NOT NULL;

-- =============================================
-- Step 3: Update existing Contractors to Leads
-- All current Contractors become Leads in the new system
-- =============================================
UPDATE users
SET user_level = 'Lead'
WHERE user_level = 'Contractor';

-- =============================================
-- Step 4: Rename manager_assignments to lead_assignments
-- This table now tracks Lead -> Member relationships
-- =============================================
RENAME TABLE manager_assignments TO lead_assignments_old;

CREATE TABLE lead_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    lead_username VARCHAR(50) NOT NULL,
    member_username VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_assignment (lead_username, member_username),
    CONSTRAINT fk_lead_username
        FOREIGN KEY (lead_username) REFERENCES users(username)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_member_username
        FOREIGN KEY (member_username) REFERENCES users(username)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_lead (lead_username),
    INDEX idx_member (member_username)
);

-- Note: lead_assignments_old is kept for now but empty
-- Members will be created by Leads after migration

-- =============================================
-- Step 5: Create manager_lead_assignments table
-- This tracks Manager -> Lead relationships
-- Managers can view/manage these Leads and their Members
-- =============================================
CREATE TABLE manager_lead_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    manager_username VARCHAR(50) NOT NULL,
    lead_username VARCHAR(50) NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_manager_lead (manager_username, lead_username),
    CONSTRAINT fk_manager_lead_manager
        FOREIGN KEY (manager_username) REFERENCES users(username)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_manager_lead_lead
        FOREIGN KEY (lead_username) REFERENCES users(username)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX idx_manager_lead (manager_username),
    INDEX idx_lead_manager (lead_username)
);

-- Migrate old manager-contractor assignments to manager-lead assignments
INSERT INTO manager_lead_assignments (manager_username, lead_username, assigned_at)
SELECT manager_username, contractor_username, assigned_at
FROM lead_assignments_old;

-- =============================================
-- Step 6: Update time_entries to work with new system
-- No schema changes needed, but add comments for clarity
-- =============================================
-- Note: time_entries.username can now reference Manager, Lead, or Member
-- Members will have time_entries created via QR code check-in/out
-- approved_by should reference the Lead who manages that Member

-- =============================================
-- Step 7: Update qr_requests table column names for clarity
-- =============================================
-- Rename worker_username to member_username for clarity
-- Rename manager_username to lead_username (as Leads generate QR codes)

-- Drop old foreign keys first
ALTER TABLE qr_requests
DROP FOREIGN KEY fk_qr_manager,
DROP FOREIGN KEY fk_qr_worker;

-- Rename columns
ALTER TABLE qr_requests
CHANGE COLUMN manager_username lead_username VARCHAR(50) NOT NULL,
CHANGE COLUMN worker_username member_username VARCHAR(50) NOT NULL;

-- Add new foreign keys with updated names
ALTER TABLE qr_requests
ADD CONSTRAINT fk_qr_lead
    FOREIGN KEY (lead_username) REFERENCES users(username)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
ADD CONSTRAINT fk_qr_member
    FOREIGN KEY (member_username) REFERENCES users(username)
    ON DELETE CASCADE
    ON UPDATE CASCADE;

-- Update index names
DROP INDEX idx_worker ON qr_requests;
ALTER TABLE qr_requests ADD INDEX idx_member (member_username);

-- =============================================
-- Step 8: Add helpful comments to track relationships
-- =============================================
-- Relationship hierarchy:
--   Manager (super-user)
--     └─> Leads (via manager_lead_assignments)
--           └─> Members (via lead_assignments)
--
-- Access Control:
--   - Manager: Can view/manage ALL Leads and Members
--   - Lead: Can only view/manage their own Members
--   - Member: No login, QR code only

-- =============================================
-- Step 9: Verification queries
-- =============================================
-- Run these to verify the migration:

-- Count users by type
-- SELECT user_level, COUNT(*) as count FROM users GROUP BY user_level;

-- View Manager-Lead relationships
-- SELECT mla.manager_username, u1.display_name as manager_name,
--        mla.lead_username, u2.display_name as lead_name
-- FROM manager_lead_assignments mla
-- JOIN users u1 ON mla.manager_username = u1.username
-- JOIN users u2 ON mla.lead_username = u2.username;

-- View Lead-Member relationships (will be empty initially)
-- SELECT la.lead_username, u1.display_name as lead_name,
--        la.member_username, u2.display_name as member_name
-- FROM lead_assignments la
-- JOIN users u1 ON la.lead_username = u1.username
-- JOIN users u2 ON la.member_username = u2.username;

-- =============================================
-- Migration Complete
-- =============================================
-- Next steps:
-- 1. Update backend API to handle new user types
-- 2. Update frontend to support three-tier system
-- 3. Test Manager -> Lead creation
-- 4. Test Lead -> Member creation
-- 5. Test QR code workflow with Members

-- To rollback (if needed):
-- DROP TABLE IF EXISTS manager_lead_assignments;
-- DROP TABLE IF EXISTS lead_assignments;
-- RENAME TABLE lead_assignments_old TO manager_assignments;
-- UPDATE users SET user_level = 'Contractor' WHERE user_level = 'Lead';
-- ALTER TABLE users MODIFY COLUMN user_level ENUM('Manager', 'Contractor') NOT NULL;
