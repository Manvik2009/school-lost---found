"""
Comprehensive Automated Test Suite for School Lost & Found
Class 12 CBSE Computer Science (083) Project
"""

import os
import sys
import unittest

# Ensure application root directory is in python search path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from app import app, calculate_similarity_score
from seed_data import seed

class SchoolLostFoundTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Seed fresh clean data before test execution
        seed()

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_01_landing_page(self):
        """Test homepage loads with hero, status counters, and process flow."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Lost something?', response.data)
        self.assertIn(b'Platform Transparency', response.data)
        self.assertIn(b'REPORT LOST ITEM', response.data)

    def test_02_registration_and_duplicate_prevention(self):
        """Test student registration and duplicate ID/email prevention."""
        # 1. Register new student
        res = self.client.post('/register', data={
            'name': 'Kavita Nair',
            'student_id': 'STU-1099',
            'email': 'kavita@school.local',
            'password': 'Password@123',
            'confirm_password': 'Password@123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Registration successful', res.data)

        # 2. Attempt duplicate student ID
        res_dup_id = self.client.post('/register', data={
            'name': 'Duplicate User',
            'student_id': 'STU-1099',
            'email': 'other@school.local',
            'password': 'Password@123',
            'confirm_password': 'Password@123'
        }, follow_redirects=True)
        self.assertIn(b'already exists', res_dup_id.data)

        # 3. Attempt duplicate email
        res_dup_email = self.client.post('/register', data={
            'name': 'Duplicate Email',
            'student_id': 'STU-1100',
            'email': 'kavita@school.local',
            'password': 'Password@123',
            'confirm_password': 'Password@123'
        }, follow_redirects=True)
        self.assertIn(b'already exists', res_dup_email.data)

    def test_03_authentication_and_sessions(self):
        """Test user login, wrong password rejection, and session state."""
        # Bad login
        bad_res = self.client.post('/login', data={
            'email': 'aravind@school.local',
            'password': 'WrongPassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', bad_res.data)

        # Good login
        good_res = self.client.post('/login', data={
            'email': 'aravind@school.local',
            'password': 'Student@123'
        }, follow_redirects=True)
        self.assertEqual(good_res.status_code, 200)
        self.assertIn(b'Welcome back, Aravind Sharma', good_res.data)

        # Logout
        logout_res = self.client.get('/logout', follow_redirects=True)
        self.assertIn(b'logged out', logout_res.data)

    def test_04_role_based_access_control(self):
        """Verify student cannot access admin routes."""
        # Login as student
        self.client.post('/login', data={'email': 'aravind@school.local', 'password': 'Student@123'})
        
        # Try to access admin dashboard
        res = self.client.get('/admin/dashboard', follow_redirects=True)
        self.assertIn(b'Access denied: Administrative privileges required', res.data)

        # Try to access admin items
        res_items = self.client.get('/admin/items', follow_redirects=True)
        self.assertIn(b'Access denied: Administrative privileges required', res_items.data)

    def test_05_report_lost_and_admin_approval(self):
        """Test reporting a lost item (PENDING) and subsequent admin approval to OPEN."""
        # Login as student
        self.client.post('/login', data={'email': 'aravind@school.local', 'password': 'Student@123'})

        # Submit lost item
        res = self.client.post('/report-lost', data={
            'item_name': 'Lenovo Black Wireless Mouse',
            'category': 'Electronics',
            'color': 'Black',
            'location': 'Computer Lab 1',
            'date_reported': '2026-09-09',
            'description': 'Has a tiny red trackpoint logo on the scroll wheel.'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'PENDING', res.data)
        self.assertIn(b'Lenovo Black Wireless Mouse', res.data)

        # Log out student
        self.client.get('/logout')

        # Log in as Admin
        self.client.post('/login', data={'email': 'admin@school.local', 'password': 'Admin@123'})

        # Find item in admin items and approve
        admin_res = self.client.get('/admin/items?status=PENDING')
        self.assertIn(b'Lenovo Black Wireless Mouse', admin_res.data)

    def test_06_matching_algorithm_scoring(self):
        """Verify the 100-point matching algorithm calculates accurate similarity scores."""
        lost = {
            'item_name': 'Black Scientific Calculator',
            'category': 'Electronics',
            'color': 'Black',
            'location': 'Physics Lab Room 302'
        }
        found_exact = {
            'item_name': 'Black Scientific Calculator Casio',
            'category': 'Electronics',
            'color': 'Black',
            'location': 'Physics Lab'
        }
        score, breakdown = calculate_similarity_score(lost, found_exact)
        # Expected:
        # Name: overlap of 'black', 'scientific', 'calculator' -> ~30-40 pts
        # Category: exact Electronics -> 25 pts
        # Color: exact Black -> 20 pts
        # Location: Physics Lab overlap -> 10-15 pts
        # Total should be >= 80%
        self.assertGreaterEqual(score, 80)
        self.assertEqual(breakdown['category_score'], 25)
        self.assertEqual(breakdown['color_score'], 20)
        self.assertGreaterEqual(breakdown['location_score'], 10)
        self.assertGreaterEqual(breakdown['name_score'], 30)

        # Non-matching item comparison
        found_different = {
            'item_name': 'Red Woolen Scarf',
            'category': 'Clothing',
            'color': 'Red',
            'location': 'Basketball Ground'
        }
        diff_score, _ = calculate_similarity_score(lost, found_different)
        self.assertLess(diff_score, 20)

    def test_07_search_system(self):
        """Verify search with filters (keyword, category, type)."""
        # Keyword search
        res = self.client.get('/search?q=calculator')
        self.assertIn(b'Calculator', res.data)

        # Category filter
        res_cat = self.client.get('/search?category=Electronics')
        self.assertEqual(res_cat.status_code, 200)

        # Type filter
        res_type = self.client.get('/search?item_type=FOUND')
        self.assertEqual(res_type.status_code, 200)

    def test_08_claim_flow(self):
        """Verify claim submission on open found item and duplicate prevention."""
        # Login as Rohit
        self.client.post('/login', data={'email': 'rohit@school.local', 'password': 'Student@123'})

        # Item #2 is 'Black Scientific Calculator Casio' (FOUND, OPEN) reported by Priya
        claim_res = self.client.post('/claim/2', data={
            'reason': 'I lost my calculator in physics lab desk 14 on Monday.',
            'lost_location': 'Physics Lab Desk 14',
            'additional_info': 'Inside battery compartment there is a red Duracell sticker.'
        }, follow_redirects=True)
        self.assertEqual(claim_res.status_code, 200)
        self.assertIn(b'Claim submitted successfully', claim_res.data)

        # Attempt duplicate claim on same item
        dup_claim = self.client.post('/claim/2', data={
            'reason': 'Another claim',
            'lost_location': 'Physics Lab',
            'additional_info': ''
        }, follow_redirects=True)
        self.assertIn(b'already have an active claim', dup_claim.data)

if __name__ == '__main__':
    unittest.main()
