# project/server/__init__.py

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app_settings = os.getenv("APP_SETTINGS", "server.config.LocalDevConfig")
app.config.from_object(app_settings)

db = SQLAlchemy(app)

from server.auth.views import auth_blueprint

app.register_blueprint(auth_blueprint)
