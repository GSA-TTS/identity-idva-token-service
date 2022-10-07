# project/server/tests/test_config.py


import unittest
import os

from flask import current_app
from flask_testing import TestCase

from server import app

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

PSQL_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@localhost"

DB_NAME = "idva_token"


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object("server.config.LocalDevConfig")
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config["DEBUG"] is True)
        self.assertFalse(current_app is None)
        # print('{PSQL_URL}/flask_jwt_auth')
        self.assertTrue(
            app.config["SQLALCHEMY_DATABASE_URI"] == f"{PSQL_URL}/{DB_NAME}"
        )


if __name__ == "__main__":
    unittest.main()
