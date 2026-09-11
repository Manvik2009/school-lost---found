"""
=============================================================================
CBSE Class 12 Computer Science (083) Project
Project Title: School Lost & Found Management System
Backend: Python 3 & Flask Web Framework
Database: MySQL with mysql.connector (with transparent fallback)
=============================================================================
"""

import os
import re
import sqlite3
import mysql.connector
from datetime import datetime, date
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, abort, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from init_db import init_sqlite_db

# Initialize Flask application
app = Flask(__name__)
app.config.from_object(Config)

# ---------------------------------------------------------------------------
# Database Connectivity & Management (CBSE CS 083 Concepts)
# Demonstrates: MySQL Connection, Cursor, Execute, Commit, Fetch, and Exception Handling
# Includes zero-configuration SQLite cloud fallback for Render & Firebase hosting
# ---------------------------------------------------------------------------

ACTIVE_DB_TYPE = None  # 'mysql' or 'sqlite'
DB_ENGINE = "MySQL 8.0"

def get_db_connection():
    """
    Establishes and returns a database connection.
    - Default/CBSE Mode: MySQL 8.0 using mysql.connector
    - Cloud/Offline Mode: Seamlessly falls back to SQLite if MySQL is offline or in cloud deployment.
    """
    global ACTIVE_DB_TYPE, DB_ENGINE

    # Explicit SQLite mode
    if Config.DB_MODE == 'sqlite':
        ACTIVE_DB_TYPE = 'sqlite'
        DB_ENGINE = "SQLite 3 (Cloud Fallback)"
        if not os.path.exists(Config.SQLITE_PATH):
            init_sqlite_db(Config.SQLITE_PATH)
        conn = sqlite3.connect(Config.SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    # Explicit MySQL mode or already determined MySQL
    if Config.DB_MODE == 'mysql' or (Config.DB_MODE == 'auto' and ACTIVE_DB_TYPE == 'mysql'):
        try:
            conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB,
                port=Config.MYSQL_PORT,
                connection_timeout=3
            )
            ACTIVE_DB_TYPE = 'mysql'
            DB_ENGINE = "MySQL 8.0"
            return conn
        except Exception as e:
            if Config.DB_MODE == 'mysql':
                raise e
            # auto fallback:
            ACTIVE_DB_TYPE = 'sqlite'
            DB_ENGINE = "SQLite 3 (Cloud Fallback)"

    # Auto mode first probe
    if Config.DB_MODE == 'auto':
        try:
            conn = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DB,
                port=Config.MYSQL_PORT,
                connection_timeout=2
            )
            ACTIVE_DB_TYPE = 'mysql'
            DB_ENGINE = "MySQL 8.0"
            return conn
        except Exception:
            ACTIVE_DB_TYPE = 'sqlite'
            DB_ENGINE = "SQLite 3 (Cloud Fallback)"

    # SQLite fallback
    if not os.path.exists(Config.SQLITE_PATH):
        init_sqlite_db(Config.SQLITE_PATH)
    conn = sqlite3.connect(Config.SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=(), commit=False, fetchone=False, fetchall=False):
    """
    Executes a SQL query on MySQL or SQLite, with parameter mapping (%s -> ? for SQLite).
    Returns Python dictionaries for seamless template compatibility.
    """
    conn = get_db_connection()
    result = None
    try:
        is_sqlite = (ACTIVE_DB_TYPE == 'sqlite')
        if is_sqlite:
            # Adapt parameterized query placeholder from %s to ?
            sql = query.replace('%s', '?')
            cursor = conn.cursor()
            cursor.execute(sql, params)
            if commit:
                conn.commit()
                result = cursor.lastrowid
            elif fetchone:
                row = cursor.fetchone()
                result = dict(row) if row is not None else None
            elif fetchall:
                rows = cursor.fetchall()
                result = [dict(r) for r in rows] if rows else []
            cursor.close()
        else:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)
            if commit:
                conn.commit()
                result = cursor.lastrowid
            elif fetchone:
                result = cursor.fetchone()
            elif fetchall:
                result = cursor.fetchall()
            cursor.close()
    except Exception as e:
        print("Database Error [{}]:".format(ACTIVE_DB_TYPE or 'DB'), e)
        if commit and conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise e
    finally:
        if conn:
            conn.close()

    return result

# ---------------------------------------------------------------------------
# Authentication & Role-Based Access Control Decorators
# ---------------------------------------------------------------------------

def login_required(f):
    """Decorator to protect routes requiring logged-in users."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to protect administrative routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in as an administrator.", "warning")
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash("Access denied: Administrative privileges required.", "danger")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------------------------
# Lost <-> Found Matching Algorithm (Explainable Pure Python)
# Scoring Weights:
# 1. Item Name Similarity = up to 40 pts
# 2. Category Match       = 25 pts
# 3. Color Match          = 20 pts
# 4. Location Match       = 15 pts
# Total Maximum           = 100 pts
# ---------------------------------------------------------------------------

def calculate_similarity_score(lost_item, found_item):
    """
    Computes a match score (0-100) between a LOST item and a FOUND item.
    Returns (total_score, breakdown_dict).
    """
    breakdown = {
        'name_score': 0,
        'category_score': 0,
        'color_score': 0,
        'location_score': 0,
        'reasons': []
    }

    # 1. Name Similarity (up to 40 points)
    # Tokenize words, strip punctuation, compare word overlap
    name1 = re.sub(r'[^\w\s]', '', str(lost_item.get('item_name', '')).lower())
    name2 = re.sub(r'[^\w\s]', '', str(found_item.get('item_name', '')).lower())
    words1 = set(name1.split())
    words2 = set(name2.split())

    # Filter out common stop words
    stop_words = {'a', 'an', 'the', 'my', 'in', 'at', 'of', 'for', 'with', 'and', 'or'}
    words1 = {w for w in words1 if w not in stop_words and len(w) > 1}
    words2 = {w for w in words2 if w not in stop_words and len(w) > 1}

    common_words = words1.intersection(words2)
    if words1 and words2:
        overlap_ratio = len(common_words) / max(len(words1), len(words2))
        breakdown['name_score'] = round(overlap_ratio * 40)
        if common_words:
            breakdown['reasons'].append("Keywords match: {}".format(", ".join(common_words)))
    elif name1 == name2 and name1:
        breakdown['name_score'] = 40
        breakdown['reasons'].append("Exact item name match")

    # If one name contains the other as substring (e.g. 'calculator' in 'scientific calculator')
    if (name1 in name2 or name2 in name1) and len(name1) > 3 and len(name2) > 3:
        breakdown['name_score'] = max(breakdown['name_score'], 32)
        if "Keywords match" not in str(breakdown['reasons']):
            breakdown['reasons'].append("Item name substring match")

    # 2. Category Match (25 points)
    cat1 = str(lost_item.get('category', '')).strip().lower()
    cat2 = str(found_item.get('category', '')).strip().lower()
    if cat1 and cat2 and cat1 == cat2:
        breakdown['category_score'] = 25
        breakdown['reasons'].append("Category match ({})".format(lost_item.get('category')))

    # 3. Color Match (20 points)
    col1 = str(lost_item.get('color', '')).strip().lower()
    col2 = str(found_item.get('color', '')).strip().lower()
    if col1 and col2 and col1 != 'other' and col2 != 'other':
        if col1 == col2:
            breakdown['color_score'] = 20
            breakdown['reasons'].append("Identical color ({})".format(lost_item.get('color')))
        elif col1 in col2 or col2 in col1:
            breakdown['color_score'] = 14
            breakdown['reasons'].append("Color shade match ({})".format(col1))

    # 4. Location Match (15 points)
    loc1 = re.sub(r'[^\w\s]', '', str(lost_item.get('location', '')).lower())
    loc2 = re.sub(r'[^\w\s]', '', str(found_item.get('location', '')).lower())
    loc_words1 = {w for w in loc1.split() if w not in stop_words and len(w) > 2}
    loc_words2 = {w for w in loc2.split() if w not in stop_words and len(w) > 2}
    common_loc = loc_words1.intersection(loc_words2)

    if loc1 == loc2 and loc1:
        breakdown['location_score'] = 15
        breakdown['reasons'].append("Exact location match ({})".format(lost_item.get('location')))
    elif common_loc:
        breakdown['location_score'] = min(15, 8 + (len(common_loc) * 3))
        breakdown['reasons'].append("Location proximity match ({})".format(", ".join(common_loc)))

    total_score = (
        breakdown['name_score'] +
        breakdown['category_score'] +
        breakdown['color_score'] +
        breakdown['location_score']
    )
    return min(total_score, 100), breakdown

def find_matches_for_item(target_item):
    """
    Finds possible matches for a given item:
    - If target_item is LOST, searches against OPEN FOUND items.
    - If target_item is FOUND, searches against OPEN LOST items.
    Returns list of matching item dictionaries sorted by highest match score.
    """
    opposite_type = 'FOUND' if target_item.get('item_type') == 'LOST' else 'LOST'
    query = """
    SELECT i.*, u.name as reporter_name
    FROM items i
    JOIN users u ON i.reported_by = u.user_id
    WHERE i.item_type = %s AND i.status = 'OPEN' AND i.item_id != %s
    ORDER BY i.date_reported DESC
    """
    candidates = execute_query(query, (opposite_type, target_item.get('item_id')), fetchall=True) or []
    matches = []

    for cand in candidates:
        if target_item.get('item_type') == 'LOST':
            score, breakdown = calculate_similarity_score(target_item, cand)
        else:
            score, breakdown = calculate_similarity_score(cand, target_item)

        if score >= 35:  # Minimum threshold for a relevant match recommendation
            cand_copy = dict(cand)
            cand_copy['match_score'] = score
            cand_copy['match_breakdown'] = breakdown
            matches.append(cand_copy)

    # Sort descending by match score
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches

# ---------------------------------------------------------------------------
# Statistics Helper (CBSE SQL Aggregations: COUNT, GROUP BY, WHERE)
# ---------------------------------------------------------------------------

def get_statistics():
    """Gathers school platform metrics via SQL aggregation queries."""
    stats = {}
    try:
        # Total items
        r = execute_query("SELECT COUNT(*) as total FROM items", fetchone=True)
        stats['total_items'] = r['total'] if r else 0

        # Items by type
        r = execute_query("SELECT COUNT(*) as count FROM items WHERE item_type = 'LOST'", fetchone=True)
        stats['lost_items'] = r['count'] if r else 0

        r = execute_query("SELECT COUNT(*) as count FROM items WHERE item_type = 'FOUND'", fetchone=True)
        stats['found_items'] = r['count'] if r else 0

        # Items returned to rightful owners
        r = execute_query("SELECT COUNT(*) as count FROM items WHERE status = 'RETURNED'", fetchone=True)
        stats['returned_items'] = r['count'] if r else 0

        # Open items currently active
        r = execute_query("SELECT COUNT(*) as count FROM items WHERE status = 'OPEN'", fetchone=True)
        stats['open_items'] = r['count'] if r else 0

        # Pending reports awaiting admin approval
        r = execute_query("SELECT COUNT(*) as count FROM items WHERE status = 'PENDING'", fetchone=True)
        stats['pending_reports'] = r['count'] if r else 0

        # Pending claims awaiting admin review
        r = execute_query("SELECT COUNT(*) as count FROM claims WHERE status = 'PENDING'", fetchone=True)
        stats['pending_claims'] = r['count'] if r else 0

        # Total registered users
        r = execute_query("SELECT COUNT(*) as count FROM users WHERE role = 'student'", fetchone=True)
        stats['active_students'] = r['count'] if r else 0

        r = execute_query("SELECT COUNT(*) as count FROM users", fetchone=True)
        stats['total_users'] = r['count'] if r else 0

    except Exception as e:
        print("Error calculating statistics:", e)
        stats = {
            'total_items': 0, 'lost_items': 0, 'found_items': 0,
            'returned_items': 0, 'open_items': 0, 'pending_reports': 0,
            'pending_claims': 0, 'active_students': 0, 'total_users': 0
        }
    return stats

# Context processor to inject database engine status & app info to all templates
@app.context_processor
def inject_global_vars():
    return {
        'app_name': Config.APP_NAME,
        'current_year': datetime.now().year,
        'db_engine': DB_ENGINE
    }

# ---------------------------------------------------------------------------
# Public / Landing Page Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    """Homepage with hero section, process workflow, platform metrics, and recent open items."""
    stats = get_statistics()
    # Fetch top 6 recent open items
    recent_items = execute_query("""
        SELECT i.*, u.name as reporter_name
        FROM items i
        JOIN users u ON i.reported_by = u.user_id
        WHERE i.status = 'OPEN'
        ORDER BY i.date_reported DESC
        LIMIT 6
    """, fetchall=True) or []

    return render_template('index.html', stats=stats, recent_items=recent_items)

# ---------------------------------------------------------------------------
# Authentication Routes (Register, Login, Logout)
# ---------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User account registration with strict validation."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        student_id = request.form.get('student_id', '').strip().upper()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validations
        if not name or not student_id or not email or not password:
            flash("All fields are required.", "danger")
            return render_template('register.html', form=request.form)

        # Basic email format check
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            flash("Please provide a valid email address.", "danger")
            return render_template('register.html', form=request.form)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return render_template('register.html', form=request.form)

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html', form=request.form)

        # Check unique email
        existing_email = execute_query("SELECT user_id FROM users WHERE email = %s", (email,), fetchone=True)
        if existing_email:
            flash("An account with this email address already exists.", "danger")
            return render_template('register.html', form=request.form)

        # Check unique student ID
        existing_id = execute_query("SELECT user_id FROM users WHERE student_id = %s", (student_id,), fetchone=True)
        if existing_id:
            flash("An account with this Student ID already exists.", "danger")
            return render_template('register.html', form=request.form)

        # Hash password securely
        hashed_password = generate_password_hash(password)

        try:
            execute_query("""
                INSERT INTO users (name, student_id, email, password, role)
                VALUES (%s, %s, %s, %s, 'student')
            """, (name, student_id, email, hashed_password), commit=True)
            flash("Registration successful! You can now log in with your credentials.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash("Registration failed due to a database error. Please try again.", "danger")
            print("Registration Error:", e)

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login with Werkzeug password hash verification and session creation."""
    if 'user_id' in session:
        return redirect(url_for('admin_dashboard' if session.get('role') == 'admin' else 'dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('login.html', email=email)

        user = execute_query("SELECT * FROM users WHERE email = %s", (email,), fetchone=True)

        if user and check_password_hash(user['password'], password):
            # Set Flask session
            session['user_id'] = user['user_id']
            session['name'] = user['name']
            session['email'] = user['email']
            session['student_id'] = user['student_id']
            session['role'] = user['role']

            flash("Welcome back, {}!".format(user['name']), "success")
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password. Please try again.", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logs out user and clears Flask session."""
    session.clear()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for('login'))

# ---------------------------------------------------------------------------
# Student Dashboard & Features
# ---------------------------------------------------------------------------

@app.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard overview with personal counts, recent items, and potential matches."""
    user_id = session['user_id']

    # Personal statistics
    my_lost = execute_query("SELECT COUNT(*) as count FROM items WHERE reported_by = %s AND item_type = 'LOST'", (user_id,), fetchone=True)['count']
    my_found = execute_query("SELECT COUNT(*) as count FROM items WHERE reported_by = %s AND item_type = 'FOUND'", (user_id,), fetchone=True)['count']
    my_claims = execute_query("SELECT COUNT(*) as count FROM claims WHERE user_id = %s", (user_id,), fetchone=True)['count']
    my_returned = execute_query("SELECT COUNT(*) as count FROM items WHERE reported_by = %s AND status = 'RETURNED'", (user_id,), fetchone=True)['count']

    # User's recent reports
    my_recent_reports = execute_query("""
        SELECT * FROM items
        WHERE reported_by = %s
        ORDER BY created_at DESC
        LIMIT 5
    """, (user_id,), fetchall=True) or []

    # Potential matches for this student's LOST items
    my_lost_items = execute_query("""
        SELECT * FROM items
        WHERE reported_by = %s AND item_type = 'LOST' AND status IN ('PENDING', 'OPEN')
    """, (user_id,), fetchall=True) or []

    suggestions = []
    for lost_item in my_lost_items:
        matches = find_matches_for_item(lost_item)
        if matches:
            suggestions.append({
                'lost_item': lost_item,
                'best_match': matches[0],
                'all_matches': matches[:3]
            })

    return render_template('dashboard.html',
        my_lost=my_lost,
        my_found=my_found,
        my_claims=my_claims,
        my_returned=my_returned,
        my_recent_reports=my_recent_reports,
        suggestions=suggestions
    )

@app.route('/report-lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    """Student submits a report for a lost item."""
    categories = [
        'Electronics', 'Stationery', 'Clothing', 'Accessories',
        'Books', 'Water Bottle', 'ID Card', 'Other'
    ]

    if request.method == 'POST':
        item_name = request.form.get('item_name', '').strip()
        category = request.form.get('category', '').strip()
        color = request.form.get('color', '').strip()
        location = request.form.get('location', '').strip()
        date_reported = request.form.get('date_reported', '')
        description = request.form.get('description', '').strip()

        if not item_name or not category or not location or not date_reported:
            flash("Please fill in all mandatory fields.", "danger")
            return render_template('report_lost.html', categories=categories, form=request.form)

        try:
            item_id = execute_query("""
                INSERT INTO items (item_name, category, description, color, location, date_reported, item_type, status, reported_by)
                VALUES (%s, %s, %s, %s, %s, %s, 'LOST', 'PENDING', %s)
            """, (item_name, category, description, color, location, date_reported, session['user_id']), commit=True)

            flash("Your lost item report has been submitted! It is currently PENDING review by school staff.", "success")
            return redirect(url_for('item_details', item_id=item_id))
        except Exception as e:
            flash("Failed to submit report. Please try again.", "danger")
            print("Report Lost Error:", e)

    today = date.today().isoformat()
    return render_template('report_lost.html', categories=categories, today=today)

@app.route('/report-found', methods=['GET', 'POST'])
@login_required
def report_found():
    """Student submits a report for a found item."""
    categories = [
        'Electronics', 'Stationery', 'Clothing', 'Accessories',
        'Books', 'Water Bottle', 'ID Card', 'Other'
    ]

    if request.method == 'POST':
        item_name = request.form.get('item_name', '').strip()
        category = request.form.get('category', '').strip()
        color = request.form.get('color', '').strip()
        location = request.form.get('location', '').strip()
        date_reported = request.form.get('date_reported', '')
        description = request.form.get('description', '').strip()

        if not item_name or not category or not location or not date_reported:
            flash("Please fill in all mandatory fields.", "danger")
            return render_template('report_found.html', categories=categories, form=request.form)

        try:
            item_id = execute_query("""
                INSERT INTO items (item_name, category, description, color, location, date_reported, item_type, status, reported_by)
                VALUES (%s, %s, %s, %s, %s, %s, 'FOUND', 'PENDING', %s)
            """, (item_name, category, description, color, location, date_reported, session['user_id']), commit=True)

            flash("Thank you! Your found item report has been submitted for PENDING staff verification.", "success")
            return redirect(url_for('item_details', item_id=item_id))
        except Exception as e:
            flash("Failed to submit report. Please try again.", "danger")
            print("Report Found Error:", e)

    today = date.today().isoformat()
    return render_template('report_found.html', categories=categories, today=today)

@app.route('/search')
def search():
    """
    Search items with filters (keyword, category, color, location, item_type).
    Demonstrates parameterized SQL with LIKE, WHERE, and ORDER BY.
    """
    query_param = request.args.get('q', '').strip()
    category = request.args.get('category', '').strip()
    color = request.args.get('color', '').strip()
    location = request.args.get('location', '').strip()
    item_type = request.args.get('item_type', 'ALL').strip().upper()

    sql = """
        SELECT i.*, u.name as reporter_name
        FROM items i
        JOIN users u ON i.reported_by = u.user_id
        WHERE i.status = 'OPEN'
    """
    params = []

    if item_type in ('LOST', 'FOUND'):
        sql += " AND i.item_type = %s"
        params.append(item_type)

    if category and category != 'ALL':
        sql += " AND i.category = %s"
        params.append(category)

    if color:
        sql += " AND i.color LIKE %s"
        params.append("%{}%".format(color))

    if location:
        sql += " AND i.location LIKE %s"
        params.append("%{}%".format(location))

    if query_param:
        sql += " AND (i.item_name LIKE %s OR i.description LIKE %s OR i.location LIKE %s)"
        like_str = "%{}%".format(query_param)
        params.extend([like_str, like_str, like_str])

    sql += " ORDER BY i.date_reported DESC"

    results = execute_query(sql, tuple(params), fetchall=True) or []

    categories = [
        'Electronics', 'Stationery', 'Clothing', 'Accessories',
        'Books', 'Water Bottle', 'ID Card', 'Other'
    ]

    return render_template('search.html',
        items=results,
        query_param=query_param,
        category=category,
        color=color,
        location=location,
        item_type=item_type,
        categories=categories,
        total_results=len(results)
    )

@app.route('/item/<int:item_id>')
def item_details(item_id):
    """View complete details of an item and see computed matching items."""
    item = execute_query("""
        SELECT i.*, u.name as reporter_name, u.email as reporter_email, u.student_id as reporter_student_id
        FROM items i
        JOIN users u ON i.reported_by = u.user_id
        WHERE i.item_id = %s
    """, (item_id,), fetchone=True)

    if not item:
        abort(404)

    # Permission check: normal students can only view OPEN/RETURNED/CLAIMED items,
    # OR their own items if PENDING/REJECTED. Admins can view any item.
    is_owner = ('user_id' in session and session['user_id'] == item['reported_by'])
    is_admin = (session.get('role') == 'admin')

    if item['status'] in ('PENDING', 'REJECTED') and not (is_owner or is_admin):
        flash("This item report is pending approval or has been archived.", "warning")
        return redirect(url_for('search'))

    # Check if logged-in user already filed a claim on this item
    user_has_claimed = False
    existing_claim = None
    if 'user_id' in session:
        existing_claim = execute_query("""
            SELECT * FROM claims WHERE item_id = %s AND user_id = %s
        """, (item_id, session['user_id']), fetchone=True)
        if existing_claim:
            user_has_claimed = True

    # Find possible matches using the explainable scoring algorithm
    matches = find_matches_for_item(item)

    return render_template('item_details.html',
        item=item,
        is_owner=is_owner,
        is_admin=is_admin,
        user_has_claimed=user_has_claimed,
        existing_claim=existing_claim,
        matches=matches
    )

@app.route('/claim/<int:item_id>', methods=['GET', 'POST'])
@login_required
def claim_item(item_id):
    """Students submit a claim for an OPEN FOUND item."""
    item = execute_query("SELECT * FROM items WHERE item_id = %s", (item_id,), fetchone=True)
    if not item:
        abort(404)

    # Validations
    if item['item_type'] != 'FOUND':
        flash("Claims can only be filed for FOUND items.", "warning")
        return redirect(url_for('item_details', item_id=item_id))

    if item['status'] != 'OPEN':
        flash("This item is not open for claims (Current status: {}).".format(item['status']), "warning")
        return redirect(url_for('item_details', item_id=item_id))

    if item['reported_by'] == session['user_id']:
        flash("You cannot claim an item you reported yourself.", "warning")
        return redirect(url_for('item_details', item_id=item_id))

    # Duplicate claim check
    existing = execute_query("""
        SELECT claim_id FROM claims WHERE item_id = %s AND user_id = %s AND status IN ('PENDING', 'APPROVED')
    """, (item_id, session['user_id']), fetchone=True)
    if existing:
        flash("You already have an active claim submitted for this item.", "info")
        return redirect(url_for('item_details', item_id=item_id))

    if request.method == 'POST':
        reason = request.form.get('reason', '').strip()
        lost_location = request.form.get('lost_location', '').strip()
        additional_info = request.form.get('additional_info', '').strip()

        if not reason or not lost_location:
            flash("Please answer all required questions in the claim form.", "danger")
            return render_template('item_details.html', item=item)

        try:
            execute_query("""
                INSERT INTO claims (item_id, user_id, reason, lost_location, additional_info, status)
                VALUES (%s, %s, %s, %s, %s, 'PENDING')
            """, (item_id, session['user_id'], reason, lost_location, additional_info), commit=True)

            flash("Claim submitted successfully! School administration will review your claim details.", "success")
            return redirect(url_for('my_claims'))
        except Exception as e:
            flash("Failed to submit claim. Please try again.", "danger")
            print("Claim Error:", e)

    return redirect(url_for('item_details', item_id=item_id))

@app.route('/my-reports')
@login_required
def my_reports():
    """View all reports created by the currently logged-in user."""
    status_filter = request.args.get('status', 'ALL').upper()

    sql = "SELECT * FROM items WHERE reported_by = %s"
    params = [session['user_id']]

    if status_filter in ('PENDING', 'OPEN', 'CLAIMED', 'RETURNED', 'REJECTED'):
        sql += " AND status = %s"
        params.append(status_filter)

    sql += " ORDER BY created_at DESC"
    reports = execute_query(sql, tuple(params), fetchall=True) or []

    return render_template('my_reports.html', reports=reports, current_filter=status_filter)

@app.route('/my-claims')
@login_required
def my_claims():
    """View all claims submitted by the currently logged-in student."""
    claims = execute_query("""
        SELECT c.*, i.item_name, i.category, i.color, i.location as found_location, i.status as item_status
        FROM claims c
        JOIN items i ON c.item_id = i.item_id
        WHERE c.user_id = %s
        ORDER BY c.created_at DESC
    """, (session['user_id'],), fetchall=True) or []

    return render_template('my_claims.html', claims=claims)

@app.route('/profile')
@login_required
def profile():
    """Display student user profile and activity statistics."""
    user = execute_query("SELECT * FROM users WHERE user_id = %s", (session['user_id'],), fetchone=True)
    if not user:
        abort(404)

    # Activity stats
    stats = {
        'reports_count': execute_query("SELECT COUNT(*) as c FROM items WHERE reported_by = %s", (session['user_id'],), fetchone=True)['c'],
        'claims_count': execute_query("SELECT COUNT(*) as c FROM claims WHERE user_id = %s", (session['user_id'],), fetchone=True)['c'],
        'returned_count': execute_query("SELECT COUNT(*) as c FROM items WHERE reported_by = %s AND status = 'RETURNED'", (session['user_id'],), fetchone=True)['c']
    }

    return render_template('profile.html', user=user, stats=stats)

# ---------------------------------------------------------------------------
# Administrative Routes (Dashboard, Items, Claims, Users Moderation)
# ---------------------------------------------------------------------------

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    """Comprehensive school administrative analytics dashboard."""
    stats = get_statistics()

    # Pending items requiring review
    pending_items = execute_query("""
        SELECT i.*, u.name as reporter_name
        FROM items i
        JOIN users u ON i.reported_by = u.user_id
        WHERE i.status = 'PENDING'
        ORDER BY i.created_at ASC
        LIMIT 5
    """, fetchall=True) or []

    # Pending claims requiring review
    pending_claims = execute_query("""
        SELECT c.*, i.item_name, u.name as claimant_name
        FROM claims c
        JOIN items i ON c.item_id = i.item_id
        JOIN users u ON c.user_id = u.user_id
        WHERE c.status = 'PENDING'
        ORDER BY c.created_at ASC
        LIMIT 5
    """, fetchall=True) or []

    return render_template('admin_dashboard.html',
        stats=stats,
        pending_items=pending_items,
        pending_claims=pending_claims
    )

@app.route('/admin/items')
@admin_required
def admin_items():
    """Admin item moderation management table with filtering and actions."""
    status_filter = request.args.get('status', 'ALL').upper()
    type_filter = request.args.get('type', 'ALL').upper()

    sql = """
        SELECT i.*, u.name as reporter_name, u.email as reporter_email, u.student_id as reporter_student_id
        FROM items i
        JOIN users u ON i.reported_by = u.user_id
        WHERE 1=1
    """
    params = []

    if status_filter in ('PENDING', 'OPEN', 'CLAIMED', 'RETURNED', 'REJECTED'):
        sql += " AND i.status = %s"
        params.append(status_filter)

    if type_filter in ('LOST', 'FOUND'):
        sql += " AND i.item_type = %s"
        params.append(type_filter)

    sql += " ORDER BY i.created_at DESC"
    items = execute_query(sql, tuple(params), fetchall=True) or []

    return render_template('admin_items.html',
        items=items,
        status_filter=status_filter,
        type_filter=type_filter
    )

@app.route('/admin/item/<int:item_id>/approve', methods=['POST'])
@admin_required
def admin_approve_item(item_id):
    """Approve a PENDING item report so it becomes OPEN to the school."""
    execute_query("UPDATE items SET status = 'OPEN' WHERE item_id = %s", (item_id,), commit=True)
    flash("Item #{} approved and is now OPEN on the school board.".format(item_id), "success")
    return redirect(request.referrer or url_for('admin_items'))

@app.route('/admin/item/<int:item_id>/reject', methods=['POST'])
@admin_required
def admin_reject_item(item_id):
    """Reject an inappropriate or duplicate item report."""
    execute_query("UPDATE items SET status = 'REJECTED' WHERE item_id = %s", (item_id,), commit=True)
    flash("Item #{} marked as REJECTED.".format(item_id), "warning")
    return redirect(request.referrer or url_for('admin_items'))

@app.route('/admin/item/<int:item_id>/return', methods=['POST'])
@admin_required
def admin_mark_returned(item_id):
    """Mark an item as successfully RETURNED to its owner."""
    execute_query("UPDATE items SET status = 'RETURNED' WHERE item_id = %s", (item_id,), commit=True)
    flash("Item #{} marked as RETURNED to owner.".format(item_id), "success")
    return redirect(request.referrer or url_for('admin_items'))

@app.route('/admin/item/<int:item_id>/delete', methods=['POST'])
@admin_required
def admin_delete_item(item_id):
    """Permanently delete an item report."""
    execute_query("DELETE FROM items WHERE item_id = %s", (item_id,), commit=True)
    flash("Item #{} permanently deleted.".format(item_id), "info")
    return redirect(request.referrer or url_for('admin_items'))

@app.route('/admin/claims')
@admin_required
def admin_claims():
    """Admin claims review queue."""
    status_filter = request.args.get('status', 'ALL').upper()

    sql = """
        SELECT c.*, i.item_name, i.category, i.location as found_location, i.status as item_status,
               u.name as claimant_name, u.email as claimant_email, u.student_id as claimant_student_id
        FROM claims c
        JOIN items i ON c.item_id = i.item_id
        JOIN users u ON c.user_id = u.user_id
        WHERE 1=1
    """
    params = []

    if status_filter in ('PENDING', 'APPROVED', 'REJECTED'):
        sql += " AND c.status = %s"
        params.append(status_filter)

    sql += " ORDER BY c.created_at DESC"
    claims = execute_query(sql, tuple(params), fetchall=True) or []

    return render_template('admin_claims.html', claims=claims, status_filter=status_filter)

@app.route('/admin/claim/<int:claim_id>/approve', methods=['POST'])
@admin_required
def admin_approve_claim(claim_id):
    """Approve claim and update item status to CLAIMED."""
    claim = execute_query("SELECT * FROM claims WHERE claim_id = %s", (claim_id,), fetchone=True)
    if not claim:
        abort(404)

    # Approve claim
    execute_query("UPDATE claims SET status = 'APPROVED' WHERE claim_id = %s", (claim_id,), commit=True)
    # Update item status to CLAIMED
    execute_query("UPDATE items SET status = 'CLAIMED' WHERE item_id = %s", (claim['item_id'],), commit=True)

    flash("Claim #{} APPROVED. Item marked as CLAIMED.".format(claim_id), "success")
    return redirect(request.referrer or url_for('admin_claims'))

@app.route('/admin/claim/<int:claim_id>/reject', methods=['POST'])
@admin_required
def admin_reject_claim(claim_id):
    """Reject claim."""
    execute_query("UPDATE claims SET status = 'REJECTED' WHERE claim_id = %s", (claim_id,), commit=True)
    flash("Claim #{} REJECTED.".format(claim_id), "warning")
    return redirect(request.referrer or url_for('admin_claims'))

@app.route('/admin/users')
@admin_required
def admin_users():
    """User directory management table."""
    users = execute_query("""
        SELECT u.*,
               (SELECT COUNT(*) FROM items WHERE reported_by = u.user_id) as total_reports,
               (SELECT COUNT(*) FROM claims WHERE user_id = u.user_id) as total_claims
        FROM users u
        ORDER BY u.created_at DESC
    """, fetchall=True) or []

    return render_template('admin_users.html', users=users)

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    """Delete a user account. Prevents self-deletion."""
    if user_id == session['user_id']:
        flash("You cannot delete your own administrative account.", "danger")
        return redirect(url_for('admin_users'))

    execute_query("DELETE FROM users WHERE user_id = %s", (user_id,), commit=True)
    flash("User account #{} successfully removed.".format(user_id), "info")
    return redirect(url_for('admin_users'))

@app.context_processor
def inject_global_vars():
    """Inject dynamic variables into all Jinja2 templates."""
    return {
        'db_engine': DB_ENGINE,
        'app_name': Config.APP_NAME
    }

# ---------------------------------------------------------------------------
# Error Handling (Custom CBSE 404 & 500 Pages)
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 Page."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Custom 500 Page."""
    return render_template('500.html'), 500

# ---------------------------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1')
    print("=" * 60)
    print(" Starting School Lost & Found Platform (CBSE CS 083)")
    print(" Default Admin: {} | Password: {}".format(Config.ADMIN_EMAIL, Config.ADMIN_DEFAULT_PASSWORD))
    print(" Listening on: http://{}:{} (Debug: {})".format(Config.HOST, Config.PORT, debug_mode))
    print("=" * 60)
    app.run(debug=debug_mode, host=Config.HOST, port=Config.PORT)
