import sqlite3

def create_database():
    conn = sqlite3.connect('ntsoekhe.db')
    cursor = conn.cursor()

# Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS patients (
        PatientID INTEGER PRIMARY KEY,
        Name TEXT,
        DateOfBirth TEXT,
        Gender TEXT,
        ContactInformation TEXT,
        InsuranceInformation TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        DoctorID INTEGER PRIMARY KEY,
        Name TEXT,
        Specialization TEXT,
        ContactInformation TEXT,
        DepartmentID INTEGER,
        FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS nurses (
        NurseID INTEGER PRIMARY KEY,
        Name TEXT,
        ContactInformation TEXT,
        DepartmentID INTEGER,
        FOREIGN KEY (DepartmentID) REFERENCES Department(DepartmentID)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        DepartmentID INTEGER PRIMARY KEY,
        DepartmentName TEXT,
        DepartmentHead TEXT,
        Location TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        AppointmentID INTEGER PRIMARY KEY,
        PatientID INTEGER,
        DoctorID INTEGER,
        AppointmentDateTime TEXT,
        Purpose TEXT,
        FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
        FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medical_records (
        RecordID INTEGER PRIMARY KEY,
        PatientID INTEGER,
        DoctorID INTEGER,
        DateOfVisit TEXT,
        Diagnosis TEXT,
        TreatmentPlan TEXT,
        FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
        FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS prescriptions (
        PrescriptionID INTEGER PRIMARY KEY,
        PatientID INTEGER,
        DoctorID INTEGER,
        Medication TEXT,
        Dosage TEXT,
        Instructions TEXT,
        FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
        FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID)
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS billings (
        BillingID INTEGER PRIMARY KEY,
        PatientID INTEGER,
        TotalCost REAL,
        PaymentStatus TEXT,
        DateOfBilling TEXT,
        FOREIGN KEY (PatientID) REFERENCES Patient(PatientID)
    )''')

# Commit changes and close connection
    conn.commit()
    conn.close()
    print("SUCCESSFULLY CREATED THE TABLES")
