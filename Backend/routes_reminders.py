import os
import uuid
from flask import request, jsonify, session, send_from_directory
from models import db, Reminders, Medicines, MedicineLogs, VoiceReminder
from datetime import datetime, date
from flasgger.utils import swag_from
from werkzeug.utils import secure_filename

def routes_reminders(app, db):
    """
    Defines the routes for reminder management.
    """

    @app.route('/api/reminders', methods=['POST'])
    @swag_from("docs/create_reminder.yml")
    def create_reminder():
        """
        Creates a new reminder for the currently logged-in user.
        """
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated', 'status': 'fail'}), 401

        data = request.get_json()
        required_fields = ['medicine_name', 'time_of_day', 'frequency']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields (medicine_name, time_of_day, frequency)', 'status': 'fail'}), 400

        try:
            medicine = Medicines.query.filter_by(user_id=user_id, name=data['medicine_name']).first()
            if not medicine:
                medicine = Medicines(user_id=user_id, name=str(data['medicine_name']).strip()[:200], dosage=str(data.get('dosage') or '').strip()[:100] or None)
                db.session.add(medicine)
                db.session.commit()

            new_reminder = Reminders(
                user_id=user_id,
                medicine_id=medicine.medicine_id,
                time_of_day=data['time_of_day'],
                relation_to_meal=data.get('relation_to_meal'),
                frequency=data['frequency'],
                notification_type=data.get('notification_type', 'sms'),
                is_active=data.get('is_active', True)
            )

            db.session.add(new_reminder)
            db.session.commit()

            return jsonify({
                'message': 'Reminder created successfully',
                'status': 'success',
                'reminder_id': new_reminder.reminder_id
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error creating reminder: {str(e)}', 'status': 'fail'}), 500

    @app.route('/api/reminders', methods=['GET'])
    @swag_from("docs/get_reminders.yml")
    def get_reminders():
        """
        Gets all reminders for the currently logged-in user.
        """
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated', 'status': 'fail'}), 401

        try:
            reminders = Reminders.query.filter_by(user_id=user_id).order_by(Reminders.time_of_day).all()

            today = date.today()
            todays_logs = MedicineLogs.query.filter(
                MedicineLogs.reminder_id.in_([r.reminder_id for r in reminders]),
                MedicineLogs.log_date == today
            ).all()
            latest_status_by_reminder = {}
            for log in todays_logs:
                latest_status_by_reminder[log.reminder_id] = log.status

            reminders_list = []
            for r in reminders:
                reminders_list.append({
                    'reminder_id': r.reminder_id,
                    'medicine_name': r.medicine.name,
                    'dosage': r.medicine.dosage,
                    'time_of_day': r.time_of_day,
                    'frequency': r.frequency,
                    'relation_to_meal': r.relation_to_meal,
                    'is_active': r.is_active,
                    'today_status': latest_status_by_reminder.get(r.reminder_id, 'pending')
                })
            return jsonify({'status': 'success', 'reminders': reminders_list}), 200

        except Exception as e:
            return jsonify({'error': f'Error fetching reminders: {str(e)}', 'status': 'fail'}), 500

    @app.route('/api/reminders/<int:reminder_id>', methods=['GET'])
    @swag_from("docs/get_reminder_by_id.yml")
    def get_reminder_by_id(reminder_id):
        """
        Gets a single reminder by its ID.
        """
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated', 'status': 'fail'}), 401

        try:
            reminder = Reminders.query.filter_by(reminder_id=reminder_id, user_id=user_id).first()

            if not reminder:
                return jsonify({'error': 'Reminder not found or access denied', 'status': 'fail'}), 404

            return jsonify({
                'status': 'success',
                'reminder': {
                    'reminder_id': reminder.reminder_id,
                    'medicine_name': reminder.medicine.name,
                    'dosage': reminder.medicine.dosage,
                    'time_of_day': reminder.time_of_day,
                    'frequency': reminder.frequency,
                    'relation_to_meal': reminder.relation_to_meal,
                    'is_active': reminder.is_active
                }
            }), 200

        except Exception as e:
            return jsonify({'error': f'Error fetching reminder: {str(e)}', 'status': 'fail'}), 500

    @app.route('/api/reminders/<int:reminder_id>', methods=['PUT'])
    @swag_from("docs/update_reminder.yml")
    def update_reminder(reminder_id):
        """
        Updates a specific reminder for the logged-in user.
        """
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated', 'status': 'fail'}), 401

        try:
            reminder = Reminders.query.filter_by(reminder_id=reminder_id, user_id=user_id).first()

            if not reminder:
                return jsonify({'error': 'Reminder not found or access denied', 'status': 'fail'}), 404

            data = request.get_json()

            if 'medicine_name' in data:
                medicine = Medicines.query.filter_by(user_id=user_id, name=data['medicine_name']).first()
                if not medicine:
                    medicine = Medicines(user_id=user_id, name=str(data['medicine_name']).strip()[:200], dosage=str(data.get('dosage') or '').strip()[:100] or None)
                    db.session.add(medicine)
                    db.session.commit()
                reminder.medicine_id = medicine.medicine_id

            if 'time_of_day' in data:
                reminder.time_of_day = data['time_of_day']
            if 'frequency' in data:
                reminder.frequency = data['frequency']
            if 'relation_to_meal' in data:
                reminder.relation_to_meal = data['relation_to_meal']
            if 'is_active' in data:
                reminder.is_active = data['is_active']
            if 'notification_type' in data:
                reminder.notification_type = data['notification_type']

            db.session.commit()

            return jsonify({'message': 'Reminder updated successfully', 'status': 'success'}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error updating reminder: {str(e)}', 'status': 'fail'}), 500

    @app.route('/api/reminders/<int:reminder_id>', methods=['DELETE'])
    @swag_from("docs/delete_reminder.yml")
    def delete_reminder(reminder_id):
        """
        Deletes a specific reminder for the logged-in user.
        """
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated', 'status': 'fail'}), 401

        try:
            reminder = Reminders.query.filter_by(reminder_id=reminder_id, user_id=user_id).first()

            if not reminder:
                return jsonify({'error': 'Reminder not found or access denied', 'status': 'fail'}), 404


            db.session.delete(reminder)
            db.session.commit()

            return jsonify({'message': 'Reminder deleted successfully', 'status': 'success'}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error deleting reminder: {str(e)}', 'status': 'fail'}), 500

    VOICE_UPLOAD_DIR = os.path.join(os.path.dirname(__file__), 'uploads', 'voice_reminders')
    os.makedirs(VOICE_UPLOAD_DIR, exist_ok=True)

    @app.route('/api/voice-reminders', methods=['POST'])
    def create_voice_reminder():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated', 'status': 'fail'}), 401

        title = (request.form.get('title') or 'Voice reminder').strip()[:200]
        audio = request.files.get('audio')
        if not audio:
            return jsonify({'error': 'An audio file is required', 'status': 'fail'}), 400
        allowed_extensions = {'.m4a', '.mp3', '.wav', '.webm', '.ogg', '.aac'}
        original_name = secure_filename(audio.filename or '')
        ext = os.path.splitext(original_name)[1].lower() or '.m4a'
        if ext not in allowed_extensions:
            return jsonify({'error': 'Unsupported audio format', 'status': 'fail'}), 400

        try:
            stored_name = f"{user_id}_{uuid.uuid4().hex[:12]}{ext}"
            audio.save(os.path.join(VOICE_UPLOAD_DIR, stored_name))

            reminder = VoiceReminder(
                user_id=user_id,
                title=title,
                audio_url=f"/api/voice-reminders/audio/{stored_name}"
            )
            db.session.add(reminder)
            db.session.commit()
            return jsonify(reminder.to_dict()), 201
        except Exception as exc:
            db.session.rollback()
            return jsonify({'error': f'Could not save voice reminder: {str(exc)}', 'status': 'fail'}), 500

    @app.route('/api/voice-reminders', methods=['GET'])
    def get_voice_reminders():
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated', 'status': 'fail'}), 401
        reminders = (VoiceReminder.query.filter_by(user_id=user_id)
                     .order_by(VoiceReminder.created_at.desc()).all())
        return jsonify([r.to_dict() for r in reminders]), 200

    @app.route('/api/voice-reminders/audio/<path:filename>', methods=['GET'])
    def serve_voice_reminder_audio(filename):
        reminder = VoiceReminder.query.filter_by(
            user_id=session.get('user_id'),
            audio_url=f'/api/voice-reminders/audio/{filename}',
        ).first()
        if not reminder:
            return jsonify({'error': 'Audio reminder not found', 'status': 'fail'}), 404
        return send_from_directory(VOICE_UPLOAD_DIR, filename)
