#celery_worker.py

from celery import Celery
from .models import Base, Patient, Doctor, Nurse, Department, Appointment, MedicalRecord, Prescription, Billing  # Assuming models.py is in the directory
from .database import create_all_tables, get_db, insert_patient, get_all_patients, get_patient_by_id, update_patient

# Configure Celery Broker and Backend (replace with your configuration details)
app = Celery('tasks', broker='amqp://localhost:5672', backend='redis://localhost:6379')

# Optional: Automatically create tables on Celery worker startup
create_all_tables()

@app.task
def add_patient(patient_data):
    """
    Celery task to add a new patient record to the database.

    Args:
        patient_data: A dictionary containing patient information (name, dob, etc.).

    Returns:
        The ID of the newly inserted patient record.
    """
    patient = Patient(**patient_data)
    db = get_db()
    insert_patient(patient)
    db.close()
    return patient.PatientID


@app.task
def get_patients():
    """
    Celery task to retrieve all patient records from the database.

    Returns:
        A list of Patient objects representing all patients in the database.
    """
    db = get_db()
    patients = get_all_patients()
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
    db = get_db()
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
    db = get_db()
    patient = update_patient(patient_id, **new_data)  # Unpack new_data dictionary
    db.close()
    return patient

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
