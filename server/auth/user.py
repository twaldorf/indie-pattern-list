from bson import ObjectId
from flask_login import UserMixin
from argon2 import PasswordHasher
from werkzeug.security import generate_password_hash, check_password_hash

from server.db_operations import db_collect_pattern, db_get_user_by_id

ph = PasswordHasher()

class User(UserMixin):
    def __init__(self, _id, username, password_hash, lists=None, content=None):
        # ObjectID as a string
        self._id = _id
        # Unique username
        self.username = username
        # Salted and hashed password
        self.password_hash = password_hash
        # Profile info, settings, likes, edits, collection, reviews, etc.
        self.lists = lists
        self.content = content

    def __update(self, collection):
        user = db_get_user_by_id(self._id, collection)
        if user:
            self.lists=user.get('lists')
            return True
        else:
            return False

    def data(self):
        data = { 
            "username": self.username,
             "lists": self.lists }
        return data
    
    def get_id(self):
        return self._id

    def get_by_id(_id, collection):
        user = db_get_user_by_id(_id, collection)
        if user:
            return User(
                username=user['username'], 
                _id=str(user['_id']), 
                password_hash=user['password_hash'],
                lists=user.get('lists'))
        else:
            return None

    def get_username(self):
        return self.username
    
    def get_password_hash(self):
        return self.password_hash
    
    def collect_pattern(self, pid, collection):
        success = db_collect_pattern(self.get_id(), collection, pid, "My List")
        self.__update(collection=collection)
        return success
    
    # Static method for creating a salted and hashed password for new user creation
    @staticmethod
    def hash_password(password):
        return ph.hash(password)
        
    # Static method for authenticating passwords during a log in attempt
    @staticmethod
    def check_password(hash, password):
        verity = ph.verify(hash, password)
        if verity:
            return True
        return False