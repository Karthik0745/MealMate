from flask import Blueprint, request
from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from app import db
from app.models.meal import Meal
from app.models.category import Category
from app.utils.helpers import success_response, error_response
from app.utils.auth import require_auth

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/summary', methods=['GET'])
@require_auth
def get_dashboard_summary(current_user):
    """Get overall dashboard summary"""
    try:
        today = datetime.utcnow().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Today's summary
        today_meals = Meal.query.filter(
            and_(
                Meal.user_id == current_user.id,
                func.date(Meal.logged_at) == today
            )
        ).all()
        
        today_calories = sum(meal.calories for meal in today_meals)
        today_protein = sum(meal.protein for meal in today_meals)
        today_carbs = sum(meal.carbs for meal in today_meals)
        today_fat = sum(meal.fat for meal in today_meals)
        
        # Week summary
        week_meals = Meal.query.filter(
            and_(
                Meal.user_id == current_user.id,
                func.date(Meal.logged_at) >= week_ago
            )
        ).all()
        
        # Month summary
        month_meals = Meal.query.filter(
            and_(
                Meal.user_id == current_user.id,
                func.date(Meal.logged_at) >= month_ago
            )
        ).all()
        
        # Calculate averages
        week_avg_calories = sum(meal.calories for meal in week_meals) / 7 if week_meals else 0
        month_avg_calories = sum(meal.calories for meal in month_meals) / 30 if month_meals else 0
        
        # Progress towards goal
        calorie_goal_progress = (today_calories / current_user.daily_calorie_goal * 100) if current_user.daily_calorie_goal > 0 else 0
        
        # Recent meals (last 5)
        recent_meals = Meal.query.filter_by(user_id=current_user.id)\
                                .order_by(desc(Meal.logged_at))\
                                .limit(5).all()
        
        return success_response({
            'today': {
                'calories': today_calories,
                'protein': round(today_protein, 1),
                'carbs': round(today_carbs, 1),
                'fat': round(today_fat, 1),
                'meals_count': len(today_meals),
                'calorie_goal': current_user.daily_calorie_goal,
                'goal_progress': round(calorie_goal_progress, 1)
            },
            'week': {
                'avg_calories': round(week_avg_calories, 1),
                'total_meals': len(week_meals),
                'days_logged': len(set(meal.logged_at.date() for meal in week_meals))
            },
            'month': {
                'avg_calories': round(month_avg_calories, 1),
                'total_meals': len(month_meals),
                'days_logged': len(set(meal.logged_at.date() for meal in month_meals))
            },
            'recent_meals': [
                {
                    'id': meal.id,
                    'name': meal.name,
                    'calories': meal.calories,
                    'category_name': meal.category.name if meal.category else None,
                    'logged_at': meal.logged_at.isoformat()
                }
                for meal in recent_meals
            ]
        }, 'Dashboard summary retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get dashboard summary: {str(e)}', status_code=500)


@dashboard_bp.route('/daily-calories', methods=['GET'])
@require_auth
def get_daily_calories_chart(current_user):
    """Get daily calories data for chart"""
    try:
        # Get date range from query params (default to last 7 days)
        days = request.args.get('days', 7, type=int)
        days = min(days, 90)  # Limit to 90 days
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)
        
        # Query daily calories
        daily_data = db.session.query(
            func.date(Meal.logged_at).label('date'),
            func.sum(Meal.calories).label('total_calories'),
            func.count(Meal.id).label('meal_count')
        ).filter(
            and_(
                Meal.user_id == current_user.id,
                func.date(Meal.logged_at) >= start_date,
                func.date(Meal.logged_at) <= end_date
            )
        ).group_by(func.date(Meal.logged_at)).all()
        
        # Create complete dataset with missing dates as 0
        daily_calories = {}
        for data in daily_data:
            daily_calories[data.date.isoformat()] = {
                'calories': int(data.total_calories),
                'meal_count': data.meal_count,
                'goal': current_user.daily_calorie_goal
            }
        
        # Fill missing dates
        current_date = start_date
        result = []
        while current_date <= end_date:
            date_str = current_date.isoformat()
            result.append({
                'date': date_str,
                'calories': daily_calories.get(date_str, {}).get('calories', 0),
                'meal_count': daily_calories.get(date_str, {}).get('meal_count', 0),
                'goal': current_user.daily_calorie_goal
            })
            current_date += timedelta(days=1)
        
        return success_response({
            'daily_data': result,
            'period': f'Last {days} days'
        }, 'Daily calories chart data retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get daily calories chart: {str(e)}', status_code=500)


@dashboard_bp.route('/macros-breakdown', methods=['GET'])
@require_auth
def get_macros_breakdown(current_user):
    """Get macronutrient breakdown for pie chart"""
    try:
        # Get date range (default to last 7 days)
        days = request.args.get('days', 7, type=int)
        start_date = datetime.utcnow().date() - timedelta(days=days-1)
        
        meals = Meal.query.filter(
            and_(
                Meal.user_id == current_user.id,
                func.date(Meal.logged_at) >= start_date
            )
        ).all()
        
        if not meals:
            return success_response({
                'total_calories': 0,
                'macros': {
                    'protein': {'grams': 0, 'calories': 0, 'percentage': 0},
                    'carbs': {'grams': 0, 'calories': 0, 'percentage': 0},
                    'fat': {'grams': 0, 'calories': 0, 'percentage': 0}
                },
                'period': f'Last {days} days'
            }, 'No meals found for the specified period')
        
        # Calculate totals
        total_protein = sum(meal.protein for meal in meals)
        total_carbs = sum(meal.carbs for meal in meals)
        total_fat = sum(meal.fat for meal in meals)
        total_calories = sum(meal.calories for meal in meals)
        
        # Calculate calories from macros (Protein=4, Carbs=4, Fat=9 cal/g)
        protein_calories = total_protein * 4
        carbs_calories = total_carbs * 4
        fat_calories = total_fat * 9
        
        # Calculate percentages
        macro_calories_total = protein_calories + carbs_calories + fat_calories
        if macro_calories_total > 0:
            protein_percentage = (protein_calories / macro_calories_total) * 100
            carbs_percentage = (carbs_calories / macro_calories_total) * 100
            fat_percentage = (fat_calories / macro_calories_total) * 100
        else:
            protein_percentage = carbs_percentage = fat_percentage = 0
        
        return success_response({
            'total_calories': total_calories,
            'macros': {
                'protein': {
                    'grams': round(total_protein, 1),
                    'calories': round(protein_calories, 1),
                    'percentage': round(protein_percentage, 1)
                },
                'carbs': {
                    'grams': round(total_carbs, 1),
                    'calories': round(carbs_calories, 1),
                    'percentage': round(carbs_percentage, 1)
                },
                'fat': {
                    'grams': round(total_fat, 1),
                    'calories': round(fat_calories, 1),
                    'percentage': round(fat_percentage, 1)
                }
            },
            'period': f'Last {days} days'
        }, 'Macros breakdown retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get macros breakdown: {str(e)}', status_code=500)


@dashboard_bp.route('/category-distribution', methods=['GET'])
@require_auth
def get_category_distribution(current_user):
    """Get meal distribution by category"""
    try:
        # Get date range (default to last 30 days)
        days = request.args.get('days', 30, type=int)
        start_date = datetime.utcnow().date() - timedelta(days=days-1)
        
        # Query category distribution
        category_data = db.session.query(
            Category.name.label('category_name'),
            Category.color.label('category_color'),
            func.count(Meal.id).label('meal_count'),
            func.sum(Meal.calories).label('total_calories')
        ).join(Meal).filter(
            and_(
                Meal.user_id == current_user.id,
                func.date(Meal.logged_at) >= start_date
            )
        ).group_by(Category.id, Category.name, Category.color).all()
        
        total_meals = sum(data.meal_count for data in category_data)
        
        result = []
        for data in category_data:
            percentage = (data.meal_count / total_meals * 100) if total_meals > 0 else 0
            result.append({
                'category': data.category_name,
                'color': data.category_color,
                'meal_count': data.meal_count,
                'total_calories': int(data.total_calories),
                'percentage': round(percentage, 1)
            })
        
        return success_response({
            'categories': result,
            'total_meals': total_meals,
            'period': f'Last {days} days'
        }, 'Category distribution retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get category distribution: {str(e)}', status_code=500)


@dashboard_bp.route('/weekly-trends', methods=['GET'])
@require_auth
def get_weekly_trends(current_user):
    """Get weekly nutrition trends"""
    try:
        # Get last 4 weeks of data
        weeks = request.args.get('weeks', 4, type=int)
        weeks = min(weeks, 12)  # Limit to 12 weeks
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(weeks=weeks)
        
        # Query weekly data
        weekly_data = db.session.query(
            func.extract('week', Meal.logged_at).label('week'),
            func.extract('year', Meal.logged_at).label('year'),
            func.avg(Meal.calories).label('avg_calories'),
            func.sum(Meal.protein).label('total_protein'),
            func.sum(Meal.carbs).label('total_carbs'),
            func.sum(Meal.fat).label('total_fat'),
            func.count(Meal.id).label('meal_count')
        ).filter(
            and_(
                Meal.user_id == current_user.id,
                Meal.logged_at >= start_date
            )
        ).group_by(
            func.extract('year', Meal.logged_at),
            func.extract('week', Meal.logged_at)
        ).order_by(
            func.extract('year', Meal.logged_at),
            func.extract('week', Meal.logged_at)
        ).all()
        
        result = []
        for data in weekly_data:
            # Calculate week start date
            week_start = datetime.strptime(f'{int(data.year)}-W{int(data.week)}-1', '%Y-W%U-%w').date()
            
            result.append({
                'week_start': week_start.isoformat(),
                'week_number': int(data.week),
                'year': int(data.year),
                'avg_calories_per_meal': round(data.avg_calories, 1) if data.avg_calories else 0,
                'total_protein': round(data.total_protein, 1),
                'total_carbs': round(data.total_carbs, 1),
                'total_fat': round(data.total_fat, 1),
                'meal_count': data.meal_count
            })
        
        return success_response({
            'weekly_trends': result,
            'period': f'Last {weeks} weeks'
        }, 'Weekly trends retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get weekly trends: {str(e)}', status_code=500)


@dashboard_bp.route('/nutrition-goals', methods=['GET'])
@require_auth
def get_nutrition_goals_progress(current_user):
    """Get progress towards nutrition goals"""
    try:
        today = datetime.utcnow().date()
        
        # Get today's meals
        today_meals = Meal.query.filter(
            and_(
                Meal.user_id == current_user.id,
                func.date(Meal.logged_at) == today
            )
        ).all()
        
        # Calculate totals
        total_calories = sum(meal.calories for meal in today_meals)
        total_protein = sum(meal.protein for meal in today_meals)
        total_carbs = sum(meal.carbs for meal in today_meals)
        total_fat = sum(meal.fat for meal in today_meals)
        
        # Calculate recommended macros based on calorie goal
        calorie_goal = current_user.daily_calorie_goal
        
        # Standard macro distribution: 50% carbs, 30% fat, 20% protein
        protein_goal = (calorie_goal * 0.20) / 4  # grams
        carbs_goal = (calorie_goal * 0.50) / 4    # grams
        fat_goal = (calorie_goal * 0.30) / 9      # grams
        
        return success_response({
            'goals': {
                'calories': {
                    'current': total_calories,
                    'goal': calorie_goal,
                    'progress': round((total_calories / calorie_goal * 100) if calorie_goal > 0 else 0, 1),
                    'remaining': max(0, calorie_goal - total_calories)
                },
                'protein': {
                    'current': round(total_protein, 1),
                    'goal': round(protein_goal, 1),
                    'progress': round((total_protein / protein_goal * 100) if protein_goal > 0 else 0, 1),
                    'remaining': max(0, round(protein_goal - total_protein, 1))
                },
                'carbs': {
                    'current': round(total_carbs, 1),
                    'goal': round(carbs_goal, 1),
                    'progress': round((total_carbs / carbs_goal * 100) if carbs_goal > 0 else 0, 1),
                    'remaining': max(0, round(carbs_goal - total_carbs, 1))
                },
                'fat': {
                    'current': round(total_fat, 1),
                    'goal': round(fat_goal, 1),
                    'progress': round((total_fat / fat_goal * 100) if fat_goal > 0 else 0, 1),
                    'remaining': max(0, round(fat_goal - total_fat, 1))
                }
            },
            'date': today.isoformat()
        }, 'Nutrition goals progress retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to get nutrition goals: {str(e)}', status_code=500)