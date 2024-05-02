# database.py

import datetime
import requests
import socket
import random
import sqlalchemy
from sqlite3 import IntegrityError
from flask import jsonify
from config import Config
from flask_login import login_user
from contextlib import contextmanager
from sqlalchemy import create_engine, Table, Column, MetaData, Integer, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from models import Base, Patient, Doctor, User, Prescription, Appointment
from exceptions import DatabaseIntegrityError, ValueError, TypeError

# Database manager class
class DatabaseManager:
    def __init__(self):
        self.DATABASE_URL = Config.SQLALCHEMY_DATABASE_URI
        self.NODES = Config.NODES
        self.MY_NODE_ID = socket.gethostname()
        
    def create_tables(self):
        engine = create_engine(self.DATABASE_URL)
        Base.metadata.create_all(engine)
        
    def get_session(self):
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
    def generate_user_id(self, role):
        prefix = {'admin': 'a', 'patient': 'p', 'doctor': 'd', 'nurse': 'n'}
        with self.get_db() as db:
            while True:
                user_id = prefix[role] + ''.join([str(random.randint(0, 9)) for _ in range(5)])
                if not db.query(User).filter(User.UserID == user_id).one_or_none():
                    return user_id
    def ensure_admin_user(self):
        with self.get_db() as db:
            admin_user = db.query(User).filter(User.Username == 'admin').one_or_none()
            if not admin_user:
                admin_id = self.generate_user_id('admin')
                new_admin = User(admin_id, 'admin', 'admin123', 'admin') 
                db.add(new_admin)
                try:
                    db.commit()
                except Exception as e:
                    print(f"Error occurred during commit: {e}")

    def load_user(self, user_id):
        with self.get_db() as db:
            return db.query(User).get(user_id)

    def insert_user(self, user):
        with self.get_db() as db:
            try:
                if db.query(User).filter(User.Username == user['Username']).one_or_none():
                    raise Exception('Username already exists')
                user_id = user.get('UserID') or self.generate_user_id(user['Role'])
                username = user['Username']
                password = user['Password']
                role = user['Role']
                new_user = User(user_id, username, password, role)
                db.add(new_user)
                db.commit()
                # Replicate the data to other nodes
                #self.replicate_data('insert', new_user.to_dict(), 'user')
                return new_user.UserID
            except Exception as e:
                raise Exception(f"Error occurred during user insertion: {e}") from e

    def insert_patient(self, patient):
        with self.get_db() as db:
            try:
                patient_id = patient['PatientID']
                name = patient['Name']
                date_of_birth = datetime.datetime.strptime(patient['DateOfBirth'], '%Y-%m-%d').date()
                gender = patient['Gender']
                phone_number = patient['PhoneNumber']
                
                new_patient = Patient(patient_id, name, date_of_birth, gender, phone_number)
                db.add(new_patient)
                db.commit()
                # Replicate the data to other nodes
                #self.replicate_data('insert', new_patient.to_dict(), 'patient')
                return new_patient.PatientID
            except IntegrityError as e:
                raise DatabaseIntegrityError(
                    f"Error creating patient (data integrity): {e}"
                ) from e
            except ValueError as e:
                raise ValueError(f"Error creating patient: {str(e)}") from e
            except Exception as e:
                raise Exception(f"Error creating patient: {str(e)}") from e
                
    def insert_doctor(self, doctor):
        with self.get_db() as db:
            try:
                doctor_id = doctor['DoctorID']
                name = doctor['DoctorName']
                specialization = doctor['Specilization']
                phone_number = doctor['PhoneNumber']
                department_id = doctor['DepartmentID']
                
                new_doctor = Doctor(doctor_id, name, specialization, phone_number, department_id)
                db.add(new_doctor)
                db.commit()
                # Replicate the data to other nodes
                #self.replicate_data('insert', new_doctor.to_dict(), 'doctor')
                return new_doctor.DoctorID
            except IntegrityError as e:
                raise DatabaseIntegrityError(
                    f"Error creating doctor (data integrity): {e}"
                ) from e
            except ValueError as e:
                raise ValueError(f"Error creating doctor: {str(e)}") from e
            except Exception as e:
                raise Exception(f"Error creating doctor: {str(e)}") from e

    def delete_patient(self, patient_id):
        try:
            if patient_id is None:
                raise ValueError("Invalid patient ID")
            with self.get_db() as db:
                if (
                    patient := db.query(Patient)
                    .filter(Patient.PatientID == patient_id)
                    .one_or_none()
                ):
                    db.delete(patient)
                    db.commit()
                    return jsonify({"message": "Deletion successful"}), 200
                else:
                    return jsonify({"error": "Patient not found"}), 404
        except Exception as e:
            print(f"Error occurred during patient deletion: {e}")
            return jsonify({"error": str(e)}), 500
        
    def delete_user(self, user_id):
        try:
            if user_id is None:
                raise ValueError("Invalid patient ID")
            with self.get_db() as db:
                if (
                    user := db.query(User)
                    .filter(User.UserID == user_id)
                    .one_or_none()
                ):
                    db.delete(user)
                    db.commit()
                    return jsonify({"message": "Deletion successful"}), 200
                else:
                    return jsonify({"error": "User not found"}), 404
        except Exception as e:
            print(f"Error occurred during User deletion: {e}")
            return jsonify({"error": str(e)}), 500

    def update_patient(self, patient_id, new_data):
        with self.get_db() as db:
            if patient := db.query(Patient).filter(Patient.PatientID == patient_id).one_or_none():
                for key, value in new_data.items():
                    setattr(patient, key, value)
        db.commit()

    def get_all_patients(self):
        with self.get_db() as db:
            return db.query(Patient).all()

    def get_patient_by_id(self, patient_id):
        if patient_id is None:
            raise ValueError("Invalid patient ID")
        with self.get_db() as db:
            try:
                patient = db.query(Patient).filter(Patient.PatientID == patient_id).one_or_none()
                if patient is None:
                    return jsonify({"error": "Patient not found"}), 404
                patient_dict = {
                    'PatientID': patient.PatientID,
                    'Name': patient.Name,
                    'DateOfBirth': patient.DateOfBirth.strftime('%Y-%m-%d'),
                    'Gender': patient.Gender,
                    'PhoneNumber': patient.PhoneNumber
                }
                return jsonify(patient_dict), 200
            except Exception as e:
                print(f'Error occurred during get patient by id: {e}')
                return jsonify({"error": str(e)}), 500

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
            if doctor := db.query(Doctor).filter(Doctor.DoctorID == doctor_id).one_or_none():
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
            print(f"Error occurred during authentication: {e}")
            return None


  
    def replicate_data(self, action, data, ObjectType):
        for node in self.NODES:
            if node != self.NODE_ID:
                try:
                    url = f"https://{node}/replicate/{action}/{ObjectType}"
                    data_with_type = {'data': data, 'ObjectType': ObjectType}
                    response = requests.post(url, json=data_with_type)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    return jsonify({"error": f"Error replicating data to node {node}: {str(e)}"}), 500
                
    def insert_prescription(self, prescription):
        with self.get_db() as db:
            try:
                patient_id = prescription['PatientID']
                doctor_id = prescription['DoctorID']
                medication = prescription['Medication']
                dosage = medication['Dosage']
                frequency = prescription['Frequency']
                refills = prescription['Refills']
                instructions = prescription['Instruction']
                
                new_prescription = Prescription(
                    PatientID=patient_id,
                    DoctorID=doctor_id,
                    Medication=medication,
                    Dosage=dosage,
                    Frequency=frequency,
                    Refills=refills,
                    Instructions=instructions,
                )
                db.add(new_prescription)
                db.commit()
                return new_prescription.PrescriptionID
            except IntegrityError as e:
                raise DatabaseIntegrityError(f"Failed to insert prescription: {e}") from e
            except Exception as e:
                raise e

    def get_all_appointments(self):
        with self.get_db() as db:
            return db.query(Appointment).all()
    def get_appointments_by_doctor_id(self, doctor_id):
        with self.get_db() as db:
            return db.query(Appointment).filter(Appointment.DoctorID == doctor_id).all()