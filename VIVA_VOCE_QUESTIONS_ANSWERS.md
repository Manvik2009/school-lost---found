# CBSE Class 12 Computer Science (083) — Viva Voce Preparation Guide
# Project: School Lost & Found Management System

This document contains real questions frequently asked by CBSE External and Internal Examiners during the Class 12 Practical Examination, along with model answers and code references.

---

## Section 1: Project Overview & Concept Questions

### Q1. What is the title and objective of your project?
> **Model Answer:**
> "The project is titled **'Digital Belongings Portal — School Lost & Found Management System'**. Its objective is to digitize and automate the reporting, tracking, matching, and recovery of misplaced student articles (such as calculators, ID cards, water bottles, and books) within a school campus. It features role-based student and admin access, an automated smart matching recommendation engine, and a claim verification workflow."

### Q2. What technologies did you use to build this project?
> **Model Answer:**
> - **Backend:** Python 3.12+ with the Flask micro-framework.
> - **Database:** MySQL 8.0 relational database (with automated SQLite fallback for local development).
> - **Database Connectivity:** `mysql-connector-python` using connection pooling and parameterized SQL queries.
> - **Frontend:** HTML5, modern Vanilla CSS (with glassmorphism and card UI), and JavaScript.
> - **Authentication & Security:** Werkzeug security module (`scrypt` password hashing) and Flask cryptographically signed session cookies.

### Q3. Why did you choose Flask instead of Django or a desktop Tkinter application?
> **Model Answer:**
> "Flask is lightweight, modular, and does not hide core web mechanisms behind heavy abstractions, which allowed me to directly write and control the SQL queries and database connectivity as required by the CBSE 083 syllabus. A web interface allows multiple students and administrators across different school computers and mobile devices to access the system simultaneously, unlike a single-desktop Tkinter GUI."

---

## Section 2: Database & SQL Connectivity (CBSE Syllabus Unit 3)

### Q4. How did you connect Python with MySQL? Explain the steps.
> **Model Answer:**
> "I used the official `mysql.connector` library. The standard process involves:
> 1. **Importing the module:** `import mysql.connector`
> 2. **Establishing Connection:** `conn = mysql.connector.connect(host=..., user=..., password=..., database=...)` or retrieving a connection from a connection pool.
> 3. **Creating a Cursor:** `cursor = conn.cursor(dictionary=True)` which acts as a pointer/control structure to traverse and fetch database records.
> 4. **Executing Queries:** `cursor.execute(sql_query, params)`
> 5. **Committing Changes:** For DML queries (`INSERT`, `UPDATE`, `DELETE`), calling `conn.commit()`.
> 6. **Fetching Data:** For DQL queries (`SELECT`), calling `cursor.fetchone()` or `cursor.fetchall()`.
> 7. **Closing Resources:** In the `finally` block, closing both the cursor and the connection to prevent memory and connection leaks."

### Q5. What is the difference between `cursor.fetchone()` and `cursor.fetchall()`?
> **Model Answer:**
> - **`cursor.fetchone()`**: Retrieves only the next single row from the query result set as a tuple or dictionary, or returns `None` if no more rows are available. Ideal for single-item lookups by primary key (e.g. finding user by email or item by `item_id`).
> - **`cursor.fetchall()`**: Retrieves all remaining rows from the result set as a list of rows. Ideal for displaying lists or tables, such as search results or dashboard tables.

### Q6. Why do we need `conn.commit()`? What happens if you forget it?
> **Model Answer:**
> "MySQL transactions follow the ACID properties (Atomicity, Consistency, Isolation, Durability). By default, DML operations (`INSERT`, `UPDATE`, `DELETE`) are buffered inside a pending transaction. `conn.commit()` permanently saves these modifications to the physical storage. If we forget `conn.commit()`, the changes will be rolled back when the connection closes, and the data will never be written to the database."

### Q7. What is `conn.rollback()` and where did you use it?
> **Model Answer:**
> "In `app.py`, inside the `execute_query` function, database operations are enclosed in a `try...except...finally` block. If an error or exception occurs during query execution (such as a database timeout or integrity constraint violation), `conn.rollback()` is invoked in the `except` block to undo any half-completed changes, ensuring database consistency."

### Q8. What is SQL Injection, and how did you prevent it in your code?
> **Model Answer:**
> "SQL Injection is a major security vulnerability where malicious SQL commands are entered into form fields (e.g. `' OR 1=1 --`) to manipulate the backend query.
>
> In my project, I strictly avoided string concatenation (e.g. `f'SELECT * FROM users WHERE email=\"{email}\"'`). Instead, I used **parameterized queries** with `%s` placeholders:
> ```python
> execute_query(\"SELECT * FROM users WHERE email = %s\", (email,), fetchone=True)
> ```
> The database driver treats the parameters strictly as data values, automatically escaping special characters and making SQL injection impossible."

### Q9. What are Primary Keys and Foreign Keys in your database? Give examples from your tables.
> **Model Answer:**
> - **Primary Key:** A column (or set of columns) that uniquely identifies each record in a table. It cannot contain `NULL` or duplicate values.
>   - *Example:* `user_id` in table `users`, `item_id` in table `items`, `claim_id` in table `claims`.
> - **Foreign Key:** A column in one table that references the Primary Key of another table, establishing a relationship and enforcing referential integrity.
>   - *Example:* In `items`, `reported_by` is a Foreign Key referencing `users(user_id)`.
>   - *Example:* In `claims`, `item_id` references `items(item_id)` and `user_id` references `users(user_id)`.

### Q10. What is `ON DELETE CASCADE` and why did you use it?
> **Model Answer:**
> "`ON DELETE CASCADE` is a referential action. When a parent record in the referenced table is deleted, all corresponding child records in referencing tables are automatically deleted by the database engine.
> For instance, if an item is deleted from the `items` table, all associated claims in the `claims` table are automatically removed, preventing 'orphaned' records that point to a non-existent item."

### Q11. Can you write an SQL query demonstrating an `INNER JOIN` in your project?
> **Model Answer:**
> "Yes, in `app.py` and `database.sql`, to show the item along with the name of the student who reported it:
> ```sql
> SELECT items.item_id, items.item_name, items.item_type, items.status, users.name AS reporter_name
> FROM items
> INNER JOIN users ON items.reported_by = users.user_id
> WHERE items.status = 'OPEN';
> ```
> This combines rows from both tables wherever `reported_by` matches `user_id`."

---

## Section 3: Python & Flask Application Logic

### Q12. What is a Python Decorator? How is `@login_required` implemented?
> **Model Answer:**
> "A decorator is a design pattern in Python that allows us to dynamically extend or modify the behavior of a function without modifying its source code. It wraps the target function.
>
> In `app.py`, `@login_required` wraps route handler functions:
> ```python
> def login_required(f):
>     @wraps(f)
>     def decorated_function(*args, **kwargs):
>         if 'user_id' not in session:
>             flash(\"Please log in to access this page.\", \"warning\")
>             return redirect(url_for('login'))
>         return f(*args, **kwargs)
>     return decorated_function
> ```
> Before loading protected pages like `/dashboard` or `/report-lost`, it verifies if `user_id` exists in the current session. If not, it redirects to the login screen."

### Q13. How does Session Management work in Flask? Is it secure?
> **Model Answer:**
> "Flask uses **cryptographically signed client-side cookies** for session management. When a user logs in, their identity data (`user_id`, `role`, `name`) is serialized and signed using the secret key (`Config.SECRET_KEY`).
> The browser sends this cookie on subsequent requests. Because the cookie is cryptographically signed with HMAC, if a user attempts to modify or tamper with their role from 'student' to 'admin', Flask detects the signature mismatch and invalidates the session."

### Q14. Why did you use Werkzeug password hashing instead of storing plaintext passwords?
> **Model Answer:**
> "Storing plaintext passwords is an egregious security violation. If the database is compromised, all user passwords would be exposed.
> I used `generate_password_hash(password)` from `werkzeug.security`, which implements the **scrypt** one-way cryptographic hashing algorithm with an automatic unique salt. It cannot be decrypted or reverse-engineered. When logging in, `check_password_hash(stored_hash, input_password)` computes the hash of the input and checks for a match."

### Q15. How does your Lost-and-Found Matching Recommendation Algorithm work?
> **Model Answer:**
> "The matching engine uses an explainable 100-point heuristic scoring system (`calculate_similarity_score` in `app.py`):
> 1. **Item Name (40 points):** Strips punctuation, removes common English stop words (`a`, `the`, `my`), and computes word set intersection ratio between the lost item title and found item title. Substrings also award partial points.
> 2. **Category Match (25 points):** Verifies if both items belong to the same category (e.g. Electronics).
> 3. **Color Match (20 points):** Checks if the primary color matches or is a substring.
> 4. **Location Match (15 points):** Checks for common venue keywords (e.g., 'Physics Lab').
>
> Any pair scoring 35 or above is presented as a high-confidence match on the student dashboard and item details page."

### Q16. What is Database Connection Pooling, and why was it implemented?
> **Model Answer:**
> "Normally, establishing a fresh TCP connection to a remote database server requires a three-way network handshake, taking 200–300 milliseconds on every single HTTP request.
> To optimize this, I initialized a `mysql.connector.pooling.MySQLConnectionPool` with a pool size of 5 connections at startup (`_init_connection_pool()`). Flask workers pull pre-established connections from this pool and return them after the query completes, eliminating connection latency and significantly accelerating page loads."

### Q17. How do you prevent a student from claiming their own item or filing duplicate claims?
> **Model Answer:**
> "In the `/claim/<int:item_id>` route:
> 1. We check if `item['reported_by'] == session['user_id']`. If true, the system flashes an error: *'You cannot claim an item you reported yourself'*.
> 2. We execute an SQL check:
>    ```sql
>    SELECT claim_id FROM claims WHERE item_id = %s AND user_id = %s AND status IN ('PENDING', 'APPROVED')
>    ```
>    If an active claim already exists, duplicate submissions are rejected."

### Q18. What is the difference between DDL and DML in SQL?
> **Model Answer:**
> - **DDL (Data Definition Language):** Defines or modifies the structure/schema of the database. Commands include `CREATE TABLE`, `ALTER TABLE`, and `DROP TABLE`. Changes are auto-committed.
> - **DML (Data Manipulation Language):** Manipulates the data stored within tables. Commands include `INSERT`, `UPDATE`, and `DELETE`. Requires explicit transaction management (`commit()`).

---

## Section 4: Quick Fire Definitions (Examiner Rapid Round)

| Concept | 1-Sentence CBSE Definition |
|---|---|
| **Candidate Key** | Any attribute or set of attributes capable of uniquely identifying a record; the chosen candidate key becomes the Primary Key. |
| **Referential Integrity** | A rule in relational databases stating that a foreign key value must always match an existing primary key value in the referenced table, or be NULL. |
| **Degree of a Relation** | The total number of attributes (columns) in a table. (In our `items` table, Degree = 11). |
| **Cardinality of a Relation** | The total number of tuples (rows) currently stored in a table. |
| **Equi-Join** | A join condition that matches records across tables using the equality operator (`=`). |
| **Aggregate Functions** | Functions like `COUNT()`, `SUM()`, `AVG()`, `MIN()`, `MAX()` that operate on multiple values and return a single summary value. |
