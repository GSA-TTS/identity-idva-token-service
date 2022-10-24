# server/auth/responses.py

from flask import make_response, jsonify


class Responses:
    """
    Functions that generate and return specific http responses
    """

    def exist():
        return (
            make_response(jsonify({"status": "success", "message": "Token exists"})),
            200,
        )

    def refresh():
        return (
            make_response(
                jsonify({"status": "success", "message": "Token successfully invoked"})
            ),
            200,
        )

    def exhaust():
        return (
            make_response(
                jsonify(
                    {"status": "success", "message": "Token successfully exhausted"}
                )
            ),
            200,
        )

    def error():
        return (
            make_response(
                jsonify(
                    {
                        "status": "fail",
                        "message": "Some error occurred. Please try again.",
                    }
                )
            ),
            401,
        )

    def expired():
        return (
            make_response(jsonify({"status": "fail", "message": "Token expired"})),
            403,
        )

    def exhausted():
        return (
            make_response(jsonify({"status": "fail", "message": "Token exhausted"})),
            403,
        )

    def unauthorized():
        return (
            make_response(jsonify({"status": "fail", "message": "Unauthorized"})),
            403,
        )
