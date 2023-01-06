"""Test user views."""
# Import necessary modules
import os
from unittest import TestCase
from models import db, User, Message, Follows, Likes
from app import app

# Set up Flask app and test client
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
os.environ['TESTING'] = 'True'


class UserViewsTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(
            username="testuser",
            email="test@gmail.com",
            password="testuser")
        
    
            