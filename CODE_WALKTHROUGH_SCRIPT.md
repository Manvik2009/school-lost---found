# Examiner Presentation & Code Walkthrough Script
# Digital Belongings Portal — School Lost & Found Management System

This guide is your **step-by-step presentation script**. Use it when demonstrating the application and presenting the code to internal and external examiners.

---

## Part 1: The 2-Minute Spoken Introduction (Elevator Pitch)

Memorize or practice this short speech when the examiner asks: *"Explain your project"*:

> *"Good morning/afternoon, Sir/Ma'am.*
>
> *My project is the **Digital Belongings Portal — School Lost & Found Management System**, developed in Python using Flask and MySQL connectivity, following the CBSE Class 12 Computer Science (083) curriculum.*
>
> *In any school, students frequently misplace calculators, ID cards, notebooks, and sports gear. Traditional lost-and-found registers are either manual, disorganized, or lack privacy. This portal digitizes the whole cycle:*
> 1. *Students can securely log in and report an item they have lost or found.*
> 2. *The system runs an **automated matching algorithm** that calculates similarity scores between lost and found items in real-time based on keywords, category, color, and location.*
> 3. *Students can submit a formal **ownership claim** with verification details.*
> 4. *The school administration has a **dedicated admin moderation dashboard** to approve reports, review claims, mark items as returned, and manage the student registry.*
>
> *Technically, it demonstrates relational database design with 3NF tables, Primary and Foreign Keys with `ON DELETE CASCADE`, parameterized SQL queries to prevent SQL injection, secure password hashing using Werkzeug, and connection pooling for optimal performance.*
>
> *May I show you a live demonstration and the code implementation?"*

---

## Part 2: 5-Step Live Demonstration Script

Keep these test credentials ready:
- **Admin Account:** `admin@school.local` | Password: `Admin@123`
- **Student Account:** `aravind@school.local` | Password: `Student@123`
- **Second Student:** `priya@school.local` | Password: `Student@123`

### Step 1: Show the Public Landing Page (`/`)
- Point out the clean user interface, platform statistics (`Total Items`, `Active Reports`, `Returned Items`), and recently reported items.
- Point out the status tag indicating **MySQL 8.0 Connected**.

### Step 2: Log in as a Student (`aravind@school.local`)
- Navigate to `/login`. Enter student credentials.
- Land on the **Student Dashboard (`/dashboard`)**.
- Highlight the personal metric cards (My Lost Reports, My Found Reports, My Claims).
- Show the **"Potential Matches" section**: The system automatically flagged a match for Aravind's lost Casio calculator!

### Step 3: Demonstrate Item Search & Filters (`/search`)
- Go to the Search page.
- Type in `"calculator"` or filter by category `"Electronics"`.
- Explain: *"This executes a dynamic parameterized SQL query utilizing `WHERE`, `LIKE`, and `ORDER BY date_reported DESC` without exposing the system to SQL injection."*

### Step 4: Submit a Claim on a Found Item
- Open an item marked **FOUND** reported by another student.
- Click **"Claim This Item"**.
- Fill in the verification form: mention location and a specific identification mark (e.g. *"Sticker on the solar panel"*).
- Submit the claim. It now shows under **My Claims** with status `PENDING`.

### Step 5: Switch to Admin Portal (`admin@school.local`)
- Log out, then log in as the School Administrator.
- Open **Admin Dashboard (`/admin/dashboard`)**.
- Go to **Claims Moderation (`/admin/claims`)**:
  - View the newly submitted claim from Aravind.
  - Click **Approve Claim**.
  - Notice the item status automatically changes to `CLAIMED` via relational database updates.
- Show the **Item Moderation table (`/admin/items`)** and **User Directory (`/admin/users`)**.

---

## Part 3: Code Walkthrough — Where to Point in `app.py`

When the examiner asks to see the code, open `app.py` and navigate directly to these key line ranges:

### 1. Database Connection & Pooling
- **Where:** `app.py`, Lines 35 – 123
- **Functions:** `_init_connection_pool()` and `get_db_connection()`
- **What to say:**
  > *"Here I created a MySQL Connection Pool (`MySQLConnectionPool`) with a pool size of 5. Instead of reconnecting to the database on every HTTP request, connections are pre-established and reused, which cuts latency by 200–300 milliseconds. If MySQL is unavailable locally, it features a fallback to SQLite."*

### 2. Centralized Query Execution & SQL Injection Prevention
- **Where:** `app.py`, Lines 124 – 172
- **Function:** `execute_query(query, params, commit, fetchone, fetchall)`
- **What to say:**
  > *"All SQL execution is routed through this single function. It creates a dictionary cursor, runs parameterized queries using `%s` placeholders, commits transactions on DML statements, handles rollback on exceptions, and safely closes cursors in the finally block."*

### 3. Role-Based Security Decorators
- **Where:** `app.py`, Lines 174 – 198
- **Functions:** `@login_required` and `@admin_required`
- **What to say:**
  > *"These are custom Python decorators using `functools.wraps`. Before executing any view function, they inspect `session['user_id']` and `session['role']`. If a regular student tries to access `/admin/items`, the decorator rejects them with an access denied flash message."*

### 4. The Smart Matching Algorithm
- **Where:** `app.py`, Lines 201 – 324
- **Functions:** `calculate_similarity_score()` and `find_matches_for_item()`
- **What to say:**
  > *"This is a 100-point heuristic scoring algorithm. It tokenizes item names, removes common English stop words, and measures keyword overlap (40 pts), category equality (25 pts), color matching (20 pts), and location proximity (15 pts). Items scoring 35% or above are suggested to students."*

### 5. Authentication & Password Hashing
- **Where:** `app.py`, Lines 409 – 508
- **Functions:** `register()`, `login()`, `logout()`
- **What to say:**
  > *"In the registration route, we validate mandatory fields, verify email regex, and check for unique constraints before hashing the password with Werkzeug's `generate_password_hash()`. In the login route, we verify the password using `check_password_hash()`."*

### 6. Relational Joins & Admin Actions
- **Where:** `app.py`, Lines 873 – 985
- **Functions:** `admin_items()`, `admin_claims()`, `admin_approve_claim()`
- **What to say:**
  > *"In `admin_claims`, we perform an `INNER JOIN` across three tables (`claims`, `items`, and `users`) in a single query to display the item name, category, claimant name, and student ID together."*

---

## Part 4: Database Schema Walkthrough (`database.sql`)

Keep `database.sql` open in another tab. Point out:
1. **`users` Table:** Primary Key `user_id AUTO_INCREMENT`, `UNIQUE` constraints on `student_id` and `email`.
2. **`items` Table:** Foreign Key `reported_by` references `users(user_id)` with `ON DELETE CASCADE`.
3. **`claims` Table:** Dual Foreign Keys (`item_id` and `user_id`).
4. **Sample Queries:** Show Step 4 in `database.sql` with `INNER JOIN`, `GROUP BY`, `COUNT(*)`, and `LIKE` examples.

---

## Part 5: Top 5 Examiner "Gotchas" & How to Answer

1. **Examiner asks:** *"What if someone types `' OR '1'='1` in the login box?"*
   - **Answer:** *"Nothing malicious will happen, Sir. We pass the input through parameterized `%s` tuples in `cursor.execute()`. MySQL treats the entire string literally as an email address, so the lookup simply returns zero records."*

2. **Examiner asks:** *"Why do you store `reported_by` as an integer instead of student name in the items table?"*
   - **Answer:** *"Storing the student name directly would violate Database Normalization (redundant data). If a student updates their name, we would have to update multiple tables. By storing only the foreign key `user_id`, we maintain normalization and referential integrity."*

3. **Examiner asks:** *"What is the difference between a session and a cookie?"*
   - **Answer:** *"A cookie is a small data file stored in the client's browser. A session is the logical state of a user. In Flask, session data is stored inside a cryptographically signed cookie on the client, ensuring the server can verify it has not been tampered with."*

4. **Examiner asks:** *"Where are your static files like CSS and images stored?"*
   - **Answer:** *"Flask serves static assets from the `static/` directory using `url_for('static', filename='...')`, while HTML templates with Jinja2 syntax reside in the `templates/` folder."*

5. **Examiner asks:** *"What happens if the MySQL server goes down?"*
   - **Answer:** *"The application includes a resilient fallback mechanism in `get_db_connection()`. If MySQL is unreachable, it automatically initializes and queries an embedded SQLite database (`school_lost_found.db`), ensuring zero application downtime."*
