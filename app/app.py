from dbutils.pooled_db import PooledDB
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from celery import Celery
import sqlite3
from flask import Flask, render_template, request, jsonify, abort
import requests
import os
import json
app = Flask(__name__)

# List of other nodes in the network
OTHER_NODES = ['http://172.17.0.2:8081','http://172.17.0.3:8082']
PORT = int(os.environ.get('PORT', 8081))
# Endpoint for the home page
@app.route('/')
def index():
    return render_template('create_patient.html')

@app.route('/patients/create', methods=['GET'])
def create_patient_form():
    return render_template('create_patient.html')

# Endpoint for replication
@app.route('/replicate', methods=['POST'])
def replicate_patient():
    replicated_data = request.get_json()
    conn = pool.connection()
    cursor = conn.cursor()

    # Insert the replicated patient into the database
    cursor.execute('INSERT INTO patients (PatientID, Name, DateOfBirth, Gender, ContactInformation, InsuranceInformation) VALUES (?, ?, ?, ?, ?, ?)',
               (replicated_data['PatientID'], replicated_data['Name'], replicated_data['DateOfBirth'], replicated_data['Gender'], replicated_data['ContactInformation'], replicated_data['InsuranceInformation']))

    conn.commit()
    conn.close()
    return jsonify({'message': 'patient replicated successfully'}), 201

@app.route('/patients', methods=['POST'])
def create_patient():  

    patient_data=request.get_json()
    # broadcast data to all the nodes inclusive of self 
    for node in OTHER_NODES:
        try:
            celery.send_task('replicate_patient', args=[node, patient_data])
        except Exception as e:
            app.logger.error(f'Error replicating patient to node {node}: {e}')

    # Return a response indicating success
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

    # Return the patients as JSON
    return jsonify({'patients': patient_list})

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
    conn.close()
    return jsonify({'message': 'Patient being deleted across successfully'}), 200

@app.route('/patients', methods=['GET'])
def get_patients():
    patients = session.query(Patient).all()
    patient_list = [{'PatientID': patient.PatientID, 'Name': patient.Name, 'DateOfBirth': patient.DateOfBirth, 'Gender': patient.Gender, 'ContactInformation': patient.ContactInformation, 'InsuranceInformation': patient.InsuranceInformation} for patient in patients]
    return render_template('display_patients.html', patients=patient_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
