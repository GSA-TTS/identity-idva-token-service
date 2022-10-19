# server/__init__.py

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app_settings = os.getenv("APP_SETTINGS", "server.config.LocalDevConfig")

app.config.from_object(app_settings)

config = app.config

db = SQLAlchemy(app)
db.create_all()

from server.auth.views import auth_blueprint

app.register_blueprint(auth_blueprint)
