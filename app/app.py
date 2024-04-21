from dbutils.pooled_db import PooledDB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from celery import Celery
import sqlite3
from flask import Flask, render_template, request, jsonify, abort
import requests
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
    cursor.execute('INSERT INTO patients (Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?)',
                   (replicated_data['Name'], replicated_data['DateOfBirth'], replicated_data['Gender'], replicated_data['ContactInformation'], replicated_data['InsuranceInformation']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'patient replicated successfully'}), 201

@app.route('/patients', methods=['POST'])
def create_patient():
    patient_data = request.get_json()
    for node in OTHER_NODES:
        try:
            celery.send_task('replicate_patient', args=[node, patient_data])
        except Exception as e:
            app.logger.error(f'Error replicating patient to node {node}: {e}')
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
    for node in OTHER_NODES:
        try:
            response = requests.delete(f'{node}/patients/deleteAcross/{patient_id}')
            if response.status_code != 200:
                app.logger.error(f'Failed to replicate delete operation to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating delete operation to node {node}: {e}')
    return jsonify({'message': 'Patient deleted successfully'}), 200

@app.route('/patients/deleteAcross/<int:patient_id>', methods=['DELETE'])
def delete_every_patient(patient_id):
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

@app.route('/patients', methods=['GET'])
def get_patients():
    patients = session.query(Patient).all()
    patient_list = [{'PatientID': patient.PatientID, 'Name': patient.Name, 'DateOfBirth': patient.DateOfBirth, 'Gender': patient.Gender, 'ContactInformation': patient.ContactInformation, 'InsuranceInformation': patient.InsuranceInformation} for patient in patients]
    return render_template('display_patients.html', patients=patient_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
