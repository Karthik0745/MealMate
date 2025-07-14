from flask import jsonify, request
from functools import wraps


def success_response(data=None, message='Success', status_code=200):
    """Standard success response format"""
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code


def error_response(message='Error occurred', errors=None, status_code=400):
    """Standard error response format"""
    response = {
        'success': False,
        'message': message
    }
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status_code


def validate_json(required_fields=None):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return error_response('Content-Type must be application/json', status_code=400)
            
            data = request.get_json()
            if not data:
                return error_response('No JSON data provided', status_code=400)
            
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None or data[field] == '':
                        missing_fields.append(field)
                
                if missing_fields:
                    return error_response(
                        'Missing required fields',
                        {'missing_fields': missing_fields},
                        status_code=400
                    )
            
            return f(data, *args, **kwargs)
        return decorated_function
    return decorator


def paginate_query(query, page=1, per_page=20):
    """Paginate SQLAlchemy query"""
    try:
        page = int(request.args.get('page', page))
        per_page = int(request.args.get('per_page', per_page))
        per_page = min(per_page, 100)  # Limit to 100 items per page
    except ValueError:
        page = 1
        per_page = 20
    
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return {
        'items': pagination.items,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'per_page': pagination.per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }