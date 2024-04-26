<<<<<<< HEAD
# app.py

import flask
import os
from config import app_config
from flask import Flask, redirect, render_template, request, url_for, flash, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user  
from database import DatabaseManager
from models import User

db_manager = DatabaseManager()

app = Flask(__name__)
app.config.from_object(app_config)
# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_page'


# Required: Automatically ensure there is an admin user on App worker startup
db_manager.ensure_admin_user()
def create_dashboard_route(role):
    if role not in ['admin', 'doctor', 'patient']:
        raise ValueError('Invalid role')
    
    def dashboard():
        return render_template(f"{role}_dashboard.html")
    dashboard.__name__ = f"{role}_dashboard"  # Set a unique function name based on the role
    return dashboard

@app.route('/user/info')
@login_required
def user_info():
    user_id = current_user.id
    with db_manager.get_db() as db:
        user = db.query(User).get(user_id)
        if not user:
            flask.abort(404, description="User not found")
        user_data = {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    return jsonify(user_data)

@login_manager.user_loader
def load_user(user_id):
    with db_manager.get_db() as db:
        return db.query(User).get(int(user_id))

# Home page route
@app.route('/')
def index():
    return render_template('index.html')


# User loader function for Flask-Login (using imported function)
@app.login_manager.user_loader
def load_user_route(user_id):
    return db_manager.load_user(user_id)  # Call the imported function


# Login page route
@app.route('/login_page')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('login.html')

    username = request.form.get('Username', '')
    password = request.form.get('Password', '')

    if not username or not password:
        flask.abort(400)

    user = db_manager.authenticate_user(username, password)
    if not user:
        flask.abort(401)
    login_user(user)
    # User authenticated, proceed with logic using refreshed current_user
    role_dashboard_urls = {
        'admin': 'admin_dashboard',
        'doctor': 'doctor_dashboard',
        'patient': 'patient_dashboard'
    }
    return jsonify({'redirect': url_for(role_dashboard_urls[current_user.Role])})

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

# Display patients page route (assuming functionality in the API)
@app.route('/display/patients')
@login_required
def display_patients():
    flash('Use the API endpoint to retrieve patient data.')
    return render_template('display_patients.html')

# Create user page route (assuming functionality in the API)
@app.route('/create/users')
@login_required
def create_user():
    flash('Use the API endpoint to create new patients.')
    return render_template('create_user.html')

# Create patients page route 
@app.route('/create/patients')
@login_required
def create_patient():
    flash('Use the API endpoint to create new patients.')
    return render_template('create_patient.html')
# Create doctors page route 
@app.route('/create/doctors')
@login_required
def create_doctor():
    flash('Use the API endpoint to create new doctors.')
    return render_template('create_doctor.html')
# Main function
if __name__ == '__main__':
    debug_mode = os.environ.get('DEBUG_MODE', 'True').lower() in ['true', '1', 't']
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    app.run(host=host, port=port, debug=debug_mode)
=======
from flask import Flask, jsonify, request,render_template
import sqlite3
import requests
import os   
import json
from ntsoekheCreation import create_database
app = Flask(__name__)
create_database()
# List of other nodes in the network
OTHER_NODES = ['http://172.18.0.4:8083','http://172.18.0.3:8082','http://172.18.0.2:8081','http://172.18.0.5:8084','http://172.18.0.6:8085']

PORT = int(os.environ.get('PORT', 8081))
# Endpoint for the home page
@app.route('/')
def index():
    return render_template('welcomePoe.html')
@app.route('/options')
def theOptions():
    return render_template('options.html')

@app.route('/patients/create', methods=['GET'])
def create_patient_form():
    return render_template('create_patient.html')

#endpoint for replication
@app.route('/replicate', methods=['POST'])
def replicate_patient():
    replicated_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the replicated patient into the database
    cursor.execute('INSERT INTO patients (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
               ( replicated_data['Name'], replicated_data['DateOfBirth'], replicated_data['Gender'], replicated_data['ContactInformation'], replicated_data['InsuranceInformation']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Return a response indicating success
    return jsonify({'message': 'patient replicated successfully'}), 201

# Endpoint for creating a new patient
@app.route('/patients', methods=['POST'])
def create_patient():  
    # Get the patient data from the request body
    patient_data = request.get_json()
    
     # Send patient data to other nodes including self
    for node in OTHER_NODES:
        try:

            response = requests.post(f'{node}/replicate', json=patient_data)
            
            if response.status_code != 201:
                app.logger.error(f'Failed to replicate patient to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating patient to node {node}: {e}')

    # Return a response indicating success
    
    return jsonify({'message': 'patient created successfully'}), 201


# Endpoint for updating an existing patient
@app.route('/patients/<int:patient_id>', methods=['PUT', 'PATCH'])
def update_patient(patient_id):
    # Get the updated patient data from the request body
    updated_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Update the patient information in the database
    if 'Name' in updated_data:
        cursor.execute('UPDATE patients SET Name = ? WHERE PatientID = ?', (updated_data['Name'], patient_id))
    if 'DateOfBirth' in updated_data:
        cursor.execute('UPDATE patients SET DateOfBirth = ? WHERE PatientID = ?', (updated_data['DateOfBirth'], patient_id))
    if 'Gender' in updated_data:
        cursor.execute('UPDATE patients SET Gender = ? WHERE PatientID = ?', (updated_data['Gender'], patient_id))
    if 'ContactInformation' in updated_data:
        cursor.execute('UPDATE patients SET ContactInformation = ? WHERE PatientID = ?', (updated_data['ContactInformation'], patient_id))
    if 'InsuranceInformation' in updated_data:
        cursor.execute('UPDATE patients SET InsuranceInformation = ? WHERE PatientID = ?', (updated_data['InsuranceInformation'], patient_id))

    conn.commit()

    # Close the database connection
    conn.close()

    # Replicate the updated patient data to other nodes
    for node in OTHER_NODES:
        try:
            response = requests.put(f'{node}/patients/{patient_id}', json=updated_data)
            if response.status_code != 200:
                app.logger.error(f'Failed to replicate update to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating update to node {node}: {e}')

    # Return a response indicating success
    return jsonify({'message': 'patient updated successfully'}), 200

# Endpoint for deleting a patient
@app.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Check if the patient exists
    cursor.execute('SELECT * FROM patients WHERE PatientID = ?', (patient_id,))
    patient = cursor.fetchone()

    if patient is None:
        # Close the database connection
        conn.close()
        return jsonify({'message': 'Patient not found'}), 404

    # Delete the patient from the database
    cursor.execute('DELETE FROM patients WHERE PatientID = ?', (patient_id,))
    conn.commit()

    # Close the database connection
    conn.close()
    
    # Replicate delete operation to other nodes
    for node in OTHER_NODES:
        try:
            response = requests.delete(f'{node}/patients/deleteAcross/{patient_id}')
            if response.status_code != 200:
                app.logger.error(f'Failed to replicate delete operation to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating delete operation to node {node}: {e}')
    
    # Return a response indicating success
    return jsonify({'message': 'Patient deleted successfully'}), 200

@app.route('/patients/deleteAcross/<int:patient_id>', methods=['DELETE'])
def delete_every_patient(patient_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Check if the patient exists
    cursor.execute('SELECT * FROM patients WHERE PatientID = ?', (patient_id,))
    patient = cursor.fetchone()

    if patient is None:
        # Close the database connection
        conn.close()
        return jsonify({'message': 'Patient not found'}), 404

    # Delete the patient from the database
    cursor.execute('DELETE FROM patients WHERE PatientID = ?', (patient_id,))
    conn.commit()

    # Close the database connection
    conn.close()
    return jsonify({'message': 'Patient being  deleted across successfully'}), 200

# Endpoint for retrieving all patients
@app.route('/patients', methods=['GET'])

def get_patients():
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Retrieve all patients from the database
    cursor.execute('SELECT * FROM patients')
    patients = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the patients to a list of dictionaries
    patient_list = [{'PatientID': patient[0], 'Name': patient[1], 'DateOfBirth': patient[2], 'Gender': patient[3], 'ContactInformation': patient[4], 'InsuranceInformation': patient[5]} for patient in patients]

    # Return the patients as HTML template
    return render_template('display_patients.html', patients=patient_list)


#endpoint for replication
@app.route('/replicate', methods=['POST'])
def replicate_doctor():
    replicated_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the replicated doctor into the database
    cursor.execute('INSERT INTO doctors (DoctorID, Name, Specialization, ContactInformation, DepartmentID) VALUES (?, ?, ?, ?, ?)',
               (replicated_data['DoctorID'], replicated_data['Name'], replicated_data['Specialization'], replicated_data['ContactInformation'], replicated_data['DepartmentID']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Return a response indicating success
    return jsonify({'message': 'doctor replicated successfully'}), 201

# Endpoint for creating a new doctor
@app.route('/doctors', methods=['POST'])
def create_doctor():  
    # Get the doctor data from the request body
    doctor_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the new doctor into the database
    cursor.execute('INSERT INTO doctors (DoctorID, Name, Specialization, ContactInformation, DepartmentID) VALUES (?, ?, ?, ?, ?)',
               (doctor_data['DoctorID'], doctor_data['Name'], doctor_data['Specialization'], doctor_data['ContactInformation'], doctor_data['DepartmentID']))


    conn.commit()

    # Close the database connection
    conn.close()

    # Send doctor data to other nodes
    for node in OTHER_NODES:
        try:

            response = requests.post(f'{node}/replicate', json=doctor_data)
            
            if response.status_code != 201:
                app.logger.error(f'Failed to replicate doctor to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating doctor to node {node}: {e}')

    # Return a response indicating success
    return jsonify({'message': 'doctor created successfully'}), 201

# Endpoint for retrieving all doctors
@app.route('/doctors', methods=['GET'])
def get_doctors():
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Retrieve all doctors from the database
    cursor.execute('SELECT * FROM doctors')
    doctors = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the doctors to a list of dictionaries
    doctor_list = [{'DoctorID': doctor[0], 'Name': doctor[1], 'Specialization': doctor[2], 'ContactInformation': doctor[3], 'DepartmentID': doctor[4]} for doctor in doctors]

    # Return the doctors as JSON
    return jsonify({'doctors': doctor_list})




#endpoint for replication
@app.route('/replicate', methods=['POST'])
def replicate_nurse():
    replicated_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the replicated nurse into the database
    cursor.execute('INSERT INTO nurses (Name, ContactInformation, DepartmentID) VALUES (?, ?, ?)',
               (replicated_data['Name'], replicated_data['ContactInformation'], replicated_data['DepartmentID']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Return a response indicating success
    return jsonify({'message': 'nurse replicated successfully'}), 201

# Endpoint for creating a new nurse
@app.route('/nurses', methods=['POST'])
def create_nurse():  
    # Get the nurse data from the request body
    nurse_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the new nurse into the database
    cursor.execute('INSERT INTO nurses (Name, ContactInformation, DepartmentID) VALUES (?, ?, ?)',
               (nurse_data['Name'], nurse_data['ContactInformation'], nurse_data['DepartmentID']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Send nurse data to other nodes
    for node in OTHER_NODES:
        try:

            response = requests.post(f'{node}/replicate', json=nurse_data)
            
            if response.status_code != 201:
                app.logger.error(f'Failed to replicate nurse to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating nurse to node {node}: {e}')

    # Return a response indicating success
    return jsonify({'message': 'nurse created successfully'}), 201

# Endpoint for retrieving all nurses
@app.route('/nurses', methods=['GET'])
def get_nurses():
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Retrieve all nurses from the database
    cursor.execute('SELECT * FROM nurses')
    nurses = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the nurses to a list of dictionaries
    nurse_list = [{'NurseID': nurse[0], 'Name': nurse[1], 'ContactInformation': nurse[2], 'DepartmentID': nurse[3]} for nurse in nurses]

    # Return the nurses as JSON
    return jsonify({'nurses': nurse_list})



#endpoint for replication
@app.route('/replicate', methods=['POST'])
def replicate_department():
    replicated_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the replicated department into the database
    cursor.execute('INSERT INTO departments (DepartmentID, DepartmentName, DepartmentHead, Location) VALUES (?, ?, ?, ?)',
               (replicated_data['DepartmentID'], replicated_data['DepartmentName'], replicated_data['DepartmentHead'], replicated_data['Location']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Return a response indicating success
    return jsonify({'message': 'department replicated successfully'}), 201

# Endpoint for creating a new department
@app.route('/departments', methods=['POST'])
def create_department():  
    # Get the department data from the request body
    department_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

   # Insert the new department into the database
    cursor.execute('INSERT INTO departments (DepartmentName, DepartmentHead, Location) VALUES (?, ?, ?)',
               (department_data['DepartmentName'], department_data['DepartmentHead'], department_data['Location']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Send department data to other nodes
    for node in OTHER_NODES:
        try:

            response = requests.post(f'{node}/replicate', json=department_data)
            
            if response.status_code != 201:
                app.logger.error(f'Failed to replicate department to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating department to node {node}: {e}')

    # Return a response indicating success
    return jsonify({'message': 'department created successfully'}), 201

# Endpoint for retrieving all departments
@app.route('/departments', methods=['GET'])
def get_departments():
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Retrieve all departments from the database
    cursor.execute('SELECT * FROM departments')
    departments = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the departments to a list of dictionaries
    department_list = [{'DepartmentID': department[0], 'DepartmentName': department[1], 'DepartmentHead': department[2], 'Location': department[3]} for department in departments]

    # Return the departments as JSON
    return jsonify({'departments': department_list})



#endpoint for replication
@app.route('/replicate', methods=['POST'])
def replicate_medical_record():
    replicated_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the replicated medical_record into the database
    cursor.execute('INSERT INTO medical_records (PatientID, Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?, ?)',
               (replicated_data['PatientID'], replicated_data['Name'], replicated_data['DateOfBirth'], replicated_data['Gender'], replicated_data['ContactInformation'], replicated_data['InsuranceInformation']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Return a response indicating success
    return jsonify({'message': 'medical_record replicated successfully'}), 201

# Endpoint for creating a new medical_record
@app.route('/medical_records', methods=['POST'])
def create_medical_record():  
    # Get the medical_record data from the request body
    medical_record_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the new medical_record into the database
    cursor.execute('INSERT INTO medical_records (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
               (medical_record_data['Name'], medical_record_data['DateOfBirth'], medical_record_data['Gender'], medical_record_data['ContactInformation'], medical_record_data['InsuranceInformation']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Send medical_record data to other nodes
    for node in OTHER_NODES:
        try:

            response = requests.post(f'{node}/replicate', json=medical_record_data)
            
            if response.status_code != 201:
                app.logger.error(f'Failed to replicate medical_record to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating medical_record to node {node}: {e}')

    # Return a response indicating success
    return jsonify({'message': 'medical_record created successfully'}), 201

# Endpoint for retrieving all medical_records
@app.route('/medical_records', methods=['GET'])
def get_medical_records():
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Retrieve all medical_records from the database
    cursor.execute('SELECT * FROM medical_records')
    medical_records = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the medical_records to a list of dictionaries
    medical_record_list = [{'PatientID': medical_record[0], 'Name': medical_record[1], 'DateOfBirth': medical_record[2], 'Gender': medical_record[3], 'ContactInformation': medical_record[4], 'InsuranceInformation': medical_record[5]} for medical_record in medical_records]

    # Return the medical_records as JSON
    return jsonify({'medical_records': medical_record_list})



#endpoint for replication
@app.route('/replicate', methods=['POST'])
def replicate_prescription():
    replicated_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the replicated prescription into the database
    cursor.execute('INSERT INTO prescriptions (PatientID, Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?, ?)',
               (replicated_data['PatientID'], replicated_data['Name'], replicated_data['DateOfBirth'], replicated_data['Gender'], replicated_data['ContactInformation'], replicated_data['InsuranceInformation']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Return a response indicating success
    return jsonify({'message': 'prescription replicated successfully'}), 201

# Endpoint for creating a new prescription
@app.route('/prescriptions', methods=['POST'])
def create_prescription():  
    # Get the prescription data from the request body
    prescription_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the new prescription into the database
    cursor.execute('INSERT INTO prescriptions (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
               (prescription_data['Name'], prescription_data['DateOfBirth'], prescription_data['Gender'], prescription_data['ContactInformation'], prescription_data['InsuranceInformation']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Send prescription data to other nodes
    for node in OTHER_NODES:
        try:

            response = requests.post(f'{node}/replicate', json=prescription_data)
            
            if response.status_code != 201:
                app.logger.error(f'Failed to replicate prescription to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating prescription to node {node}: {e}')

    # Return a response indicating success
    return jsonify({'message': 'prescription created successfully'}), 201

# Endpoint for retrieving all prescriptions
@app.route('/prescriptions', methods=['GET'])
def get_prescriptions():
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Retrieve all prescriptions from the database
    cursor.execute('SELECT * FROM prescriptions')
    prescriptions = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the prescriptions to a list of dictionaries
    prescription_list = [{'PatientID': prescription[0], 'Name': prescription[1], 'DateOfBirth': prescription[2], 'Gender': prescription[3], 'ContactInformation': prescription[4], 'InsuranceInformation': prescription[5]} for prescription in prescriptions]

    # Return the prescriptions as JSON
    return jsonify({'prescriptions': prescription_list})



#endpoint for replication
@app.route('/replicate', methods=['POST'])
def replicate_billing():
    replicated_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the replicated billing into the database
    cursor.execute('INSERT INTO billings (PatientID, Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?, ?)',
               (replicated_data['PatientID'], replicated_data['Name'], replicated_data['DateOfBirth'], replicated_data['Gender'], replicated_data['ContactInformation'], replicated_data['InsuranceInformation']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Return a response indicating success
    return jsonify({'message': 'billing replicated successfully'}), 201

# Endpoint for creating a new billing
@app.route('/billings', methods=['POST'])
def create_billing():  
    # Get the billing data from the request body
    billing_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the new billing into the database
    cursor.execute('INSERT INTO billings (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
               (billing_data['Name'], billing_data['DateOfBirth'], billing_data['Gender'], billing_data['ContactInformation'], billing_data['InsuranceInformation']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Send billing data to other nodes
    for node in OTHER_NODES:
        try:

            response = requests.post(f'{node}/replicate', json=billing_data)
            
            if response.status_code != 201:
                app.logger.error(f'Failed to replicate billing to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating billing to node {node}: {e}')

    # Return a response indicating success
    return jsonify({'message': 'billing created successfully'}), 201

# Endpoint for retrieving all billings
@app.route('/billings', methods=['GET'])
def get_billings():
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Retrieve all billings from the database
    cursor.execute('SELECT * FROM billings')
    billings = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the billings to a list of dictionaries
    billing_list = [{'PatientID': billing[0], 'Name': billing[1], 'DateOfBirth': billing[2], 'Gender': billing[3], 'ContactInformation': billing[4], 'InsuranceInformation': billing[5]} for billing in billings]

    # Return the billings as JSON
    return jsonify({'billings': billing_list})



#endpoint for replication
@app.route('/replicate', methods=['POST'])
def replicate_appointment():
    replicated_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the replicated appointment into the database
    cursor.execute('INSERT INTO appointments (PatientID, Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?, ?)',
               (replicated_data['PatientID'], replicated_data['Name'], replicated_data['DateOfBirth'], replicated_data['Gender'], replicated_data['ContactInformation'], replicated_data['InsuranceInformation']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Return a response indicating success
    return jsonify({'message': 'appointment replicated successfully'}), 201

# Endpoint for creating a new appointment
@app.route('/appointments', methods=['POST'])
def create_appointment():  
    # Get the appointment data from the request body
    appointment_data = request.get_json()
    
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Insert the new appointment into the database
    cursor.execute('INSERT INTO appointments (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
               (appointment_data['Name'], appointment_data['DateOfBirth'], appointment_data['Gender'], appointment_data['ContactInformation'], appointment_data['InsuranceInformation']))

    conn.commit()

    # Close the database connection
    conn.close()

    # Send appointment data to other nodes
    for node in OTHER_NODES:
        try:

            response = requests.post(f'{node}/replicate', json=appointment_data)
            
            if response.status_code != 201:
                app.logger.error(f'Failed to replicate appointment to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating appointment to node {node}: {e}')

    # Return a response indicating success
    return jsonify({'message': 'appointment created successfully'}), 201

# Endpoint for retrieving all appointments
@app.route('/appointments', methods=['GET'])
def get_appointments():
    # Connect to the SQLite database
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

    # Retrieve all appointments from the database
    cursor.execute('SELECT * FROM appointments')
    appointments = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Convert the appointments to a list of dictionaries
    appointment_list = [{'PatientID': appointment[0], 'Name': appointment[1], 'DateOfBirth': appointment[2], 'Gender': appointment[3], 'ContactInformation': appointment[4], 'InsuranceInformation': appointment[5]} for appointment in appointments]

    # Return the appointments as JSON
    return jsonify({'appointments': appointment_list})




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)




    
>>>>>>> 57846e8bc2350b31ad2682a8c4683fd0e9b6813c
