from flask import Blueprint, request, jsonify
from flask_login import login_required
from app import app
from models import Patient, Doctor, Nurse, Department, Appointment, MedicalRecord, Prescription, Billing, User
from database import DatabaseManager

api = Blueprint('api', __name__)

db_manager = DatabaseManager()

# Endpoint for creating a user
@api.route('/users', methods=['POST'])
@login_required
def create_user():
    user_data = request.get_json()
    if not user_data:
        return jsonify({'message': 'Missing user data'}), 400

    try:
        db_manager.insert_user(User(**user_data))
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        print(f"Error creating user: {e}")
        return jsonify({'message': 'Failed to create user'}), 500


# Endpoint for creating a patient
@api.route('/create/patients', methods=['POST'])
@login_required
def create_patient():
    patient_data = request.get_json()
    if not patient_data:
        return jsonify({'message': 'Missing patient data'}), 400
    try:
        db_manager.insert_patient(Patient(**patient_data))
        return jsonify({'message': 'Patient created successfully'}), 201
    except Exception as e:
        print(f"Error creating patient: {e}")
        return jsonify({'message': 'Failed to create patient'}), 500


# Endpoint for retrieving patient by ID
@api.route('/patients/<int:patient_id>', methods=['GET'])
@login_required
def get_patient_by_id(patient_id):
    if patient := db_manager.get_patient_by_id(patient_id):
        return jsonify(patient.serialize()), 200
    else:
        return jsonify({'message': f'Patient with ID {patient_id} not found'}), 404


# Endpoint for updating patient
@api.route('/patients/<int:patient_id>', methods=['PUT'])
@login_required
def update_patient(patient_id):
    update_data = request.get_json()
    if not update_data:
        return jsonify({'message': 'Missing update data'}), 400

    try:
        db_manager.update_patient(patient_id, update_data)
        return jsonify({'message': 'Patient updated successfully'}), 200
    except Exception as e:
        print(f"Error updating patient: {e}")
        return jsonify({'message': 'Failed to update patient'}), 500


# Endpoint for deleting patient
@api.route('/patients/<int:patient_id>', methods=['DELETE'])
@login_required
def delete_patient(patient_id):
    try:
        db_manager.delete_patient(patient_id)
        return jsonify({'message': 'Patient deleted successfully'}), 200
    except Exception as e:
        print(f"Error deleting patient: {e}")
        return jsonify({'message': 'Failed to delete patient'}), 500


# Endpoint for creating a doctor
@api.route('/create/doctors', methods=['POST'])
@login_required
def create_doctor():
    doctor_data = request.get_json()
    if not doctor_data:
        return jsonify({'message': 'Missing doctor data'}), 400

    try:
        db_manager.insert_doctor(Doctor(**doctor_data))
        return jsonify({'message': 'Doctor created successfully'}), 201
    except Exception as e:
        print(f"Error creating doctor: {e}")
        return jsonify({'message': 'Failed to create doctor'}), 500

app.register_blueprint(api)
