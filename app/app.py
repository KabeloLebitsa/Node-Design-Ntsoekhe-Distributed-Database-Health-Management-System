# app.py

import os
from config import app_config
from flask import Flask, abort, redirect, render_template, request, url_for, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user  
from database import DatabaseManager
from models import User
from api import api

db_manager = DatabaseManager()

app = Flask(__name__)
# Initialize Flask-Login
app.config.from_object(app_config)
app.register_blueprint(api)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'


# Required: Automatically ensure there is an admin user on App worker startup
db_manager.ensure_admin_user()
@login_manager.user_loader
def load_user(user_id):
    with db_manager.get_db() as db:
        return db.query(User).get(int(user_id))
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('login.html')

    username = request.form['Username']
    password = request.form['Password']

    user = db_manager.authenticate_user(username, password)

    if not user:
        abort(401)
    login_user(user)
    # User authenticated, proceed with logic using refreshed current_user
    role_dashboard_urls = {
        'admin': 'admin_dashboard',
        'doctor': 'doctor_dashboard',
        'patient': 'patient_dashboard'
    }
    return jsonify({'redirect': url_for(role_dashboard_urls[current_user.Role])})

def create_dashboard_route(role):
    if role not in ['admin', 'doctor', 'patient']:
        raise ValueError('Invalid role')

    def dashboard():
        return render_template(f"{role}_dashboard.html")
    dashboard.__name__ = f"{role}_dashboard"
    return dashboard

@app.route('/user/info')
@login_required
def user_info():
    user_id = current_user.UserID
    with db_manager.get_db() as db:
        if user := db.query(User).get(user_id):
            user_data = {
                "id": user.UserID,
                "username": user.Username,
                "role": user.Role
            }
        else:
            return abort(404, description="User not found")
    return jsonify(user_data)

# Home page route
@app.route('/')
def index():
    return render_template('index.html')

# User loader function for Flask-Login (using imported function)
@app.login_manager.user_loader
def load_user(user_id):
    return db_manager.load_user(user_id)

# Login page route
@app.route('/login_page')
def login_page():
    return render_template('login.html')

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_page'))

# Dashboard routes (using helper function)
app.route('/dashboard/admin')(create_dashboard_route('admin'))
app.route('/dashboard/doctors')(create_dashboard_route('doctor'))
app.route('/dashboard/patients')(create_dashboard_route('patient'))

# Create user page route 
@app.route('/register/users')
def create_user():
    return render_template('create_user.html')

# Create patients page route 
@app.route('/register/patients')
def create_patient():
    return render_template('create_patient.html')
# Create doctors page route 
@app.route('/register/doctors')
def create_doctor():
    return render_template('create_doctor.html')

# Main function
if __name__ == '__main__':
    debug_mode = app_config.DEBUG
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port, debug=debug_mode)