import mysql.connector
from werkzeug.security import generate_password_hash
from config import Config

def seed():
    conn = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB,
        port=Config.MYSQL_PORT
    )
    cur = conn.cursor()

    # Disable foreign key checks to truncate/repopulate cleanly
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    cur.execute("TRUNCATE TABLE claims")
    cur.execute("TRUNCATE TABLE items")
    cur.execute("TRUNCATE TABLE users")
    cur.execute("TRUNCATE TABLE login_credentials")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")

    admin_pwd = generate_password_hash(Config.ADMIN_DEFAULT_PASSWORD)
    stu_pwd = generate_password_hash("Student@123")

    cur.executemany("INSERT INTO users (name, student_id, email, password, role) VALUES (%s, %s, %s, %s, %s)", [
        ('System Administrator', 'ADMIN-001', Config.ADMIN_EMAIL, admin_pwd, 'admin'),
        ('Aravind Sharma', 'STU-1001', 'aravind@school.local', stu_pwd, 'student'),
        ('Priya Patel', 'STU-1002', 'priya@school.local', stu_pwd, 'student'),
        ('Rohit Verma', 'STU-1003', 'rohit@school.local', stu_pwd, 'student'),
        ('Ananya Iyer', 'STU-1004', 'ananya@school.local', stu_pwd, 'student'),
    ])

    cur.executemany("""
    INSERT INTO items (item_name, category, description, color, location, date_reported, item_type, status, reported_by)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [
        ('Black Scientific Calculator', 'Electronics', 'Casio fx-991EX ClassWiz calculator with solar panel sticker on back.', 'Black', 'Physics Lab Room 302', '2026-09-02', 'LOST', 'OPEN', 2),
        ('Black Scientific Calculator Casio', 'Electronics', 'Casio fx-991EX calculator found near desk 14 on Monday morning.', 'Black', 'Physics Lab', '2026-09-03', 'FOUND', 'OPEN', 3),
        ('Blue Stainless Steel Water Bottle', 'Water Bottle', 'Milton 750ml blue thermos with scratch on base and silver screw cap.', 'Blue', 'Sports Ground Pavilion', '2026-09-04', 'FOUND', 'OPEN', 4),
        ('School Student ID Card', 'ID Card', 'Class 12 ID card for student Priya Patel STU-1002 with lanyard.', 'White', 'Library Reading Hall', '2026-09-05', 'FOUND', 'OPEN', 5),
        ('Wireless Bluetooth Earphones', 'Electronics', 'Boat Airdopes in white charging case with astronaut sticker.', 'White', 'Computer Lab 2', '2026-09-06', 'LOST', 'PENDING', 4),
        ('Mathematics Classmate Notebook', 'Books', '200 pages spiral notebook with Class 12 Calculus handwritten notes.', 'Brown', 'Room 204 Senior Block', '2026-09-06', 'FOUND', 'OPEN', 2),
        ('Black Wildcraft Backpack', 'Accessories', 'Double compartment bag containing biology textbook and pencil pouch.', 'Black', 'School Canteen Hall', '2026-09-07', 'FOUND', 'CLAIMED', 3),
        ('Camlin Geometry Box', 'Stationery', 'Metal tin geometry box containing compass, divider and set squares.', 'Silver', 'Room 102 Junior Wing', '2026-09-08', 'LOST', 'OPEN', 5),
        ('Senior School Uniform Tie', 'Clothing', 'Maroon and gold striped standard school tie with crest clip.', 'Maroon', 'Morning Assembly Ground', '2026-09-08', 'FOUND', 'OPEN', 4),
        ('Silver Digital Wristwatch', 'Accessories', 'Fastrack silver chain wristwatch with blue dial face.', 'Silver', 'Basketball Court Bleachers', '2026-09-01', 'LOST', 'RETURNED', 2),
    ])

    cur.executemany("""
    INSERT INTO claims (item_id, user_id, reason, lost_location, additional_info, status)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, [
        (7, 2, 'I forgot my Wildcraft school bag after 4th period lunch break.', 'School Canteen Hall', 'Contains my transit pass and orange highlighter in front zip.', 'APPROVED'),
        (3, 3, 'Lost my blue water bottle right after basketball practice.', 'Sports Ground Pavilion', 'Has initials P.P. scratched underneath.', 'PENDING')
    ])

    # Seed login_credentials table
    cur.executemany("""
    INSERT INTO login_credentials (login_type, email, password, role, description)
    VALUES (%s, %s, %s, %s, %s)
    """, [
        ('Admin Login', 'admin@school.local', 'Admin@123', 'admin', 'Full Administrative Access to review items & claims'),
        ('Student Login', 'aravind@school.local', 'Student@123', 'student', 'Student Portal to report lost/found items & submit claims')
    ])

    conn.commit()
    cur.close()
    conn.close()
    print("MySQL Database seeded successfully.")

if __name__ == '__main__':
    seed()
