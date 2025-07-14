import os
import openai
from typing import List, Dict, Any
import json
from datetime import datetime, timedelta


class AIService:
    """Service for AI-powered dietary suggestions using Azure OpenAI"""
    
    def __init__(self):
        self.api_key = os.getenv('AZURE_OPENAI_KEY')
        self.endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-35-turbo')
        
        if self.api_key and self.endpoint:
            openai.api_type = "azure"
            openai.api_base = self.endpoint
            openai.api_version = "2023-05-15"
            openai.api_key = self.api_key
    
    def is_configured(self) -> bool:
        """Check if Azure OpenAI is properly configured"""
        return bool(self.api_key and self.endpoint)
    
    def analyze_meal_history(self, user_data: Dict[str, Any], meals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze user's meal history and provide dietary suggestions"""
        if not self.is_configured():
            return {
                'suggestions': ['Azure OpenAI not configured. Please set up your API credentials.'],
                'analysis': 'Service unavailable',
                'recommendations': []
            }
        
        try:
            # Prepare meal data for analysis
            meal_summary = self._prepare_meal_summary(meals)
            user_profile = self._prepare_user_profile(user_data)
            
            # Create prompt for AI analysis
            prompt = self._create_analysis_prompt(user_profile, meal_summary)
            
            # Call Azure OpenAI
            response = openai.ChatCompletion.create(
                engine=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a certified nutritionist and dietitian providing personalized dietary advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            # Parse AI response
            ai_response = response.choices[0].message.content
            return self._parse_ai_response(ai_response)
            
        except Exception as e:
            return {
                'suggestions': [f'Error generating suggestions: {str(e)}'],
                'analysis': 'Analysis failed',
                'recommendations': []
            }
    
    def _prepare_meal_summary(self, meals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepare a summary of user's recent meals"""
        if not meals:
            return {
                'total_meals': 0,
                'avg_calories': 0,
                'avg_protein': 0,
                'avg_carbs': 0,
                'avg_fat': 0,
                'meal_frequency': {},
                'recent_days': 0
            }
        
        # Calculate totals and averages
        total_meals = len(meals)
        total_calories = sum(meal.get('calories', 0) for meal in meals)
        total_protein = sum(meal.get('protein', 0) for meal in meals)
        total_carbs = sum(meal.get('carbs', 0) for meal in meals)
        total_fat = sum(meal.get('fat', 0) for meal in meals)
        
        # Count meal categories
        meal_frequency = {}
        for meal in meals:
            category = meal.get('category_name', 'Unknown')
            meal_frequency[category] = meal_frequency.get(category, 0) + 1
        
        # Calculate date range
        dates = [meal.get('logged_at', '') for meal in meals if meal.get('logged_at')]
        recent_days = len(set(date[:10] for date in dates if date))  # Count unique days
        
        return {
            'total_meals': total_meals,
            'avg_calories': round(total_calories / max(total_meals, 1), 1),
            'avg_protein': round(total_protein / max(total_meals, 1), 1),
            'avg_carbs': round(total_carbs / max(total_meals, 1), 1),
            'avg_fat': round(total_fat / max(total_meals, 1), 1),
            'meal_frequency': meal_frequency,
            'recent_days': recent_days,
            'daily_avg_calories': round(total_calories / max(recent_days, 1), 1) if recent_days > 0 else 0
        }
    
    def _prepare_user_profile(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare user profile for AI analysis"""
        return {
            'age': user_data.get('age'),
            'weight': user_data.get('weight'),
            'height': user_data.get('height'),
            'activity_level': user_data.get('activity_level', 'moderate'),
            'daily_calorie_goal': user_data.get('daily_calorie_goal', 2000),
            'bmr': user_data.get('bmr'),
            'tdee': user_data.get('tdee')
        }
    
    def _create_analysis_prompt(self, user_profile: Dict[str, Any], meal_summary: Dict[str, Any]) -> str:
        """Create a prompt for AI dietary analysis"""
        prompt = f"""
        Please analyze the following user's dietary patterns and provide personalized nutrition advice:

        User Profile:
        - Age: {user_profile.get('age', 'Not specified')}
        - Weight: {user_profile.get('weight', 'Not specified')} kg
        - Height: {user_profile.get('height', 'Not specified')} cm
        - Activity Level: {user_profile.get('activity_level', 'moderate')}
        - Daily Calorie Goal: {user_profile.get('daily_calorie_goal', 2000)} calories
        - Estimated TDEE: {user_profile.get('tdee', 'Not calculated')} calories

        Recent Meal Analysis ({meal_summary['recent_days']} days):
        - Total meals logged: {meal_summary['total_meals']}
        - Daily average calories: {meal_summary['daily_avg_calories']}
        - Average per meal - Calories: {meal_summary['avg_calories']}, Protein: {meal_summary['avg_protein']}g, Carbs: {meal_summary['avg_carbs']}g, Fat: {meal_summary['avg_fat']}g
        - Meal frequency by category: {meal_summary['meal_frequency']}

        Please provide:
        1. 3-5 specific, actionable dietary suggestions
        2. Brief analysis of their current eating patterns
        3. 2-3 recommendations for improvement

        Format your response as JSON with keys: "suggestions", "analysis", "recommendations"
        """
        
        return prompt
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response and extract structured data"""
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # If not JSON, parse manually
            lines = response.strip().split('\n')
            suggestions = []
            analysis = ""
            recommendations = []
            
            current_section = None
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if 'suggestion' in line.lower() and ':' in line:
                    current_section = 'suggestions'
                    continue
                elif 'analysis' in line.lower() and ':' in line:
                    current_section = 'analysis'
                    continue
                elif 'recommendation' in line.lower() and ':' in line:
                    current_section = 'recommendations'
                    continue
                
                if current_section == 'suggestions':
                    if line.startswith(('-', '*', '•')) or line[0].isdigit():
                        suggestions.append(line.lstrip('-*•0123456789. '))
                elif current_section == 'analysis':
                    analysis += line + " "
                elif current_section == 'recommendations':
                    if line.startswith(('-', '*', '•')) or line[0].isdigit():
                        recommendations.append(line.lstrip('-*•0123456789. '))
            
            return {
                'suggestions': suggestions or ['Focus on balanced nutrition with adequate protein, complex carbs, and healthy fats.'],
                'analysis': analysis.strip() or 'Meal analysis completed.',
                'recommendations': recommendations or ['Track your meals consistently', 'Stay hydrated', 'Include variety in your diet']
            }
            
        except Exception as e:
            return {
                'suggestions': ['Unable to parse AI response. Please try again.'],
                'analysis': f'Parsing error: {str(e)}',
                'recommendations': ['Track your meals consistently', 'Consult with a nutritionist']
            }
    
    def get_food_suggestion(self, query: str) -> Dict[str, Any]:
        """Get food suggestions based on user query"""
        if not self.is_configured():
            return {
                'suggestions': ['Azure OpenAI not configured'],
                'message': 'Service unavailable'
            }
        
        try:
            prompt = f"""
            User is asking about: "{query}"
            
            Please provide helpful nutrition information or food suggestions related to this query.
            Keep the response concise and practical.
            
            Format as JSON with keys: "suggestions" (array), "message" (string)
            """
            
            response = openai.ChatCompletion.create(
                engine=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a helpful nutrition assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            try:
                return json.loads(ai_response)
            except:
                return {
                    'suggestions': [ai_response],
                    'message': 'Food suggestion provided'
                }
                
        except Exception as e:
            return {
                'suggestions': [f'Error: {str(e)}'],
                'message': 'Failed to get suggestions'
            }