# project/tests/test_user_model.py

import unittest
from uuid import UUID

from server import db
from server.models import Token
from tests.base import BaseTestCase


class TestUserModel(BaseTestCase):
    def test_encode_auth_token(self):
        token = Token()

        db.session.add(token)
        db.session.commit()
        auth_token = token.id
        self.assertTrue(isinstance(auth_token, UUID))


if __name__ == "__main__":
    unittest.main()
