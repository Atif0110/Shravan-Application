# from config import app, db
from flask import Flask
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from models import *
import json
from config import app,db
from routes_functions import function_routes
from routes_user import routes_user
from routes_analytics import routes_analytics
from routes_content import routes_content
from routes_doctors import routes_doctors
from routes_emergency import routes_emergency
from routes_reminders import routes_reminders
from routes_health import routes_health
from routes_asanas import asana_routes
from routes_content import routes_content
from populate_yoga_data import populate_yoga_data

load_dotenv()

# Restrict CORS to known frontend origins instead of allowing all origins.
# Set ALLOWED_ORIGINS in .env as a comma-separated list, e.g.:
# ALLOWED_ORIGINS=http://localhost:5173,https://yourdomain.com
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
CORS(app, origins=[origin.strip() for origin in allowed_origins.split(",") if origin.strip()], supports_credentials=True)

# API keys now live in Backend/.env (see .env.example) instead of a separate
# authorisation.json file, so a fresh checkout no longer crashes on startup
# if that file is missing.
auth = {
    "GROQ_API_KEY": os.environ.get("GROQ_API_KEY"),
    "GOOGLE_MAPS_API_KEY": os.environ.get("GOOGLE_MAPS_API_KEY"),
    "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
}
missing_keys = [k for k, v in auth.items() if not v]
if missing_keys:
    print(f"WARNING: Missing API key(s) in .env: {', '.join(missing_keys)}. Related features will fail.")

@app.route("/")
def index():
    return {"message": "Welcome to the Shravan API!"}



function_routes(app, db, auth)
routes_user(app, db)
routes_analytics(app, db)
asana_routes(app)
routes_doctors(app, db)
routes_emergency(app, db)
routes_reminders(app, db)
routes_health(app, db)
routes_content(app, db)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
        if Roles.query.count() == 0:
            default_roles = [
                Roles(name='ngo', description='Non-Governmental Organization'),
                Roles(name='caretaker', description='Doctor,Nurse etc'),
                Roles(name='user', description='General User')
            ]
            db.session.bulk_save_objects(default_roles)
            db.session.commit()

        # Age-Friendly Yoga was showing "No yoga asanas found" because the
        # asana table was only ever filled by manually running
        # populate_yoga_data.py -- easy to forget on a fresh database. Seed
        # it here the same way roles are seeded above, and skip it if the
        # data is already there so this stays safe to run on every restart.
        if YogaAsana.query.count() == 0:
            populate_yoga_data()
    # Debug mode is controlled via .env (FLASK_DEBUG=True for local dev only).
    # Flask's debugger can execute arbitrary code -- never leave this True
    # on a server that's reachable from the internet.
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("1", "true", "yes")
    app.run(debug=debug_mode)