#app.py

import users
from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from models import User  

# Application configuration
app = Flask(__name__)
app.config.from_object('config')

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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
    if user := users.authenticate(username, password):
        login_user(user)
        return redirect(url_for('/dashboard'))
    return 'Invalid username or password'

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
    app.run(debug=True,host='0.0.0.0',port=5000)
