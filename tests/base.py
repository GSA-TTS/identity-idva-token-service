# server/tests/base.py


from flask_testing import TestCase

from auth.main import app, db


class BaseTestCase(TestCase):
    """Base Tests"""

    def create_app(self):
        app.config.from_object("tests.config.TestConfig")
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
