#api.py

from flask import Flask, request, jsonify, abort, current_user
from flask_login import LoginManager, login_required
from requests import post
import celery_worker

app = Flask(__name__)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.html'  # Redirect to login page on unauthorized access

@app.route('/patients', methods=['POST'])
@login_required
def create_patient():
    if not current_user.can_create_patient:
        return abort(403)

    patient_data = request.get_json()
    # Enqueue the creation task to Celery
    task = celery_worker.add_patient.delay(patient_data)
    return jsonify({'message': 'Patient creation task enqueued', 'task_id': task.id}), 202

# Retrieve a patient by ID
@app.route('/patients/<int:patient_id>', methods=['GET'])
@login_required
def get_patient_by_id(patient_id):
    if not current_user.can_read_patient:
        return abort(403)  # Forbidden

    if patient := celery_worker.get_patient_by_id(patient_id):
        return jsonify(patient.serialize()), 200
    else:
        return jsonify({'message': f'Patient with ID {patient_id} not found'}), 404  # Not Found

# Endpoint for replication
@app.route('/replicate', methods=['POST'])
@login_required
def replicate_patient():
    replicated_data = request.get_json()
    # Enqueue the replication task to Celery
    task = celery_worker.replicate_data.delay(replicated_data)
    return jsonify({'message': 'Replication task enqueued', 'task_id': task.id}), 202

@app.route('/patients/<int:patient_id>', methods=['PUT'])
@login_required
def update_patient(patient_id):
    if not current_user.can_update_patient:
        return abort(403)  # Forbidden

    update_data = request.get_json()

    # Enqueue the update task to Celery
    task = celery_worker.update_patient.delay(patient_id, update_data)
    return jsonify({'message': 'Update request received', 'task_id': task.id}), 202

@app.route('/patients/<int:patient_id>', methods=['DELETE'])
@login_required
def delete_patient(patient_id):
    if not current_user.can_delete_patient:
        return abort(403)

    # Enqueue the delete task to Celery
    task = celery_worker.delete_patient.delay(patient_id)
    return jsonify({'message': 'Delete request received', 'task_id': task.id}), 202