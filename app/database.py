#database.py

import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from models import Base, Patient, Doctor, User
#from connection_pool import create_connection_pool

DATABASE_URL = 'ntsoekhe.db'
pool = QueuePool(creator=sqlite3.connect(DATABASE_URL),  # Use sqlite3.connect as the creator
                  pool_size=10,
                  max_overflow=0)

engine = create_engine(DATABASE_URL, pool=pool)  # Explicitly set the pool
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
        db.merge(user)

def insert_patient(patient):
    with get_db() as db:
        db.merge(patient)

def delete_patient(patient_id):
    with get_db() as db:
        if patient := db.query(Patient).filter(Patient.id == patient_id).one_or_none():
            db.delete(patient)

def update_patient(patient_id, new_data):
    with get_db() as db:
        if patient := db.query(Patient).filter(Patient.id == patient_id).one_or_none():
            for key, value in new_data.items():
                setattr(patient, key, value)

def get_all_patients():
    with get_db() as db:
        return db.query(Patient).all()

def get_patient_by_id(patient_id):
    with get_db() as db:
        return db.query(Patient).filter(Patient.id == patient_id).one_or_none()

def insert_doctor(doctor):
    with get_db() as db:
        db.merge(doctor)

def update_doctor(doctor_id, new_data):
    with get_db() as db:
        if doctor := db.query(Doctor).filter(Doctor.id == doctor_id).one_or_none():
            for key, value in new_data.items():
                setattr(doctor, key, value)

def get_all_doctors():
    with get_db() as db:
        return db.query(Doctor).all()

def get_doctor_by_id(doctor_id):
    with get_db() as db:
        return db.query(Doctor).filter(Doctor.id == doctor_id).one_or_none()

def delete_doctor(doctor_id):
    with get_db() as db:
        if doctor := db.query(Doctor).filter(Doctor.id == doctor_id).one_or_none():
            db.delete(doctor)

def authenticate_user(username, password):
    """
    This function authenticates a user based on username and password.

    Args:
        username (str): Username provided by the user during login.
        password (str): Password provided by the user during login.

    Returns:
        User object: Returns the User object if authentication is successful, otherwise None.
    """
    try:
        with get_db() as db:
            if u_password := db.query(User.Password).filter_by(username).scalar():
                # Check stored password against provided password
                return None if u_password != password else db.query(User).filter_by(username).first()
            else:
                return None
    except Exception as e:
        # Handle database errors
        print(f"Error occurred during authentication: {e}")
        return None

def load_user(user_id):
    with get_db() as db:
        return db.query(User).get(user_id)