import { apiService } from './api';
import { 
  DashboardSummary,
  DailyCaloriesData,
  MacrosBreakdown,
  CategoryDistribution,
  NutritionGoals
} from '../types';

class DashboardService {
  // Get overall dashboard summary
  async getSummary(): Promise<DashboardSummary> {
    const response = await apiService.get<DashboardSummary>('/api/dashboard/summary');
    
    if (response.success && response.data) {
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to get dashboard summary');
  }

  // Get daily calories chart data
  async getDailyCalories(days: number = 7): Promise<DailyCaloriesData> {
    const response = await apiService.get<DailyCaloriesData>('/api/dashboard/daily-calories', {
      days
    });
    
    if (response.success && response.data) {
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to get daily calories data');
  }

  // Get macronutrient breakdown
  async getMacrosBreakdown(days: number = 7): Promise<MacrosBreakdown> {
    const response = await apiService.get<MacrosBreakdown>('/api/dashboard/macros-breakdown', {
      days
    });
    
    if (response.success && response.data) {
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to get macros breakdown');
  }

  // Get category distribution
  async getCategoryDistribution(days: number = 30): Promise<CategoryDistribution> {
    const response = await apiService.get<CategoryDistribution>('/api/dashboard/category-distribution', {
      days
    });
    
    if (response.success && response.data) {
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to get category distribution');
  }

  // Get nutrition goals progress
  async getNutritionGoals(): Promise<NutritionGoals> {
    const response = await apiService.get<NutritionGoals>('/api/dashboard/nutrition-goals');
    
    if (response.success && response.data) {
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to get nutrition goals');
  }

  // Get weekly trends
  async getWeeklyTrends(weeks: number = 4): Promise<any> {
    const response = await apiService.get('/api/dashboard/weekly-trends', {
      weeks
    });
    
    if (response.success && response.data) {
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to get weekly trends');
  }

  // Helper method to format chart data
  formatDailyCaloriesForChart(data: DailyCaloriesData) {
    return {
      labels: data.daily_data.map(item => {
        const date = new Date(item.date);
        return date.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric' 
        });
      }),
      datasets: [
        {
          label: 'Calories Consumed',
          data: data.daily_data.map(item => item.calories),
          backgroundColor: 'rgba(59, 130, 246, 0.5)',
          borderColor: 'rgb(59, 130, 246)',
          borderWidth: 2,
          fill: true,
        },
        {
          label: 'Daily Goal',
          data: data.daily_data.map(item => item.goal),
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          borderColor: 'rgb(239, 68, 68)',
          borderWidth: 2,
          borderDash: [5, 5],
          fill: false,
        }
      ]
    };
  }

  // Helper method to format macros for pie chart
  formatMacrosForChart(data: MacrosBreakdown) {
    return {
      labels: ['Protein', 'Carbs', 'Fat'],
      datasets: [
        {
          data: [
            data.macros.protein.percentage,
            data.macros.carbs.percentage,
            data.macros.fat.percentage
          ],
          backgroundColor: [
            '#ef4444', // Red for protein
            '#3b82f6', // Blue for carbs
            '#f59e0b'  // Orange for fat
          ],
          borderWidth: 2,
          borderColor: '#ffffff'
        }
      ]
    };
  }

  // Helper method to format category distribution for chart
  formatCategoryForChart(data: CategoryDistribution) {
    return {
      labels: data.categories.map(cat => cat.category),
      datasets: [
        {
          data: data.categories.map(cat => cat.percentage),
          backgroundColor: data.categories.map(cat => cat.color),
          borderWidth: 2,
          borderColor: '#ffffff'
        }
      ]
    };
  }

  // Calculate BMI
  calculateBMI(weight: number, height: number): number {
    // height in cm, weight in kg
    const heightInMeters = height / 100;
    return weight / (heightInMeters * heightInMeters);
  }

  // Get BMI category
  getBMICategory(bmi: number): string {
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal weight';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
  }

  // Calculate calories needed for weight goal
  calculateCaloriesForGoal(
    currentWeight: number,
    targetWeight: number,
    timeframe: number, // weeks
    tdee: number
  ): number {
    const weightDifference = targetWeight - currentWeight;
    const totalCalorieChange = weightDifference * 7700; // 7700 cal per kg
    const dailyCalorieChange = totalCalorieChange / (timeframe * 7);
    return Math.round(tdee + dailyCalorieChange);
  }

  // Get nutrition recommendations based on goals
  getNutritionRecommendations(goals: NutritionGoals): string[] {
    const recommendations: string[] = [];
    const { calories, protein, carbs, fat } = goals.goals;

    if (calories.progress < 80) {
      recommendations.push('Consider eating more calorie-dense foods to meet your daily goal');
    } else if (calories.progress > 120) {
      recommendations.push('You\'re consuming more calories than your goal. Consider portion control');
    }

    if (protein.progress < 80) {
      recommendations.push('Increase protein intake with lean meats, eggs, or legumes');
    }

    if (fat.progress < 60) {
      recommendations.push('Add healthy fats like nuts, avocado, or olive oil to your meals');
    } else if (fat.progress > 140) {
      recommendations.push('Consider reducing fat intake for better balance');
    }

    if (carbs.progress > 150) {
      recommendations.push('Consider reducing refined carbs and focus on complex carbohydrates');
    }

    if (recommendations.length === 0) {
      recommendations.push('Great job! Your nutrition is well balanced today');
    }

    return recommendations;
  }
}

export const dashboardService = new DashboardService();
export default dashboardService;