from app import db, ma
from datetime import datetime


class AudioNote(db.Model):
    __tablename__ = 'audio_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meal_id = db.Column(db.Integer, db.ForeignKey('meals.id'), nullable=True)  # Optional meal association
    
    # Audio information
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    filename = db.Column(db.String(255), nullable=False)  # Path to audio file
    duration = db.Column(db.Float)  # Duration in seconds
    file_size = db.Column(db.Integer)  # File size in bytes
    mime_type = db.Column(db.String(50), default='audio/mpeg')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert audio note to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meal_id': self.meal_id,
            'meal_name': self.meal.name if self.meal else None,
            'title': self.title,
            'description': self.description,
            'filename': self.filename,
            'duration': self.duration,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class AudioNoteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AudioNote
        load_instance = True
        include_fk = True
    
    meal_name = ma.Method('get_meal_name')
    
    def get_meal_name(self, obj):
        return obj.meal.name if obj.meal else None


audio_note_schema = AudioNoteSchema()
audio_notes_schema = AudioNoteSchema(many=True)