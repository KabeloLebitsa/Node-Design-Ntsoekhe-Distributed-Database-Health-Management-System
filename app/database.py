# database.py

from sqlite3 import IntegrityError
from flask import jsonify
import requests
from config import Config
from flask_login import login_user
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Patient, Doctor, User
from exceptions import DatabaseIntegrityError

# Database manager class
class DatabaseManager:
    def __init__(self):
        self.DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI
        self.OTHER_NODES = Config.OTHER_NODES

    def get_session(self):
        # Create a new engine and sessionmaker each time
        engine = create_engine(self.DATABASE_URL)
        Session = sessionmaker(bind=engine)
        return Session()

    @contextmanager
    def get_db(self):
        db = self.get_session()
        try:
            yield db
        finally:
            db.close()

    def ensure_admin_user(self):
        with self.get_db() as db:
            admin_user = db.query(User).filter(User.Role == 'admin').one_or_none()
            if not admin_user:
                new_admin = User(Username='admin', Password='admin123', Role='admin') 
                db.add(new_admin)
                db.commit()

    def load_user(self, user_id):
        with self.get_db() as db:
            return db.query(User).get(user_id)

    def insert_user(self, user):
        with self.get_db() as db:
            db.add(user)
            db.commit()
            return user

    def insert_patient(self, patient):
        with self.get_db() as db:
            try:
                db.add(patient)
                db.commit()
                return True  
            except IntegrityError as e:
                raise DatabaseIntegrityError(
                    f"Error creating patient (data integrity): {e}"
                ) from e
            except Exception as e:
                return jsonify({"error": f"Error creating patient: {str(e)}"}), 500

    def delete_patient(self, patient_id):
        with self.get_db() as db:
            if patient := db.query(Patient).filter(Patient.id == patient_id).one_or_none():
                db.delete(patient)
        db.commit()

    def update_patient(self, patient_id, new_data):
        with self.get_db() as db:
            if patient := db.query(Patient).filter(Patient.id == patient_id).one_or_none():
                for key, value in new_data.items():
                    setattr(patient, key, value)
        db.commit()

    def get_all_patients(self):
        with self.get_db() as db:
            return db.query(Patient).all()

    def get_patient_by_id(self, patient_id):
        with self.get_db() as db:
            return db.query(Patient).filter(Patient.id == patient_id).one_or_none()

    def insert_doctor(self, doctor):
        with self.get_db() as db:
            db.add(doctor)
        db.commit()

    def update_doctor(self, doctor_id, new_data):
        with self.get_db() as db:
            if doctor := db.query(Doctor).filter(Doctor.id == doctor_id).one_or_none():
                for key, value in new_data.items():
                    setattr(doctor, key, value)
        db.commit()

    def get_all_doctors(self):
        with self.get_db() as db:
            return db.query(Doctor).all()

    def get_doctor_by_id(self, doctor_id):
        with self.get_db() as db:
            return db.query(Doctor).filter(Doctor.id == doctor_id).one_or_none()

    def delete_doctor(self, doctor_id):
        with self.get_db() as db:
            if doctor := db.query(Doctor).filter(Doctor.id == doctor_id).one_or_none():
                db.delete(doctor)
        db.commit() 

    def authenticate_user(self, username, password):
        try:
            with self.get_db() as db:
                user = db.query(User).filter(User.Username == username).one_or_none()
                if user and user.Password == password:
                    user.IsAuthenticated = True
                    user.IsActive = True
                    user.IsAnonymous = False
                    login_user(user)
                    return user
                else:
                    print("Invalid username or password.")
                return None
        except Exception as e:
            # Handle database errors
            print(f"Error occurred during authentication: {e}")
            return None

    def replicate_data(self, action, data):
        for node in self.OTHER_NODES:
            try:
                response = requests.post(f"https://{node}/replicate-{action}", json=data)
                response.raise_for_status()  # Raise exception for non-2xx response codes
            except requests.exceptions.RequestException as e:
                print(f"Error replicating data to node {node}: {e}")
