from auth.config import BaseConfig

import os


class TestConfig(BaseConfig):
    DEFAULT_SECONDS = 10
    DEFAULT_USES = 1

    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    postgres_local_base = f"postgresql://{DB_USER}:{DB_PASSWORD}@localhost/"
    local_database_name = "idva_token"

    SECRET_KEY = os.getenv("SECRET_KEY", "this_is_a_secret")
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = postgres_local_base + local_database_name
