# Technical Architecture & Languages Guide
# Digital Belongings Portal — School Lost & Found Management System
**CBSE Class 12 Computer Science (Subject Code: 083) Practical Project**

---

## Executive Overview

This project uses a modern multi-tier client-server web architecture. Each language handles a distinct layer of the system:

```
+-------------------------------------------------------------------------------+
|                             CLIENT-SIDE (BROWSER)                             |
|                                                                               |
|   HTML5 (Structure)   +   CSS3 (Styling/UI)   +   JavaScript (Interactivity)  |
+---------------------------------------+---------------------------------------+
                                        |
                             HTTP / HTTPS Requests
                               (GET / POST Forms)
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                            SERVER-SIDE (BACKEND)                              |
|                                                                               |
|                              PYTHON 3.12+ (Flask)                             |
|          - Routing & Dispatcher Controller (app.py)                           |
|          - Role-Based Security Decorators (@login_required, @admin_required)  |
|          - Cryptographic Password Hashing (Werkzeug scrypt)                   |
|          - 100-Point Weighted Heuristic Matching Engine                       |
|          - Jinja2 Template Engine (Renders dynamic HTML)                      |
+---------------------------------------+---------------------------------------+
                                        |
                              mysql.connector (Python)
                             Parameterized Queries (%s)
                             Connection Pool (5 workers)
                                        |
                                        v
+-------------------------------------------------------------------------------+
|                             DATABASE STORAGE LAYER                            |
|                                                                               |
|                             SQL (MySQL 8.0 Engine)                            |
|          - Relational Tables (users, items, claims, login_credentials)        |
|          - Integrity Constraints (PK, FK with ON DELETE CASCADE, UNIQUE)      |
|          - DDL, DML, DQL (INNER JOIN, LIKE, GROUP BY, COUNT)                  |
+-------------------------------------------------------------------------------+
```

---

## 1. 🐍 Python (Backend Server & Application Logic)

### Primary Files:
- [`app.py`](app.py) — Core application controllers, routing, security, and recommendation algorithm.
- [`config.py`](config.py) — Centralized configuration variables (database credentials, secret keys, port).
- [`init_db.py`](init_db.py) — Automated database initialization and table creation script.
- [`check_tables.py`](check_tables.py) — Command-line utility to inspect live database records.

### Exact Role in This Project:
1. **HTTP Web Server (Flask Framework):**
   - Intercepts incoming web requests from the user's browser.
   - Maps URL endpoints to Python functions using `@app.route()` decorators (e.g., `@app.route('/report-lost')`, `@app.route('/search')`).
   - Reads form submission payloads via `request.form` and URL parameters via `request.args`.

2. **Database Driver & Query Management (`mysql.connector`):**
   - Initializes a high-performance **Connection Pool** (`MySQLConnectionPool`, pool size = 5) at startup to avoid TCP handshake overhead on every page load.
   - Centralizes all SQL execution inside the `execute_query()` function.
   - Converts raw MySQL row tuples into clean Python dictionaries (`cursor(dictionary=True)`).
   - Manages database transactions: executes `conn.commit()` on successful insertions/updates, and executes `conn.rollback()` in `except` blocks if an error occurs.

3. **Intelligent Heuristic Matching Algorithm:**
   - Implemented entirely in Python functions `calculate_similarity_score()` and `find_matches_for_item()`.
   - Tokenizes strings, removes English stop words (`a`, `the`, `my`, `in`, `for`), computes word set intersection ratios, and calculates an explainable 100-point compatibility score across title, category, color, and location.

4. **Cybersecurity & Cryptography:**
   - **Password Protection:** Uses `werkzeug.security.generate_password_hash()` to encrypt student passwords with the **scrypt** cryptographic hashing algorithm and automatic unique salts. Plaintext passwords are never saved in storage.
   - **Authentication Check:** Uses `check_password_hash()` during login.
   - **Route Guards (Decorators):** Custom decorators `@login_required` and `@admin_required` inspect active session cookies before allowing access to sensitive student or admin pages.
   - **Session Integrity:** Cryptographically signs client session cookies using HMAC SHA-256 with `Config.SECRET_KEY`.

---

## 2. 🗄️ SQL — Structured Query Language (Database Layer)

### Primary Files:
- [`database.sql`](database.sql) — Complete DDL schema creation, constraints, sample seed data, and demo queries.
- Inside [`app.py`](app.py) — Embedded parameterized SQL queries executed via `mysql.connector`.

### Exact Role in This Project:
1. **DDL (Data Definition Language) — Schema & Integrity:**
   - Creates normalized relational tables: `users`, `items`, `claims`, and `login_credentials`.
   - **Primary Keys:** `user_id`, `item_id`, `claim_id` ensure every single record has a unique physical identity.
   - **Foreign Keys & Referential Integrity:**
     - `items.reported_by REFERENCES users(user_id)`
     - `claims.item_id REFERENCES items(item_id)`
     - `claims.user_id REFERENCES users(user_id)`
   - **Cascade Deletions (`ON DELETE CASCADE`):** If an item or user is deleted, all related claims and reports are automatically removed by MySQL, preventing dangling orphan records.
   - **Constraints:** `UNIQUE` (prevents duplicate student IDs and emails), `NOT NULL`, and `DEFAULT CURRENT_TIMESTAMP`.

2. **DML (Data Manipulation Language) — Transaction Operations:**
   - `INSERT`: Adds newly registered students, lost/found reports, and claims.
   - `UPDATE`: Changes item status from `PENDING` to `OPEN`, `CLAIMED`, or `RETURNED`.
   - `DELETE`: Removes found items or rejected claims from the system.

3. **DQL (Data Query Language) — Advanced CBSE 083 Concepts:**
   - **Relational Joins (`INNER JOIN`):**
     Combines multiple tables in a single query so the frontend can display the reporter's full name and student ID alongside the item details:
     ```sql
     SELECT i.*, u.name AS reporter_name, u.student_id AS reporter_student_id
     FROM items i
     JOIN users u ON i.reported_by = u.user_id
     WHERE i.status = 'OPEN';
     ```
   - **Pattern Matching (`LIKE`):**
     Powers multi-field keyword searching across item names, descriptions, and locations:
     ```sql
     WHERE item_name LIKE %s OR description LIKE %s OR location LIKE %s
     ```
   - **SQL Aggregations (`COUNT()`, `GROUP BY`):**
     Calculates analytics and dashboard counters (`total_items`, `returned_items`, `active_students`).
   - **SQL Injection Immunization:**
     Every single query uses `%s` placeholders. Values are sent separately from the SQL statement, forcing the database engine to treat inputs strictly as literal values rather than executable code.

---

## 3. 🌐 HTML5 (Structure & Templating)

### Primary Files:
- [`templates/base.html`](templates/base.html) — Master template containing the global navigation bar, flash alert containers, and footer.
- [`templates/index.html`](templates/index.html) — Public landing portal and statistics grid.
- [`templates/dashboard.html`](templates/dashboard.html) — Student dashboard overview and matching suggestions.
- [`templates/search.html`](templates/search.html) — Search filter controls and catalog cards.
- [`templates/item_details.html`](templates/item_details.html) — Full item detail view, claim forms, and found removal button.
- [`templates/admin_items.html`](templates/admin_items.html), [`templates/admin_claims.html`](templates/admin_claims.html), [`templates/admin_users.html`](templates/admin_users.html) — Administrative moderation interfaces.

### Exact Role in This Project:
1. **Page Structure & Semantics:**
   - Uses semantic HTML5 tags (`<nav>`, `<header>`, `<main>`, `<section>`, `<table>`, `<footer>`) instead of unorganized `<div>` tags.
   - Defines accessible forms with modern validation attributes: `required`, `type="email"`, `type="date"`, `maxlength`.

2. **Jinja2 Dynamic Templating (Python-to-HTML Integration):**
   - **Template Inheritance (`{% extends "base.html" %}`, `{% block content %}`):** Eliminates code duplication across pages.
   - **Dynamic Conditionals (`{% if %}` / `{% elif %}` / `{% endif %}`):**
     Controls what the user sees based on login status and role (e.g., normal students see "Submit Claim", admins see "Approve Claim", guests see "Log In").
   - **Dynamic Iterations (`{% for item in items %}`):** Automatically iterates over query result dictionaries and generates responsive cards and table rows.
   - **Safe Value Interpolation (`{{ item.item_name }}`):** Automatically escapes output to defend against Cross-Site Scripting (XSS).

---

## 4. 🎨 CSS3 (Visual Design, Layouts & Themes)

### Primary Files:
- [`static/css/style.css`](static/css/style.css) — Custom modern design system.

### Exact Role in This Project:
1. **Modern Dark Theme & Design Tokens:**
   - Defines central CSS custom properties (`:root`) for colors, radii, shadows, and fonts:
     - Dark slate background (`--bg-primary: #0b0f19`)
     - Elevated card backgrounds (`--card-bg: rgba(17, 24, 39, 0.85)`)
     - High-visibility accent cyan (`--accent-cyan: #00b4d8`)
     - Soft border highlights (`--border-glass: rgba(255, 255, 255, 0.08)`)

2. **Glassmorphism & Visual Polish:**
   - Employs `backdrop-filter: blur(12px)` and layered translucent borders to create an elevated glass UI aesthetic.
   - Status color coding:
     - Lost / Rejected: Red / Rose badges
     - Found / Approved: Emerald green badges
     - Pending: Amber / Orange badges
     - Claimed: Purple badges

3. **Layout Engines (Flexbox & CSS Grid):**
   - **CSS Grid (`grid-template-columns: repeat(auto-fill, minmax(300px, 1fr))`):** Auto-arranges item catalog cards cleanly across any screen size.
   - **Flexbox (`display: flex; align-items: center; justify-content: space-between`):** Used in navigation menus, button toolbars, and metadata badge rows.

4. **Responsive Media Queries (`@media`):**
   - Optimizes layout for tablets and smartphones below 768px, wrapping tables in horizontal scroll containers and stacking navigation bars vertically.

---

## 5. ⚡ JavaScript (Client-Side Interactivity)

### Primary Files:
- [`static/js/main.js`](static/js/main.js) — Client-side interaction logic.

### Exact Role in This Project:
1. **Instant Client-Side Table Filtering:**
   - Intercepts input events on `#liveTableSearch` fields in real time.
   - Uses `String.toLowerCase()` and `element.textContent` to filter through table rows on the fly, instantly hiding rows that don't match without contacting the backend server.

2. **Accidental Click Protection (Modal Confirmations):**
   - Listens for button clicks with `data-confirm` attributes (such as "Delete Item", "Reject Claim", or "Found (Remove)").
   - Prompts the user with a confirmation dialog before allowing destructive HTTP POST requests to proceed.

3. **1-Click Demo Credential Auto-Fill:**
   - On the `/login` page, clicking "Admin Demo Login" or "Student Demo Login" uses JavaScript to automatically populate the email and password fields. This enables swift demonstrations during practical exams.

4. **Flash Notification Auto-Dismissal:**
   - Automatically detects temporary server flash messages and applies a smooth fade-out animation after 5 seconds.

---

## Language Comparison Summary Table

| Language | Execution Location | Primary Function | Example in Project |
|---|---|---|---|
| **Python** | Server (Backend) | Routing, database connection pooling, algorithm math, authentication | Computes 40-pt name match in `calculate_similarity_score()` |
| **SQL** | Database (MySQL) | Schema definition, relational joins, indexing, data persistence | `INNER JOIN users ON items.reported_by = users.user_id` |
| **HTML5** | Client (Browser) | Webpage layout, form fields, Jinja2 conditional templates | `<form method="POST" action="/report-lost">` |
| **CSS3** | Client (Browser) | Dark theme styling, glassmorphism, flex/grid layouts | `.card { backdrop-filter: blur(12px); }` |
| **JavaScript** | Client (Browser) | Instant table search, action confirmation dialogs, demo auto-fill | Live search filtering on `keyup` event without page reload |
