import requests
from functools import wraps
from flask import Flask, request, redirect, send_from_directory,render_template, url_for, session,abort,flash,jsonify
from models import *
from modules.chatbot import Chatbot
from datetime import datetime,date
import uuid
from flasgger import Swagger
from flasgger.utils import swag_from
from sqlalchemy import func
import re
from security import login_required, CONTENT_MANAGERS, login_rate_limited, record_login_failure, clear_login_failures


def routes_user(app, db):
    @app.route('/api/create_user', methods=['POST'])
    @swag_from("docs/create_user.yml")
    def create_user():
        try:
            data = request.get_json(silent=True) or {}
            required_fields = ['user_name', 'password', 'email', 'mobile_number', 'gender', 'dob']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'error': f'{field} is required', 'status': 'fail'}), 400

            email = str(data['email']).strip().lower()
            user_name = str(data['user_name']).strip()
            mobile_number = str(data['mobile_number']).strip()
            password = str(data['password'])
            if len(password) < 10 or len(password) > 128:
                return jsonify({'error': 'Password must be between 10 and 128 characters', 'status': 'fail'}), 400
            if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
                return jsonify({'error': 'Invalid email address', 'status': 'fail'}), 400
            if not re.fullmatch(r'\+?[0-9]{10,15}', mobile_number):
                return jsonify({'error': 'Invalid mobile number', 'status': 'fail'}), 400
            if data.get('pincode') and not re.fullmatch(r'[0-9]{6}', str(data['pincode'])):
                return jsonify({'error': 'Pincode must contain 6 digits', 'status': 'fail'}), 400
            existing_user = User.query.filter(
                (User.user_name == user_name) |
                (User.email == email) |
                (User.mobile_number == mobile_number)
            ).first()

            if existing_user:
                return jsonify({'error': 'User with this user_name, email or mobile already exists', 'status': 'fail'}), 409

            new_user = User(
                user_name=user_name,
                email=email,
                mobile_number=mobile_number,
                gender=data.get('gender'),
                dob=datetime.strptime(data['dob'], "%Y-%m-%d").date() if data.get('dob') else None,
                address=data.get('address'),
                pincode=data.get('pincode')
            )
            new_user.set_password(password)

            requested_role = (data.get('role') or 'user').strip().lower()
            current_user = User.query.filter_by(user_id=session.get('user_id')).first() if session.get('user_id') else None
            if requested_role != 'user':
                if not current_user or not current_user.role or current_user.role.name not in {'ngo'}:
                    return jsonify({'error': 'Only authorized organization users can assign elevated roles', 'status': 'fail'}), 403
                if requested_role not in CONTENT_MANAGERS | {'user'}:
                    return jsonify({'error': 'Invalid role', 'status': 'fail'}), 400
            role_to_assign = Roles.query.filter_by(name=requested_role).first()
            if not role_to_assign:
                return jsonify({'error': 'Application roles are not initialized', 'status': 'fail'}), 500
            new_user.role = role_to_assign

            db.session.add(new_user)
            db.session.commit()

            return jsonify({
                'message': 'User created successfully',
                'status': 'success',
                'user': {
                    'user_id': new_user.user_id,
                    'user_name': new_user.user_name,
                    'email': new_user.email,
                    'mobile_number': new_user.mobile_number,
                    'gender': new_user.gender,
                    'dob': new_user.dob.isoformat() if new_user.dob else None,
                    'address': new_user.address,
                    'pincode': new_user.pincode,
                    "role": new_user.role.name if new_user.role else None
                }
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error creating user: {str(e)}', 'status': 'fail'}), 500


    @app.route('/api/users', methods=['GET'])
    @swag_from("docs/get_all_users.yml")
    @login_required
    def get_all_users():
        try:
            if _current_user_role_name() != 'ngo':
                return jsonify({'error': 'Insufficient permissions', 'status': 'fail'}), 403

            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)

            users = User.query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )

            users_list = []
            for user in users.items:
                users_list.append({
                    'user_id': user.user_id,
                    'user_name': user.user_name,
                    'email': user.email,
                    'mobile_number': user.mobile_number,
                    'gender': user.gender,
                    'dob': user.dob.isoformat() if user.dob else None,
                    'address': user.address
                })

            return jsonify({
                'users': users_list,
                'pagination': {
                    'page': users.page,
                    'pages': users.pages,
                    'per_page': users.per_page,
                    'total': users.total
                },
                'status': 'success'
            }), 200

        except Exception as e:
            return jsonify({'error': f'Error fetching users: {str(e)}', 'status': 'fail'}), 500

    @app.route('/api/users/<int:user_id>', methods=['GET'])
    @swag_from("docs/get_user_by_id.yml")
    @login_required
    def get_user_by_id(user_id):
        try:
            if not _can_access_user(user_id):
                return jsonify({'error': 'Insufficient permissions', 'status': 'fail'}), 403

            user = User.query.filter_by(user_id=user_id).first()

            if not user:
                return jsonify({'error': 'User not found', 'status': 'fail'}), 404

            return jsonify({
                'user': {
                    'user_id': user.user_id,
                    'user_name': user.user_name,
                    'email': user.email,
                    'mobile_number': user.mobile_number,
                    'gender': user.gender,
                    'dob': user.dob.isoformat() if user.dob else None,
                    'address': user.address
                },
                'status': 'success'
            }), 200

        except Exception as e:
            return jsonify({'error': f'Error fetching user: {str(e)}', 'status': 'fail'}), 500

    @app.route('/api/users/search', methods=['GET'])
    @swag_from("docs/search_users.yml")
    @login_required
    def search_users():
        try:
            if _current_user_role_name() != 'ngo':
                return jsonify({'error': 'Insufficient permissions', 'status': 'fail'}), 403

            query = request.args.get('q', '').strip()
            if not query:
                return jsonify({'error': 'Search query is required', 'status': 'fail'}), 400

            users = User.query.filter(
                (User.user_name.contains(query)) |
                (User.email.contains(query))
            ).all()

            users_list = []
            for user in users:
                users_list.append({
                    'user_id': user.user_id,
                    'user_name': user.user_name,
                    'email': user.email,
                    'mobile_number': user.mobile_number,
                    'gender': user.gender,
                    'dob': user.dob.isoformat() if user.dob else None,
                    'address': user.address
                })

            return jsonify({
                'users': users_list,
                'count': len(users_list),
                'status': 'success'
            }), 200

        except Exception as e:
            return jsonify({'error': f'Error searching users: {str(e)}', 'status': 'fail'}), 500

    @app.route('/api/users/<int:user_id>', methods=['PUT'])
    @swag_from("docs/update_user.yml")
    @login_required
    def update_user(user_id):
        try:
            if not _can_access_user(user_id):
                return jsonify({'error': 'Insufficient permissions', 'status': 'fail'}), 403

            user = User.query.filter_by(user_id=user_id).first()

            if not user:
                return jsonify({'error': 'User not found', 'status': 'fail'}), 404

            data = request.get_json()

            if 'email' in data and data['email'] != user.email:
                if User.query.filter_by(email=data['email']).first():
                    return jsonify({'error': 'Email already exists', 'status': 'fail'}), 409

            if 'mobile_number' in data and data['mobile_number'] != user.mobile_number:
                if User.query.filter_by(mobile_number=data['mobile_number']).first():
                    return jsonify({'error': 'Mobile number already exists', 'status': 'fail'}), 409

            if 'user_name' in data and data['user_name'] != user.user_name:
                if User.query.filter_by(user_name=data['user_name']).first():
                    return jsonify({'error': 'Username already exists', 'status': 'fail'}), 409

            user.user_name = data.get('user_name', user.user_name)
            if 'password' in data:
                user.set_password(data['password'])
            user.email = data.get('email', user.email)
            user.mobile_number = data.get('mobile_number', user.mobile_number)
            user.gender = data.get('gender', user.gender)
            user.address = data.get('address', user.address)
            if 'dob' in data:
                user.dob = datetime.strptime(data['dob'], "%Y-%m-%d").date() if data.get('dob') else None

            db.session.commit()

            return jsonify({
                'message': 'User updated successfully',
                'status': 'success',
                'user': {
                    'user_id': user.user_id,
                    'user_name': user.user_name,
                    'email': user.email,
                    'mobile_number': user.mobile_number,
                    'gender': user.gender,
                    'dob': user.dob.isoformat() if user.dob else None,
                    'address': user.address
                }
            }), 200

        except ValueError as e:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD', 'status': 'fail'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error updating user: {str(e)}', 'status': 'fail'}), 500

    @app.route('/api/users/<int:user_id>', methods=['PATCH'])
    @swag_from("docs/partial_user_update.yml")
    @login_required
    def partial_update_user(user_id):
        try:
            if not _can_access_user(user_id):
                return jsonify({'error': 'Insufficient permissions', 'status': 'fail'}), 403

            user = User.query.filter_by(user_id=user_id).first()

            if not user:
                return jsonify({'error': 'User not found', 'status': 'fail'}), 404

            data = request.get_json()

            for key, value in data.items():
                if key == 'user_id':
                    continue
                elif key in ('role_id', 'role'):
                    if _current_user_role_name() != 'ngo':
                        return jsonify({'error': 'Insufficient permissions to change role', 'status': 'fail'}), 403
                    role_name = value if key == 'role' else None
                    role = Roles.query.filter_by(name=role_name).first() if role_name else Roles.query.get(value)
                    if not role:
                        return jsonify({'error': 'Invalid role', 'status': 'fail'}), 400
                    user.role = role
                elif key == 'dob':
                    user.dob = datetime.strptime(value, "%Y-%m-%d").date() if value else None
                elif key == 'password':
                    user.set_password(value)
                elif hasattr(user, key):
                    if key in ['email', 'mobile_number', 'user_name'] and value != getattr(user, key):
                        if User.query.filter(getattr(User, key) == value).first():
                            return jsonify({'error': f'{key} already exists', 'status': 'fail'}), 409
                    setattr(user, key, value)

            db.session.commit()

            return jsonify({
                'message': 'User updated successfully',
                'status': 'success',
                'user': {
                    'user_id': user.user_id,
                    'user_name': user.user_name,
                    'email': user.email,
                    'mobile_number': user.mobile_number,
                    'gender': user.gender,
                    'dob': user.dob.isoformat() if user.dob else None,
                    'address': user.address
                }
            }), 200

        except ValueError as e:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD', 'status': 'fail'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error updating user: {str(e)}', 'status': 'fail'}), 500

    @app.route('/api/users/<int:user_id>', methods=['DELETE'])
    @swag_from("docs/delete_user.yml")
    @login_required
    def delete_user(user_id):
        try:
            if not _can_access_user(user_id):
                return jsonify({'error': 'Insufficient permissions', 'status': 'fail'}), 403

            user = User.query.filter_by(user_id=user_id).first()

            if not user:
                return jsonify({'error': 'User not found', 'status': 'fail'}), 404

            db.session.delete(user)
            db.session.commit()

            return jsonify({
                'message': 'User deleted successfully',
                'status': 'success'
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error deleting user: {str(e)}', 'status': 'fail'}), 500

    @app.route('/api/users/login', methods=['POST'])
    @swag_from("docs/user_login.yml")
    def user_login():
        try:
            data = request.get_json()

            if not data.get('email') or not data.get('password'):
                return jsonify({'error': 'Email and password are required', 'status': 'fail'}), 400

            email = data['email'].strip().lower()
            if login_rate_limited(email):
                return jsonify({'error': 'Too many login attempts. Try again later.', 'status': 'fail'}), 429

            user = User.query.filter_by(email=email).first()
            if not user or not user.check_password(data['password']):
                record_login_failure(email)
                return jsonify({'error': 'Invalid credentials', 'status': 'fail'}), 401

            clear_login_failures(email)
            session.clear()
            session['user_id'] = user.user_id
            session['user_name'] = user.user_name
            now = __import__('time').time()
            session['session_created_at'] = now
            session['session_last_seen'] = now

            role = Roles.query.filter_by(role_id=user.role_id).first()

            return jsonify({
                'message': 'Login successful',
                'status': 'success',
                'user': {
                    'user_id': user.user_id,
                    'user_name': user.user_name,
                    'email': user.email,
                    'mobile_number': user.mobile_number,
                    'gender': user.gender,
                    'dob': user.dob.isoformat() if user.dob else None,
                    'address': user.address,
                    'role': user.role.name if user.role else None
                }
            }), 200

        except Exception as e:
            return jsonify({'error': f'Login error: {str(e)}', 'status': 'fail'}), 500

    @app.route('/api/users/logout', methods=['POST'])
    @swag_from("docs/user_logout.yml")
    def user_logout():
        try:
            session.clear()
            return jsonify({
                'message': 'Logout successful',
                'status': 'success'
            }), 200

        except Exception as e:
            return jsonify({'error': f'Logout error: {str(e)}', 'status': 'fail'}), 500

    @app.route('/api/users/me', methods=['GET'])
    @swag_from("docs/get_current_user.yml")
    def get_current_user():
        try:
            if 'user_id' not in session:
                return jsonify({'error': 'Not authenticated', 'status': 'fail'}), 401

            user = User.query.filter_by(user_id=session['user_id']).first()

            if not user:
                session.clear()
                return jsonify({'error': 'User not found', 'status': 'fail'}), 404

            return jsonify({
                'user': {
                    'user_id': user.user_id,
                    'user_name': user.user_name,
                    'email': user.email,
                    'mobile_number': user.mobile_number,
                    'gender': user.gender,
                    'dob': user.dob.isoformat() if user.dob else None,
                    'address': user.address
                },
                'status': 'success'
            }), 200

        except Exception as e:
            return jsonify({'error': f'Error fetching current user: {str(e)}', 'status': 'fail'}), 500
