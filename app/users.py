#users.py

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin):
    def __init__(self, user_id, username, password, role):
        self.id = user_id
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.role = role  # List of user roles (e.g., "admin", "doctor")

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Implement methods for additional user information (e.g., email, name)

    def can(self, permission):
        permissions = {
            "CREATE_PATIENT": ["admin","doctor"],
            "READ_PATIENT": ["admin", "doctor"],
            "UPDATE_PATIENT": ["admin","doctor"],
            "DELETE_PATIENT": ["admin"],
            
            "CREATE_DOCTOR": ["admin"],
            "READ_DOCTOR": ["admin"],
            "UPDATE_DOCTOR": ["admin"],
            "DELETE_DCTOR": ["admin"],
        }

        return any(
            perm == permission
            and any(role in self.roles.split(",") for role in allowed_roles)
            for perm, allowed_roles in permissions.items()
        )

# user authentication logic 
def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    return user if user and user.verify_password(password) else None
