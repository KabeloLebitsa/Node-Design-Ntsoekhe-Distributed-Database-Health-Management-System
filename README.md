    ## Flask Healthcare API

This is a Flask-based RESTful API for managing healthcare data including patients, doctors, nurses, departments, appointments, medical records, prescriptions, and billings.

## Features

- Create, read, update, and delete operations for patients, doctors, nurses, departments, appointments, medical records, prescriptions, and billings.
- Data replication across multiple nodes in the network.
- SQLite database backend.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/KabeloLebitsa/NodeDesignDDBSPrototype.git
```
##dependancy 
yml file takes care of those

## Usage

### Endpoints

#### Patients

- `POST /patients`: Create a new patient.
- `GET /patients`: Retrieve all patients.
- `PUT /patients/<patient_id>`: Update an existing patient.
- `DELETE /patients/<patient_id>`: Delete a patient.

#### Doctors

- `POST /doctors`: Create a new doctor.
- `GET /doctors`: Retrieve all doctors.

#### Nurses

- `POST /nurses`: Create a new nurse.
- `GET /nurses`: Retrieve all nurses.

#### Departments

- `POST /departments`: Create a new department.
- `GET /departments`: Retrieve all departments.

#### Appointments

- `POST /appointments`: Create a new appointment.
- `GET /appointments`: Retrieve all appointments.

#### Medical Records

- `POST /medical_records`: Create a new medical record.
- `GET /medical_records`: Retrieve all medical records.

#### Prescriptions

- `POST /prescriptions`: Create a new prescription.
- `GET /prescriptions`: Retrieve all prescriptions.

#### Billings

- `POST /billings`: Create a new billing.
- `GET /billings`: Retrieve all billings.

## Running  Docker Applications

you run the application using yml file 
-it builds the images and containers statically

1. running application:
    docker-compose up

the nodes will run at five links
['https://172.0.1.1:8081','https://172.0.1.2:8082',
'https://172.0.1.3:8083','https://172.0.1.4:8084',
'https://172.0.1.5:8085'],  
this are defined statically in the yml file

NOTE : due to static network address assignments ,  is advisable to remove all existing custom docker networks, to aavoid ip overlap causing malfunction 


## Database

The SQLite database file `ntsoekhe.db` is included in the repository. It contains tables for patients, doctors, nurses, departments, appointments, medical records, prescriptions, and billings.

## Dependencies(they are handled by the yml file )

- Flask
- Requests

## License

[MIT License](LICENSE)
```

Feel free to customize it further to better suit your project's needs!


