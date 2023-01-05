# server/auth/views.py
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


"""

/auth/register -> POST /auth
/auth/validate -> GET /auth/{token}
/auth/exhaust -> DELETE /auth/{token}
/auth/invoke -> POST /auth/{token}/decrement/

"""


@auth_blueprint.route("", methods=["POST"])
@req_auth.login_required
def register():
    """
    Token registration route
    """
    # get the post data
    post_data = request.get_json()
    try:
        seconds = config["DEFAULT_SECONDS"]
        uses = config["DEFAULT_USES"]

        if post_data:
            if post_data.get("seconds"):
                seconds = post_data.get("seconds")
            if post_data.get("uses"):
                uses = post_data.get("uses")

        token = Token(seconds, uses)

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
        return Responses.error()


@auth_blueprint.route("/<token_param>", methods=["GET"])
@req_auth.login_required
def validate(token_param):
    """
    Token validation route
    """
    # post_data = request.get_json()
    try:
        token = Token.query.filter_by(id=token_param).first()
        # check if token exists
        if token:
            # check if token is expired
            if token.is_expired():
                return Responses.expired()
            else:
                return Responses.exist()
        else:
            return Responses.not_exist()
    except:
        return Responses.unauthorized()


@auth_blueprint.route("/<token_param>/decrement", methods=["POST"])
@req_auth.login_required
def invoke(token_param):
    """
    Token invocation route
    """
    try:
        token = Token.query.filter_by(id=token_param).first()
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
        else:
            return Responses.not_exist()
    except Exception:
        return Responses.unauthorized()


@auth_blueprint.route("/<token_param>", methods=["DELETE"])
def exhaust(token_param):
    """
    Token exhaustion route
    """
    try:
        token = Token.query.filter_by(id=token_param).first()
        # check if token exists
        if token:
            # check if token is expired
            if token.is_expired():
                return Responses.expired()
            else:
                db.session.delete(token)
                db.session.commit()
                return Responses.exhaust()
        else:
            return Responses.not_exist()
    except Exception:
        return Responses.unauthorized()
