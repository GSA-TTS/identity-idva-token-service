import uuid

from datetime import datetime, timedelta
from sqlalchemy.dialects.postgresql import UUID
from auth.main import db


class APIWorkerModel(db.Model):
    """Model for holding a pointer to an interal API task"""

    __tablename__ = "gateway_workers"

    id = db.Column(db.String, primary_key=True)
    result = db.Column(db.String, nullable=True)
    registered_on = db.Column(db.DateTime, nullable=False)
    expires_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, id: str, expiration_seconds: int):
        """
        Creates a pointer to a worker to run a HTTP request

        Args:
            id (str): Any string identifier to "name" the process. (Ex. email)
            target (str): target URI
            body_json (str): json input body
            expiration_seconds (int): how long the process has to live
        """
        self.id = id
        self.registered_on = datetime.utcnow()
        self.expires_on = self.registered_on + timedelta(seconds=expiration_seconds)
        self.result = None


class Token(db.Model):
    """Token Model for storing a token with meta information"""

    __tablename__ = "tokens"

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid1().hex
    )
    registered_on = db.Column(db.DateTime, nullable=False)
    expires_on = db.Column(db.DateTime, nullable=False)
    refresh = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String, nullable=False, default="init")
    exhausted = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, seconds, uses):
        self.registered_on = datetime.now()
        self.expires_on = datetime.now() + timedelta(days=0, seconds=seconds)
        self.refresh = uses

    def is_expired(self):
        time_of_request = datetime.now()
        return self.expires_on < time_of_request
