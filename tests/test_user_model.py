# tests/test_user_model.py

import unittest
from uuid import UUID

from token_service.main import db, config
from token_service.models import Token
from tests.base import BaseTestCase


class TestUserModel(BaseTestCase):
    def test_encode_auth_token(self):
        seconds = config["DEFAULT_SECONDS"]
        uses = config["DEFAULT_USES"]
        token = Token(seconds, uses)

        db.session.add(token)
        db.session.commit()
        auth_token = token.id
        self.assertTrue(isinstance(auth_token, UUID))


if __name__ == "__main__":
    unittest.main()
