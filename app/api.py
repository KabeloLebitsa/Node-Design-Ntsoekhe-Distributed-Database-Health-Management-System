#api.py

import datetime
from sqlite3 import IntegrityError
from flask import Blueprint, request, jsonify, render_template,current_app
from flask_login import login_required, current_user
from exceptions import PatientDeletionError, PatientNotFoundException, InvalidRequestException, DatabaseIntegrityError, InternalServerError
from models import Patient, Doctor, Nurse, Department, Appointment, Prescription, Billing, User
from database import DatabaseManager
import logging
import requests
from config import Config
import json
import logging
api = Blueprint('api', __name__)
db_manager = DatabaseManager()


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# Create a logger instance
logger = logging.getLogger(__name__)

def create_user(user_data):
    # Get the patient data from the request body
    #user_data = request.get_json()
    if not user_data:
        return jsonify ({"message":"Missing user data"}),400

    # Create the patient locally
    try:
        user_id = db_manager.insert_user(user_data)
        return user_id
    except InvalidRequestException as e:
        logging.error(f"Invalid request: {str(e)}")
        return jsonify({'message': str(e)}), 400
    except DatabaseIntegrityError as e:
        logging.error(f"Database integrity error: {str(e)}")
        return jsonify({'message': str(e)}), 501
    except InternalServerError as e:
        print(f"Error creating user: {e}")
        return jsonify({'message': 'Failed to create user'}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'message': 'Internal server error'}), 502

def create_patient(patient_data):
    #patient_data = request.get_json()
    required_fields = ["Name", "DateOfBirth", "Gender", "PhoneNumber"]

    if missing_fields := [
        field for field in required_fields if field not in patient_data
    ]:
        return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    try:
        db_manager.insert_patient(patient_data)
       # return jsonify({'redirect': '/dashboard/admin'}), 201
    except IntegrityError as e:
        return jsonify({'message': 'Failed to create patient (data integrity issue)'}), 500
    except Exception as e:
        print(f"Error creating patient: {e}")
        return jsonify({'message': 'Failed to create patient'}), 500

@api.route('/create/user_patient', methods=['POST'])
def create_user_patient():
    # Get the combined data from the request
    
    data = request.get_json()
    
    # Extract user and patient data from the combined data
    user_data = {
        "Username": data.get("Username"),
        "Password": data.get("Password"),
        "Role": "patient"
    }
    patient_data = {
        "Name": data.get("Name"),
        "DateOfBirth": data.get("DateOfBirth"),
        "Gender": data.get("Gender"),
        "PhoneNumber": data.get("PhoneNumber"),
        "PatientID": None  # Placeholder for the user ID
    }
    
    try:
        # Create the user and get the user ID
          # Implement this function to handle user creation in the database
        user_id =create_user(user_data)

        patient_data["PatientID"] = user_id
        
    #     # Create the patient using the user ID
        create_patient(patient_data)  # Implement this function to handle patient creation in the database
        
    #     return jsonify({"message": "User and patient created successfully"}), 201
    except Exception as e:
    #     # Handle any errors that may occur during the process
        print(f"Unexpected error: {e}")
        return jsonify({"error": f"Error creating user and patient: {e}"}), 500
    return jsonify({'message': 'Patient created successfully' }), 201


#REPLICATION 
@api.route('/create/replicate', methods=['POST'])
def replicate_user_patients():
    # Get the patient data from the request body
    patient_data = request.get_json()
    
    # Send patient data to other nodes including self
    all_success = True

    for node in Config.REPLICATION_NODES:
        try:
            response = requests.post(f"{node}/create/user_patient", json=patient_data)
            if response.status_code != 201:
                #print("TRYING TO REPLICATE BUT FAILS \n\n")# Log error and mark the replication as failed
                logging.error(f'Failed to replicate patient to node {node}: {response.text}')
                all_success = False
        except Exception as e:
            # Log exception and mark the replication as failed
            logging.error(f'Error replicating patient to node {node}: {e}')
            all_success = False

    if all_success:
        return jsonify({'message': 'patient created successfully'}), 201
    else:
        return jsonify({'message': 'Replication failed to one or more nodes'}), 500






# def create_patients():
     
#     # Get the patient data from the request body
#     patient_data = request.get_json()
    
#     #  # Send patient data to other nodes including self
#     for node in Config.NODES:
        
#         try:
#             response = requests.post(f"{node}/create/user_patient", json=patient_data)
            
#            # print("START")
#             if response.status_code != 201:
#                 #logging.error(f'Failed to replicate patient to node {node}: {response.text}')
#                 return jsonify({'message': 'failed to establish connection'}), 501
#         except Exception as e:
#             logging.error(f'Error replicating patient to node {node}: {e}')
#             return jsonify({'message': 'patient  with error :{e}'}), 500
#         # Return a response indicating success
#        # print("STARTingASFHAHEGFWAHJAMafdmafdgmJ\n\n")
#     return jsonify({'message': 'patient created successfully'}), 201
#     '''



































#@api.route('/create/users', methods=['POST'])
'''
@api.route('/create', methods=['POST'])
def create_the_patient():  
    # Get the patient data from the request body
    patient_data = request.get_json()
    
     # Send patient data to other nodes including self
    for node in Config.NODES:
        try:

            response = requests.post(f'{node}/create/patients', json=patient_data)
            
            if response.status_code != 201:
                api.logger.error(f'Failed to replicate patient to node {node}: {response.text}')
        except Exception as e:
            api.logger.error(f'Error replicating patient to node {node}: {e}')
            #return jsonify({"message":"error"})

    # Return a response indicating success
    
    return jsonify({'message': 'patient created successfully'}), 201

#--------------------------------------------------------------------------------
'''


# Endpoint for creating a patient
#@api.route('/create/patients', methods=['POST'])
#@login_required


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


#@api.route('/patients/<string:patient_id>', methods=['DELETE'])
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


@api.route('/patients/<string:patient_id>', methods=['DELETE'])
#deleting patient across
def delete_patient(patient_id):
    # Flag to track if the deletion was successful on all nodes
    all_success = True

    # Iterate through each node
    for node in Config.NODES:
        try:
            # Send a DELETE request to the current node
            response = requests.delete(f"{node}/patients/{patient_id}")
            print("tried node :",node)
            # Check if the request was successful (status code 200 for delete)
            if response.status_code != 200:
                # Log an error message if the request failed
                logging.error(f'Failed to delete patient on node {node}: {response.text}')
                # Mark the replication as not successful
                all_success = False
        except Exception as e:
            # Log the exception if an error occurs
            logging.error(f'Error deleting patient on node {node}: {e}')
            # Mark the replication as not successful
            all_success = False

    # Check if all deletions were successful
    if all_success:
        return jsonify({'message': 'Patient deleted successfully on all nodes'}), 200
    else:
        return jsonify({'message': 'Failed to delete patient on one or more nodes'}), 500


















# Endpoint for creating a doctor
@api.route('/create/doctors', methods=['POST'])
#@login_required
def create_doctor():
    doctor_data = request.get_json()
    required_fields = ["Name", "Specialization", "PhoneNumber", "DepartmentName"]
    with db_manager.get_db() as conn:
        DepartmentID = conn.query(Department).filter(Department.DepartmentName == doctor_data['DepartmentName']).one_or_none()
    doctor_data['DepartmentID'] = DepartmentID
    if missing_fields := [
        field for field in required_fields if field not in doctor_data
    ]:
        return jsonify({'message': f'Missing required fields: {", ".join(missing_fields)}'}), 400

    try:
        db_manager.insert_doctor(**doctor_data)
        return jsonify({'redirect': '/dashboard/admin'}), 201
    except IntegrityError as e:
        return jsonify({'message': 'Failed to create doctor (data integrity issue)'}), 500
    except Exception as e:
        print(f"Error creating doctor: {e}")
        return jsonify({'message': 'Failed to create doctor'}), 500

@api.route(/patients/display', methods=["GET"])
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

