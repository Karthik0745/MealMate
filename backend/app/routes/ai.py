from flask import Blueprint, request
from datetime import datetime, timedelta
from app.models.meal import Meal, meals_schema
from app.models.user import user_schema
from app.services.ai_service import AIService
from app.utils.helpers import success_response, error_response, validate_json
from app.utils.auth import require_auth

ai_bp = Blueprint('ai', __name__)
ai_service = AIService()


@ai_bp.route('/suggestions', methods=['GET'])
@require_auth
def get_dietary_suggestions(current_user):
    """Get AI-powered dietary suggestions based on user's meal history"""
    try:
        # Get recent meals (last 14 days by default)
        days = request.args.get('days', 14, type=int)
        days = min(days, 30)  # Limit to 30 days
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        recent_meals = Meal.query.filter(
            Meal.user_id == current_user.id,
            Meal.logged_at >= start_date
        ).order_by(Meal.logged_at.desc()).all()
        
        # Prepare user data and meals for AI analysis
        user_data = user_schema.dump(current_user)
        meals_data = meals_schema.dump(recent_meals)
        
        # Get AI suggestions
        suggestions = ai_service.analyze_meal_history(user_data, meals_data)
        
        return success_response({
            'suggestions': suggestions,
            'analysis_period': f'Last {days} days',
            'meals_analyzed': len(recent_meals),
            'ai_configured': ai_service.is_configured()
        }, 'Dietary suggestions generated successfully')
        
    except Exception as e:
        return error_response(f'Failed to generate suggestions: {str(e)}', status_code=500)


@ai_bp.route('/food-suggestion', methods=['POST'])
@require_auth
@validate_json(['query'])
def get_food_suggestion(current_user, data):
    """Get AI-powered food suggestions based on user query"""
    try:
        query = data['query'].strip()
        
        if not query:
            return error_response('Query cannot be empty')
        
        if len(query) > 200:
            return error_response('Query too long. Please keep it under 200 characters.')
        
        # Get AI food suggestions
        suggestions = ai_service.get_food_suggestion(query)
        
        return success_response({
            'query': query,
            'suggestions': suggestions,
            'ai_configured': ai_service.is_configured()
        }, 'Food suggestions generated successfully')
        
    except Exception as e:
        return error_response(f'Failed to get food suggestions: {str(e)}', status_code=500)


@ai_bp.route('/meal-analysis', methods=['POST'])
@require_auth
@validate_json(['meal_id'])
def analyze_specific_meal(current_user, data):
    """Analyze a specific meal and provide feedback"""
    try:
        meal_id = data['meal_id']
        
        # Get the specific meal
        meal = Meal.query.filter_by(id=meal_id, user_id=current_user.id).first()
        
        if not meal:
            return error_response('Meal not found', status_code=404)
        
        # Prepare meal data for analysis
        meal_data = {
            'name': meal.name,
            'calories': meal.calories,
            'protein': meal.protein,
            'carbs': meal.carbs,
            'fat': meal.fat,
            'fiber': meal.fiber,
            'sugar': meal.sugar,
            'sodium': meal.sodium,
            'category': meal.category.name if meal.category else 'Unknown'
        }
        
        # Get user data for context
        user_data = user_schema.dump(current_user)
        
        # Analyze the meal
        analysis = ai_service.analyze_meal_history(user_data, [meal_data])
        
        return success_response({
            'meal': meal_data,
            'analysis': analysis,
            'ai_configured': ai_service.is_configured()
        }, 'Meal analysis completed successfully')
        
    except Exception as e:
        return error_response(f'Failed to analyze meal: {str(e)}', status_code=500)


@ai_bp.route('/nutrition-tips', methods=['GET'])
@require_auth
def get_nutrition_tips(current_user):
    """Get general nutrition tips based on user profile"""
    try:
        # Get user profile data
        user_data = user_schema.dump(current_user)
        
        # Create a query based on user's profile
        activity_level = user_data.get('activity_level', 'moderate')
        age = user_data.get('age')
        weight = user_data.get('weight')
        height = user_data.get('height')
        
        query_parts = []
        if age:
            query_parts.append(f"age {age}")
        if activity_level:
            query_parts.append(f"{activity_level} activity level")
        if weight and height:
            bmi = weight / ((height/100) ** 2) if height > 0 else None
            if bmi:
                if bmi < 18.5:
                    query_parts.append("underweight")
                elif bmi > 25:
                    query_parts.append("overweight")
                else:
                    query_parts.append("normal weight")
        
        query = f"Nutrition tips for person with {', '.join(query_parts) if query_parts else 'general health goals'}"
        
        # Get AI suggestions
        tips = ai_service.get_food_suggestion(query)
        
        return success_response({
            'profile_context': query_parts,
            'tips': tips,
            'ai_configured': ai_service.is_configured()
        }, 'Nutrition tips generated successfully')
        
    except Exception as e:
        return error_response(f'Failed to get nutrition tips: {str(e)}', status_code=500)


@ai_bp.route('/meal-recommendations', methods=['GET'])
@require_auth
def get_meal_recommendations(current_user):
    """Get meal recommendations based on user's current nutrition status"""
    try:
        # Get today's meals
        today = datetime.utcnow().date()
        today_meals = Meal.query.filter(
            Meal.user_id == current_user.id,
            Meal.logged_at >= today
        ).all()
        
        # Calculate current nutrition intake
        total_calories = sum(meal.calories for meal in today_meals)
        total_protein = sum(meal.protein for meal in today_meals)
        total_carbs = sum(meal.carbs for meal in today_meals)
        total_fat = sum(meal.fat for meal in today_meals)
        
        # Calculate remaining needs
        calorie_goal = current_user.daily_calorie_goal
        remaining_calories = max(0, calorie_goal - total_calories)
        
        # Determine meal category based on time of day
        current_hour = datetime.utcnow().hour
        if current_hour < 10:
            meal_type = "breakfast"
        elif current_hour < 14:
            meal_type = "lunch"
        elif current_hour < 17:
            meal_type = "snack"
        else:
            meal_type = "dinner"
        
        # Create query for meal recommendations
        query = f"Healthy {meal_type} ideas with approximately {remaining_calories} calories"
        
        if remaining_calories > 0:
            if total_protein < (calorie_goal * 0.20 / 4):
                query += " high in protein"
            if total_fiber_consumed := sum(meal.fiber for meal in today_meals) < 25:
                query += " high in fiber"
        
        # Get AI recommendations
        recommendations = ai_service.get_food_suggestion(query)
        
        return success_response({
            'meal_type': meal_type,
            'current_nutrition': {
                'calories': total_calories,
                'protein': round(total_protein, 1),
                'carbs': round(total_carbs, 1),
                'fat': round(total_fat, 1)
            },
            'remaining_calories': remaining_calories,
            'recommendations': recommendations,
            'ai_configured': ai_service.is_configured()
        }, 'Meal recommendations generated successfully')
        
    except Exception as e:
        return error_response(f'Failed to get meal recommendations: {str(e)}', status_code=500)


@ai_bp.route('/weekly-report', methods=['GET'])
@require_auth
def get_weekly_nutrition_report(current_user):
    """Get AI-generated weekly nutrition report"""
    try:
        # Get last week's meals
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=7)
        
        weekly_meals = Meal.query.filter(
            Meal.user_id == current_user.id,
            Meal.logged_at >= start_date,
            Meal.logged_at <= end_date
        ).order_by(Meal.logged_at.desc()).all()
        
        if not weekly_meals:
            return success_response({
                'message': 'No meals logged in the past week',
                'suggestions': ['Start logging your meals to get personalized insights'],
                'period': 'Last 7 days'
            }, 'Weekly report generated (no data)')
        
        # Prepare data for AI analysis
        user_data = user_schema.dump(current_user)
        meals_data = meals_schema.dump(weekly_meals)
        
        # Get comprehensive AI analysis
        report = ai_service.analyze_meal_history(user_data, meals_data)
        
        # Calculate weekly statistics
        total_calories = sum(meal.calories for meal in weekly_meals)
        avg_daily_calories = total_calories / 7
        days_logged = len(set(meal.logged_at.date() for meal in weekly_meals))
        
        return success_response({
            'period': 'Last 7 days',
            'statistics': {
                'total_meals': len(weekly_meals),
                'days_logged': days_logged,
                'total_calories': total_calories,
                'avg_daily_calories': round(avg_daily_calories, 1),
                'goal_achievement': round((avg_daily_calories / current_user.daily_calorie_goal * 100), 1) if current_user.daily_calorie_goal > 0 else 0
            },
            'ai_report': report,
            'ai_configured': ai_service.is_configured()
        }, 'Weekly nutrition report generated successfully')
        
    except Exception as e:
        return error_response(f'Failed to generate weekly report: {str(e)}', status_code=500)


@ai_bp.route('/config', methods=['GET'])
@require_auth
def get_ai_config_status(current_user):
    """Get AI service configuration status"""
    try:
        return success_response({
            'ai_configured': ai_service.is_configured(),
            'has_api_key': bool(ai_service.api_key),
            'has_endpoint': bool(ai_service.endpoint),
            'deployment': ai_service.deployment
        }, 'AI configuration status retrieved')
        
    except Exception as e:
        return error_response(f'Failed to get AI config: {str(e)}', status_code=500)