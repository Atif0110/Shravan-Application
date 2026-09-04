from flask import request, jsonify
from models import db, EmergencyContacts
from flasgger.utils import swag_from
from security import current_user_id


def routes_emergency(app, db):
    @app.route('/api/emergency-contacts', methods=['POST'])
    @swag_from("docs/add_emergency_contact.yml")
    def add_emergency_contact():
        data = request.get_json(silent=True) or {}
        if not data.get('contact_name') or not data.get('contact_number'):
            return jsonify({'error': 'Contact name and number are required', 'status': 'fail'}), 400

        contact = EmergencyContacts(
            user_id=current_user_id(),
            contact_name=str(data['contact_name']).strip()[:120],
            contact_number=str(data['contact_number']).strip()[:30],
            relation=str(data.get('relation') or '').strip()[:80] or None,
        )
        db.session.add(contact)
        db.session.commit()
        return jsonify({'message': 'Emergency contact added', 'status': 'success'}), 201

    @app.route('/api/emergency-contacts', methods=['PUT'])
    @swag_from("docs/get_emergency_contacts.yml")
    def get_emergency_contacts():
        contacts = EmergencyContacts.query.filter_by(user_id=current_user_id()).all()
        return jsonify({'contacts': [{
            'contact_id': c.emergency_contact_id,
            'name': c.contact_name,
            'number': c.contact_number,
            'relation': c.relation,
        } for c in contacts]}), 200
