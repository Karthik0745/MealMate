// User types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  age?: number;
  weight?: number;
  height?: number;
  activity_level: ActivityLevel;
  daily_calorie_goal: number;
  is_admin: boolean;
  created_at: string;
  bmr?: number;
  tdee?: number;
}

export type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'active' | 'very_active';

export interface AuthResponse {
  user: User;
  access_token: string;
}

// Meal types
export interface Meal {
  id: number;
  user_id: number;
  category_id: number;
  category_name?: string;
  name: string;
  description?: string;
  quantity: number;
  unit: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  sugar: number;
  sodium: number;
  logged_at: string;
  created_at: string;
  macros_percentage: {
    protein: number;
    carbs: number;
    fat: number;
  };
  audio_notes_count: number;
}

export interface CreateMealData {
  name: string;
  category_id: number;
  description?: string;
  quantity?: number;
  unit?: string;
  calories: number;
  protein?: number;
  carbs?: number;
  fat?: number;
  fiber?: number;
  sugar?: number;
  sodium?: number;
  logged_at?: string;
}

// Category types
export interface Category {
  id: number;
  name: string;
  description?: string;
  color: string;
  icon?: string;
  created_at: string;
  meal_count?: number;
}

// Audio Note types
export interface AudioNote {
  id: number;
  user_id: number;
  meal_id?: number;
  meal_name?: string;
  title: string;
  description?: string;
  filename: string;
  duration?: number;
  file_size: number;
  mime_type: string;
  created_at: string;
  updated_at: string;
}

// Dashboard types
export interface DashboardSummary {
  today: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    meals_count: number;
    calorie_goal: number;
    goal_progress: number;
  };
  week: {
    avg_calories: number;
    total_meals: number;
    days_logged: number;
  };
  month: {
    avg_calories: number;
    total_meals: number;
    days_logged: number;
  };
  recent_meals: Array<{
    id: number;
    name: string;
    calories: number;
    category_name?: string;
    logged_at: string;
  }>;
}

export interface DailyCaloriesData {
  daily_data: Array<{
    date: string;
    calories: number;
    meal_count: number;
    goal: number;
  }>;
  period: string;
}

export interface MacrosBreakdown {
  total_calories: number;
  macros: {
    protein: {
      grams: number;
      calories: number;
      percentage: number;
    };
    carbs: {
      grams: number;
      calories: number;
      percentage: number;
    };
    fat: {
      grams: number;
      calories: number;
      percentage: number;
    };
  };
  period: string;
}

export interface CategoryDistribution {
  categories: Array<{
    category: string;
    color: string;
    meal_count: number;
    total_calories: number;
    percentage: number;
  }>;
  total_meals: number;
  period: string;
}

export interface NutritionGoals {
  goals: {
    calories: {
      current: number;
      goal: number;
      progress: number;
      remaining: number;
    };
    protein: {
      current: number;
      goal: number;
      progress: number;
      remaining: number;
    };
    carbs: {
      current: number;
      goal: number;
      progress: number;
      remaining: number;
    };
    fat: {
      current: number;
      goal: number;
      progress: number;
      remaining: number;
    };
  };
  date: string;
}

// AI types
export interface AISuggestions {
  suggestions: string[];
  analysis: string;
  recommendations: string[];
}

export interface FoodSuggestion {
  suggestions: string[];
  message: string;
}

// API Response types
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  errors?: any;
}

export interface PaginationInfo {
  total: number;
  pages: number;
  current_page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: PaginationInfo;
}

// Form types
export interface LoginFormData {
  username: string;
  password: string;
}

export interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  age?: number;
  weight?: number;
  height?: number;
  activity_level?: ActivityLevel;
  daily_calorie_goal?: number;
}

export interface ProfileFormData {
  first_name: string;
  last_name: string;
  email: string;
  age?: number;
  weight?: number;
  height?: number;
  activity_level: ActivityLevel;
  daily_calorie_goal: number;
}

// Chart types
export interface ChartDataPoint {
  x: string | number;
  y: number;
}

export interface ChartData {
  labels: string[];
  datasets: Array<{
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
    fill?: boolean;
  }>;
}

// Socket types
export interface SocketEvent {
  meal_created: { meal: Meal; user_id: number };
  meal_updated: { meal: Meal; user_id: number };
  meal_deleted: { meal_id: number; user_id: number };
  meals_bulk_created: { meals: Meal[]; user_id: number };
}

// Error types
export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  status?: number;
}