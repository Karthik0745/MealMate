from app import db, ma
from datetime import datetime


class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#6366f1')  # Hex color code
    icon = db.Column(db.String(50))  # Icon name/class
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    meals = db.relationship('Meal', backref='category', lazy=True)
    
    def to_dict(self):
        """Convert category to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'icon': self.icon,
            'created_at': self.created_at.isoformat(),
            'meal_count': len(self.meals)
        }


class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        load_instance = True
    
    meal_count = ma.Method('get_meal_count')
    
    def get_meal_count(self, obj):
        return len(obj.meals)


category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)