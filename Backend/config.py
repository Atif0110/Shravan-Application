import os
import secrets
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__, static_folder="../Frontend")
secret_key = os.environ.get("SECRET_KEY")
if not secret_key or secret_key.startswith("replace-") or "your_" in secret_key:
    secret_key = secrets.token_hex(32)

app.config.update(
    SECRET_KEY=secret_key,
    SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", f"sqlite:///{DATABASE_PATH}"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    MAX_CONTENT_LENGTH=8 * 1024 * 1024,
    SESSION_TYPE="filesystem",
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
    SESSION_REFRESH_EACH_REQUEST=True,
    SESSION_USE_SIGNER=True,
    SESSION_COOKIE_NAME="__Host-shravan_session" if os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true" else "shravan_session",
    SESSION_COOKIE_SECURE=os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE=os.environ.get("SESSION_COOKIE_SAMESITE", "Lax"),
    SESSION_COOKIE_PATH="/",
)

Session(app)
db = SQLAlchemy(app)

swagger_config = {
    "headers": [],
    "specs": [{
        "endpoint": "apispec_1",
        "route": "/apispec_1.json",
        "rule_filter": lambda rule: True,
        "model_filter": lambda tag: True,
    }],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Shravan API",
        "description": "API documentation for Shravan Health App",
        "version": "2.0.0",
    },
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)
