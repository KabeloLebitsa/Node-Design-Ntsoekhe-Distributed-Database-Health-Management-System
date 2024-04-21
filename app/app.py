from dbutils.pooled_db import PooledDB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from celery import Celery
import sqlite3
from flask import Flask, render_template, request, jsonify, abort
import requests
<<<<<<< HEAD
from ntsoekheCreation import create_database

app = Flask(__name__)
create_database()

OTHER_NODES = ['https://172.18.0.4:8083', 'https://172.18.0.3:8082', 'https://172.18.0.2:8081', 'https://172.18.0.5:8084', 'https://172.18.0.6:8085']

# Create a connection pool
pool = PooledDB(
    creator=sqlite3,
    database='ntsoekhe.db',
    maxconnections=10,
    blocking=True
)

# Create an engine for SQLAlchemy
engine = create_engine('sqlite:///ntsoekhe.db')
Session = sessionmaker(bind=engine)
session = Session()

# Create a Celery instance
celery = Celery(app.name, broker='redis://localhost:6379/0')

# Endpoint for the home page
@app.route('/')
def index():
    return render_template('welcome_page.html')

@app.route('/options')
def the_options():
=======
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
>>>>>>> 39db4eac43d5a94f67bffb37a271fbd52dee8936
    return render_template('options.html')

@app.route('/patients/create', methods=['GET'])
def create_patient_form():
    return render_template('create_patient.html')

# Endpoint for replication
@app.route('/replicate', methods=['POST'])
def replicate_patient():
    replicated_data = request.get_json()
    conn = pool.connection()
    cursor = conn.cursor()
<<<<<<< HEAD
    cursor.execute('INSERT INTO patients (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
                   (replicated_data['Name'], replicated_data['DateOfBirth'], replicated_data['Gender'], replicated_data['ContactInformation'], replicated_data['InsuranceInformation']))
=======

    # Insert the replicated patient into the database
    cursor.execute('INSERT INTO patients (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
               ( replicated_data['Name'], replicated_data['DateOfBirth'], replicated_data['Gender'], replicated_data['ContactInformation'], replicated_data['InsuranceInformation']))

>>>>>>> 39db4eac43d5a94f67bffb37a271fbd52dee8936
    conn.commit()
    conn.close()
    return jsonify({'message': 'patient replicated successfully'}), 201

@app.route('/patients', methods=['POST'])
<<<<<<< HEAD
def create_patient():
    patient_data = request.get_json()
=======
def create_patient():  
    # Get the patient data from the request body
    patient_data = request.get_json()
    
     # Send patient data to other nodes including self
>>>>>>> 39db4eac43d5a94f67bffb37a271fbd52dee8936
    for node in OTHER_NODES:
        try:
            celery.send_task('replicate_patient', args=[node, patient_data])
        except Exception as e:
            app.logger.error(f'Error replicating patient to node {node}: {e}')
<<<<<<< HEAD
=======

    # Return a response indicating success
    
>>>>>>> 39db4eac43d5a94f67bffb37a271fbd52dee8936
    return jsonify({'message': 'patient created successfully'}), 201

@celery.task
def replicate_patient(node, patient_data):
    replicated_data = patient_data
    conn = pool.connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO patients (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
                   (replicated_data['Name'], replicated_data['DateOfBirth'], replicated_data['Gender'], replicated_data['ContactInformation'], replicated_data['InsuranceInformation']))
    conn.commit()
    conn.close()
    try:
        response = requests.post(f'{node}/replicate', json=patient_data)
        if response.status_code != 201:
            app.logger.error(f'Failed to replicate patient to node {node}: {response.text}')
    except Exception as e:
        app.logger.error(f'Error replicating patient to node {node}: {e}')

@app.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    conn = pool.connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients WHERE PatientID = ?', (patient_id,))
    patient = cursor.fetchone()
    if patient is None:
        conn.close()
        abort(404, 'Patient not found')
    cursor.execute('DELETE FROM patients WHERE PatientID = ?', (patient_id,))
    conn.commit()
    conn.close()
<<<<<<< HEAD
=======
    
    # Replicate delete operation to other nodes
>>>>>>> 39db4eac43d5a94f67bffb37a271fbd52dee8936
    for node in OTHER_NODES:
        try:
            response = requests.delete(f'{node}/patients/deleteAcross/{patient_id}')
            if response.status_code != 200:
                app.logger.error(f'Failed to replicate delete operation to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating delete operation to node {node}: {e}')
<<<<<<< HEAD
=======
    
    # Return a response indicating success
>>>>>>> 39db4eac43d5a94f67bffb37a271fbd52dee8936
    return jsonify({'message': 'Patient deleted successfully'}), 200

@app.route('/patients/deleteAcross/<int:patient_id>', methods=['DELETE'])
def delete_every_patient(patient_id):
<<<<<<< HEAD
    conn = pool.connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients WHERE PatientID = ?', (patient_id,))
    patient = cursor.fetchone()
    if patient is None:
        conn.close()
        return jsonify({'message': 'Patient not found'}), 404
    cursor.execute('DELETE FROM patients WHERE PatientID = ?', (patient_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Patient being deleted across successfully'}), 200

=======
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
>>>>>>> 39db4eac43d5a94f67bffb37a271fbd52dee8936
@app.route('/patients', methods=['GET'])

def get_patients():
<<<<<<< HEAD
    patients = session.query(Patient).all()
    patient_list = [{'PatientID': patient.PatientID, 'Name': patient.Name, 'DateOfBirth': patient.DateOfBirth, 'Gender': patient.Gender, 'ContactInformation': patient.ContactInformation, 'InsuranceInformation': patient.InsuranceInformation} for patient in patients]
    return render_template('display_patients.html', patients=patient_list)
=======
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



>>>>>>> 39db4eac43d5a94f67bffb37a271fbd52dee8936

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
