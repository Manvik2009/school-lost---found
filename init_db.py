"""
Database Initialization Script for School Lost & Found
Class 12 CBSE Computer Science (083) Project

This script connects to MySQL, creates the database 'school_lost_found' if not present,
creates all tables (users, items, claims), hashes security passwords,
and seeds rich realistic sample records.
"""

import sys
from werkzeug.security import generate_password_hash
from config import Config

def init_mysql_db():
    try:
        import socket
        # Fast socket check to avoid long OS TCP timeout
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        check_result = sock.connect_ex((Config.MYSQL_HOST, Config.MYSQL_PORT))
        sock.close()
        if check_result != 0:
            print("! MySQL Server is not currently reachable on {}:{}.".format(Config.MYSQL_HOST, Config.MYSQL_PORT))
            return False

        import mysql.connector
        from mysql.connector import errorcode

        print("-> Connecting to MySQL Server at {}:{}...".format(Config.MYSQL_HOST, Config.MYSQL_PORT))
        
        # Connect to MySQL Server without specifying DB first (to create database if needed)
        cnx = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            port=Config.MYSQL_PORT,
            connection_timeout=3
        )
        cursor = cnx.cursor()

        # Step 1: Create Database
        cursor.execute("CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8mb4'".format(Config.MYSQL_DB))
        print("-> Database '{}' checked/created successfully.".format(Config.MYSQL_DB))

        cursor.execute("USE {}".format(Config.MYSQL_DB))

        # Step 2: Create Tables
        tables = {}
        tables['users'] = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            student_id VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(150) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """

        tables['items'] = """
        CREATE TABLE IF NOT EXISTS items (
            item_id INT PRIMARY KEY AUTO_INCREMENT,
            item_name VARCHAR(100) NOT NULL,
            category VARCHAR(50) NOT NULL,
            description TEXT,
            color VARCHAR(50),
            location VARCHAR(150) NOT NULL,
            date_reported DATE NOT NULL,
            item_type VARCHAR(10) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
            reported_by INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (reported_by) REFERENCES users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """

        tables['claims'] = """
        CREATE TABLE IF NOT EXISTS claims (
            claim_id INT PRIMARY KEY AUTO_INCREMENT,
            item_id INT NOT NULL,
            user_id INT NOT NULL,
            reason TEXT NOT NULL,
            lost_location VARCHAR(150) NOT NULL,
            additional_info TEXT,
            status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        ) ENGINE=InnoDB;
        """

        tables['login_credentials'] = """
        CREATE TABLE IF NOT EXISTS login_credentials (
            credential_id INT PRIMARY KEY AUTO_INCREMENT,
            login_type VARCHAR(50) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            password VARCHAR(100) NOT NULL,
            role VARCHAR(20) NOT NULL,
            description VARCHAR(255)
        ) ENGINE=InnoDB;
        """

        for table_name, ddl in tables.items():
            cursor.execute(ddl)
            print("-> Table '{}' created/verified.".format(table_name))

        # Step 3: Check if default admin exists
        cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", (Config.ADMIN_EMAIL,))
        admin_count = cursor.fetchone()[0]

        if admin_count == 0:
            print("-> Seeding default Administrator and Student accounts...")
            admin_pwd = generate_password_hash(Config.ADMIN_DEFAULT_PASSWORD)
            stu_pwd = generate_password_hash("Student@123")

            seed_users = [
                ('System Administrator', 'ADMIN-001', Config.ADMIN_EMAIL, admin_pwd, 'admin'),
                ('Aravind Sharma', 'STU-1001', 'aravind@school.local', stu_pwd, 'student'),
                ('Priya Patel', 'STU-1002', 'priya@school.local', stu_pwd, 'student'),
                ('Rohit Verma', 'STU-1003', 'rohit@school.local', stu_pwd, 'student'),
                ('Ananya Iyer', 'STU-1004', 'ananya@school.local', stu_pwd, 'student'),
            ]
            user_insert = "INSERT INTO users (name, student_id, email, password, role) VALUES (%s, %s, %s, %s, %s)"
            cursor.executemany(user_insert, seed_users)
            cnx.commit()

            # Seed Items
            seed_items = [
                ('Black Scientific Calculator', 'Electronics', 'Casio fx-991EX ClassWiz calculator with solar panel.', 'Black', 'Physics Lab Room 302', '2026-09-02', 'LOST', 'OPEN', 2),
                ('Black Scientific Calculator Casio', 'Electronics', 'Casio fx-991EX calculator found near desk 14.', 'Black', 'Physics Lab', '2026-09-03', 'FOUND', 'OPEN', 3),
                ('Blue Stainless Steel Water Bottle', 'Water Bottle', 'Milton 750ml blue thermos with scratch on base.', 'Blue', 'Sports Ground Pavilion', '2026-09-04', 'FOUND', 'OPEN', 4),
                ('School Student ID Card', 'ID Card', 'Class 12 ID card for student Priya Patel STU-1002.', 'White', 'Library Reading Hall', '2026-09-05', 'FOUND', 'OPEN', 5),
                ('Wireless Bluetooth Earphones', 'Electronics', 'Boat Airdopes in white charging case.', 'White', 'Computer Lab 2', '2026-09-06', 'LOST', 'PENDING', 4),
                ('Mathematics Classmate Notebook', 'Books', '200 pages spiral notebook with handwritten notes.', 'Brown', 'Room 204 Senior Block', '2026-09-06', 'FOUND', 'OPEN', 2),
                ('Black Wildcraft Backpack', 'Accessories', 'Double compartment bag with textbooks inside.', 'Black', 'School Canteen Hall', '2026-09-07', 'FOUND', 'CLAIMED', 3),
                ('Camlin Geometry Box', 'Stationery', 'Metal tin geometry box containing compass and divider.', 'Silver', 'Room 102 Junior Wing', '2026-09-08', 'LOST', 'OPEN', 5),
                ('Senior School Uniform Tie', 'Clothing', 'Maroon and gold striped standard school tie.', 'Maroon', 'Morning Assembly Ground', '2026-09-08', 'FOUND', 'OPEN', 4),
                ('Silver Digital Wristwatch', 'Accessories', 'Fastrack silver chain wristwatch with blue dial.', 'Silver', 'Basketball Court Bleachers', '2026-09-01', 'LOST', 'RETURNED', 2),
            ]
            item_insert = """
            INSERT INTO items (item_name, category, description, color, location, date_reported, item_type, status, reported_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(item_insert, seed_items)
            cnx.commit()

            # Seed Claims
            seed_claims = [
                (7, 2, 'I forgot my Wildcraft school bag after 4th period lunch break.', 'School Canteen Hall', 'Contains my transit pass and orange highlighter in front zip.', 'APPROVED'),
                (3, 3, 'Lost my blue water bottle right after basketball practice.', 'Sports Ground Pavilion', 'Has initials P.P. scratched underneath.', 'PENDING')
            ]
            claim_insert = """
            INSERT INTO claims (item_id, user_id, reason, lost_location, additional_info, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(claim_insert, seed_claims)
            cnx.commit()

            # Seed Login Credentials (Plaintext for Viva / Practical Demonstration)
            cred_insert = """
            INSERT INTO login_credentials (login_type, email, password, role, description)
            VALUES (%s, %s, %s, %s, %s)
            """
            seed_creds = [
                ('Admin Login', 'admin@school.local', 'Admin@123', 'admin', 'Full Administrative Access to review items & claims'),
                ('Student Login', 'aravind@school.local', 'Student@123', 'student', 'Student Portal to report lost/found items & submit claims')
            ]
            cursor.executemany(cred_insert, seed_creds)
            cnx.commit()

            print("-> Successfully inserted demo users, items, claims, and login credentials.")
        else:
            print("-> Existing database contains {} user(s). Skipping seed insertion.".format(admin_count))

        cursor.close()
        cnx.close()
        print("-> MySQL database initialization and seeding complete!")
        return True

    except Exception as e:
        print("! MySQL Database Initialization Error:", str(e))
        return False

def init_sqlite_db(db_path=None):
    """
    Initializes a zero-configuration SQLite database with identical schema and seed records.
    Ensures seamless deployment to Render, Firebase, Docker, or offline environments.
    """
    import sqlite3
    import os

    if not db_path:
        db_path = Config.SQLITE_PATH

    print("-> Initializing SQLite Database at: {}".format(db_path))

    # Ensure parent directory exists
    parent_dir = os.path.dirname(db_path)
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign keys in SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        student_id TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'student',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Items Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        color TEXT,
        location TEXT NOT NULL,
        date_reported TEXT NOT NULL,
        item_type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING',
        reported_by INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (reported_by) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)

    # 3. Claims Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        reason TEXT NOT NULL,
        lost_location TEXT NOT NULL,
        additional_info TEXT,
        status TEXT NOT NULL DEFAULT 'PENDING',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)

    # 4. Login Credentials Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS login_credentials (
        credential_id INTEGER PRIMARY KEY AUTOINCREMENT,
        login_type TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        description TEXT
    );
    """)

    # Check if admin exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = ?", (Config.ADMIN_EMAIL,))
    admin_count = cursor.fetchone()[0]

    if admin_count == 0:
        print("-> Seeding default Administrator and Student accounts into SQLite...")
        admin_pwd = generate_password_hash(Config.ADMIN_DEFAULT_PASSWORD)
        stu_pwd = generate_password_hash("Student@123")

        seed_users = [
            ('System Administrator', 'ADMIN-001', Config.ADMIN_EMAIL, admin_pwd, 'admin'),
            ('Aravind Sharma', 'STU-1001', 'aravind@school.local', stu_pwd, 'student'),
            ('Priya Patel', 'STU-1002', 'priya@school.local', stu_pwd, 'student'),
            ('Rohit Verma', 'STU-1003', 'rohit@school.local', stu_pwd, 'student'),
            ('Ananya Iyer', 'STU-1004', 'ananya@school.local', stu_pwd, 'student'),
        ]
        cursor.executemany("INSERT INTO users (name, student_id, email, password, role) VALUES (?, ?, ?, ?, ?)", seed_users)
        conn.commit()

        # Seed Items
        seed_items = [
            ('Black Scientific Calculator', 'Electronics', 'Casio fx-991EX ClassWiz calculator with solar panel.', 'Black', 'Physics Lab Room 302', '2026-09-02', 'LOST', 'OPEN', 2),
            ('Black Scientific Calculator Casio', 'Electronics', 'Casio fx-991EX calculator found near desk 14.', 'Black', 'Physics Lab', '2026-09-03', 'FOUND', 'OPEN', 3),
            ('Blue Stainless Steel Water Bottle', 'Water Bottle', 'Milton 750ml blue thermos with scratch on base.', 'Blue', 'Sports Ground Pavilion', '2026-09-04', 'FOUND', 'OPEN', 4),
            ('School Student ID Card', 'ID Card', 'Class 12 ID card for student Priya Patel STU-1002.', 'White', 'Library Reading Hall', '2026-09-05', 'FOUND', 'OPEN', 5),
            ('Wireless Bluetooth Earphones', 'Electronics', 'Boat Airdopes in white charging case.', 'White', 'Computer Lab 2', '2026-09-06', 'LOST', 'PENDING', 4),
            ('Mathematics Classmate Notebook', 'Books', '200 pages spiral notebook with handwritten notes.', 'Brown', 'Room 204 Senior Block', '2026-09-06', 'FOUND', 'OPEN', 2),
            ('Black Wildcraft Backpack', 'Accessories', 'Double compartment bag with textbooks inside.', 'Black', 'School Canteen Hall', '2026-09-07', 'FOUND', 'CLAIMED', 3),
            ('Camlin Geometry Box', 'Stationery', 'Metal tin geometry box containing compass and divider.', 'Silver', 'Room 102 Junior Wing', '2026-09-08', 'LOST', 'OPEN', 5),
            ('Senior School Uniform Tie', 'Clothing', 'Maroon and gold striped standard school tie.', 'Maroon', 'Morning Assembly Ground', '2026-09-08', 'FOUND', 'OPEN', 4),
            ('Silver Digital Wristwatch', 'Accessories', 'Fastrack silver chain wristwatch with blue dial.', 'Silver', 'Basketball Court Bleachers', '2026-09-01', 'LOST', 'RETURNED', 2),
        ]
        cursor.executemany("""
        INSERT INTO items (item_name, category, description, color, location, date_reported, item_type, status, reported_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, seed_items)
        conn.commit()

        # Seed Claims
        seed_claims = [
            (7, 2, 'I forgot my Wildcraft school bag after 4th period lunch break.', 'School Canteen Hall', 'Contains my transit pass and orange highlighter in front zip.', 'APPROVED'),
            (3, 3, 'Lost my blue water bottle right after basketball practice.', 'Sports Ground Pavilion', 'Has initials P.P. scratched underneath.', 'PENDING')
        ]
        cursor.executemany("""
        INSERT INTO claims (item_id, user_id, reason, lost_location, additional_info, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, seed_claims)
        conn.commit()

        # Seed Login Credentials
        seed_creds = [
            ('Admin Login', 'admin@school.local', 'Admin@123', 'admin', 'Full Administrative Access to review items & claims'),
            ('Student Login', 'aravind@school.local', 'Student@123', 'student', 'Student Portal to report lost/found items & submit claims')
        ]
        cursor.executemany("""
        INSERT INTO login_credentials (login_type, email, password, role, description)
        VALUES (?, ?, ?, ?, ?)
        """, seed_creds)
        conn.commit()

        print("-> Successfully seeded SQLite database with demo records.")
    else:
        print("-> Existing SQLite database contains {} user(s). Skipping seed insertion.".format(admin_count))

    cursor.close()
    conn.close()
    print("-> SQLite database initialization complete!")
    return True

if __name__ == '__main__':
    print("=== Initializing School Lost & Found Database ===")
    mode = Config.DB_MODE

    if mode == 'sqlite':
        print("DB_MODE is 'sqlite'. Setting up SQLite...")
        init_sqlite_db()
        print("=== Database Setup Ready (SQLite) ===")
    elif mode == 'mysql':
        print("DB_MODE is 'mysql'. Setting up MySQL...")
        success = init_mysql_db()
        if not success:
            sys.exit(1)
        print("=== Database Setup Ready (MySQL) ===")
    else:
        # 'auto' mode: Try MySQL, fallback to SQLite
        print("DB_MODE is 'auto'. Checking MySQL availability...")
        success = init_mysql_db()
        if success:
            print("=== Database Setup Ready (MySQL 8.0) ===")
        else:
            print("-> MySQL is unavailable. Setting up SQLite cloud fallback...")
            init_sqlite_db()
            print("=== Database Setup Ready (SQLite Cloud Fallback) ===")
