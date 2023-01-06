"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from app import app
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

# os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
# os.environ['TESTING'] = 'True'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///warbler-test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Don't req CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False
# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()
        
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD", 
            bio = "test bio",
            location = "test location",
            image_url = "test image",
            header_image_url = "test header image"
        )
        
        db.session.add(u)
        db.session.commit()
        
        self.u_id = u.id
        
    def tearDown(self):
        """Clean up fouled transactions."""
        
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""
        
        User.query.delete()
        
        u = User(
            email="testemail@test.com",
            username="testusername",
            password="testpassword", 
            bio = "test bio",
            location = "test location",
            image_url = "test image",
            header_image_url = "test header image"
        )
        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)
        
        # test is_following working when following user2
        
        # test is_following working with not following user2
        
        # test is_followed_by working when user2 is following user1
        
        # test is_followed_by working when user2 is not following user1
        
        # test User.create successfully creates a new user given valid credentials
        
        # test User.create fails to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail
        
        # test User.authenticate successfully returns a user when given a valid username and password
        
        # test user.authenticate returns False when the username is invalid
        
        # test user.authenticate returns False when the password is invalid