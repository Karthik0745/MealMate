from flask import Blueprint, request, send_file, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, timedelta
from app import db
from app.models.audio_note import AudioNote, audio_note_schema, audio_notes_schema
from app.models.meal import Meal
from app.utils.helpers import success_response, error_response, validate_json, paginate_query
from app.utils.auth import require_auth

audio_bp = Blueprint('audio', __name__)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'audio')
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'm4a', 'webm'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@audio_bp.route('/upload', methods=['POST'])
@require_auth
def upload_audio_note(current_user):
    """Upload an audio note"""
    try:
        # Check if file is in request
        if 'audio' not in request.files:
            return error_response('No audio file provided')
        
        file = request.files['audio']
        if file.filename == '':
            return error_response('No file selected')
        
        # Validate file
        if not file or not allowed_file(file.filename):
            return error_response('Invalid file type. Allowed: mp3, wav, ogg, m4a, webm')
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return error_response('File too large. Maximum size is 10MB')
        
        # Get form data
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        meal_id = request.form.get('meal_id')
        
        if not title:
            return error_response('Title is required')
        
        # Validate meal_id if provided
        meal = None
        if meal_id:
            try:
                meal_id = int(meal_id)
                meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first()
                if not meal:
                    return error_response('Meal not found or access denied')
            except (ValueError, TypeError):
                return error_response('Invalid meal_id')
        
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        
        # Save file
        file.save(filepath)
        
        # Create audio note record
        audio_note = AudioNote(
            user_id=current_user.id,
            meal_id=meal_id,
            title=title,
            description=description,
            filename=unique_filename,
            file_size=file_size,
            mime_type=f"audio/{file_extension}"
        )
        
        db.session.add(audio_note)
        db.session.commit()
        
        return success_response(
            audio_note_schema.dump(audio_note),
            'Audio note uploaded successfully',
            201
        )
        
    except Exception as e:
        db.session.rollback()
        # Clean up file if it was saved
        try:
            if 'unique_filename' in locals():
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
        except:
            pass
        
        return error_response(f'Failed to upload audio note: {str(e)}', status_code=500)


@audio_bp.route('/', methods=['GET'])
@require_auth
def get_audio_notes(current_user):
    """Get user's audio notes with filtering and pagination"""
    try:
        # Build base query
        query = AudioNote.query.filter_by(user_id=current_user.id)
        
        # Filter by meal_id
        meal_id = request.args.get('meal_id', type=int)
        if meal_id:
            query = query.filter_by(meal_id=meal_id)
        
        # Search by title
        search = request.args.get('search')
        if search:
            query = query.filter(AudioNote.title.ilike(f'%{search}%'))
        
        # Order by creation date descending
        query = query.order_by(AudioNote.created_at.desc())
        
        # Paginate results
        pagination_data = paginate_query(query)
        
        return success_response({
            'audio_notes': audio_notes_schema.dump(pagination_data['items']),
            'pagination': {
                'total': pagination_data['total'],
                'pages': pagination_data['pages'],
                'current_page': pagination_data['current_page'],
                'per_page': pagination_data['per_page'],
                'has_next': pagination_data['has_next'],
                'has_prev': pagination_data['has_prev']
            }
        }, 'Audio notes retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get audio notes: {str(e)}', status_code=500)


@audio_bp.route('/<int:note_id>', methods=['GET'])
@require_auth
def get_audio_note(current_user, note_id):
    """Get a specific audio note"""
    try:
        audio_note = AudioNote.query.filter_by(id=note_id, user_id=current_user.id).first()
        
        if not audio_note:
            return error_response('Audio note not found', status_code=404)
        
        return success_response(
            audio_note_schema.dump(audio_note),
            'Audio note retrieved successfully'
        )
        
    except Exception as e:
        return error_response(f'Failed to get audio note: {str(e)}', status_code=500)


@audio_bp.route('/<int:note_id>/download', methods=['GET'])
@require_auth
def download_audio_note(current_user, note_id):
    """Download/stream an audio note file"""
    try:
        audio_note = AudioNote.query.filter_by(id=note_id, user_id=current_user.id).first()
        
        if not audio_note:
            return error_response('Audio note not found', status_code=404)
        
        filepath = os.path.join(UPLOAD_FOLDER, audio_note.filename)
        
        if not os.path.exists(filepath):
            return error_response('Audio file not found on server', status_code=404)
        
        return send_file(
            filepath,
            mimetype=audio_note.mime_type,
            as_attachment=False,  # Stream instead of download
            download_name=f"{audio_note.title}.{audio_note.filename.split('.')[-1]}"
        )
        
    except Exception as e:
        return error_response(f'Failed to download audio note: {str(e)}', status_code=500)


@audio_bp.route('/<int:note_id>', methods=['PUT'])
@require_auth
def update_audio_note(current_user, note_id):
    """Update audio note metadata"""
    try:
        audio_note = AudioNote.query.filter_by(id=note_id, user_id=current_user.id).first()
        
        if not audio_note:
            return error_response('Audio note not found', status_code=404)
        
        data = request.get_json()
        if not data:
            return error_response('No data provided')
        
        # Update allowed fields
        if 'title' in data:
            if not data['title'].strip():
                return error_response('Title cannot be empty')
            audio_note.title = data['title'].strip()
        
        if 'description' in data:
            audio_note.description = data['description'].strip()
        
        # Update meal association
        if 'meal_id' in data:
            if data['meal_id']:
                # Validate meal exists and belongs to user
                meal = Meal.query.filter_by(id=data['meal_id'], user_id=current_user.id).first()
                if not meal:
                    return error_response('Meal not found or access denied')
                audio_note.meal_id = data['meal_id']
            else:
                # Remove meal association
                audio_note.meal_id = None
        
        db.session.commit()
        
        return success_response(
            audio_note_schema.dump(audio_note),
            'Audio note updated successfully'
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update audio note: {str(e)}', status_code=500)


@audio_bp.route('/<int:note_id>', methods=['DELETE'])
@require_auth
def delete_audio_note(current_user, note_id):
    """Delete an audio note"""
    try:
        audio_note = AudioNote.query.filter_by(id=note_id, user_id=current_user.id).first()
        
        if not audio_note:
            return error_response('Audio note not found', status_code=404)
        
        # Delete file from filesystem
        filepath = os.path.join(UPLOAD_FOLDER, audio_note.filename)
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            # Log the error but don't fail the deletion
            print(f"Warning: Could not delete audio file {filepath}: {e}")
        
        # Delete database record
        db.session.delete(audio_note)
        db.session.commit()
        
        return success_response(message='Audio note deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete audio note: {str(e)}', status_code=500)


@audio_bp.route('/meal/<int:meal_id>', methods=['GET'])
@require_auth
def get_meal_audio_notes(current_user, meal_id):
    """Get all audio notes for a specific meal"""
    try:
        # Verify meal belongs to user
        meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first()
        if not meal:
            return error_response('Meal not found or access denied', status_code=404)
        
        audio_notes = AudioNote.query.filter_by(
            user_id=current_user.id,
            meal_id=meal_id
        ).order_by(AudioNote.created_at.desc()).all()
        
        return success_response(
            audio_notes_schema.dump(audio_notes),
            f'Audio notes for meal "{meal.name}" retrieved successfully'
        )
        
    except Exception as e:
        return error_response(f'Failed to get meal audio notes: {str(e)}', status_code=500)


@audio_bp.route('/stats', methods=['GET'])
@require_auth
def get_audio_stats(current_user):
    """Get user's audio notes statistics"""
    try:
        total_notes = AudioNote.query.filter_by(user_id=current_user.id).count()
        
        # Total storage used
        total_size = db.session.query(
            db.func.sum(AudioNote.file_size)
        ).filter_by(user_id=current_user.id).scalar() or 0
        
        # Notes with meal association
        notes_with_meals = AudioNote.query.filter(
            AudioNote.user_id == current_user.id,
            AudioNote.meal_id.isnot(None)
        ).count()
        
        # Recent notes (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_notes = AudioNote.query.filter(
            AudioNote.user_id == current_user.id,
            AudioNote.created_at >= week_ago
        ).count()
        
        return success_response({
            'total_notes': total_notes,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'notes_with_meals': notes_with_meals,
            'notes_without_meals': total_notes - notes_with_meals,
            'recent_notes_week': recent_notes
        }, 'Audio statistics retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get audio stats: {str(e)}', status_code=500)


@audio_bp.route('/config', methods=['GET'])
@require_auth
def get_audio_config(current_user):
    """Get audio upload configuration"""
    try:
        return success_response({
            'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024),
            'allowed_formats': list(ALLOWED_EXTENSIONS),
            'upload_enabled': True
        }, 'Audio configuration retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get audio config: {str(e)}', status_code=500)