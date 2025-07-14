import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useSocket } from '../hooks/useSocket';
import { dashboardService } from '../services/dashboard';
import { 
  DashboardSummary, 
  DailyCaloriesData, 
  MacrosBreakdown, 
  NutritionGoals 
} from '../types';
import LoadingSpinner from '../components/common/LoadingSpinner';
import Button from '../components/common/Button';
import DailyCaloriesChart from '../components/charts/DailyCaloriesChart';
import toast from 'react-hot-toast';

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const socket = useSocket();
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [dailyCalories, setDailyCalories] = useState<DailyCaloriesData | null>(null);
  const [macrosBreakdown, setMacrosBreakdown] = useState<MacrosBreakdown | null>(null);
  const [nutritionGoals, setNutritionGoals] = useState<NutritionGoals | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  // Listen for real-time meal updates
  useEffect(() => {
    const handleMealUpdate = () => {
      // Refresh dashboard data when meals are updated
      loadDashboardData();
    };

    socket.on('meal_created', handleMealUpdate);
    socket.on('meal_updated', handleMealUpdate);
    socket.on('meal_deleted', handleMealUpdate);

    return () => {
      socket.off('meal_created', handleMealUpdate);
      socket.off('meal_updated', handleMealUpdate);
      socket.off('meal_deleted', handleMealUpdate);
    };
  }, [socket]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load all dashboard data in parallel
      const [summaryData, caloriesData, macrosData, goalsData] = await Promise.all([
        dashboardService.getSummary(),
        dashboardService.getDailyCalories(7),
        dashboardService.getMacrosBreakdown(7),
        dashboardService.getNutritionGoals()
      ]);

      setSummary(summaryData);
      setDailyCalories(caloriesData);
      setMacrosBreakdown(macrosData);
      setNutritionGoals(goalsData);
    } catch (error: any) {
      toast.error('Failed to load dashboard data');
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  const getProgressColor = (progress: number) => {
    if (progress < 50) return 'bg-red-500';
    if (progress < 80) return 'bg-yellow-500';
    if (progress <= 100) return 'bg-green-500';
    return 'bg-blue-500';
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.first_name}!
          </h1>
          <p className="text-gray-600">
            Here's your nutrition overview for today
          </p>
        </div>
        <Button onClick={loadDashboardData} variant="outline">
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </Button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Today's Calories */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Today's Calories</p>
                <p className="text-2xl font-bold text-gray-900">
                  {summary.today.calories.toLocaleString()}
                </p>
                <p className="text-sm text-gray-500">
                  Goal: {summary.today.calorie_goal.toLocaleString()}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full transition-all duration-300 ${getProgressColor(summary.today.goal_progress)}`}
                  style={{ width: `${Math.min(summary.today.goal_progress, 100)}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {summary.today.goal_progress.toFixed(0)}% of daily goal
              </p>
            </div>
          </div>

          {/* Today's Meals */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Meals Logged</p>
                <p className="text-2xl font-bold text-gray-900">
                  {summary.today.meals_count}
                </p>
                <p className="text-sm text-gray-500">Today</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
            </div>
          </div>

          {/* Weekly Average */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Weekly Average</p>
                <p className="text-2xl font-bold text-gray-900">
                  {summary.week.avg_calories.toLocaleString()}
                </p>
                <p className="text-sm text-gray-500">calories/day</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
          </div>

          {/* Monthly Stats */}
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">This Month</p>
                <p className="text-2xl font-bold text-gray-900">
                  {summary.month.total_meals}
                </p>
                <p className="text-sm text-gray-500">total meals</p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m-6 8h6m-6 0l6-6m-6 6l6 6" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Calories Chart */}
        {dailyCalories && (
          <div className="lg:col-span-2">
            <DailyCaloriesChart data={dailyCalories} height={350} />
          </div>
        )}

        {/* Macros Breakdown */}
        {macrosBreakdown && (
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Macronutrient Breakdown (Last 7 days)
            </h3>
            <div className="space-y-4">
              {/* Protein */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium text-gray-700">Protein</span>
                  <span className="text-sm text-gray-500">
                    {macrosBreakdown.macros.protein.grams}g ({macrosBreakdown.macros.protein.percentage}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="h-2 bg-red-500 rounded-full transition-all duration-300"
                    style={{ width: `${macrosBreakdown.macros.protein.percentage}%` }}
                  />
                </div>
              </div>

              {/* Carbs */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium text-gray-700">Carbohydrates</span>
                  <span className="text-sm text-gray-500">
                    {macrosBreakdown.macros.carbs.grams}g ({macrosBreakdown.macros.carbs.percentage}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="h-2 bg-blue-500 rounded-full transition-all duration-300"
                    style={{ width: `${macrosBreakdown.macros.carbs.percentage}%` }}
                  />
                </div>
              </div>

              {/* Fat */}
              <div>
                <div className="flex justify-between items-center mb-1">
                  <span className="text-sm font-medium text-gray-700">Fat</span>
                  <span className="text-sm text-gray-500">
                    {macrosBreakdown.macros.fat.grams}g ({macrosBreakdown.macros.fat.percentage}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="h-2 bg-yellow-500 rounded-full transition-all duration-300"
                    style={{ width: `${macrosBreakdown.macros.fat.percentage}%` }}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Recent Meals */}
        {summary && (
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Meals</h3>
            <div className="space-y-3">
              {summary.recent_meals.length > 0 ? (
                summary.recent_meals.map((meal) => (
                  <div key={meal.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{meal.name}</p>
                      <p className="text-sm text-gray-500">{meal.category_name}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-gray-900">{meal.calories} cal</p>
                      <p className="text-xs text-gray-500">
                        {new Date(meal.logged_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8">
                  <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  <p className="text-gray-500">No meals logged yet</p>
                  <p className="text-sm text-gray-400">Start tracking your nutrition!</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Button 
            onClick={() => window.location.href = '/meals'}
            className="flex items-center justify-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <span>Log New Meal</span>
          </Button>
          
          <Button 
            variant="outline"
            onClick={() => window.location.href = '/profile'}
            className="flex items-center justify-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>Update Profile</span>
          </Button>
          
          <Button 
            variant="outline"
            onClick={loadDashboardData}
            className="flex items-center justify-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <span>View Analytics</span>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;