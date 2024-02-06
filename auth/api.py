# server/auth/views.py
from flask_cors import CORS, cross_origin
import requests
import flask_pydantic
import logging

from flask import Blueprint, request, make_response, jsonify
from pydantic import BaseModel
from flask_httpauth import HTTPTokenAuth
from auth.main import db, config
from auth.models import Token
from auth.responses import Responses
from typing import Optional


auth_blueprint = Blueprint("auth", __name__)
gdrive_blueprint = Blueprint("gdrive", __name__)
redirect_blueprint = Blueprint("redirect", __name__)

CORS(redirect_blueprint, origins=["https://feedback.gsa.gov"])

req_auth = HTTPTokenAuth(header="X-API-Key")


@req_auth.verify_token
def verify_token(token):
    """
    Verify api key from header.
    """
    return token in config["SECRET_KEYS"]


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
    seconds = config["DEFAULT_SECONDS"]
    uses = config["DEFAULT_USES"]

    # get the post data
    if (
        "Content-Type" in request.headers
        and request.headers["Content-Type"] == "application/json"
    ):
        post_data = request.get_json()
        if post_data.get("seconds"):
            seconds = post_data.get("seconds")
        if post_data.get("uses"):
            uses = post_data.get("uses")

    try:
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
        print(e)
        return Responses.error()


@auth_blueprint.route("/state", methods=["GET"])
@req_auth.login_required
def state():
    """
    Token state
    """
    token_param = request.args.get("token", "")
    try:
        token = Token.query.filter_by(id=token_param).first()
        # check if token exists
        if token:
            return Responses.state(token.state)
        return Responses.not_exist()
    except:
        return Responses.unauthorized()


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
            if token.exhausted:
                return Responses.exhausted(token.state)
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
            if token.exhausted:
                return Responses.exhausted(token.state)
            # check if token is expired
            if token.is_expired():
                return Responses.expired()
            else:
                # check if token is has anymore use
                # if token refresh value is 0 (exhausted)
                if token.refresh < 1:
                    token.exhausted = True
                    db.session.commit()
                    return Responses.exhausted(token.state)
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
@req_auth.login_required
def exhaust(token_param):
    """
    Token exhaustion route
    """
    try:
        token = Token.query.filter_by(id=token_param).first()
        # check if token exists
        if token:
            if token.exhausted:
                return Responses.exhausted(token.state)
            # check if token is expired
            elif token.is_expired():
                return Responses.expired()
            else:
                token.exhausted = True
                state = request.args.get("state", "")
                token.state = state
                db.session.commit()
                return Responses.exhaust()
        else:
            return Responses.not_exist()
    except Exception:
        return Responses.unauthorized()


class SurveyParticipantModel(BaseModel):
    """
    Request body format for the `/survey-response` endpoint
    """

    surveyId: str
    responseId: str
    participant: Optional[dict] = None


@gdrive_blueprint.route("/survey-response", methods=["POST"])
@flask_pydantic.validate()
@req_auth.login_required
def export(body: SurveyParticipantModel):
    """
    GDrive microservice interface
    """

    requests.post(
        f"http://{config['GDRIVE_APP_HOST']}:{config['GDRIVE_APP_PORT']}/survey-export",
        data=body.json(),
        timeout=5,
    )
    return "Response ID successfully posted", 200


class RedirectModel(BaseModel):
    """
    Request body format for the `/redirect` endpoint
    """

    surveyId: str
    targetSurveyId: str
    RulesConsentID: str  # Client dependent
    SurveyswapID: str  # Client dependent
    SurveyswapGroup: str  # Client dependent
    utm_campaign: str
    utm_medium: str
    utm_source: str
    email: str
    firstName: str
    lastName: str


@redirect_blueprint.route("/", methods=["POST"])
@flask_pydantic.validate()
def get_redirect(body: RedirectModel):
    logging.info(
        f"Redirect request ({body.targetSurveyId}, {body.email}) routing to Qualtrix"
    )

    resp = requests.post(
        f"http://{config['QUALTRIX_APP_HOST']}:{config['QUALTRIX_APP_PORT']}/redirect",
        data=body.json(),
        timeout=5,
    )

    logging.info(f"Qualtrix Request returned with status code {resp.status_code}")

    return resp.json(), resp.status_code
