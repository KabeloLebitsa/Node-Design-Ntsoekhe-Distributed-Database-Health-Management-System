#database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Patient, Doctor

# Define the connection string to your database (replace with your details)
DATABASE_URL = 'sqlite:///ntsoekhe.db'

engine = create_engine(DATABASE_URL)
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


def get_all_doctors():
    db = get_db()
    doctors = db.query(Doctor).all()
    db.close()
    return doctors
