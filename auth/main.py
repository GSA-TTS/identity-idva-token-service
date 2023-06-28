import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app_settings = os.getenv("APP_SETTINGS")

app.config.from_object(app_settings)

config = app.config
db = SQLAlchemy(app)

from auth.api import auth_blueprint, gdrive_blueprint

app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(gdrive_blueprint, url_prefix="/export")

with app.app_context():
    db.drop_all()
    db.create_all()
