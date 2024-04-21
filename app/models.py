# models.py

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'

    PatientID = Column(Integer, primary_key=True)
    Name = Column(String)
    DateOfBirth = Column(Text)
    Gender = Column(String)
    ContactInformation = Column(String)
    InsuranceInformation = Column(String)

    appointments = relationship("Appointment", backref='patient')
    medical_records = relationship("MedicalRecord", backref='patient')
    prescriptions = relationship("Prescription", backref='patient')
    billings = relationship("Billing", backref='patient')

class Doctor(Base):
    __tablename__ = 'doctors'

    DoctorID = Column(Integer, primary_key=True)
    Name = Column(String)
    Specialization = Column(String)
    ContactInformation = Column(String)
    DepartmentID = Column(Integer, ForeignKey('departments.DepartmentID'))

    appointments = relationship("Appointment", backref='doctor')
    medical_records = relationship("MedicalRecord", backref='doctor')
    prescriptions = relationship("Prescription", backref='doctor')

class Nurse(Base):
    __tablename__ = 'nurses'

    NurseID = Column(Integer, primary_key=True)
    Name = Column(String)
    ContactInformation = Column(String)
    DepartmentID = Column(Integer, ForeignKey('departments.DepartmentID'))

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
    AppointmentDateTime = Column(Text)
    Purpose = Column(String)

class MedicalRecord(Base):
    __tablename__ = 'medical_records'

    RecordID = Column(Integer, primary_key=True)
    PatientID = Column(Integer, ForeignKey('patients.PatientID'))
    DoctorID = Column(Integer, ForeignKey('doctors.DoctorID'))
    DateOfVisit = Column(Text)
    Diagnosis = Column(Text)
    TreatmentPlan = Column(Text)

class Prescription(Base):
    __tablename__ = 'prescriptions'

    PrescriptionID = Column(Integer, primary_key=True)
    PatientID = Column(Integer, ForeignKey('patients.PatientID'))
    DoctorID = Column(Integer, ForeignKey('doctors.DoctorID'))
    Medication = Column(String)
    Dosage = Column(String)
    Instructions = Column(Text)

class Billing(Base):
    __tablename__ = 'billings'

    BillingID = Column(Integer, primary_key=True)
    PatientID = Column(Integer, ForeignKey('patients.PatientID'))
    TotalCost = Column(Float)  # Using Float for monetary values
    PaymentStatus = Column(String)
    DateOfBilling = Column(Text)
