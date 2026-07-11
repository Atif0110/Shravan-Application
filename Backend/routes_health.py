from flask import Flask, request, jsonify, session
from models import *
from datetime import date, datetime
from flasgger.utils import swag_from

def routes_health(app, db):
    # Endpoint for the senior to log taking a medicine
    @app.route('/api/medicine-logs', methods=['POST'])
    @swag_from("docs/log_medicine_intake.yml")
    def log_medicine_intake():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated', 'status': 'fail'}), 401

        data = request.get_json()
        reminder_id = data.get('reminder_id')
        status = data.get('status', 'taken')  # 'taken' or 'skipped'

        if not reminder_id:
            return jsonify({'error': 'Reminder ID is required'}), 400

        # Make sure the reminder actually belongs to the logged-in user,
        # same check the other reminder routes use.
        reminder = Reminders.query.filter_by(reminder_id=reminder_id, user_id=user_id).first()
        if not reminder:
            return jsonify({'error': 'Reminder not found or access denied', 'status': 'fail'}), 404

        today = date.today()

        # If this reminder was already logged today, update that row instead
        # of inserting a second one -- otherwise tapping "Taken" twice (or a
        # refresh replaying the request) would leave two log rows for the
        # same medicine on the same day.
        existing_log = MedicineLogs.query.filter_by(reminder_id=reminder_id, log_date=today).first()
        if existing_log:
            existing_log.status = status
            existing_log.actual_time = datetime.now().time()
        else:
            existing_log = MedicineLogs(
                reminder_id=reminder_id,
                log_date=today,
                status=status,
                actual_time=datetime.now().time()
            )
            db.session.add(existing_log)

        db.session.commit()
        return jsonify({'message': 'Medicine intake logged successfully', 'status': 'success'}), 201

    @app.route('/api/users/<int:user_id>/health-summary', methods=['GET'])
    @swag_from("docs/get_health_summary.yml")
    def get_health_summary(user_id):
        
        today = date.today()
        logs = MedicineLogs.query.join(Reminders).filter(Reminders.user_id == user_id, MedicineLogs.log_date == today).all()

        summary = {
            'date': today.isoformat(),
            'medicine_taken': len([l for l in logs if l.status == 'taken']),
            'medicine_skipped': len([l for l in logs if l.status == 'skipped']),
            'log_details': [{
                'medicine_name': l.reminder.medicine.name,
                'status': l.status,
                'time': l.actual_time.strftime('%H:%M:%S') if l.actual_time else None
            } for l in logs]
        }
        return jsonify(summary), 200