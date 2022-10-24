# server/config.py

import os
import json
import logging

log = logging.getLogger(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

postgres_local_base = f"postgresql://{DB_USER}:{DB_PASSWORD}@localhost/"
local_database_name = "idva_token"


class BaseConfig:
    """Base configuration."""

    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class LocalDevConfig(BaseConfig):
    """Development configuration for local deployments."""

    DEFAULT_SECONDS = 10
    DEFAULT_USES = 1

    SECRET_KEY = os.getenv("SECRET_KEY", "this_is_a_secret")
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = postgres_local_base + local_database_name


class CloudDevConfig(BaseConfig):
    """Development configuration for cloud foundry deployments."""

    DEFAULT_SECONDS = 604800
    DEFAULT_USES = 1

    SECRET_KEY = os.getenv("SECRET_KEY")

    vcap_services = os.getenv("VCAP_SERVICES", "")
    try:
        db_uri = json.loads(vcap_services)["aws-rds"][0]["credentials"]["uri"]
    except (json.JSONDecodeError, KeyError) as err:
        log.warning("Unable to load db_uri from VCAP_SERVICES")
        log.debug("Error: %s", str(err))
        db_uri = ""

    # Sqlalchemy requires 'postgresql' as the protocol
    db_uri = db_uri.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = db_uri
