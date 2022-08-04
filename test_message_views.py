"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase



# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY
import seed

from models import User, Message, db
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

def add_user(user):
    db.session.add(user)
    db.session.commit()

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
            self.assertEqual(msg.user_id, self.testuser.id)
    
    def test_delete_message(self):
        """When you’re logged in, can you delete a message as yourself?
        When you’re logged out, are you prohibited from adding messages?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            c.post("/messages/new", data={"text": "Hello"})
            
            amt_msgs=db.session.query(Message).count()
            self.assertEqual(amt_msgs, 1)            

            msg = Message.query.one()
            
            resp=c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html=resp.get_data(as_text=True)

            amt_msgs=db.session.query(Message).count()
            self.assertEqual(amt_msgs, 0)
            self.assertIn('<a href="/users/301">0</a>',html)

            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY] 
            
            resp_logged_out=c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            html_logged_out=resp_logged_out.get_data(as_text=True)
            self.assertIn('div class="alert alert-danger">Access unauthorized.</div>',html_logged_out)

    
    def test_view_following_pages(self):
        '''When you’re logged in, can you see the follower / following pages for any user?'''
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
            new_user=User.signup(
                username="testuser1",
                password="HASHED_PW",
                email="puppies@gmail.com",
                image_url=None
        )

            db.session.commit()
            
            resp=c.get(f'/users/{new_user.id}')
            html=resp.get_data(as_text=True)
            self.assertIn("Following", html)
            self.assertIn("Followers", html)            

            with c.session_transaction() as sess:
                del sess[CURR_USER_KEY] 

            logged_out_resp=c.get(f'/users/{new_user.id}/followers', follow_redirects=True)
            logged_out_html=logged_out_resp.get_data(as_text=True)

            self.assertIn("unauthorized", logged_out_html)            
        
           
    