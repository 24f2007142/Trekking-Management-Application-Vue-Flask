"""Authentication, Admin and Staff entry point (Milestones 2–4)."""
import os
import secrets
from datetime import timedelta
from functools import wraps

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, set_access_cookies, unset_jwt_cookies,
    jwt_required, get_jwt_identity,
)
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from models import User, Staff

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
    SQLALCHEMY_DATABASE_URI='sqlite:///users.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    JWT_TOKEN_LOCATION=['cookies'],
    JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=2),
    JWT_COOKIE_CSRF_PROTECT=True,
)
db.init_app(app)
JWTManager(app)
CORS(app, resources={r'/api/*': {'origins': [
    'http://127.0.0.1:5173', 'http://localhost:5173',
]}}, supports_credentials=True)


def role_required(role):
    def decorator(view):
        @wraps(view)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = db.session.get(User, int(get_jwt_identity()))
            if not user or user.role != role or user.approval_status != 'approved':
                return jsonify(message='Access denied'), 403
            return view(*args, **kwargs)
        return wrapper
    return decorator


@app.route("/api/who", methods=["GET"])
@jwt_required()
def get_current_user():

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user or user.approval_status != 'approved':
        return jsonify({
            'message': 'Unauthorized'
        }), 401

    return jsonify({
        'user': {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "role": user.role,
                    "approval_status": user.approval_status
                }
    }), 200


@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not isinstance (data, dict):

        return jsonify({
            'message': 'Invalid request data'
        }), 400

    email = data.get('email')
    password = data.get('password')

    if (not isinstance(email, str) or not email.strip()
        or not isinstance(password, str) or not password.strip()):
        return jsonify({
            "message": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email.strip().lower()).first()

    if not user:

        return jsonify({

            'message': 'Invalid email address'
        }), 401

    if not check_password_hash(user.password, password):

        return jsonify({
            'message': 'Password incorrect'
        }), 401

    if user.approval_status == 'pending':

        return jsonify({
                'message': 'Your account is awaiting admin approval.',
            }), 403

    elif user.approval_status == 'blacklist':

        return jsonify({
            'message': 'User Blacklisted'
        }), 403

    elif user.approval_status == 'approved':

        access_token = create_access_token(identity=str(user.id))

        response = jsonify({
            'message': 'Login  Successful',
            'user': {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "approval_status": user.approval_status
            }
        })

        set_access_cookies(response, access_token)

        return response, 200

    else:

        return jsonify({
                'message': 'Invalid Approval Status'
            }), 403

@app.route('/api/logout', methods=['POST'])
def logout():
    response = jsonify({'message': 'Logged out successfully'})
    unset_jwt_cookies(response)
    return response, 200


@app.route("/api/register",  methods=["POST"])
def register():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):

        return jsonify(
            {'message': 'Invalid request data.'}
            ), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if any(not isinstance(value, str) or not value.strip()
           for value in (username, email, password)):
        return jsonify({'message': 'Name, email and password are required.'}), 400
    username = username.strip()
    email = email.strip().lower()
    if len(username) > 100 or len(email) > 100 or email.count('@') != 1:
        return jsonify({'message': 'Enter a valid name and email.'}), 400
    if User.query.filter_by(email=email.strip().lower()).first():
        return jsonify({'message': 'Email already exists.'}), 400
    password = generate_password_hash(password)

    user = User(
        username=username,
        email=email,
        password=password,
        role='user'
    )


    try:

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User registered successfully'
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
                'message': 'User registration failed'
        }), 400


# Full Admin management replaces the Milestone 2 Admin placeholders.
from routes.admin import admin_bp
app.register_blueprint(admin_bp, url_prefix='/api/admin')


from routes.staff import staff_bp
app.register_blueprint(staff_bp, url_prefix='/api/staff')


@app.get('/api/user/dashboard')
@role_required('user')
def user_dashboard():
    return jsonify(message='Welcome to the Trekker dashboard')


if __name__ == '__main__':
    # Run init_db.py first to create the schema and Admin.
    app.run(debug=True, port=5000)
