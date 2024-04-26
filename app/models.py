# models.py

from sqlalchemy import Boolean, Column, Float, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'

    PatientID = Column(Integer, primary_key=True)
    Name = Column(String)
    DateOfBirth = Column(Date)
    Gender = Column(String)
    PhoneNumber = Column(Integer, unique=True)
    #needs_replication = Column(Boolean, default=True)
    
    appointments = relationship("Appointment", backref='patient')
    medical_records = relationship("MedicalRecord", backref='patient')
    prescriptions = relationship("Prescription", backref='patient')
    billings = relationship("Billing", backref='patient')

class Doctor(Base):
    __tablename__ = 'doctors'

    DoctorID = Column(Integer, primary_key=True)
    Name = Column(String)
    Specialization = Column(String)
    PhoneNumber = Column(Integer, unique=True)
    DepartmentID = Column(Integer, ForeignKey('departments.DepartmentID'))
    #needs_replication = Column(Boolean, default=True)
    
    appointments = relationship("Appointment", backref='doctor')
    medical_records = relationship("MedicalRecord", backref='doctor')
    prescriptions = relationship("Prescription", backref='doctor')

class Nurse(Base):
    __tablename__ = 'nurses'

    NurseID = Column(Integer, primary_key=True)
    Name = Column(String)
    PhoneNumber = Column(Integer, unique=True)
    DepartmentID = Column(Integer, ForeignKey('departments.DepartmentID'))
    #needs_replication = Column(Boolean, default=True)
    
class Department(Base):
    __tablename__ = 'departments'

    DepartmentID = Column(Integer, primary_key=True)
    DepartmentName = Column(String)
    DepartmentHead = Column(String)
    Location = Column(String)

    doctors = relationship("Doctor", backref='department')
    nurses = relationship("Nurse", backref='department')

class Appointment(Base):
    __tablename__ = 'appointments'

    AppointmentID = Column(Integer, primary_key=True)
    PatientID = Column(Integer, ForeignKey('patients.PatientID'))
    DoctorID = Column(Integer, ForeignKey('doctors.DoctorID'))
    AppointmentDateTime = Column(Date)
    Purpose = Column(String)
    #needs_replication = Column(Boolean, default=True)
class MedicalRecord(Base):
    __tablename__ = 'medical_records'

    RecordID = Column(Integer, primary_key=True)
    PatientID = Column(Integer, ForeignKey('patients.PatientID'))
    DoctorID = Column(Integer, ForeignKey('doctors.DoctorID'))
    DateOfVisit = Column(Date)
    Diagnosis = Column(Text)
    TreatmentPlan = Column(Text)
    #needs_replication = Column(Boolean, default=True)
class Prescription(Base):
    __tablename__ = 'prescriptions'

    PrescriptionID = Column(Integer, primary_key=True)
    PatientID = Column(Integer, ForeignKey('patients.PatientID'))
    DoctorID = Column(Integer, ForeignKey('doctors.DoctorID'))
    Medication = Column(String)
    Dosage = Column(String)
    Instructions = Column(Text)
    #needs_replication = Column(Boolean, default=True)
class Billing(Base):
    __tablename__ = 'billings'

    BillingID = Column(Integer, primary_key=True)
    PatientID = Column(Integer, ForeignKey('patients.PatientID'))
    TotalCost = Column(Float)  
    PaymentStatus = Column(String)
    DateOfBilling = Column(Date)
    #needs_replication = Column(Boolean, default=True)

from flask_login import UserMixin

class User(Base):
    __tablename__ = 'users'

    UserID = Column(Integer, primary_key=True)
    Username = Column(String, unique=True, nullable=False)
    Password = Column(String, nullable=False)
    Role = Column(String, nullable=False)
    IsActive = Column(Boolean, default=False)
    IsAuthenticated = Column(Boolean, default=False)
    IsAnonymous = Column(Boolean, default=False)

    PatientID = Column(Integer, ForeignKey('patients.PatientID'), nullable=True)
    DoctorID = Column(Integer, ForeignKey('doctors.DoctorID'), nullable=True)

    patient = relationship("Patient", backref="user", foreign_keys=[PatientID], primaryjoin="and_(User.PatientID==Patient.PatientID, User.Role=='patient')")
    doctor = relationship("Doctor", backref="user", foreign_keys=[DoctorID], primaryjoin="and_(User.DoctorID==Doctor.DoctorID, User.Role=='doctor')")

    def get_id(self):
        return str(self.UserID)  

    @property
    def is_authenticated(self):
        return self.IsAuthenticated

    @property
    def is_active(self):
        return self.IsActive

    @property
    def is_anonymous(self):
        return self.IsAnonymous

    def __repr__(self):
        return f"<User(Username={self.Username}, Role={self.Role})>"