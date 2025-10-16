from flask import Blueprint, request, jsonify, current_app
# UPDATED: Corrected the import statement for PyJWT
import jwt
import datetime
from .extensions import bcrypt
from .models import UserProfile
from . import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if UserProfile.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'User with this email already exists'}), 409

    new_user = UserProfile(
        name=data['name'],
        email=data['email'],
        password=data['password']
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

    # This line now uses the correctly imported module
    token = jwt.encode({
        'name': user.name,
        'email': user.email,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})

