from celery import Celery
from . import api  # Assuming replicate_patient function is now in api.py


app = Celery('ntsoekhe_tasks', broker='redis://localhost:6379/0')


@app.task
def replicate_patient(node, patient_data):
    response = api.replicate_patient_to_node(node, patient_data)
    if response.status_code != 201:
        api.app.logger.error(f'Failed to replicate patient to node {node}: {response.text}')
