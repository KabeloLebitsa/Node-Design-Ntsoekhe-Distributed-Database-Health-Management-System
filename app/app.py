#appy.py

from flask import Flask, render_template, request, jsonify, abort
from requests import post, delete
from . import connection_pool, database, celery_worker 
from .models import Patient  

OTHER_NODES = ['https://172.18.0.4:8083', 'https://172.18.0.3:8082', 'https://172.18.0.2:8081', 'https://172.18.0.5:8084', 'https://172.18.0.6:8085']

app = Flask(__name__)

# Database connection related functions
def get_connection():
    return connection_pool.create_connection_pool().connection()


def get_patients():
    engine, session = database.create_database_connection()
    patients = session.query(Patient).all()
    patient_list = [{'PatientID': patient.PatientID, 'Name': patient.Name, 'DateOfBirth': patient.DateOfBirth.strftime('%Y-%m-%d'),
                     'Gender': patient.Gender, 'ContactInformation': patient.ContactInformation,
                     'InsuranceInformation': patient.InsuranceInformation} for patient in patients]
    return render_template('display_patients.html', patients=patient_list)


@app.route('/')
def index():
    return render_template('welcome_page.html')


@app.route('/options')
def the_options():
    return render_template('options.html')


@app.route('/patients/create', methods=['GET'])
def create_patient_form():
    return render_template('create_patient.html')


# Endpoint for replication
@app.route('/replicate', methods=['POST'])
def replicate_patient():
    replicated_data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO patients (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
                   (replicated_data['Name'], replicated_data['DateOfBirth'], replicated_data['Gender'],
                    replicated_data['ContactInformation'], replicated_data['InsuranceInformation']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'patient replicated successfully'}), 201


@app.route('/patients', methods=['POST'])
def create_patient():
    patient_data = request.get_json()
    for node in OTHER_NODES:
        celery_worker.replicate_patient.delay(node, patient_data)
    new_patient = Patient(Name=patient_data['Name'], DateOfBirth=patient_data['DateOfBirth'],
                           Gender=patient_data['Gender'], ContactInformation=patient_data['ContactInformation'],
                           InsuranceInformation=patient_data['InsuranceInformation'])
    engine, session = database.create_database_connection()
    session.add(new_patient)
    session.commit()
    session.close()
    return jsonify({'message': 'patient created successfully'}), 201


def replicate_patient_to_node(node, patient_data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO patients (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
                   (patient_data['Name'], patient_data['DateOfBirth'], patient_data['Gender'],
                    patient_data['ContactInformation'], patient_data['InsuranceInformation']))
    conn.commit()
    conn.close()
    try:
        response = post(f'{node}/replicate', json=patient_data)
        if response.status_code != 201:
            app.logger.error(f'Failed to replicate patient to node {node}: {response.text}')
    except Exception as e:
        app.logger.error(f'Error replicating patient to node {node}: {e}')


@app.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients WHERE PatientID = ?', (patient_id,))
    patient = cursor.fetchone()
