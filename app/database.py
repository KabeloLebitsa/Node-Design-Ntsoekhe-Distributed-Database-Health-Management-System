#database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Patient, Doctor
from .connection_pool import create_connection_pool

pool = create_connection_pool()
def get_connection():
    return pool.connection()
# Define the connection string to your database
DATABASE_URL = 'sqlite:///ntsoekhe.db'
engine = create_engine(DATABASE_URL, creator=get_connection)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    Base.metadata.create_all(bind=engine)
    print("SUCCESSFULLY CREATED ALL TABLES")


# Functions to interact with the database using models

def insert_patient(patient):
    db = get_db()
    db.add(patient)
    db.commit()
    db.close()

def delete_patient(patient_id):
    db = get_db()
    if patient := db.query(Patient).filter_by(PatientID=patient_id).first():
        db.delete(patient)
        db.commit()
    db.close()
def update_patient(patient_id, new_data):
    db = get_db()
    if patient := db.query(Patient).filter_by(PatientID=patient_id).first():
        for key, value in new_data.items():
            setattr(patient, key, value)
        db.commit()
    db.close()
    
def get_all_patients():
    db = get_db()
    patients = db.query(Patient).all()
    db.close()
    return patients


def get_patient_by_id(patient_id):
    db = get_db()
    patient = db.query(Patient).filter_by(PatientID=patient_id).first()
    db.close()
    return patient


def insert_doctor(doctor):
    db = get_db()
    db.add(doctor)
    db.commit()
    db.close()
    
def update_doctor(doctor_id, new_data):
    db = get_db()
    if doctor := db.query(Doctor).filter_by(DoctorID=doctor_id).first():
        for key, value in new_data.items():
            setattr(doctor, key, value)
        db.commit()
    db.close()
    
def get_all_doctors():
    db = get_db()
    doctors = db.query(Doctor).all()
    db.close()
    return doctors

def get_doctor_by_id(doctor_id):
    db = get_db()
    doctor = db.query(Doctor).filter_by(DoctorID=doctor_id).first()
    db.close()
    return doctor

def update_doctor(doctor_id, update_fields):
    db = get_db()
    if doctor := db.query(Doctor).filter_by(DoctorID=doctor_id).first():
        for key, value in update_fields.items():
            setattr(doctor, key, value)
        db.commit()
    db.close()

    
def delete_doctor(doctor_id):
    db = get_db()
    if doctor := db.query(Doctor).filter_by(DoctorID=doctor_id).first():
        db.delete(doctor)
        db.commit()
    db.close()