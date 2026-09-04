from flask import jsonify
from models import User, Doctors, Reminders, EmergencyContacts
from sqlalchemy import func


def routes_stats(app, db):
    @app.route('/api/stats', methods=['GET'])
    def get_app_statistics():
        try:
            return jsonify({
                'users': db.session.query(func.count(User.user_id)).scalar() or 0,
                'doctors': db.session.query(func.count(Doctors.doctor_id)).scalar() or 0,
                'reminders': db.session.query(func.count(Reminders.reminder_id)).scalar() or 0,
                'emergencyContacts': db.session.query(func.count(EmergencyContacts.emergency_contact_id)).scalar() or 0,
            })
        except Exception:
            return jsonify({'error': 'Statistics are temporarily unavailable', 'status': 'fail'}), 503
