from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'

    PatientID = Column(Integer, primary_key=True)
    Name = Column(String)
    DateOfBirth = Column(Date)
    Gender = Column(String)
    ContactInformation = Column(String)
    InsuranceInformation = Column(String)
