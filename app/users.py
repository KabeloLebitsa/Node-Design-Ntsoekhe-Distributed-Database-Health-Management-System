#users.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import User

class Users(UserMixin):
    def __init__(self, user_id, username, password, role):
        self.id = user_id
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.role = role  # List of user roles (e.g., "admin", "doctor")

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Implement methods for additional user information (e.g., email, name)

    # user authentication logic 
    def authenticate(self, username, password):
        usr = self.username
        user = User.query.filter_by(usr=username).first()
        return user if user and self.verify_password(password) else None
