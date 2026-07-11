from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
from dotenv import load_dotenv
from flask_session import Session  # For server-side session managementAdd commentMore actions
from flasgger import Swagger

load_dotenv()

app = Flask(__name__, static_folder="../Frontend")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


secret_key = os.environ.get('SECRET_KEY')
if not secret_key:
    # Falls back to a random key so the app still runs, but this means
    # sessions/cookies won't survive a restart. Set SECRET_KEY in your
    # .env for real (local dev or production) use.
    secret_key = secrets.token_hex(32)
    print(
        "WARNING: SECRET_KEY not set in environment. Using a temporary "
        "random key for this run only -- add SECRET_KEY to Backend/.env "
        "to keep sessions stable across restarts."
    )
app.config['SECRET_KEY'] = secret_key
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False

# Frontend (5173) and backend (5000) run on different origins during
# development, so the session cookie is "cross-site" from the browser's
# point of view. Without SameSite=None, browsers refuse to send it back
# on fetch() calls, which is why login state kept disappearing (profile
# 401s, medicine reminder "taken" status resetting on navigation, etc.)
# SameSite=None requires Secure, so we only turn it on when the app is
# actually served over https. Locally over http, SameSite=Lax is used as
# a fallback -- it works as long as frontend and backend share the same
# hostname (127.0.0.1 for both, or localhost for both, not a mix).
FLASK_ENV_HTTPS = os.environ.get("SESSION_COOKIE_SECURE", "False").lower() == "true"
app.config["SESSION_COOKIE_SAMESITE"] = "None" if FLASK_ENV_HTTPS else "Lax"
app.config["SESSION_COOKIE_SECURE"] = FLASK_ENV_HTTPS
app.config["SESSION_COOKIE_HTTPONLY"] = True
Session(app)


swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Shravan API",
        "description": "API documentation for Shravan Health App",
        "version": "1.0.0"
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

db = SQLAlchemy(app)