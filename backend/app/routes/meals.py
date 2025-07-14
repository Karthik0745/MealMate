from flask import Blueprint, request
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from app import db, socketio
from app.models.meal import Meal, meal_schema, meals_schema
from app.models.category import Category
from app.utils.helpers import success_response, error_response, validate_json, paginate_query
from app.utils.auth import require_auth

meals_bp = Blueprint('meals', __name__)


@meals_bp.route('/', methods=['GET'])
@require_auth
def get_meals(current_user):
    """Get user's meals with filtering and pagination"""
    try:
        # Build base query
        query = Meal.query.filter_by(user_id=current_user.id)
        
        # Apply filters
        category_id = request.args.get('category_id', type=int)
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # Date filtering
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if start_date:
            try:
                start_date = datetime.fromisoformat(start_date)
                query = query.filter(Meal.logged_at >= start_date)
            except ValueError:
                return error_response('Invalid start_date format. Use ISO format (YYYY-MM-DD)')
        
        if end_date:
            try:
                end_date = datetime.fromisoformat(end_date)
                # Add one day to include the entire end date
                end_date = end_date + timedelta(days=1)
                query = query.filter(Meal.logged_at < end_date)
            except ValueError:
                return error_response('Invalid end_date format. Use ISO format (YYYY-MM-DD)')
        
        # Search by name
        search = request.args.get('search')
        if search:
            query = query.filter(Meal.name.ilike(f'%{search}%'))
        
        # Order by logged_at descending
        query = query.order_by(desc(Meal.logged_at))
        
        # Paginate results
        pagination_data = paginate_query(query)
        
        return success_response({
            'meals': meals_schema.dump(pagination_data['items']),
            'pagination': {
                'total': pagination_data['total'],
                'pages': pagination_data['pages'],
                'current_page': pagination_data['current_page'],
                'per_page': pagination_data['per_page'],
                'has_next': pagination_data['has_next'],
                'has_prev': pagination_data['has_prev']
            }
        }, 'Meals retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get meals: {str(e)}', status_code=500)


@meals_bp.route('/<int:meal_id>', methods=['GET'])
@require_auth
def get_meal(current_user, meal_id):
    """Get a specific meal"""
    try:
        meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first()
        
        if not meal:
            return error_response('Meal not found', status_code=404)
        
        return success_response(meal_schema.dump(meal), 'Meal retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get meal: {str(e)}', status_code=500)


@meals_bp.route('/', methods=['POST'])
@require_auth
@validate_json(['name', 'category_id', 'calories'])
def create_meal(current_user, data):
    """Create a new meal"""
    try:
        # Validate category exists
        category = Category.query.get(data['category_id'])
        if not category:
            return error_response('Category not found', status_code=404)
        
        # Create meal
        meal = Meal(
            user_id=current_user.id,
            category_id=data['category_id'],
            name=data['name'],
            description=data.get('description'),
            quantity=data.get('quantity', 1.0),
            unit=data.get('unit', 'serving'),
            calories=data['calories'],
            protein=data.get('protein', 0),
            carbs=data.get('carbs', 0),
            fat=data.get('fat', 0),
            fiber=data.get('fiber', 0),
            sugar=data.get('sugar', 0),
            sodium=data.get('sodium', 0),
            logged_at=datetime.fromisoformat(data['logged_at']) if data.get('logged_at') else datetime.utcnow()
        )
        
        db.session.add(meal)
        db.session.commit()
        
        # Emit real-time update
        socketio.emit('meal_created', {
            'meal': meal_schema.dump(meal),
            'user_id': current_user.id
        }, room=f'user_{current_user.id}')
        
        return success_response(meal_schema.dump(meal), 'Meal created successfully', 201)
        
    except ValueError as e:
        return error_response(f'Invalid date format: {str(e)}')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create meal: {str(e)}', status_code=500)


@meals_bp.route('/<int:meal_id>', methods=['PUT'])
@require_auth
def update_meal(current_user, meal_id):
    """Update a meal"""
    try:
        meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first()
        
        if not meal:
            return error_response('Meal not found', status_code=404)
        
        data = request.get_json()
        if not data:
            return error_response('No data provided')
        
        # Update allowed fields
        allowed_fields = [
            'name', 'description', 'quantity', 'unit', 'calories',
            'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(meal, field, data[field])
        
        # Handle category update
        if 'category_id' in data:
            category = Category.query.get(data['category_id'])
            if not category:
                return error_response('Category not found', status_code=404)
            meal.category_id = data['category_id']
        
        # Handle logged_at update
        if 'logged_at' in data:
            try:
                meal.logged_at = datetime.fromisoformat(data['logged_at'])
            except ValueError:
                return error_response('Invalid logged_at format. Use ISO format')
        
        db.session.commit()
        
        # Emit real-time update
        socketio.emit('meal_updated', {
            'meal': meal_schema.dump(meal),
            'user_id': current_user.id
        }, room=f'user_{current_user.id}')
        
        return success_response(meal_schema.dump(meal), 'Meal updated successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update meal: {str(e)}', status_code=500)


@meals_bp.route('/<int:meal_id>', methods=['DELETE'])
@require_auth
def delete_meal(current_user, meal_id):
    """Delete a meal"""
    try:
        meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first()
        
        if not meal:
            return error_response('Meal not found', status_code=404)
        
        db.session.delete(meal)
        db.session.commit()
        
        # Emit real-time update
        socketio.emit('meal_deleted', {
            'meal_id': meal_id,
            'user_id': current_user.id
        }, room=f'user_{current_user.id}')
        
        return success_response(message='Meal deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete meal: {str(e)}', status_code=500)


@meals_bp.route('/categories', methods=['GET'])
@require_auth
def get_categories(current_user):
    """Get all meal categories"""
    try:
        from app.models.category import categories_schema
        categories = Category.query.all()
        
        return success_response(
            categories_schema.dump(categories),
            'Categories retrieved successfully'
        )
        
    except Exception as e:
        return error_response(f'Failed to get categories: {str(e)}', status_code=500)


@meals_bp.route('/bulk', methods=['POST'])
@require_auth
@validate_json(['meals'])
def create_bulk_meals(current_user, data):
    """Create multiple meals at once"""
    try:
        meals_data = data['meals']
        created_meals = []
        
        for meal_data in meals_data:
            # Validate required fields
            if not all(key in meal_data for key in ['name', 'category_id', 'calories']):
                return error_response('Each meal must have name, category_id, and calories')
            
            # Validate category exists
            category = Category.query.get(meal_data['category_id'])
            if not category:
                return error_response(f'Category with id {meal_data["category_id"]} not found')
            
            # Create meal
            meal = Meal(
                user_id=current_user.id,
                category_id=meal_data['category_id'],
                name=meal_data['name'],
                description=meal_data.get('description'),
                quantity=meal_data.get('quantity', 1.0),
                unit=meal_data.get('unit', 'serving'),
                calories=meal_data['calories'],
                protein=meal_data.get('protein', 0),
                carbs=meal_data.get('carbs', 0),
                fat=meal_data.get('fat', 0),
                fiber=meal_data.get('fiber', 0),
                sugar=meal_data.get('sugar', 0),
                sodium=meal_data.get('sodium', 0),
                logged_at=datetime.fromisoformat(meal_data['logged_at']) if meal_data.get('logged_at') else datetime.utcnow()
            )
            
            db.session.add(meal)
            created_meals.append(meal)
        
        db.session.commit()
        
        # Emit real-time update
        socketio.emit('meals_bulk_created', {
            'meals': meals_schema.dump(created_meals),
            'user_id': current_user.id
        }, room=f'user_{current_user.id}')
        
        return success_response(
            meals_schema.dump(created_meals),
            f'{len(created_meals)} meals created successfully',
            201
        )
        
    except ValueError as e:
        db.session.rollback()
        return error_response(f'Invalid date format: {str(e)}')
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to create meals: {str(e)}', status_code=500)


@meals_bp.route('/recent', methods=['GET'])
@require_auth
def get_recent_meals(current_user):
    """Get user's recent meals (last 7 days)"""
    try:
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        meals = Meal.query.filter(
            and_(
                Meal.user_id == current_user.id,
                Meal.logged_at >= seven_days_ago
            )
        ).order_by(desc(Meal.logged_at)).limit(50).all()
        
        return success_response(
            meals_schema.dump(meals),
            'Recent meals retrieved successfully'
        )
        
    except Exception as e:
        return error_response(f'Failed to get recent meals: {str(e)}', status_code=500)