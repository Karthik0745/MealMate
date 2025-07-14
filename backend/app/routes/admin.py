from flask import Blueprint, request
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app import db
from app.models.user import User, users_schema, user_schema
from app.models.meal import Meal
from app.models.category import Category, categories_schema, category_schema
from app.models.audio_note import AudioNote
from app.utils.helpers import success_response, error_response, validate_json, paginate_query
from app.utils.auth import require_admin

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@require_admin
def get_admin_dashboard(current_user):
    """Get admin dashboard overview"""
    try:
        # Get date ranges
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # User statistics
        total_users = User.query.count()
        new_users_week = User.query.filter(User.created_at >= week_ago).count()
        new_users_month = User.query.filter(User.created_at >= month_ago).count()
        active_users_week = User.query.join(Meal).filter(Meal.logged_at >= week_ago).distinct().count()
        
        # Meal statistics
        total_meals = Meal.query.count()
        meals_this_week = Meal.query.filter(Meal.logged_at >= week_ago).count()
        meals_this_month = Meal.query.filter(Meal.logged_at >= month_ago).count()
        
        # Audio notes statistics
        total_audio_notes = AudioNote.query.count()
        audio_notes_week = AudioNote.query.filter(AudioNote.created_at >= week_ago).count()
        
        # Category statistics
        total_categories = Category.query.count()
        
        # Top categories by meal count
        top_categories = db.session.query(
            Category.name,
            func.count(Meal.id).label('meal_count')
        ).join(Meal).group_by(Category.id, Category.name).order_by(
            desc(func.count(Meal.id))
        ).limit(5).all()
        
        # Most active users
        active_users = db.session.query(
            User.username,
            User.first_name,
            User.last_name,
            func.count(Meal.id).label('meal_count')
        ).join(Meal).filter(
            Meal.logged_at >= month_ago
        ).group_by(User.id).order_by(
            desc(func.count(Meal.id))
        ).limit(10).all()
        
        return success_response({
            'overview': {
                'total_users': total_users,
                'new_users_week': new_users_week,
                'new_users_month': new_users_month,
                'active_users_week': active_users_week,
                'total_meals': total_meals,
                'meals_this_week': meals_this_week,
                'meals_this_month': meals_this_month,
                'total_audio_notes': total_audio_notes,
                'audio_notes_week': audio_notes_week,
                'total_categories': total_categories
            },
            'top_categories': [
                {'name': cat.name, 'meal_count': cat.meal_count} 
                for cat in top_categories
            ],
            'most_active_users': [
                {
                    'username': user.username,
                    'name': f"{user.first_name} {user.last_name}",
                    'meal_count': user.meal_count
                }
                for user in active_users
            ]
        }, 'Admin dashboard data retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get admin dashboard: {str(e)}', status_code=500)


@admin_bp.route('/users', methods=['GET'])
@require_admin
def get_all_users(current_user):
    """Get all users with pagination and filtering"""
    try:
        # Build query
        query = User.query
        
        # Apply filters
        search = request.args.get('search')
        if search:
            query = query.filter(
                (User.username.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%')) |
                (User.first_name.ilike(f'%{search}%')) |
                (User.last_name.ilike(f'%{search}%'))
            )
        
        # Filter by admin status
        is_admin = request.args.get('is_admin')
        if is_admin is not None:
            query = query.filter(User.is_admin == (is_admin.lower() == 'true'))
        
        # Order by creation date
        query = query.order_by(desc(User.created_at))
        
        # Paginate results
        pagination_data = paginate_query(query)
        
        return success_response({
            'users': users_schema.dump(pagination_data['items']),
            'pagination': {
                'total': pagination_data['total'],
                'pages': pagination_data['pages'],
                'current_page': pagination_data['current_page'],
                'per_page': pagination_data['per_page'],
                'has_next': pagination_data['has_next'],
                'has_prev': pagination_data['has_prev']
            }
        }, 'Users retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get users: {str(e)}', status_code=500)


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@require_admin
def get_user_details(current_user, user_id):
    """Get detailed information about a specific user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', status_code=404)
        
        # Get user's meal statistics
        total_meals = Meal.query.filter_by(user_id=user_id).count()
        total_calories = db.session.query(func.sum(Meal.calories)).filter_by(user_id=user_id).scalar() or 0
        total_audio_notes = AudioNote.query.filter_by(user_id=user_id).count()
        
        # Get recent meals
        recent_meals = Meal.query.filter_by(user_id=user_id).order_by(desc(Meal.logged_at)).limit(10).all()
        
        # Get activity by category
        category_stats = db.session.query(
            Category.name,
            func.count(Meal.id).label('count'),
            func.sum(Meal.calories).label('total_calories')
        ).join(Meal).filter(Meal.user_id == user_id).group_by(Category.id, Category.name).all()
        
        return success_response({
            'user': user_schema.dump(user),
            'statistics': {
                'total_meals': total_meals,
                'total_calories': int(total_calories),
                'total_audio_notes': total_audio_notes,
                'avg_calories_per_meal': round(total_calories / total_meals, 1) if total_meals > 0 else 0
            },
            'recent_meals': [
                {
                    'id': meal.id,
                    'name': meal.name,
                    'calories': meal.calories,
                    'category': meal.category.name if meal.category else None,
                    'logged_at': meal.logged_at.isoformat()
                }
                for meal in recent_meals
            ],
            'category_breakdown': [
                {
                    'category': stat.name,
                    'meal_count': stat.count,
                    'total_calories': int(stat.total_calories)
                }
                for stat in category_stats
            ]
        }, 'User details retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get user details: {str(e)}', status_code=500)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['PUT'])
@require_admin
def toggle_user_admin_status(current_user, user_id):
    """Toggle admin status of a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', status_code=404)
        
        # Prevent removing admin from self
        if user_id == current_user.id and user.is_admin:
            return error_response('Cannot remove admin status from yourself', status_code=400)
        
        user.is_admin = not user.is_admin
        db.session.commit()
        
        return success_response(
            user_schema.dump(user),
            f'User admin status {"enabled" if user.is_admin else "disabled"} successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to toggle admin status: {str(e)}', status_code=500)


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(current_user, user_id):
    """Delete a user account"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', status_code=404)
        
        # Prevent deleting self
        if user_id == current_user.id:
            return error_response('Cannot delete your own account', status_code=400)
        
        # Store user info for response
        user_info = {
            'username': user.username,
            'email': user.email,
            'name': f"{user.first_name} {user.last_name}"
        }
        
        db.session.delete(user)
        db.session.commit()
        
        return success_response(
            user_info,
            'User account deleted successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete user: {str(e)}', status_code=500)


@admin_bp.route('/categories', methods=['GET'])
@require_admin
def get_all_categories(current_user):
    """Get all meal categories"""
    try:
        categories = Category.query.order_by(Category.name).all()
        
        return success_response(
            categories_schema.dump(categories),
            'Categories retrieved successfully'
        )
        
    except Exception as e:
        return error_response(f'Failed to get categories: {str(e)}', status_code=500)


@admin_bp.route('/categories', methods=['POST'])
@require_admin
@validate_json(['name'])
def create_category(current_user, data):
    """Create a new meal category"""
    try:
        # Check if category already exists
        existing_category = Category.query.filter_by(name=data['name']).first()
        if existing_category:
            return error_response('Category already exists')
        
        category = Category(
            name=data['name'],
            description=data.get('description'),
            color=data.get('color', '#6366f1'),
            icon=data.get('icon')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return success_response(
            category_schema.dump(category),
            'Category created successfully',
            201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create category: {str(e)}', status_code=500)


@admin_bp.route('/categories/<int:category_id>', methods=['PUT'])
@require_admin
def update_category(current_user, category_id):
    """Update a meal category"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return error_response('Category not found', status_code=404)
        
        data = request.get_json()
        if not data:
            return error_response('No data provided')
        
        # Update allowed fields
        if 'name' in data:
            # Check if new name already exists
            existing = Category.query.filter(
                Category.name == data['name'],
                Category.id != category_id
            ).first()
            if existing:
                return error_response('Category name already exists')
            category.name = data['name']
        
        if 'description' in data:
            category.description = data['description']
        if 'color' in data:
            category.color = data['color']
        if 'icon' in data:
            category.icon = data['icon']
        
        db.session.commit()
        
        return success_response(
            category_schema.dump(category),
            'Category updated successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update category: {str(e)}', status_code=500)


@admin_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@require_admin
def delete_category(current_user, category_id):
    """Delete a meal category"""
    try:
        category = Category.query.get(category_id)
        if not category:
            return error_response('Category not found', status_code=404)
        
        # Check if category has meals
        meal_count = Meal.query.filter_by(category_id=category_id).count()
        if meal_count > 0:
            return error_response(
                f'Cannot delete category. It has {meal_count} associated meals.',
                status_code=400
            )
        
        category_name = category.name
        db.session.delete(category)
        db.session.commit()
        
        return success_response(
            {'name': category_name},
            'Category deleted successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete category: {str(e)}', status_code=500)


@admin_bp.route('/statistics', methods=['GET'])
@require_admin
def get_system_statistics(current_user):
    """Get comprehensive system statistics"""
    try:
        # Date ranges
        now = datetime.utcnow()
        today = now.date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # User growth over time
        user_growth = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= month_ago
        ).group_by(func.date(User.created_at)).all()
        
        # Daily meal logging activity
        daily_activity = db.session.query(
            func.date(Meal.logged_at).label('date'),
            func.count(Meal.id).label('meals'),
            func.count(func.distinct(Meal.user_id)).label('active_users')
        ).filter(
            Meal.logged_at >= month_ago
        ).group_by(func.date(Meal.logged_at)).all()
        
        # Popular categories
        category_popularity = db.session.query(
            Category.name,
            func.count(Meal.id).label('meal_count')
        ).join(Meal).group_by(Category.id, Category.name).order_by(
            desc(func.count(Meal.id))
        ).all()
        
        # Average calories by day of week
        calories_by_weekday = db.session.query(
            func.extract('dow', Meal.logged_at).label('weekday'),
            func.avg(Meal.calories).label('avg_calories')
        ).filter(
            Meal.logged_at >= month_ago
        ).group_by(func.extract('dow', Meal.logged_at)).all()
        
        weekday_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        return success_response({
            'user_growth': [
                {'date': data.date.isoformat(), 'new_users': data.count}
                for data in user_growth
            ],
            'daily_activity': [
                {
                    'date': data.date.isoformat(),
                    'meals_logged': data.meals,
                    'active_users': data.active_users
                }
                for data in daily_activity
            ],
            'category_popularity': [
                {'category': data.name, 'meal_count': data.meal_count}
                for data in category_popularity
            ],
            'calories_by_weekday': [
                {
                    'weekday': weekday_names[int(data.weekday)],
                    'avg_calories': round(data.avg_calories, 1)
                }
                for data in calories_by_weekday
            ]
        }, 'System statistics retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get statistics: {str(e)}', status_code=500)