#utils.py

import logging
import requests
from abc import ABC, abstractmethod
import json
from flask import json
from config import Config

class ReplicationStrategy(ABC):

    def __init__(self) -> None:
        self.message_queue_url = Config.REPLICATION_NODES
        self.processed_requests = set()  # Track processed request IDs


    @abstractmethod
    def send_message(self, data: str) -> None:
        pass

    def replicate(self, action: str, data: str, object_type: str, request_id: str) -> None:
        message = {
            "action": action,
            "data": data,
            "object_type": object_type,
            "request_id": request_id
        }
        self.send_message(json.dumps(message))
        logging.info(f"Replicated {action} operation for {object_type}: {data} (Request ID: {request_id})")

    def send_message(self, data: str) -> bool:
        headers = {'Content-Type': 'application/json'}
        try:
            message = json.loads(data)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing message data: {e}")
            return False

        message_id = message.get('request_id')
        if not message_id:
            logging.error("Missing request_id in message data")
            return False

        if message_id in self.processed_requests:
            logging.info(f"Ignoring duplicate request {message_id}")
            return False

        self.processed_requests.add(message_id)

        success = True
        for url in self.message_queue_url:
            modified_url = f"{url}/replicate"
            try:
                response = requests.post(modified_url, data=data, headers=headers)
                response.raise_for_status()
                logging.info(f"Successfully sent message to {url}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Error sending message to {url}: {e}")
                success = False
        return success
