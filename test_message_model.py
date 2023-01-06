"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from app import app
from models import db, User, Message, Follows, Likes

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
# test message model
class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        
        db.drop_all()
        db.create_all()
        
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        
        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="testpassword",
            image_url=None
        )
        
        self.uid = 1000
        
        u.id = self.uid
        db.session.commit()
        
        self.u = User.query.get(self.uid)
        
        self.client = app.test_client()
      
        
    def tearDown(self):
        """Clean up fouled transactions."""
        db.session.rollback()
        
# can create a message
    def test_message_model(self):
        """Test message model."""
        
        m1 = Message(
            text = "test message",
            user_id = self.uid
        )
        
        db.session.add(m1)
        db.session.commit()
        
        # *Test the lenght and test the message itself
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "test message")
        
        
# test can like messages  
    def test_message_likes(self):
        """Test the relationship between messages and likes."""
        
        # *Must create a second user to like the message 
        
        m1 = Message(
            text = "test message",
            user_id = self.uid
        )
        
        m2 = Message(
            text = "test message 2",
            user_id = self.uid
        )
        
        test_u = User.signup(
            email="testtest@test.com",
            username="testtestuser",
            password="testtestpassword",
            image_url=None
        )
        
        uid = 1001
        test_u.id = uid
        db.session.add_all([m1, m2, test_u])
        db.session.commit()
        
        test_u.likes.append(m1)
        
        db.session.commit()
        
        like = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(like), 1)
        self.assertEqual(like[0].message_id, m1.id)
        
        
        

