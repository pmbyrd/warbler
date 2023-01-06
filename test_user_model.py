"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
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
        
        u1 = User(
            email="test@test.com",
            username="testuser",
            password="testpassword", 
            bio = "test bio",
            location = "test location",
            image_url = "test image",
            header_image_url = "test header image"
        )
        
        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="testpassword2",
            bio="test bio2",
            location="test location2",
            image_url="test image2",
            header_image_url="test header image2"
        )
        
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        
        # *When dealing with foreign keys, you need to commit the data to the database before you can use it in the test
        
        u_id_1 = 1
        u1.id = u_id_1
        
        u_id_2 = 2
        u2.id = u_id_2
        
        db.session.commit()
        
        u1 = User.query.get(u_id_1)
        u2 = User.query.get(u_id_2)
        
        # *Reassign the user objects to the ones that are in the database
        self.u1 = u1
        self.u_id_1 = u_id_1
        
        self.u2 = u2
        self.u_id_2 = u_id_2
        
        self.client = app.test_client()
        
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
        
        db.session.add(u)
        db.session.commit()
        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.following), 0)
        
        #Test if user is following another user
    def test_user_follows(self):
        """Test if user is following another user"""
        
        self.u1.following.append(self.u2)
        db.session.commit()
        
        self.assertEqual(len(self.u1.following), 1)
        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u2.followers), 1)
        
        
        # test is_followed_by working when user2 is following user1 
    def test_is_followed(self):
        """Test is_followed method works to show if user is followed by another user"""
        
        self.u1.following.append(self.u2)
        db.session.commit()
        
        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))
        
        # test User.create successfully creates a new user given valid credentials
        # test User.create fails to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail
    def test_create_user(self):
        """Test that a new user can be created and saved to the database."""
     
        test_u = User.signup("testuser3", "test3@test.com", "testpassword3", None)
        uid = 3
        test_u.id = uid
        db.session.commit()
        
        test_u = User.query.get(uid)
        # Test that a new user can be created and saved to the database
        
        self.assertEqual(test_u.username, "testuser3")
        self.assertEqual(test_u.email, "test3@test.com")
        # hashed password should start with $2b$
        self.assertTrue(test_u.password.startswith("$2b$"), "testpassword3")
        
    def test_invalid_username(self):
        """Test that a new user cannot be created with an invalid username."""
        
        invalid_user = User.signup(None, "test@test.com", "testpassword", None)
        
        uid = 999
        invalid_user.id = uid
        # Must account for the error that will be raised
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
            
    def test_invalid_email(self):
        """Test that a new user cannot be created with an invalid email."""
        
        invalid_user = User.signup("testuser", None, "testpassword", None)
        
        uid = 999
        invalid_user.id = uid
        # Must account for the error that will be raised
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
            
    def test_invalid_password(self):
        """Test that a new user cannot be created with an invalid password."""
        
        # do not need to account for user only checking invalid password
        with self.assertRaises(ValueError) as context:
            User.signup("testuser", "test@test.com", None, None)
    
    # Check for authentication
    
    def test_valid_authentication(self):
        """Test that a user can be authenticated with a valid username and password."""
        
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.u_id_1)
        
    # Check for failed authentication
    def test_invalid_username(self):
        """Test that a user cannot be authenticated with an invalid username."""
        
        self.assertFalse(User.authenticate("invalidusername", "password"))
        
    def test_invalid_password(self):
        """Test that a user cannot be authenticated with an invalid password."""
        
        self.assertFalse(User.authenticate(self.u1.username, "invalidpassword"))
            
        
        
    