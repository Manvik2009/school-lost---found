"""
Convenient CLI Table Viewer for School Lost & Found
Class 12 CBSE Computer Science (083) Project
"""

import mysql.connector
from config import Config

def show_tables():
    print("\n" + "=" * 70)
    print(" SCHOOL LOST & FOUND — LIVE MYSQL TABLES VIEWER (CBSE CS 083)")
    print("=" * 70)

    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            port=Config.MYSQL_PORT
        )
        cur = conn.cursor(dictionary=True)

        # 0. MySQL Table: login_credentials
        print("\n[TABLE: login_credentials]")
        print("-" * 80)
        cur.execute("SELECT credential_id, login_type, email, password, role, description FROM login_credentials")
        creds = cur.fetchall()
        print(f"{'ID':<3} | {'Login Type':<15} | {'Email':<22} | {'Password':<12} | {'Role':<8} | {'Description'}")
        print("-" * 80)
        for c in creds:
            desc_snip = (c['description'][:22] + '...') if len(c['description']) > 22 else c['description']
            print(f"{c['credential_id']:<3} | {c['login_type']:<15} | {c['email']:<22} | {c['password']:<12} | {c['role']:<8} | {desc_snip}")
        print("-" * 80)

        # 1. Users Table
        print("\n[TABLE: users]")
        print("-" * 70)
        cur.execute("SELECT user_id, name, student_id, email, role FROM users")
        users = cur.fetchall()
        print(f"{'ID':<4} | {'Name':<22} | {'Student ID':<12} | {'Role':<8} | {'Email'}")
        print("-" * 70)
        for u in users:
            print(f"{u['user_id']:<4} | {u['name']:<22} | {u['student_id']:<12} | {u['role']:<8} | {u['email']}")

        # 2. Items Table
        print("\n[TABLE: items]")
        print("-" * 85)
        cur.execute("SELECT item_id, item_name, category, item_type, status, location FROM items")
        items = cur.fetchall()
        print(f"{'ID':<4} | {'Item Name':<32} | {'Type':<6} | {'Status':<9} | {'Location'}")
        print("-" * 85)
        for i in items:
            print(f"{i['item_id']:<4} | {i['item_name']:<32} | {i['item_type']:<6} | {i['status']:<9} | {i['location']}")

        # 3. Claims Table
        print("\n[TABLE: claims]")
        print("-" * 75)
        cur.execute("""
            SELECT c.claim_id, c.item_id, u.name as student_name, c.reason, c.status
            FROM claims c
            JOIN users u ON c.user_id = u.user_id
        """)
        claims = cur.fetchall()
        print(f"{'Claim':<6} | {'Item':<5} | {'Student':<18} | {'Status':<9} | {'Reason'}")
        print("-" * 75)
        for c in claims:
            reason_snip = (c['reason'][:30] + '...') if len(c['reason']) > 30 else c['reason']
            print(f"#{c['claim_id']:<5} | #{c['item_id']:<4} | {c['student_name']:<18} | {c['status']:<9} | {reason_snip}")

        print("\n" + "=" * 70)
        print(" Total Records: {} users, {} items, {} claims".format(len(users), len(items), len(claims)))
        print("=" * 70 + "\n")

        cur.close()
        conn.close()

    except Exception as e:
        print("Connection Error:", e)

if __name__ == '__main__':
    show_tables()
