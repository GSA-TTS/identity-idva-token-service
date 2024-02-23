import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app_settings = os.getenv("APP_SETTINGS")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.getLogger().setLevel(LOG_LEVEL)

app.config.from_object(app_settings)

config = app.config
db = SQLAlchemy(app)

from auth.api import auth_blueprint, gdrive_blueprint, redirect_blueprint

with app.app_context():
    db.create_all()

app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(gdrive_blueprint, url_prefix="/export")
app.register_blueprint(redirect_blueprint, url_prefix="/redirect")
