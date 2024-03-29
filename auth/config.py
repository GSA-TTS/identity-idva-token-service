# server/config.py

import os
import json
import logging

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    """Base configuration."""

    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(BaseConfig):
    """Development configuration for cloud foundry deployments."""

    DEFAULT_SECONDS = 604800  # 7 days
    DEFAULT_USES = 1

    SECRET_KEYS = None

    REQUEST_TIMEOUT = getenvint("REQUEST_TIMEOUT", 10)

    GDRIVE_APP_HOST = os.getenv("GDRIVE_APP_HOST")
    GDRIVE_APP_PORT = os.getenv("GDRIVE_APP_PORT")

    QUALTRIX_APP_HOST = os.getenv("QUALTRIX_APP_HOST")
    QUALTRIX_APP_PORT = os.getenv("QUALTRIX_APP_PORT")

    vcap_services = os.getenv("VCAP_SERVICES", "")

    try:
        services = json.loads(vcap_services)
        for service in services["user-provided"]:
            if service["name"] == "token-service-secret":
                logging.info("Loading secret key from user service")
                SECRET_KEYS = service["credentials"]["keys"]
                break
        if SECRET_KEYS == None:
            logging.error("Unable to load secret key from user service")
        db_uri = services["aws-rds"][0]["credentials"]["uri"]
    except (json.JSONDecodeError, KeyError) as err:
        logging.warning("Unable to load db_uri from VCAP_SERVICES")
        logging.debug("Error: %s", str(err))
        db_uri = os.getenv("IDVA_DB_CONN_STR", "")
        SECRET_KEYS = [os.getenv("TOKEN_SECRET_KEY")]

    # Sqlalchemy requires 'postgresql' as the protocol
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_uri


def getenvint(name: str, default: int):
    try:
        return int(os.getenv(name, ""))
    except ValueError:
        return default
