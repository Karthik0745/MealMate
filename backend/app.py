from app import create_app, socketio, db
from app.models import User, Meal, Category, AudioNote
from flask_socketio import join_room, leave_room
from flask_jwt_extended import decode_token
import os

# Create Flask app
app = create_app()

# Initialize default categories
def init_default_categories():
    """Initialize default meal categories if they don't exist"""
    categories = [
        {'name': 'Breakfast', 'description': 'Morning meals', 'color': '#FF6B6B', 'icon': '🌅'},
        {'name': 'Lunch', 'description': 'Midday meals', 'color': '#4ECDC4', 'icon': '☀️'},
        {'name': 'Dinner', 'description': 'Evening meals', 'color': '#45B7D1', 'icon': '🌙'},
        {'name': 'Snack', 'description': 'Light snacks and treats', 'color': '#96CEB4', 'icon': '🍿'},
        {'name': 'Drink', 'description': 'Beverages and smoothies', 'color': '#FECA57', 'icon': '🥤'},
        {'name': 'Dessert', 'description': 'Sweet treats and desserts', 'color': '#FF9FF3', 'icon': '🍰'}
    ]
    
    with app.app_context():
        for cat_data in categories:
            existing = Category.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(**cat_data)
                db.session.add(category)
        
        try:
            db.session.commit()
            print("✅ Default categories initialized")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error initializing categories: {e}")

# SocketIO event handlers
@socketio.on('connect')
def handle_connect(auth):
    """Handle client connection"""
    try:
        # Verify JWT token from auth data
        if auth and 'token' in auth:
            token = auth['token']
            decoded_token = decode_token(token)
            user_id = decoded_token['sub']
            
            # Join user-specific room
            join_room(f'user_{user_id}')
            print(f"User {user_id} connected and joined room")
        else:
            print("Client connected without authentication")
    except Exception as e:
        print(f"Connection error: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print("Client disconnected")

@socketio.on('join_user_room')
def handle_join_user_room(data):
    """Handle joining user-specific room"""
    try:
        if 'token' in data:
            token = data['token']
            decoded_token = decode_token(token)
            user_id = decoded_token['sub']
            
            join_room(f'user_{user_id}')
            socketio.emit('joined_room', {'room': f'user_{user_id}'})
            print(f"User {user_id} joined their room")
    except Exception as e:
        print(f"Error joining room: {e}")

if __name__ == '__main__':
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Initialize default categories
        init_default_categories()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@mealmate.com',
                first_name='Admin',
                last_name='User',
                is_admin=True,
                daily_calorie_goal=2000
            )
            admin_user.set_password('admin123')  # Change this in production!
            db.session.add(admin_user)
            
            try:
                db.session.commit()
                print("✅ Admin user created (username: admin, password: admin123)")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Error creating admin user: {e}")
    
    # Run the application
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=debug_mode,
        allow_unsafe_werkzeug=True
    )