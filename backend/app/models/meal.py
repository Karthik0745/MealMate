from app import db, ma
from datetime import datetime
from marshmallow import fields


class Meal(db.Model):
    __tablename__ = 'meals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Meal information
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Float, default=1.0)  # serving size
    unit = db.Column(db.String(20), default='serving')  # serving, grams, cups, etc.
    
    # Nutritional information
    calories = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Float, default=0)  # grams
    carbs = db.Column(db.Float, default=0)    # grams
    fat = db.Column(db.Float, default=0)      # grams
    fiber = db.Column(db.Float, default=0)    # grams
    sugar = db.Column(db.Float, default=0)    # grams
    sodium = db.Column(db.Float, default=0)   # mg
    
    # Timestamps
    logged_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audio_notes = db.relationship('AudioNote', backref='meal', lazy=True, cascade='all, delete-orphan')
    
    def calculate_macros_percentage(self):
        """Calculate macronutrient percentages"""
        total_calories = self.calories
        if total_calories == 0:
            return {'protein': 0, 'carbs': 0, 'fat': 0}
        
        # Calories per gram: Protein=4, Carbs=4, Fat=9
        protein_calories = self.protein * 4
        carbs_calories = self.carbs * 4
        fat_calories = self.fat * 9
        
        return {
            'protein': round((protein_calories / total_calories) * 100, 1),
            'carbs': round((carbs_calories / total_calories) * 100, 1),
            'fat': round((fat_calories / total_calories) * 100, 1)
        }
    
    def to_dict(self):
        """Convert meal to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'name': self.name,
            'description': self.description,
            'quantity': self.quantity,
            'unit': self.unit,
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'fiber': self.fiber,
            'sugar': self.sugar,
            'sodium': self.sodium,
            'logged_at': self.logged_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'macros_percentage': self.calculate_macros_percentage(),
            'audio_notes_count': len(self.audio_notes)
        }


class MealSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Meal
        load_instance = True
        include_fk = True
    
    category_name = fields.Method('get_category_name')
    macros_percentage = fields.Method('get_macros_percentage')
    audio_notes_count = fields.Method('get_audio_notes_count')
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
    
    def get_macros_percentage(self, obj):
        return obj.calculate_macros_percentage()
    
    def get_audio_notes_count(self, obj):
        return len(obj.audio_notes)


meal_schema = MealSchema()
meals_schema = MealSchema(many=True)