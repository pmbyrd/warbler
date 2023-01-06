"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()
        
    def tearDown(self):
        """Clean up fouled transactions."""

        db.session.rollback()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    
    # test unauthorized user can't add a message
    def test_unauthorized_user_add_message(self):
        """Can an unauthorized user add a message?"""

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)
    
    # test invalid/not signed up user can't add a message
    def test_add_invalid_user(self):
        """Test user not in session can't add a message"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 9999
                
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)
         
    
    # test message show route with user in session
    def test_show_message(self):
        """Test message show route with user in session"""
        
        m = Message(
            id=12345, 
            text="Hello", 
            user_id=self.testuser.id)
        
        db.session.add(m)
        db.session.commit()
        
        # Once a test message has been created in the database, we can test the show route
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            m = Message.query.get(12345)
            
            resp = c.get(f'/messages/{m.id}')
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Hello', resp.data)
    
    # test message show route without user in session
    # def test_invalid_message_show(self):
    #     """Test message show route without user in session"""
        
    #     # get the client session and check for message that does not exist
    #     with self.client as c:
    #         with c.session_transaction() as sess:
    #             sess[CURR_USER_KEY] = self.testuser.id
                
    #         resp = c.get(f'/messages/10000000')
            
    #         self.assertEqual(resp.status_code, 404)
            

    # when logged in can delete a message
    def test_delete_message(self):
        """Test logged in user can delete a message"""
        
        m = Message(
            id=12345, 
            text="Hello", 
            user_id=self.testuser.id)
        
        db.session.add(m)
        db.session.commit()
        
        # Once a test message has been created in the database, we can test the show route
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
                
            m = Message.query.get(12345)
            
            resp = c.post(f'/messages/{m.id}/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

    # when logged in can't delete a message that isn't yours unauthorized user can't delete a message
    def test_unauthorized_message_deletion(self):
        """Test unauthorized user can't delete a message that is not theirs."""
        
        u = User.signup(
            username="testuser2",
            email="testing@test.com",
            password="password2",
            image_url=None)
        
        u.id = 33333
        
        # set the message to be the message of the testuser
        m = Message(
            id = 123456,
            text = "another test message",
            user_id = self.testuser.id)
        
        db.session.add_all([u, m])
        db.session.commit()
        
        # user the unauthorized user to try to delete the message
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 33333
                
            
            resp = c.post(f'/messages/123456/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)
    
    # test invalid/not signed up user can't delete a message
    def test_message_delete_not_authenticated(self):
        """Test that a user not signed up can't delete a message"""
        
        m = Message(
            id = 1234567,
            text = "another one",
            user_id = self.testuser.id
        )
        
        db.session.add(m)
        db.session.commit()
        
        with self.client as c:
            resp = c.post(f'/messages/1234567/delete', follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Access unauthorized", resp.data)
        
    