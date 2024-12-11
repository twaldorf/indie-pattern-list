from werkzeug.security import generate_password_hash, check_password_hash

from ..db_operations import db_get_user_by_id

class User:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get(user_id, collection):
        return db_get_user_by_id(user_id, collection)
    