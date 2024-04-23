#app.py

from flask import Flask, redirect, render_template, request, url_for, jsonify, flash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models import User 
from config import app_config 
from sqlalchemy.orm import query

# Application configuration
app = Flask(__name__)
app.config.from_object(app_config)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Optionally set the template folder explicitly (if needed)
# app.template_folder = 'app/templates'

# Home page route
@app.route('/')
def index():
    return render_template('index.html')
# Display patients page route
@app.route('/patients/display')
@login_required
def display_patients():
    return render_template('display_patients.html')
# Create patients page route
@login_required
@app.route('/patients/create')
def create_patients():
    return render_template('create_patients.html')

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

# User info route
@app.route('/user/info', methods=['GET'])
@login_required
def get_user_info():
  """
  This function retrieves the currently logged-in user's information.
  """
  return jsonify({'user': {'username': current_user.username, 'role': current_user.role}})

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return query(User).get(int(user_id))
# Login page route
@app.route('/loginpage')
def login_page():
    return render_template('login.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = query(User).filter_by(Username=username).first()
        if user is not None and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))  # Redirect to a dashboard or home page
        else:
            flash('Invalid username or password')
    return render_template('login.html')
# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

'''def validate_inputs(username, password):
  # Check if the username and password are not empty
  if not username or not password:
      return False

  # Check for minimum length requirements
  min_username_length = 5
  min_password_length = 8
  if len(username) < min_username_length or len(password) < min_password_length:
      return False

  # Check for password complexity (example: must contain at least one number and one uppercase letter)
  if not any(char.isdigit() for char in password):
      return False
  return any((char.isupper() for char in password))'''

# Main function
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
