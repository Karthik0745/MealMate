import { apiService } from './api';
import { 
  Meal, 
  CreateMealData, 
  Category, 
  PaginatedResponse 
} from '../types';

export interface MealFilters {
  category_id?: number;
  start_date?: string;
  end_date?: string;
  search?: string;
  page?: number;
  per_page?: number;
}

class MealsService {
  // Get meals with filtering and pagination
  async getMeals(filters: MealFilters = {}): Promise<PaginatedResponse<Meal>> {
    const response = await apiService.get<{
      meals: Meal[];
      pagination: any;
    }>('/api/meals', filters);
    
    if (response.success && response.data) {
      return {
        items: response.data.meals,
        pagination: response.data.pagination
      };
    }
    
    throw new Error(response.message || 'Failed to get meals');
  }

  // Get a specific meal
  async getMeal(id: number): Promise<Meal> {
    const response = await apiService.get<Meal>(`/api/meals/${id}`);
    
    if (response.success && response.data) {
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to get meal');
  }

  // Create a new meal
  async createMeal(data: CreateMealData): Promise<Meal> {
    const response = await apiService.post<Meal>('/api/meals', data);
    
    if (response.success && response.data) {
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to create meal');
  }

  // Update a meal
  async updateMeal(id: number, data: Partial<CreateMealData>): Promise<Meal> {
    const response = await apiService.put<Meal>(`/api/meals/${id}`, data);
    
    if (response.success && response.data) {
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to update meal');
  }

  // Delete a meal
  async deleteMeal(id: number): Promise<void> {
    const response = await apiService.delete(`/api/meals/${id}`);
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to delete meal');
    }
  }

  // Get meal categories
  async getCategories(): Promise<Category[]> {
    const response = await apiService.get<Category[]>('/api/meals/categories');
    
    if (response.success && response.data) {
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to get categories');
  }

  // Create multiple meals at once
  async createBulkMeals(meals: CreateMealData[]): Promise<Meal[]> {
    const response = await apiService.post<Meal[]>('/api/meals/bulk', {
      meals
    });
    
    if (response.success && response.data) {
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to create meals');
  }

  // Get recent meals (last 7 days)
  async getRecentMeals(): Promise<Meal[]> {
    const response = await apiService.get<Meal[]>('/api/meals/recent');
    
    if (response.success && response.data) {
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to get recent meals');
  }

  // Get meals for a specific date
  async getMealsForDate(date: string): Promise<Meal[]> {
    const response = await this.getMeals({
      start_date: date,
      end_date: date,
      per_page: 100
    });
    
    return response.items;
  }

  // Get meals for date range
  async getMealsForDateRange(startDate: string, endDate: string): Promise<Meal[]> {
    const response = await this.getMeals({
      start_date: startDate,
      end_date: endDate,
      per_page: 1000
    });
    
    return response.items;
  }

  // Search meals by name
  async searchMeals(query: string, limit: number = 20): Promise<Meal[]> {
    const response = await this.getMeals({
      search: query,
      per_page: limit
    });
    
    return response.items;
  }

  // Get meals by category
  async getMealsByCategory(categoryId: number): Promise<Meal[]> {
    const response = await this.getMeals({
      category_id: categoryId,
      per_page: 1000
    });
    
    return response.items;
  }

  // Quick meal templates
  getQuickMealTemplates(): CreateMealData[] {
    return [
      {
        name: 'Oatmeal with Berries',
        category_id: 1, // Breakfast
        calories: 250,
        protein: 8,
        carbs: 45,
        fat: 5,
        fiber: 8,
        description: 'Hearty breakfast with rolled oats and mixed berries'
      },
      {
        name: 'Grilled Chicken Salad',
        category_id: 2, // Lunch
        calories: 350,
        protein: 35,
        carbs: 15,
        fat: 18,
        fiber: 6,
        description: 'Fresh mixed greens with grilled chicken breast'
      },
      {
        name: 'Salmon with Quinoa',
        category_id: 3, // Dinner
        calories: 450,
        protein: 32,
        carbs: 35,
        fat: 20,
        fiber: 5,
        description: 'Baked salmon fillet with quinoa and vegetables'
      },
      {
        name: 'Greek Yogurt',
        category_id: 4, // Snack
        calories: 150,
        protein: 15,
        carbs: 20,
        fat: 0,
        fiber: 0,
        description: 'Plain Greek yogurt with honey'
      },
      {
        name: 'Green Smoothie',
        category_id: 5, // Drink
        calories: 200,
        protein: 5,
        carbs: 35,
        fat: 3,
        fiber: 8,
        description: 'Spinach, banana, apple, and almond milk smoothie'
      }
    ];
  }
}

export const mealsService = new MealsService();
export default mealsService;