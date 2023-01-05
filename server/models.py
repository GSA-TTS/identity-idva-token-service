# server/models.py
import datetime
import uuid

from server import db
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID


class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.
    """

    impl = CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


class Token(db.Model):
    """Token Model for storing a token with meta information"""

    __tablename__ = "tokens"

    id = db.Column(GUID(), primary_key=True, default=lambda: str(uuid.uuid4()))
    registered_on = db.Column(db.DateTime, nullable=False)
    expires_on = db.Column(db.DateTime, nullable=False)
    refresh = db.Column(db.Integer, nullable=False)

    def __init__(self, seconds, uses):
        self.registered_on = datetime.datetime.now()
        self.expires_on = datetime.datetime.now() + datetime.timedelta(
            days=0, seconds=seconds
        )
        self.refresh = uses

    def is_expired(self):
        time_of_request = datetime.datetime.now()
        return self.expires_on < time_of_request
