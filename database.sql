-- ====================================================================
-- CBSE Class 12 Computer Science (083) Project
-- Project Name: School Lost & Found Management System
-- Database Setup and DDL / DML Demonstration Script
-- ====================================================================

-- Step 1: Create and select the database
CREATE DATABASE IF NOT EXISTS school_lost_found;
USE school_lost_found;

-- Step 2: Drop existing tables if re-initializing (in reverse FK order)
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS items;
DROP TABLE IF EXISTS users;

-- ====================================================================
-- Table 1: USERS
-- Stores credentials and roles for students and administrators
-- Concepts: PRIMARY KEY, UNIQUE constraint, DEFAULT timestamp
-- ====================================================================
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    student_id VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ====================================================================
-- Table 2: ITEMS
-- Stores reported lost and found items
-- Concepts: FOREIGN KEY, ON DELETE CASCADE, CHECK/enum values
-- ====================================================================
CREATE TABLE items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    item_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    color VARCHAR(50),
    location VARCHAR(150) NOT NULL,
    date_reported DATE NOT NULL,
    item_type VARCHAR(10) NOT NULL, -- 'LOST' or 'FOUND'
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'OPEN', 'CLAIMED', 'RETURNED', 'REJECTED'
    reported_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reported_by) REFERENCES users(user_id) ON DELETE CASCADE
);

-- ====================================================================
-- Table 3: CLAIMS
-- Stores claims submitted by students for found items
-- Concepts: Multiple FOREIGN KEYS, ON DELETE CASCADE, Audit timestamps
-- ====================================================================
CREATE TABLE claims (
    claim_id INT PRIMARY KEY AUTO_INCREMENT,
    item_id INT NOT NULL,
    user_id INT NOT NULL,
    reason TEXT NOT NULL,
    lost_location VARCHAR(150) NOT NULL,
    additional_info TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING', -- 'PENDING', 'APPROVED', 'REJECTED'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Table 4: Login Credentials (For Viva / Demo / Quick Reference)
CREATE TABLE IF NOT EXISTS login_credentials (
    credential_id INT PRIMARY KEY AUTO_INCREMENT,
    login_type VARCHAR(50) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    description VARCHAR(255)
) ENGINE=InnoDB;

-- ====================================================================
-- Step 3: Insert Sample Data for Demonstration
-- Notice: Passwords below are hashed using Werkzeug (Default password: Admin@123 / Student@123)
-- ====================================================================

-- Insert Users (1 Admin, 3 Students)
INSERT INTO users (user_id, name, student_id, email, password, role) VALUES
(1, 'System Administrator', 'ADMIN-001', 'admin@school.local', 'scrypt:32768:8:1$7UfLhR4YvD3s$0b3ef25aa262b9a7be8e7f8d66e5114c2c5dc44e8bc1b54a01cbb47c94b7c12513476df08fc1c76943fcf30c451da74d32095fe27d142d131f479a4053ef11f7', 'admin'),
(2, 'Aravind Sharma', 'STU-1001', 'aravind@school.local', 'scrypt:32768:8:1$7UfLhR4YvD3s$0b3ef25aa262b9a7be8e7f8d66e5114c2c5dc44e8bc1b54a01cbb47c94b7c12513476df08fc1c76943fcf30c451da74d32095fe27d142d131f479a4053ef11f7', 'student'),
(3, 'Priya Patel', 'STU-1002', 'priya@school.local', 'scrypt:32768:8:1$7UfLhR4YvD3s$0b3ef25aa262b9a7be8e7f8d66e5114c2c5dc44e8bc1b54a01cbb47c94b7c12513476df08fc1c76943fcf30c451da74d32095fe27d142d131f479a4053ef11f7', 'student'),
(4, 'Rohit Verma', 'STU-1003', 'rohit@school.local', 'scrypt:32768:8:1$7UfLhR4YvD3s$0b3ef25aa262b9a7be8e7f8d66e5114c2c5dc44e8bc1b54a01cbb47c94b7c12513476df08fc1c76943fcf30c451da74d32095fe27d142d131f479a4053ef11f7', 'student'),
(5, 'Ananya Iyer', 'STU-1004', 'ananya@school.local', 'scrypt:32768:8:1$7UfLhR4YvD3s$0b3ef25aa262b9a7be8e7f8d66e5114c2c5dc44e8bc1b54a01cbb47c94b7c12513476df08fc1c76943fcf30c451da74d32095fe27d142d131f479a4053ef11f7', 'student');

-- Insert Items (Realistic variety of Lost and Found across school locations)
INSERT INTO items (item_id, item_name, category, description, color, location, date_reported, item_type, status, reported_by) VALUES
(1, 'Black Scientific Calculator', 'Electronics', 'Casio fx-991EX ClassWiz calculator with white solar panel sticker on back.', 'Black', 'Physics Lab Room 302', '2026-09-02', 'LOST', 'OPEN', 2),
(2, 'Black Scientific Calculator Casio', 'Electronics', 'Casio fx-991EX calculator found near desk 14 on Monday morning.', 'Black', 'Physics Lab', '2026-09-03', 'FOUND', 'OPEN', 3),
(3, 'Blue Stainless Steel Water Bottle', 'Water Bottle', 'Milton 750ml blue thermos with scratch on base and silver screw cap.', 'Blue', 'Sports Ground Pavilion', '2026-09-04', 'FOUND', 'OPEN', 4),
(4, 'School Student ID Card', 'ID Card', 'Class 12 ID card for student Priya Patel STU-1002 with lanyard.', 'White', 'Library Reading Hall', '2026-09-05', 'FOUND', 'OPEN', 5),
(5, 'Wireless Bluetooth Earphones', 'Electronics', 'Boat Airdopes in white charging case with cartoon astronaut sticker.', 'White', 'Computer Lab 2', '2026-09-06', 'LOST', 'PENDING', 4),
(6, 'Mathematics Classmate Notebook', 'Books', '200 pages spiral notebook with Class 12 Calculus handwritten notes.', 'Brown', 'Room 204 Senior Block', '2026-09-06', 'FOUND', 'OPEN', 2),
(7, 'Black Wildcraft Backpack', 'Accessories', 'Wildcraft double compartment bag containing biology textbook and pencil pouch.', 'Black', 'School Canteen Hall', '2026-09-07', 'FOUND', 'CLAIMED', 3),
(8, 'Camlin Geometry Box', 'Stationery', 'Metal tin geometry box containing compass, divider and set squares.', 'Silver', 'Room 102 Junior Wing', '2026-09-08', 'LOST', 'OPEN', 5),
(9, 'Senior School Uniform Tie', 'Clothing', 'Maroon and gold striped standard school tie with school crest clip.', 'Maroon', 'Morning Assembly Ground', '2026-09-08', 'FOUND', 'OPEN', 4);

-- Insert Sample Claims
INSERT INTO claims (claim_id, item_id, user_id, reason, lost_location, additional_info, status) VALUES
(1, 7, 2, 'I accidentally forgot my Wildcraft school bag after 4th period lunch break.', 'School Canteen Hall', 'Inside the front zip pocket there is an orange highlighter and student transit pass with my name.', 'APPROVED'),
(2, 3, 3, 'Lost my blue water bottle right after basketball practice yesterday.', 'Sports Ground Pavilion', 'Has my initials P.P. scratched underneath the rubber ring.', 'PENDING');

-- Insert Login Credentials (Plaintext for Examination / Viva Reference)
INSERT INTO login_credentials (login_type, email, password, role, description) VALUES
('Admin Login', 'admin@school.local', 'Admin@123', 'admin', 'Full Administrative Access to review items & claims'),
('Student Login', 'aravind@school.local', 'Student@123', 'student', 'Student Portal to report lost/found items & submit claims');

-- ====================================================================
-- Step 4: CBSE CS (083) Sample Demonstration Queries
-- These queries demonstrate essential curriculum concepts.
-- ====================================================================

-- 1. INNER JOIN Query: Retrieve items with reporter details
SELECT i.item_id, i.item_name, i.item_type, i.status, u.name AS reported_by_name, u.email
FROM items i
INNER JOIN users u ON i.reported_by = u.user_id
ORDER BY i.date_reported DESC;

-- 2. GROUP BY and COUNT() Query: Item count by category
SELECT category, COUNT(*) AS total_items
FROM items
GROUP BY category
ORDER BY total_items DESC;

-- 3. LIKE Query: Search items matching keyword in name or location
SELECT item_name, category, location, status
FROM items
WHERE item_name LIKE '%calculator%' OR location LIKE '%lab%';

-- 4. UPDATE Query: Approve a pending report to OPEN
UPDATE items
SET status = 'OPEN'
WHERE item_id = 5 AND status = 'PENDING';

-- 5. DELETE Query: Clean up rejected claims
DELETE FROM claims
WHERE status = 'REJECTED';
