#app.py

import users
from flask import Flask, redirect, render_template, request, jsonify, abort, current_user, url_for
from flask_login import LoginManager, login_required, login_user, logout_user
from .models import Patient, User  # Import models from respective files

# Application configuration
app = Flask(__name__)
app.config.from_object('config.py')

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.html'  # Redirect to login page on unauthorized access

# User loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Login and logout routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.html'))
    username = request.form['username']
    password = request.form['password']
    if user := users.authenticate(username, password):
        login_user(user)
        return redirect(url_for('dashboard'))
    return 'Invalid credentials'

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login.html'))


# Home page
@app.route('/')
def index():
    return render_template('login.html')