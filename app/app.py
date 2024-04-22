#app.py

import users
from flask import Flask, redirect, render_template, request, url_for, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models import User  

# Application configuration
app = Flask(__name__)
app.config.from_object('config')

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
    return User.query.get(int(user_id))

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('/dashboard'))
    username = request.form.get('username')
    password = request.form.get('password')
    if not username or not password:
        return 'Invalid username or password'
    # Validate username and password inputs
    if not validate_inputs(username, password):
        return 'Invalid username or password'
    try:
        if user := users.authenticate(username, password):
            login_user(user)
            return redirect(url_for('/dashboard'))
        return 'Invalid username or password'
    except Exception as e:
        return f'An error occurred: {str(e)}'

def validate_inputs(username, password):
    # Add validation logic here
    # Return True if inputs are valid, False otherwise
    ...

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    port = app.config.get('PORT', 5000)
    app.run(debug=False, host='127.0.0.1', port=port)
