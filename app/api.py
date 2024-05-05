#api.py

import datetime
from sqlite3 import IntegrityError
from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from exceptions import PatientDeletionError, PatientNotFoundException, InvalidRequestException, DatabaseIntegrityError, InternalServerError
from models import Patient, Doctor, Nurse, Department, Appointment, Prescription, Billing, User
from database import DatabaseManager
import logging

api = Blueprint('api', __name__)
db_manager = DatabaseManager()

# Endpoint for creating a user
@api.route('/users', methods=['POST'])
#@login_required
def create_user():
    user_data = request.get_json()
    if not user_data:
        return jsonify({'message': 'Missing user data'}), 400
    try:
        user_id = db_manager.insert_user(user_data, request_id=None)
        logging.info(f"User created successfully. ID: {user_id}")
        return jsonify({'UserID': user_id}), 201
    except InvalidRequestException as e:
        logging.error(f"Invalid request: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except DatabaseIntegrityError as e:
        logging.error(f"Database integrity error: {str(e)}")
        return jsonify({'message': str(e)}), 501
    except InternalServerError as e:
        logging.error(f"Internal server error: {str(e)}")
        return jsonify({'message': 'Failed to create user'}), 502
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return jsonify({'message': 'Internal server error'}), 503

# Endpoint for creating a patient
@api.route('/patients', methods=['POST'])
#@login_required
def create_patient():
    patient_data = request.get_json()
    required_fields = ["Name", "DateOfBirth", "Gender", "PhoneNumber"]

    if missing_fields := [
        field for field in required_fields if field not in patient_data
    ]:
        return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    try:
        db_manager.insert_patient(patient_data, request_id=None)
        return jsonify({'redirect': '/dashboard/admin'}), 201
    except IntegrityError as e:
        return jsonify({'message': 'Failed to create patient (data integrity issue)'}), 500
    except Exception as e:
        print(f"Error creating patient: {e}")
        return jsonify({'message': 'Failed to create patient'}), 500

@api.route('/doctors', methods=['POST'])
#@login_required
def create_doctor():
    doctor_data = request.get_json()
    required_fields = ["DoctorName", "Specialization", "PhoneNumber", "DepartmentName"]
    
    if any(field not in doctor_data for field in required_fields):
        return jsonify({'message': f'Missing required fields: {", ".join(required_fields)}'}), 400

    try:
        with db_manager.get_db() as db:
            DepartmentID = db.query(Department.DepartmentID).filter(Department.DepartmentName == doctor_data['DepartmentName']).scalar()
            
            new_doctor = Doctor(
                doctor_id=doctor_data.get('DoctorID'),
                name=doctor_data.get('DoctorName'),
                specialization=doctor_data.get('Specialization'),
                phone_number=doctor_data.get('PhoneNumber'),
                department_id=DepartmentID
            )

            new_doctor_id = db_manager.insert_doctor(new_doctor)
        return jsonify({'redirect': '/dashboard/admin', 'doctor_id': new_doctor_id}), 201

    except (IntegrityError, Exception) as e: 
        print(f"Error creating doctor: {e}")
        return jsonify({'message': 'Failed to create doctor'}), 500

# Endpoint for retrieving patient by ID
@api.route('/patients/<int:patient_id>', methods=['GET'])
#@login_required
def get_patient_by_id(patient_id):
    if patient := db_manager.get_patient_by_id(patient_id):
        return jsonify(patient.serialize()), 200
    else:
        return jsonify({'message': f'Patient with ID {patient_id} not found'}), 404

# Endpoint for updating patient
@api.route('/patients/<string:patient_id>', methods=['PUT'])
#@login_required
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

@api.route('/patients/<string:patient_id>', methods=['DELETE'])
#@login_required
def delete_patient(patient_id):
  try:
    patient = db_manager.get_patient_by_id(patient_id)
    if not patient:
      return jsonify({'message': 'Patient not found'}), 404
    db_manager.delete_user(patient_id)
    db_manager.delete_patient(patient_id)
    return jsonify({'message': 'Patient deleted successfully'}), 200

  except PatientNotFoundException as e:
    return jsonify({'message': str(e)}), 404

  except (IntegrityError, PatientDeletionError) as e:
    return jsonify({'message': f"Error deleting patient: {str(e)}"}), 400

  except Exception as e:  
    print(f"Error deleting patient: {e}")
    return jsonify({'message': 'Internal server error'}), 500

  except:
    return jsonify({'message': 'Unexpected error occurred'}), 500

@api.route('/patients/display', methods=["GET"])
#@login_required
def display_patients():
  patients = db_manager.get_all_patients()
  return render_template('display_patients.html', patients=patients)

@api.route('/patients/search', methods=["GET"])
#@login_required
def search_patients():
    query = request.args.get('query', '')
    with db_manager.get_db() as conn:
        patients = conn.query(Patient).filter(Patient.Name.ilike(f'%{query}%')).all()
    return render_template('display_patients.html', patients=patients)

@api.route('/replicate/<action>/<ObjectType>', methods=['POST'])
#@login_required
def handle_replicate():
    try:
        data = request.get_json()
        if not data:
            logging.warning("No data provided in the request")
            return jsonify({'message': 'No data provided'}), 400

        action = data.get('action')
        object_type = data.get('object_type')
        db_data = data.get('data')

        if not db_data:
            logging.warning("Missing data to process for action: {action}, object_type: {object_type}")
            return jsonify({'message': 'Missing data to process'}), 400

        logging.info(f"Processing action {action} for object_type {object_type}")

        action_method_map = {
            'user': {
                'insert': db_manager.insert_user,
                'delete': db_manager.delete_user,
            },
            'patient': {
                'insert': db_manager.insert_patient,
                'update': db_manager.update_patient,
                'delete': db_manager.delete_patient,
            },
            'doctor': {
                'insert': db_manager.insert_doctor,
                'update': db_manager.update_doctor,  
                'delete': db_manager.delete_doctor,
            },
        }
        request_id = data.get('request_id')
        action_method = action_method_map.get(object_type, {}).get(action)
        if not action_method:
            logging.error(f"Unsupported action-object type combination: {action} with {object_type}")
            return jsonify({'message': 'Unsupported action-object type combination'}), 400

        logging.info(f"Executing {action} for {object_type} with request ID {request_id}")
        action_method(db_data, request_id)  # Call the appropriate database method

        logging.info(f"{object_type} {action}d successfully")
        return jsonify({'message': f'{object_type} {action}d successfully'}), 201

    except Exception as e:
        logging.error(f"Unexpected error while replicating data: {str(e)}")
        return jsonify({'message': 'Failed to replicate data'}), 500


@api.route('/prescriptions', methods=['POST'])
def add_prescription():
    try:
        if hasattr(current_user, 'UserID'):
            doctor_id = current_user.UserID
        else:
            return jsonify({'error': 'current_user does not have UserID attribute'}), 400
        
        prescription_data = request.get_json()
        if prescription_data is None:
            return jsonify({'error': 'Missing prescription data'}), 400
        
        prescription_data['DoctorID'] = doctor_id 
        
        db_manager.insert_prescription(prescription_data)
        return jsonify({'message': 'Prescription added successfully!'}), 201
    
    except DatabaseIntegrityError as e:
        return jsonify({'error': str(e)}), 400
    
    except InternalServerError as e:
        return jsonify({'error': str(e)}), 500
     
@api.route("/appointments/upcoming", methods=["GET"])
def get_upcoming_appointments():
  doctor_id = current_user.UserID  # Get the doctor's ID
  appointments = db_manager.get_all_appointments()
  today = datetime.today()

  # Filter appointments based on date and the doctor's ID
  upcoming_appointments = [
      appointment for appointment in appointments
      if datetime.strptime(appointment["dateTime"], "%Y-%m-%dT%H:%M:%S") >= today and appointment['DoctorID'] == doctor_id
  ]

  # Limit to 5 appointments on the server-side
  upcoming_appointments = upcoming_appointments[:5]

  return jsonify(upcoming_appointments), 200

@api.route("/patients/recent", methods=["GET"])
def get_recent_patients():
  doctor_id = current_user.UserID
  appointments = db_manager.get_appointments_by_doctor_id(doctor_id)
  today = datetime.today()

  recent_patients = []
  for appointment in appointments:
    if datetime.strptime(appointment["dateTime"], "%Y-%m-%dT%H:%M:%S") < today:
      patient = db_manager.get_patient_by_id(appointment['PatientID'])
      recent_patients.append({"name": patient.Name})

  return jsonify(recent_patients), 200

