# project/server/auth/views.py

from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView

from server import db
from server.models import Token
from server.auth.responses import Responses


auth_blueprint = Blueprint("auth", __name__)


class RegisterAPI(MethodView):
    """
    Token Registration Resource
    """

    def post(self):
        # get the post data
        post_data = request.get_json()
        try:
            token = Token()
            if post_data and post_data.seconds:
                token = Token(seconds=post_data.seconds)
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


class ValidateAPI(MethodView):
    """
    Token validation
    return with a 200 if the token exists
    return with a 403 otherwise
    """

    def post(self):
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


class RefreshAPI(MethodView):
    def post(self):
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


class ExhaustAPI(MethodView):
    def post(self):
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


registration_view = RegisterAPI.as_view("register_api")
validation_view = ValidateAPI.as_view("validation_api")
refresh_view = RefreshAPI.as_view("refresh_api")
exuast_view = ExhaustAPI.as_view("exhaust_api")

auth_blueprint.add_url_rule(
    "/auth/register", view_func=registration_view, methods=["POST"]
)
auth_blueprint.add_url_rule(
    "/auth/validate", view_func=validation_view, methods=["POST"]
)
auth_blueprint.add_url_rule("/auth/refresh", view_func=refresh_view, methods=["POST"])
auth_blueprint.add_url_rule("/auth/exhaust", view_func=exuast_view, methods=["POST"])
