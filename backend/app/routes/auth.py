from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app import db
from app.models.user import User, user_schema
from app.utils.helpers import success_response, error_response, validate_json
from app.utils.auth import require_auth
import re

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
@validate_json(['username', 'email', 'password', 'first_name', 'last_name'])
def register(data):
    """Register a new user"""
    try:
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return error_response('Invalid email format')
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return error_response('Username or email already exists')
        
        # Validate password strength
        if len(data['password']) < 6:
            return error_response('Password must be at least 6 characters long')
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            age=data.get('age'),
            weight=data.get('weight'),
            height=data.get('height'),
            activity_level=data.get('activity_level', 'moderate'),
            daily_calorie_goal=data.get('daily_calorie_goal', 2000)
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return success_response({
            'user': user_schema.dump(user),
            'access_token': access_token
        }, 'User registered successfully', 201)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Registration failed: {str(e)}', status_code=500)


@auth_bp.route('/login', methods=['POST'])
@validate_json(['username', 'password'])
def login(data):
    """Login user"""
    try:
        # Find user by username or email
        user = User.query.filter(
            (User.username == data['username']) | (User.email == data['username'])
        ).first()
        
        if not user or not user.check_password(data['password']):
            return error_response('Invalid credentials', status_code=401)
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return success_response({
            'user': user_schema.dump(user),
            'access_token': access_token
        }, 'Login successful')
        
    except Exception as e:
        return error_response(f'Login failed: {str(e)}', status_code=500)


@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile(current_user):
    """Get current user profile"""
    try:
        return success_response(user_schema.dump(current_user), 'Profile retrieved successfully')
    except Exception as e:
        return error_response(f'Failed to get profile: {str(e)}', status_code=500)


@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile(current_user):
    """Update user profile"""
    try:
        data = request.get_json()
        if not data:
            return error_response('No data provided')
        
        # Update allowed fields
        allowed_fields = [
            'first_name', 'last_name', 'age', 'weight', 'height', 
            'activity_level', 'daily_calorie_goal'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(current_user, field, data[field])
        
        # Handle email update with validation
        if 'email' in data:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                return error_response('Invalid email format')
            
            # Check if email already exists for another user
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != current_user.id
            ).first()
            
            if existing_user:
                return error_response('Email already exists')
            
            current_user.email = data['email']
        
        db.session.commit()
        
        return success_response(user_schema.dump(current_user), 'Profile updated successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update profile: {str(e)}', status_code=500)


@auth_bp.route('/change-password', methods=['POST'])
@require_auth
@validate_json(['current_password', 'new_password'])
def change_password(current_user, data):
    """Change user password"""
    try:
        # Verify current password
        if not current_user.check_password(data['current_password']):
            return error_response('Current password is incorrect', status_code=401)
        
        # Validate new password
        if len(data['new_password']) < 6:
            return error_response('New password must be at least 6 characters long')
        
        # Update password
        current_user.set_password(data['new_password'])
        db.session.commit()
        
        return success_response(message='Password changed successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to change password: {str(e)}', status_code=500)


@auth_bp.route('/delete-account', methods=['DELETE'])
@require_auth
def delete_account(current_user):
    """Delete user account"""
    try:
        db.session.delete(current_user)
        db.session.commit()
        
        return success_response(message='Account deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete account: {str(e)}', status_code=500)