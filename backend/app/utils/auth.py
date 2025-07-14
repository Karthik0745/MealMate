from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User


def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({'message': 'User not found'}), 404
            
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Authentication failed', 'error': str(e)}), 401
    
    return decorated_function


def require_admin(f):
    """Decorator to require admin role"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        try:
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({'message': 'User not found'}), 404
            
            if not current_user.is_admin:
                return jsonify({'message': 'Admin access required'}), 403
            
            return f(current_user, *args, **kwargs)
        except Exception as e:
            return jsonify({'message': 'Authentication failed', 'error': str(e)}), 401
    
    return decorated_function


def get_current_user():
    """Get current authenticated user"""
    try:
        current_user_id = get_jwt_identity()
        return User.query.get(current_user_id)
    except:
        return None