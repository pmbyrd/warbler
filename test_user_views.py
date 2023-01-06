"""Test user views."""
# Import necessary modules
import os
from flask import session
from unittest import TestCase
from models import db, User, Message, Follows, Likes
from app import app, CURR_USER_KEY

# Set up Flask app and test client

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler-test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Don't req CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False
# Now we can import app

# create tables
# db.drop_all()
db.create_all()
class UserViewsTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        User.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()

        
    def tearDown(self):
        db.session.rollback()
        
        
    # *test signup page
    def test_signup(self):
        """Test signup page."""
        
        with self.client as c:
            resp = c.get("/signup")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"""<h2 class="join-message">Join Warbler today.</h2>""", html)
       
            
    # *test login page
    def test_login(self):
        """Test login page."""
        
        with self.client as c:
            resp = c.get("/login")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"""<h2 class="join-message">Welcome back.</h2>""", html)
                
                
    # *test when logged in can see the follwer and following pages
    def test_logged_in_follower_following_pages(self):
        """Test logged in follower and following pages."""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            resp = c.get(f"/users/{self.testuser.id}/followers")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"""<p class="small">Followers</p>""", html)
                
    # *test when logged out can not see the follwer and following pages
    def test_fail_logged_in_follower_following_pages(self):
        """Test that not authenticated user can not see follower and following pages."""
        
        with self.client as c:
            resp = c.get(f"/users/{self.testuser.id}/followers", follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"""<h1>What's Happening?</h1>""", html)
        
    
    # *test detail page
    def test_user_detail_page(self):
        """Test user detail page."""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"""<p class="small">Messages</p>""", html)
    
    # *test edit page
    def test_user_edit_page(self):
        """"Test user edit page."""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/profile")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"""<h2 class="join-message">Edit Your Profile.</h2>""", html)
        
    # *test show page
    def test_show_page(self):
        """Test show page."""
        
        with self.client as c:
            resp = c.get('/users')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"""<p>@{self.testuser.username}</p>""", html)
    
    
    
    
    
            