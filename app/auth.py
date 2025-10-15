# app/auth.py
from flask import Blueprint, request, jsonify, current_app
import jwt
import datetime
from .extensions import bcrypt
from .models import UserProfile
from . import db

auth_bp = Blueprint('auth', __name__)

# app/auth.py
# ... imports ...

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    user = UserProfile.query.filter_by(email=data['email']).first()
    if user:
        return jsonify({'message': 'User with this email already exists'}), 409

    # UPDATED: Include 'name' when creating a new user
    new_user = UserProfile(
        name=data['name'],
        email=data['email'],
        password=data['password'],
        dietary_preference=data['dietary_preference']
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user registered successfully!'}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    auth = request.get_json()
    user = UserProfile.query.filter_by(email=auth['email']).first()

    if not user or not bcrypt.check_password_hash(user.password_hash, auth['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    # UPDATED: Add user's name and email to the token payload
    token = jwt.encode({
        'name': user.name,
        'email': user.email,
        'dietary_preference': user.dietary_preference,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})