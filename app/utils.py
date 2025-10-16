from functools import wraps
from flask import request, jsonify, current_app
# UPDATED: Import 'decode' directly from the jwt library
import jwt
from .models import UserProfile

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # This line now works correctly because of the updated import
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = UserProfile.query.filter_by(email=data['email']).first()
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
        except Exception as e:
            return jsonify({'message': f'Token is invalid or expired! {e}'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated
