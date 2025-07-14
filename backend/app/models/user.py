from app import db, ma
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from marshmallow import fields


class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Profile information
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)  # in kg
    height = db.Column(db.Float)  # in cm
    activity_level = db.Column(db.String(20), default='moderate')  # sedentary, light, moderate, active, very_active
    daily_calorie_goal = db.Column(db.Integer, default=2000)
    
    # User role
    is_admin = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    meals = db.relationship('Meal', backref='user', lazy=True, cascade='all, delete-orphan')
    audio_notes = db.relationship('AudioNote', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def calculate_bmr(self):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if not all([self.weight, self.height, self.age]):
            return None
        
        # BMR calculation (Mifflin-St Jeor Equation)
        # For simplicity, assuming average between male/female
        bmr = (10 * self.weight) + (6.25 * self.height) - (5 * self.age) + 5
        return bmr
    
    def calculate_tdee(self):
        """Calculate Total Daily Energy Expenditure"""
        bmr = self.calculate_bmr()
        if not bmr:
            return None
        
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        multiplier = activity_multipliers.get(self.activity_level, 1.55)
        return int(bmr * multiplier)
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'weight': self.weight,
            'height': self.height,
            'activity_level': self.activity_level,
            'daily_calorie_goal': self.daily_calorie_goal,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
            'bmr': self.calculate_bmr(),
            'tdee': self.calculate_tdee()
        }


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ('password_hash',)
    
    password = fields.Str(write_only=True)
    bmr = fields.Method('get_bmr')
    tdee = fields.Method('get_tdee')
    
    def get_bmr(self, obj):
        return obj.calculate_bmr()
    
    def get_tdee(self, obj):
        return obj.calculate_tdee()


user_schema = UserSchema()
users_schema = UserSchema(many=True)