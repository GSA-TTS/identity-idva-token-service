# project/server/models.py

import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID
from server import db


class Token(db.Model):
    """Token Model for storing a token with meta information"""

    __tablename__ = "tokens"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid1)
    registered_on = db.Column(db.DateTime, nullable=False)
    expires_on = db.Column(db.DateTime, nullable=False)
    refresh = db.Column(db.Integer, nullable=False)

    def __init__(self, seconds=300):
        self.registered_on = datetime.datetime.now()
        self.expires_on = datetime.datetime.now() + datetime.timedelta(
            days=0, seconds=seconds
        )
        self.refresh = 1

    def is_expired(self):
        time_of_request = datetime.datetime.now()
        return self.expires_on < time_of_request
