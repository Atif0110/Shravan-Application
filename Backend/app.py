from flask_cors import CORS
import os
from dotenv import load_dotenv
from models import *
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
from routes_stats import routes_stats
from routes_location import routes_location
from populate_yoga_data import populate_yoga_data
from security import register_security, issue_csrf_token

load_dotenv()

allowed_origins = [
    origin.strip().rstrip("/")
    for origin in os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]
CORS(app, origins=allowed_origins, supports_credentials=True)
register_security(app)

auth = {
    "GROQ_API_KEY": os.environ.get("GROQ_API_KEY"),
    "GOOGLE_MAPS_API_KEY": os.environ.get("GOOGLE_MAPS_API_KEY"),
    "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
    "YOUTUBE_API_KEY": os.environ.get("YOUTUBE_API_KEY"),
}

@app.route("/api/csrf-token", methods=["GET"])
def csrf_token():
    return {"csrf_token": issue_csrf_token(), "status": "success"}

@app.route("/")
def index():
    return {"message": "Welcome to the Shravan API!", "status": "ok"}



function_routes(app, db, auth)
routes_user(app, db)
routes_analytics(app, db)
asana_routes(app)
routes_doctors(app, db)
routes_emergency(app, db)
routes_reminders(app, db)
routes_health(app, db)
routes_content(app, db)
routes_stats(app, db)
routes_location(app)

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

        if YogaAsana.query.count() == 0:
            populate_yoga_data()
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("1", "true", "yes")
    app.run(debug=debug_mode)
