# server/auth/views.py

from crypt import methods
from flask import Blueprint, request, make_response, jsonify
from flask_httpauth import HTTPTokenAuth
from server import db, config
from server.models import Token
from server.auth.responses import Responses

import server.config as config

auth_blueprint = Blueprint("auth", __name__)
req_auth = HTTPTokenAuth(header="X-API-Key")


@req_auth.verify_token
def verify_token(token):
    """
    Verify api key from header.
    """
    return token == config["SECRET_KEY"]


@req_auth.error_handler
def unauthorized():
    return make_response(jsonify({"message": "Unauthorized access"}), 403)


@auth_blueprint.route("/register", methods=["POST"])
@req_auth.login_required
def register():
    """
    Token registration route
    """
    # get the post data
    post_data = request.get_json()
    try:
        token = Token()
        if post_data and post_data.get("seconds"):
            token = Token(seconds=post_data["seconds"])
        # insert the user
        db.session.add(token)
        db.session.commit()
        # generate the auth token
        auth_token = token.id
        responseObject = {
            "status": "success",
            "message": "Successfully registered.",
            "auth_token": auth_token,
        }
        return make_response(jsonify(responseObject)), 201
    except Exception as e:
        print(e)
        return Responses.error()


@auth_blueprint.route("/validate", methods=["POST"])
@req_auth.login_required
def validate():
    """
    Token validation route
    """
    post_data = request.get_json()
    try:
        token = Token.query.filter_by(id=post_data.get("auth_token")).first()
        # check if token exists
        if token:
            # check if token is expired
            if token.is_expired():
                return Responses.expired()
            else:
                return Responses.exist()
    except Exception:
        return Responses.unauthorized()


@auth_blueprint.route("/invoke", methods=["POST"])
@req_auth.login_required
def invoke():
    """
    Token invocation route
    """
    post_data = request.get_json()
    try:
        token = Token.query.filter_by(id=post_data.get("auth_token")).first()
        # check if token exists
        if token:
            # check if token is expired
            if token.is_expired():
                return Responses.expired()
            else:
                # check if token is has anymore use
                # if token refresh value is 0 (exhausted)
                if token.refresh < 1:
                    db.session.delete(token)
                    db.session.commit()
                    return Responses.exhausted()
                else:
                    # decrement from the refresh count
                    # maybe delete if it's now 0?
                    token.refresh = token.refresh - 1
                    db.session.commit()
                    return Responses.refresh()

    except Exception:
        return Responses.unauthorized()


@auth_blueprint.route("/exhaust", methods=["POST"])
def exhaust():
    """
    Token exhaustion route
    """
    post_data = request.get_json()
    try:
        token = Token.query.filter_by(id=post_data.get("auth_token")).first()
        # check if token exists
        if token:
            # check if token is expired
            if token.is_expired():
                return Responses.expired()
            else:
                return Responses.exhaust()
    except Exception:
        return Responses.unauthorized()
