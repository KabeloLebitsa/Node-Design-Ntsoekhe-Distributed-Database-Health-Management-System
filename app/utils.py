import logging
import requests
from abc import ABC, abstractmethod
import json
import os
from config import Config

class ReplicationStrategy(ABC):

    def __init__(self) -> None:
        self.message_queue_url = Config.NODES
        self.processed_requests = set() 
        self.data_file = os.path.join(Config.DATA_DIR, "processed_requests.json")

        # Load existing data (optional)
        try:
            self._load_data()
        except FileNotFoundError:
            self._create_empty_file()
    def _create_empty_file(self):
        with open(self.data_file, 'w') as file:
            json.dump([], file)
    def _load_data(self):
        with open(self.data_file, 'r') as f:  
             self.processed_requests = set(json.loads(f.read()))

    def _save_data(self):
        with open(self.data_file, 'w') as f:  
             f.write(json.dumps(list(self.processed_requests)))

    @abstractmethod
    def send_message(self, data: str) -> None:
        pass

    def replicate(self, action: str, data: str, object_type: str, request_id: str, base_url: str) -> None:
        """
        Replicates an operation to message queue nodes.
        Validates data, checks for duplicates, and sends the message.
        """

        message = {
            "action": action,
            "data": data,
            "object_type": object_type,
            "request_id": request_id,
        }

        try:
            # Validate data before sending
            self._validate_message_data(message)
        except (ValueError, json.JSONDecodeError) as e:
            logging.error(f"Error validating message data: {e}")
            return

        self.send_message(json.dumps(message), base_url)
        logging.info(f"Replicated {action} operation for {object_type}: {data} (Request ID: {request_id})")

    def _validate_message_data(self, message: dict) -> None:
        """
        Ensures message has required fields and appropriate data types.
        Raises ValueError if any issue is found.
        """

        required_fields = {"action", "data", "object_type", "request_id"}
        missing_fields = required_fields - set(message.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields in message: {', '.join(missing_fields)}")

        # Add type checks for data and object_type
        #if not isinstance(message['data'], str):
        #    raise ValueError("Invalid data type for 'data'")
        #if not isinstance(message['object_type'], str):
        #    raise ValueError("Invalid data type for 'object_type'")

    def send_message(self, data: str, base_url: str) -> bool:
        """
        Sends the message to all message queue nodes, handling potential errors.
        Checks for duplicates, updates the set, and saves data after successful processing.
        """

        headers = {'Content-Type': 'application/json'}

        try:
            message = json.loads(data)
            message_id = message['request_id']

            if message_id in self.processed_requests:
                logging.info(f"Ignoring duplicate request {message_id}")
                return False

            self.processed_requests.add(message_id)

            success = True
            for url in self.message_queue_url:
                if url != base_url:   
                    modified_url = f"{url}/replicate"
                    try:
                        response = requests.post(modified_url, data=data, headers=headers)
                        response.raise_for_status()  # Raise exception for non-2xx status codes
                        logging.info(f"Successfully sent message to {url}")
                    except requests.exceptions.RequestException as e:
                        logging.error(f"Error sending message to {url}: {e}")
                        success = False

                if success:
                    self._save_data()

        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Error processing request: {e}")
            return False

        return True
