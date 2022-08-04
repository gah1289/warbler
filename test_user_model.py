"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from ast import ExceptHandler
import os
from re import A
from unittest import TestCase 

from models import db, User, Message, Follows, bcrypt

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"
# changed - to _ 



# Now we can import app

from app import app


from models import db, User, Message, Likes, Follows
# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

app.config['TESTING'] = True

def add_user(user):
    db.session.add(user)                 
    db.session.commit()    


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        
        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        add_user(u)

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_user_model_repr(self):
        """Does the repr method work as expected?"""

        u = User(
            id=1,
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        add_user(u)     

        self.assertEquals("<User #1: testuser, test@test.com>", repr(u))
        self.assertNotEqual("<User #2: testuser, test@test.com>", repr(u))
    
    def test_user_following(self):
        """Does is_following successfully detect when user1 is following user2? 
        Does is_following successfully detect when user1 is not following user2?"""

        u1 = User(
            id=1,
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD"
        )       

        u2 = User(
            id=2,
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

        add_user(u1)
        add_user(u2)

        self.assertFalse(u1.is_following(u2))
        u1.following.append(u2) 
        self.assertTrue(u1.is_following(u2))

        self.assertFalse(u2.is_following(u1))
        u2.following.append(u1) 
        self.assertTrue(u2.is_following(u1))

    def test_user_create(self):
        """Does User.create successfully create a new user given valid credentials?
        Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?"""

        user_good=User(
            id=1,
            email="test@test.com",
            username="testuser1",
            password="HASHED_PW"
        )

        add_user(user_good)

        amt_users=db.session.query(User).count()
        self.assertEqual(amt_users,1)


        user_no_pw=User(
            id=2,
            email="test@test.com",
            username="testuser2"
        ) 

        user_no_username=User(
            id=3,
            email="test@test.com",
            password="HASHED_PW"
        ) 

        user_no_email=User(
            id=4,            
            username="testuser4",
            password="HASHED_PW"
        )

        user_duplicate=User(
            id=5,
            email="test@test.com",
            username="testuser1",
            password="HASHED_PW"
        )
        
        with self.assertRaises(Exception): add_user(user_no_pw)
        with self.assertRaises(Exception): add_user(user_no_username)
        with self.assertRaises(Exception): add_user(user_no_email)
        with self.assertRaises(Exception): add_user(user_duplicate)
    
    def test_user_authenticate(self):
        """Does User.authenticate successfully return a user when given a valid username and password?
        Does User.authenticate fail to return a user when the username is invalid?
        Does User.authenticate fail to return a user when the password is invalid?"""

        user=User(
            id=1,
            email="test@test.com",
            username="testuser1",
            password=bcrypt.generate_password_hash('password').decode('UTF-8')
        )

        add_user(user)

        self.assertTrue(user.authenticate("testuser1", 'password'))
        self.assertFalse(user.authenticate("testuser1", 'wrongpassword'))
        self.assertFalse(user.authenticate("wrongusername","password"))
        
        


        


