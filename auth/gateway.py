# from http import Requests, Responses, codes
import json
import time
from flask import jsonify
from psycopg2 import IntegrityError
import requests
import logging

from datetime import datetime

from auth.main import db
from auth.models import APIWorkerModel


class APIWorker:
    worker: APIWorkerModel = None

    def __init__(self, key: str, target_uri: str, body: str, ttl: int) -> None:
        # Create model
        self.key = key  # Key
        self.target_uri = target_uri
        self.body = body
        self.ttl = ttl
        self.worker = None

    def launch(self) -> str:
        """
        Attempt to initiate a new APIWorker for this instance on

        Returns:
            str: The JSON result, or error
        """
        # Get current worker state
        if self._claim_task():
            logging.info(f"Initiating task {self.worker}...")
            result = requests.post(
                self.target_uri, data=self.body, timeout=self.ttl
            )  # launch
            # Set result and re commit when work is done
            self.worker.result = json.dumps(result.json())
            db.session.commit()
            logging.info(f"{self.worker} completed")
            return result.json()

        # Could not claim responsibility, wait for result to be published
        retries = 0
        while self.worker.result is None and datetime.utcnow() < self.worker.expires_on:
            logging.info(f"{self.worker} waiting...")
            time.sleep(1)
            db.session.refresh(self.worker)
            retries += 1

        # check one more time for a result before ending the task and commiting error
        if self.worker.result is None:
            self.worker.result = json.dumps({"error": "internal request timeout"})
            logging.info(f"Request timed out after {retries} attempts")
            db.session.commit()

        # Worker existed. Return result
        return json.loads(self.worker.result)

    def _claim_task(self):
        """
        This function atomically checks if there is already an entry in the DB for this
        request and creates a new one if there is not. If another process completes this step
        before the current one, an IntegrityError will be thrown and the job is rolled back.

        This function only returns true when it claims responsibility, allowing the identification
        of the "prime" process in the client code.
        """
        try:
            with db.session.begin_nested():
                # Get current worker state
                self.worker = APIWorkerModel.query.filter_by(id=self.key).one_or_none()
                if self.worker is None:
                    # Worker didn't exist yet. Create a new one.
                    self.worker = APIWorkerModel(self.key, self.ttl)
                    db.session.add(self.worker)
                    db.session.commit()  # Commit the transaction
                    return True
            return False
        except IntegrityError:
            # Handle integrity errors if the worker creation fails
            db.session.rollback()
            return False
