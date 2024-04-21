from flask import Flask, render_template, request, jsonify, abort
from requests import post, delete
from . import connection_pool, database, celery_worker  # Assuming these are in different files
from .models import Patient  # Import Patient class from models.py

app = Flask(__name__)

OTHER_NODES = ['https://172.18.0.4:8083', 'https://172.18.0.3:8082', 'https://172.18.0.2:8081', 'https://172.18.0.5:8084', 'https://172.18.0.6:8085']


# Database connection related functions
def get_connection():
    return connection_pool.create_connection_pool().connection()


def get_patients():
    engine, session = database.create_database_connection()
    patients = session.query(Patient).all()  # Assuming Patient model is defined elsewhere
    patient_list = [{'PatientID': patient.PatientID, 'Name': patient.Name, 'DateOfBirth': patient.DateOfBirth,
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
        celery_worker.replicate_patient.delay(node, patient_data)  # Using delay for asynchronous task
    return jsonify({'message': 'patient created successfully'}), 201


def replicate_patient_to_node(node, patient_data):
    conn = get_connection()  # Assuming get_connection establishes a database connection
    cursor = conn.cursor()


    cursor.execute('INSERT INTO patients (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
                    (patient_data['Name'], patient_data['DateOfBirth'], patient_data['Gender'],
                     patient_data['ContactInformation'], patient_data['InsuranceInformation']))

    try:
        _extracted_from_replicate_patient_to_node_12(patient_data, cursor, conn, node)
    except Exception as e:
        app.logger.error(f'Error replicating patient to node {node}: {e}')
    finally:
        conn.close()


def _extracted_from_replicate_patient_to_node_12(patient_data, cursor, conn, node):
    # Extract patient data from dictionary
    name = patient_data['Name']
    date_of_birth = patient_data['DateOfBirth']
    gender = patient_data['Gender']
    contact_information = patient_data['ContactInformation']
    insurance_information = patient_data['InsuranceInformation']

    # Remote database insertion
    cursor.execute('INSERT INTO patients (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
                   (name, date_of_birth, gender, contact_information, insurance_information))
    conn.commit()

    # Send data to remote node (assuming API endpoint at /replicate)
    response = post(f'{node}/replicate', json=patient_data)
    if response.status_code != 201:
        app.logger.error(f'Failed to replicate patient to node {node}: {response.text}')

