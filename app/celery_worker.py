#celery_worker.py

import database 
import aiohttp
import asyncio
from config import Config
from celery import Celery
from models import Patient, Doctor, Nurse, Department, Appointment, MedicalRecord, Prescription, Billing, User

# Configure Celery Broker and Backend (replace with your configuration details)
app = Celery('tasks', broker='amqp://localhost:5672', backend='redis://localhost:6379')

app.config.from_object(Config)
OTHER_NODES = app.config['OTHER_NODES']

# Optional: Automatically create tables on Celery worker startup
database.create_all_tables()

@app.task
def add_user(user_data):
    """
    Celery task to add a new user record to the database.

    Args:
        user_data: A dictionary containing user information (username, email, etc.).

    Returns:
        The ID of the newly inserted user record.
    """
    user = User(**user_data)  
    db = database.get_db()
    database.insert_user(user)  
    db.close()
    return user.UserID

@app.task
def add_patient(patient_data):
    """
    Celery task to add a new patient record to the database.

    Args:
        patient_data: A dictionary containing patient information (name, dob, etc.).

    Returns:
        The ID of the newly inserted patient record.
    """
    try:
        patient = Patient(**patient_data)
        db = database.get_db()
        database.insert_patient(patient)
        db.close()
        return patient.PatientID
    except Exception as e:
        # Handle database error
        print(f"Error adding patient: {str(e)}")
        return None

@app.task
def delete_patient(patient_id):
    """
    Celery task to delete a patient record from the database.

    Args:
        patient_id: The ID of the patient to be deleted.
    """
    db = database.get_db()
    database.delete_patient(patient_id)
    db.close()

@app.task
async def replicate_data(replicated_data):
    """
    Celery task to replicate data across multiple nodes.

    Args:
        replicated_data: Data to be replicated across the nodes.

    Returns:
        A list of responses from each node indicating success or failure of the replication.
    """
    responses = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for node in OTHER_NODES:
            task = asyncio.ensure_future(send_request(session, node, replicated_data))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
    return responses

async def send_request(session, node, replicated_data):
    try:
        async with session.post(f"{node}/replicate", json=replicated_data) as response:
            return {'node': node, 'status': response.status, 'data': await response.json()}
    except aiohttp.ClientError as e:
        return {'node': node, 'status': 'failed', 'error': str(e)}

@app.task
def get_patients():
    """
    Celery task to retrieve all patient records from the database.

    Returns:
        A list of Patient objects representing all patients in the database.
    """
    db = database.get_db()
    patients = database.get_all_patients()
    db.close()
    return patients


@app.task
def get_patient_by_id(patient_id):
    """
    Celery task to retrieve a specific patient record based on the ID.

    Args:
        patient_id: The ID of the patient to retrieve.

    Returns:
        A Patient object representing the retrieved patient or None if not found.
    """
    db = database.get_db()
    patient = get_patient_by_id(patient_id)
    db.close()
    return patient


@app.task
def update_patient(patient_id, new_data):
    """
    Celery task to update a patient record in the database.

    Args:
        patient_id: The ID of the patient to update.
        new_data: A dictionary containing the updated patient information.

    Returns:
        The updated Patient object or None if not found.
    """
    db = database.get_db()
    patient = database.update_patient(patient_id, **new_data)  # Unpack new_data dictionary
    db.close()
    return patient

@app.task
def add_doctor(doctor_data):
    """
    Celery task to add a new doctor record to the database.

    Args:
        doctor_data: A dictionary containing doctor information (name, specialty, etc.).

    Returns:
        The ID of the newly inserted doctor record.
    """
    doctor = Doctor(**doctor_data)
    db = database.get_db()
    database.insert_doctor(doctor)
    db.close()
    return doctor.DoctorID

@app.task
def get_doctors():
    """
    Celery task to retrieve all doctor records from the database.

    Returns:
        A list of Doctor objects representing all doctors in the database.
    """
    db = database.get_db()
    doctors = database.get_all_doctors()
    db.close()
    return doctors

@app.task
def get_doctor_by_id(doctor_id):
    """
    Celery task to retrieve a specific doctor record based on the ID.

    Args:
        doctor_id: The ID of the doctor to retrieve.

    Returns:
        A Doctor object representing the retrieved doctor or None if not found.
    """
    db = database.get_db()
    doctor = database.get_doctor_by_id(doctor_id)
    db.close()
    return doctor

@app.task
def update_doctor(doctor_id, new_data):
    """
    Celery task to update a doctor record in the database.

    Args:
        doctor_id: The ID of the doctor to update.
        new_data: A dictionary containing the updated doctor information.

    Returns:
        The updated Doctor object or None if not found.
    """
    db = database.get_db()
    doctor = database.update_doctor(doctor_id, **new_data)
    db.close()
    return doctor


# Similar tasks for CRUD operations on other models (Doctor, Nurse, etc.)
# Implement functions for Doctor, Nurse, Department, Appointment, MedicalRecord, Prescription, Billing
# following the same pattern as the patient examples.


# Example usage (assuming you have a message queue configured)
# You can call these tasks from another application or script

# patient_data = {'name': 'John Doe', 'dob': '1980-01-01', ...}
# result = add_patient.delay(patient_data)
# patient_id = result.wait()
# print(f"Successfully added patient with ID: {patient_id}")

# Get all patients
# result = get_patients.delay()
# patients = result.wait()
# print(f"Total Patients: {len(patients)}")

# ... similar usage for other tasks
