# tests/test_auth.py

from time import sleep
import unittest
import json

from tests.base import BaseTestCase
from auth.main import config


class TestAuthBlueprint(BaseTestCase):
    def test_registration(self):
        """Test for token registration"""
        with self.client:
            response = self.client.post(
                "/auth",
                headers={"X_API_KEY": config["SECRET_KEY"]},
            )
            print("Response:")
            print(response.data)
            data = json.loads(response.data)
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["message"], "Successfully registered.")
            self.assertTrue(data["auth_token"])
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)

    def test_validation(self):
        """Test for validity of registered token"""
        with self.client:
            response = self.client.post(
                "/auth", headers={"X_API_KEY": config["SECRET_KEY"]}
            )
            data = json.loads(response.data)
            auth_token = data["auth_token"]

            self.assertEqual(data["status"], "success")
            self.assertEqual(data["message"], "Successfully registered.")
            self.assertTrue(auth_token)
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)

            response = self.client.get(
                "/auth/" + auth_token,
                headers={"X-API-Key": config["SECRET_KEY"]},
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Token exists")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 200)

    def test_validation_does_not_exist(self):
        """Test for validity of registered token"""
        with self.client:
            response = self.client.get(
                "/auth/NOT_A_TOKEN",
                headers={"X-API-Key": config["SECRET_KEY"]},
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(data["message"] == "Unauthorized")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 403)

    def test_validation_expired(self):
        """Test for validity of registered token"""
        with self.client:
            # register token with 1 second expiration
            response = self.client.post(
                "/auth",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"seconds": 1}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            auth_token = data["auth_token"]

            self.assertEqual(data["status"], "success")
            self.assertEqual(data["message"], "Successfully registered.")
            self.assertTrue(auth_token)
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)

            # validate token
            # wait for token to expire
            sleep(5)
            response = self.client.get(
                "/auth/" + auth_token,
                headers={"X-API-Key": config["SECRET_KEY"]},
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertTrue(data["status"] == "fail")
            self.assertTrue(data["message"] == "Token expired")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 403)

    def test_validation_invoke(self):
        """Test for decrement of registered token"""
        with self.client:
            # register token with 1 second expiration
            response = self.client.post(
                "/auth",
                headers={"X-API-Key": config["SECRET_KEY"]},
            )
            data = json.loads(response.data)
            auth_token = data["auth_token"]

            self.assertEqual(data["status"], "success")
            self.assertEqual(data["message"], "Successfully registered.")
            self.assertTrue(auth_token)
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)

            # invoke token (valid attempt)
            response = self.client.post(
                "/auth/" + auth_token + "/decrement",
                headers={"X-API-Key": config["SECRET_KEY"]},
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertTrue(data["status"] == "success")
            self.assertTrue(data["message"] == "Token successfully invoked")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 200)

    def test_validation_invoke_exhausted(self):
        """Test for validity of registered token"""
        with self.client:
            # register token with 1 second expiration
            # key = "something " + config["SECRET_KEY"]
            x = config["SECRET_KEY"]
            response = self.client.post(
                "/auth",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"seconds": 60}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            auth_token = data["auth_token"]

            self.assertEqual(data["status"], "success")
            self.assertEqual(data["message"], "Successfully registered.")
            self.assertTrue(auth_token)
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)

            # invoke token (valid attempt)
            self.client.post(
                "/auth/" + auth_token + "/decrement",
                headers={"X-API-Key": config["SECRET_KEY"]},
                content_type="application/json",
            )
            # invoke token (invalid attempt)
            response = self.client.post(
                "/auth/" + auth_token + "/decrement",
                headers={"X-API-Key": config["SECRET_KEY"]},
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertEqual(data["status"], "fail")
            self.assertEqual(data["message"], "Token exhausted")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 403)

    def test_exhaust(self):
        with self.client:
            # register token with 1 second expiration
            response = self.client.post(
                "/auth",
                headers={"X-API-Key": config["SECRET_KEY"]},
                data=json.dumps({"seconds": 60}),
                content_type="application/json",
            )
            data = json.loads(response.data)
            auth_token = data["auth_token"]

            self.assertEqual(data["status"], "success")
            self.assertEqual(data["message"], "Successfully registered.")
            self.assertTrue(auth_token)
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 201)

            # exhaust token (valid attempt)
            response = self.client.delete(
                "/auth/" + auth_token,
                headers={"X-API-Key": config["SECRET_KEY"]},
                content_type="application/json",
            )
            data = json.loads(response.data)
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["message"], "Token successfully exhausted")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 200)

            response = self.client.delete(
                "/auth/" + auth_token,
                headers={"X-API-Key": config["SECRET_KEY"]},
                content_type="application/json",
            )

            data = json.loads(response.data)
            self.assertEqual(data["status"], "fail")
            self.assertEqual(data["message"], "Bad token")
            self.assertTrue(response.content_type == "application/json")
            self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
