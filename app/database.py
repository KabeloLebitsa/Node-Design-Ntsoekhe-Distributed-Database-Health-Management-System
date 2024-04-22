#database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Patient, Doctor
from connection_pool import create_connection_pool

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
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

def create_all_tables():
    Base.metadata.create_all(bind=engine)

# Functions to interact with the database using models
def insert_user(user):
    with get_db() as db:
        db.add(user)

def insert_patient(patient):
    with get_db() as db:
        db.add(patient)

def delete_patient(patient_id):
    with get_db() as db:
        if patient := db.query(Patient).get(patient_id):
            db.delete(patient)

def update_patient(patient_id, new_data):
    with get_db() as db:
        if patient := db.query(Patient).get(patient_id):
            for key, value in new_data.items():
                setattr(patient, key, value)

def get_all_patients():
    with get_db() as db:
        return db.query(Patient).all()

def get_patient_by_id(patient_id):
    with get_db() as db:
        return db.query(Patient).get(patient_id)

def insert_doctor(doctor):
    with get_db() as db:
        db.add(doctor)

def update_doctor(doctor_id, new_data):
    with get_db() as db:
        if doctor := db.query(Doctor).get(doctor_id):
            for key, value in new_data.items():
                setattr(doctor, key, value)

def get_all_doctors():
    with get_db() as db:
        return db.query(Doctor).all()

def get_doctor_by_id(doctor_id):
    with get_db() as db:
        return db.query(Doctor).get(doctor_id)

def delete_doctor(doctor_id):
    with get_db() as db:
        if doctor := db.query(Doctor).get(doctor_id):
            db.delete(doctor)