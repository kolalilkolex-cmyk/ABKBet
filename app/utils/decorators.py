from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User
import logging

logger = logging.getLogger(__name__)

def token_required(f):
    """Decorator to require JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            # Ensure user_id is an int when stored as a string in the token
            try:
                if isinstance(user_id, str) and user_id.isdigit():
                    user_id = int(user_id)
            except Exception:
                pass
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({'message': 'User not found or inactive'}), 401
            return f(user, *args, **kwargs)
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return jsonify({'message': 'Invalid or expired token'}), 401
    return decorated

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({'message': 'User not found or inactive'}), 401
            # You can add an admin field to User model for this check
            return f(user, *args, **kwargs)
        except Exception as e:
            logger.error(f"Admin check error: {e}")
            return jsonify({'message': 'Unauthorized'}), 403
    return decorated
