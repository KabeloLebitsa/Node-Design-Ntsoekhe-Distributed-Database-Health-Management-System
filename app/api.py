#api.py

from flask import Flask, redirect, render_template, request, jsonify, abort, current_user, url_for
from flask_login import LoginManager, login_required, login_user, logout_user
from requests import post
from . import connection_pool, database, celery_worker  # Assuming these are in different files
from .models import Patient  # Import Patient class from models.py
from .users import User  # users.py defines User model and authentication logic

OTHER_NODES = ['https://172.18.0.4:8083', 'https://172.18.0.3:8082', 'https://172.18.0.2:8081', 'https://172.18.0.5:8084', 'https://172.18.0.6:8085']

app = Flask(__name__)

# ... other configurations (secret key, etc.)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.html'  # Redirect to login page on unauthorized access

@app.route('/patients', methods=['POST'])
@login_required  # Require login for creating patients
def create_patient():
    if not current_user.can_create_patient:  # Implement authorization check based on user roles
        return abort(403)  # Forbidden

    patient_data = request.get_json()

    with connection_pool.get_connection() as conn:
        cursor = conn.cursor()
        try:
            # Insert patient data locally
            cursor.execute('INSERT INTO patients (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
                           (patient_data['Name'], patient_data['DateOfBirth'], patient_data['Gender'],
                            patient_data['ContactInformation'], patient_data['InsuranceInformation']))
            conn.commit()

            # Get the newly inserted patient ID
            patient_id = cursor.lastrowid

            # Replicate to other nodes asynchronously using Celery
            for node in OTHER_NODES:
                celery_worker.replicate_patient.delay(node, patient_data)

            return jsonify({'message': f'Patient created successfully with ID: {patient_id}', 'patient_id': patient_id}), 201
        except Exception as e:
            conn.rollback()
            app.logger.error(f'Error creating patient: {e}')
            return jsonify({'message': 'Failed to create patient'}), 500

# Retrieve a patient by ID
@app.route('/patients/<int:patient_id>', methods=['GET'])
@login_required
def get_patient_by_id(patient_id):
    if not current_user.can_read_patient:
        return abort(403)  # Forbidden

    if patient := database.get_patient_by_id(patient_id):
        return jsonify(patient.serialize()), 200
    else:
        return jsonify({'message': f'Patient with ID {patient_id} not found'}), 404  # Not Found

# Endpoint for replication (assuming user has appropriate permissions)
@app.route('/replicate', methods=['POST'])
@login_required
def replicate_patient():
    replicated_data = request.get_json()
    # ... process and validate replicated data

    # Use connection pool for database interactions
    with connection_pool.get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO patients (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
                           (replicated_data['Name'], replicated_data['DateOfBirth'], replicated_data['Gender'],
                            replicated_data['ContactInformation'], replicated_data['InsuranceInformation']))
            conn.commit()
            return jsonify({'message': 'patient replicated successfully'}), 201
        except Exception as e:
            conn.rollback()
            app.logger.error(f'Error replicating patient: {e}')
            return jsonify({'message': 'Failed to replicate patient'}), 500

# ... other API endpoints
