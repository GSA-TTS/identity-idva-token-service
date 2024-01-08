import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_cors import CORS, cross_origin

app = Flask(__name__)

app_settings = os.getenv("APP_SETTINGS")

app.config.from_object(app_settings)

config = app.config
db = SQLAlchemy(app)

from auth.api import auth_blueprint, gdrive_blueprint, redirect_blueprint

app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(gdrive_blueprint, url_prefix="/export")
app.register_blueprint(redirect_blueprint, url_prefix="/redirect")
