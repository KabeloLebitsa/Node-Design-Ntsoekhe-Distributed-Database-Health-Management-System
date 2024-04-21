from flask import Flask, jsonify, request, render_template
import sqlite3
import requests
import os
from ntsoekheCreation import create_database

app = Flask(__name__)
create_database()

OTHER_NODES = ['http://172.18.0.4:8083', 'http://172.18.0.3:8082', 'http://172.18.0.2:8081', 'http://172.18.0.5:8084', 'http://172.18.0.6:8085']

# Endpoint for the home page
@app.route('/')
def index():
    return render_template('welcomePoe.html')

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
    conn = sqlite3.connect('ntsoekhe.db')
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
            response = requests.post(f'{node}/replicate', json=patient_data)
            if response.status_code != 201:
                app.logger.error(f'Failed to replicate patient to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating patient to node {node}: {e}')
    return jsonify({'message': 'patient created successfully'}), 201

@app.route('/patients/<int:patient_id>', methods=['PUT', 'PATCH'])
def update_patient(patient_id):
    updated_data = request.get_json()
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()
    for key in updated_data:
        cursor.execute(f'UPDATE patients SET {key} = ? WHERE PatientID = ?', (updated_data[key], patient_id))
    conn.commit()
    conn.close()
    for node in OTHER_NODES:
        try:
            response = requests.put(f'{node}/patients/{patient_id}', json=updated_data)
            if response.status_code != 200:
                app.logger.error(f'Failed to replicate update to node {node}: {response.text}')
        except Exception as e:
            app.logger.error(f'Error replicating update to node {node}: {e}')
    return jsonify({'message': 'patient updated successfully'}), 200

@app.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients WHERE PatientID = ?', (patient_id,))
    patient = cursor.fetchone()
    if patient is None:
        conn.close()
        return jsonify({'message': 'Patient not found'}), 404
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
    conn = sqlite3.connect('ntsoekhe.db')
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
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients')
    patients = cursor.fetchall()
    conn.close()
    patient_list = [{'PatientID': patient[0], 'Name': patient[1], 'DateOfBirth': patient[2], 'Gender': patient[3], 'ContactInformation': patient[4], 'InsuranceInformation': patient[5]} for patient in patients]
    return render_template('display_patients.html', patients=patient_list)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
