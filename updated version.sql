USE practice_db;
SHOW TABLES;

CREATE TABLE user (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role ENUM('employee', 'manager') NOT NULL DEFAULT 'employee'
);


CREATE TABLE manager_employee (
    manager_id  INT NOT NULL,
    employee_id INT NOT NULL,
    PRIMARY KEY (manager_id, employee_id),
    CONSTRAINT fk_me_manager
        FOREIGN KEY (manager_id) REFERENCES user(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_me_employee
        FOREIGN KEY (employee_id) REFERENCES user(id)
        ON DELETE CASCADE
);


CREATE TABLE attendance_record (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    user_id        INT NOT NULL,
    check_in_time  DATETIME NOT NULL,
    check_out_time DATETIME NULL,
    status         ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
    approved_by    INT NULL,
    approved_at    DATETIME NULL,
    CONSTRAINT fk_ar_user
        FOREIGN KEY (user_id) REFERENCES user(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ar_approver
        FOREIGN KEY (approved_by) REFERENCES user(id)
        ON DELETE SET NULL
);
SHOW TABLES;
INSERT INTO user (name, role) VALUES
('Xuanyu Lu', 'employee'),
('Yuchen Lin', 'manager');


INSERT INTO manager_employee (manager_id, employee_id)
VALUES (2, 1);

SELECT * FROM user;
SELECT * FROM manager_employee;

