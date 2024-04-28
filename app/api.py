#api.py

from sqlite3 import IntegrityError
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required
from exceptions import PatientNotFoundException, InvalidRequestException, DatabaseIntegrityError, InternalServerError
from models import Patient, Doctor, Nurse, Department, Appointment, MedicalRecord, Prescription, Billing, User
from database import DatabaseManager

api = Blueprint('api', __name__)
db_manager = DatabaseManager()

# Endpoint for creating a user
@api.route('/create/users', methods=['POST'])
def create_user():
    user_data = request.get_json()
    if not user_data:
        return jsonify({'message': 'Missing user data'}), 400
    try:
        user_id = db_manager.insert_user(user_data)
        return jsonify({'UserID': user_id}), 201
    except InvalidRequestException as e:
        return jsonify({'message': str(e)}), 400
    except DatabaseIntegrityError as e:
        return jsonify({'message': str(e)}), 500
    except InternalServerError as e:
        print(f"Error creating user: {e}")
        return jsonify({'message': 'Failed to create user'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'message': 'Internal server error'}), 500


# Endpoint for creating a patient
@api.route('/create/patients', methods=['POST'])
def create_patient():
    patient_data = request.get_json()
    required_fields = ["Name", "DateOfBirth", "Gender", "PhoneNumber"]

    if missing_fields := [
        field for field in required_fields if field not in patient_data
    ]:
        return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    try:
        db_manager.insert_patient(patient_data)
        return jsonify({'redirect': '/dashboard/admin'}), 201
    except IntegrityError as e:
        return jsonify({'message': 'Failed to create patient (data integrity issue)'}), 500
    except Exception as e:
        print(f"Error creating patient: {e}")
        return jsonify({'message': 'Failed to create patient'}), 500


# Endpoint for retrieving patient by ID
@api.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient_by_id(patient_id):
    if patient := db_manager.get_patient_by_id(patient_id):
        return jsonify(patient.serialize()), 200
    else:
        return jsonify({'message': f'Patient with ID {patient_id} not found'}), 404


# Endpoint for updating patient
@api.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    update_data = request.get_json()
    if not update_data:
        return jsonify({'message': 'Missing update data'}), 400

    try:
        db_manager.update_patient(patient_id, update_data)
        return jsonify({'message': 'Patient updated successfully'}), 200
    except PatientNotFoundException as e:
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        print(f"Error updating patient: {e}")
        return jsonify({'message': 'Failed to update patient'}), 500


@api.route('/patients/<int:patient_id>', methods=['DELETE'])

def delete_patient(patient_id):
    try:
        patient = db_manager.get_patient(patient_id)
        if not patient:
            return jsonify({'message': 'Patient not found'}), 404

        db_manager.delete_patient(patient_id)
        return jsonify({'message': 'Patient deleted successfully'}), 200
    except PatientNotFoundException as e:
        return jsonify({'message': str(e)}), 404
    except Exception as e:
        print(f"Error deleting patient: {e}")
        return jsonify({'message': 'Internal server error'}), 500


# Endpoint for creating a doctor
@api.route('/create/doctors', methods=['POST'])
def create_doctor():
    doctor_data = request.get_json()
    required_fields = ["Name", "Specialization", "PhoneNumber", "DepartmentName"]
    conn = db_manager.get_db
    DepartmentID = conn.query(Department).filter(Department.DepartmentName == doctor_data['DepartmentName']).one_or_none()
    doctor_data['DepartmentID'] = DepartmentID
    if missing_fields := [
        field for field in required_fields if field not in doctor_data
    ]:
        return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    try:
        db_manager.insert_doctor(Doctor(**doctor_data))
        return jsonify({'redirect': '/dashboard/admin'}), 201
    except IntegrityError as e:
        return jsonify({'message': 'Failed to create doctor (data integrity issue)'}), 500
    except Exception as e:
        print(f"Error creating doctor: {e}")
        return jsonify({'message': 'Failed to create doctor'}), 500

@api.route('/display/patients')
def display_patients():
  patients = db_manager.get_all_patients()
  return render_template('display_patients.html', patients=patients)