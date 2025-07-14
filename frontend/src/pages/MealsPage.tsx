import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useSocket } from '../hooks/useSocket';
import { mealsService } from '../services/meals';
import { 
  Meal, 
  CreateMealData, 
  Category, 
  PaginatedResponse 
} from '../types';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import LoadingSpinner from '../components/common/LoadingSpinner';
import toast from 'react-hot-toast';

const MealsPage: React.FC = () => {
  const socket = useSocket();
  const [meals, setMeals] = useState<Meal[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingMeal, setEditingMeal] = useState<Meal | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue
  } = useForm<CreateMealData>();

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    loadMeals();
  }, [currentPage, searchQuery, selectedCategory]);

  // Listen for real-time meal updates
  useEffect(() => {
    socket.on('meal_created', handleMealUpdate);
    socket.on('meal_updated', handleMealUpdate);
    socket.on('meal_deleted', handleMealDelete);

    return () => {
      socket.off('meal_created', handleMealUpdate);
      socket.off('meal_updated', handleMealUpdate);
      socket.off('meal_deleted', handleMealDelete);
    };
  }, [socket]);

  const handleMealUpdate = (data: any) => {
    // Refresh meals list
    loadMeals();
  };

  const handleMealDelete = (data: any) => {
    setMeals(prev => prev.filter(meal => meal.id !== data.meal_id));
  };

  const loadInitialData = async () => {
    try {
      const categoriesData = await mealsService.getCategories();
      setCategories(categoriesData);
    } catch (error) {
      toast.error('Failed to load categories');
    }
  };

  const loadMeals = async () => {
    try {
      setLoading(true);
      const response: PaginatedResponse<Meal> = await mealsService.getMeals({
        page: currentPage,
        per_page: 10,
        search: searchQuery || undefined,
        category_id: selectedCategory || undefined
      });
      
      setMeals(response.items);
      setTotalPages(response.pagination.pages);
    } catch (error) {
      toast.error('Failed to load meals');
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data: CreateMealData) => {
    try {
      if (editingMeal) {
        await mealsService.updateMeal(editingMeal.id, data);
        toast.success('Meal updated successfully');
        setEditingMeal(null);
      } else {
        await mealsService.createMeal(data);
        toast.success('Meal logged successfully');
        setShowAddForm(false);
      }
      
      reset();
      loadMeals();
    } catch (error: any) {
      toast.error(error.message || 'Failed to save meal');
    }
  };

  const handleEdit = (meal: Meal) => {
    setEditingMeal(meal);
    setShowAddForm(true);
    
    // Pre-fill form with meal data
    setValue('name', meal.name);
    setValue('category_id', meal.category_id);
    setValue('description', meal.description || '');
    setValue('calories', meal.calories);
    setValue('protein', meal.protein);
    setValue('carbs', meal.carbs);
    setValue('fat', meal.fat);
    setValue('fiber', meal.fiber);
    setValue('sugar', meal.sugar);
    setValue('sodium', meal.sodium);
    setValue('quantity', meal.quantity);
    setValue('unit', meal.unit);
  };

  const handleDelete = async (mealId: number) => {
    if (window.confirm('Are you sure you want to delete this meal?')) {
      try {
        await mealsService.deleteMeal(mealId);
        toast.success('Meal deleted successfully');
        loadMeals();
      } catch (error) {
        toast.error('Failed to delete meal');
      }
    }
  };

  const resetForm = () => {
    reset();
    setEditingMeal(null);
    setShowAddForm(false);
  };

  const handleQuickAdd = async (templateMeal: CreateMealData) => {
    try {
      await mealsService.createMeal(templateMeal);
      toast.success('Meal logged successfully');
      loadMeals();
    } catch (error: any) {
      toast.error(error.message || 'Failed to log meal');
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Meal Tracking</h1>
          <p className="text-gray-600">Log and manage your daily meals</p>
        </div>
        <Button onClick={() => setShowAddForm(true)}>
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Log New Meal
        </Button>
      </div>

      {/* Quick Add Templates */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Add Templates</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mealsService.getQuickMealTemplates().map((template, index) => (
            <div key={index} className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 transition-colors">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-medium text-gray-900">{template.name}</h4>
                <span className="text-sm font-semibold text-primary-600">{template.calories} cal</span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{template.description}</p>
              <div className="flex justify-between items-center">
                <div className="text-xs text-gray-500">
                  P: {template.protein}g | C: {template.carbs}g | F: {template.fat}g
                </div>
                <Button size="small" onClick={() => handleQuickAdd(template)}>
                  Add
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Input
            placeholder="Search meals..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            leftIcon={
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            }
          />
          
          <select
            value={selectedCategory || ''}
            onChange={(e) => setSelectedCategory(e.target.value ? Number(e.target.value) : null)}
            className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 focus:outline-none"
          >
            <option value="">All Categories</option>
            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>

          <Button variant="outline" onClick={loadMeals}>
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </Button>
        </div>
      </div>

      {/* Add/Edit Meal Form */}
      {showAddForm && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {editingMeal ? 'Edit Meal' : 'Log New Meal'}
            </h3>
            <Button variant="outline" onClick={resetForm}>
              Cancel
            </Button>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input
                {...register('name', { required: 'Meal name is required' })}
                label="Meal Name"
                placeholder="e.g., Grilled Chicken Salad"
                error={errors.name?.message}
                fullWidth
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Category
                </label>
                <select
                  {...register('category_id', { required: 'Category is required' })}
                  className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 focus:outline-none"
                >
                  <option value="">Select category</option>
                  {categories.map(category => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
                {errors.category_id && (
                  <p className="mt-1 text-sm text-danger-600">{errors.category_id.message}</p>
                )}
              </div>

              <Input
                {...register('calories', { 
                  required: 'Calories is required',
                  min: { value: 0, message: 'Calories must be positive' }
                })}
                label="Calories"
                type="number"
                placeholder="250"
                error={errors.calories?.message}
                fullWidth
              />

              <div className="grid grid-cols-2 gap-2">
                <Input
                  {...register('quantity', { min: 0 })}
                  label="Quantity"
                  type="number"
                  step="0.1"
                  placeholder="1"
                  error={errors.quantity?.message}
                  fullWidth
                />

                <Input
                  {...register('unit')}
                  label="Unit"
                  placeholder="serving"
                  fullWidth
                />
              </div>
            </div>

            <div>
              <Input
                {...register('description')}
                label="Description (Optional)"
                placeholder="Any additional notes about this meal"
                fullWidth
              />
            </div>

            {/* Macronutrients */}
            <div>
              <h4 className="text-md font-medium text-gray-900 mb-3">Macronutrients (Optional)</h4>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                <Input
                  {...register('protein', { min: 0 })}
                  label="Protein (g)"
                  type="number"
                  step="0.1"
                  placeholder="25"
                  error={errors.protein?.message}
                  fullWidth
                />

                <Input
                  {...register('carbs', { min: 0 })}
                  label="Carbs (g)"
                  type="number"
                  step="0.1"
                  placeholder="30"
                  error={errors.carbs?.message}
                  fullWidth
                />

                <Input
                  {...register('fat', { min: 0 })}
                  label="Fat (g)"
                  type="number"
                  step="0.1"
                  placeholder="15"
                  error={errors.fat?.message}
                  fullWidth
                />

                <Input
                  {...register('fiber', { min: 0 })}
                  label="Fiber (g)"
                  type="number"
                  step="0.1"
                  placeholder="5"
                  error={errors.fiber?.message}
                  fullWidth
                />

                <Input
                  {...register('sugar', { min: 0 })}
                  label="Sugar (g)"
                  type="number"
                  step="0.1"
                  placeholder="10"
                  error={errors.sugar?.message}
                  fullWidth
                />

                <Input
                  {...register('sodium', { min: 0 })}
                  label="Sodium (mg)"
                  type="number"
                  step="0.1"
                  placeholder="500"
                  error={errors.sodium?.message}
                  fullWidth
                />
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <Button type="button" variant="outline" onClick={resetForm}>
                Cancel
              </Button>
              <Button type="submit">
                {editingMeal ? 'Update Meal' : 'Log Meal'}
              </Button>
            </div>
          </form>
        </div>
      )}

      {/* Meals List */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Recent Meals</h3>
        </div>

        {loading ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner />
          </div>
        ) : meals.length > 0 ? (
          <div className="divide-y divide-gray-200">
            {meals.map((meal) => (
              <div key={meal.id} className="p-6 hover:bg-gray-50">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="text-lg font-medium text-gray-900">{meal.name}</h4>
                      <span 
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        style={{ 
                          backgroundColor: categories.find(c => c.id === meal.category_id)?.color + '20',
                          color: categories.find(c => c.id === meal.category_id)?.color
                        }}
                      >
                        {meal.category_name}
                      </span>
                    </div>
                    
                    {meal.description && (
                      <p className="text-gray-600 mb-2">{meal.description}</p>
                    )}
                    
                    <div className="flex items-center space-x-6 text-sm text-gray-500">
                      <span className="font-semibold text-gray-900">{meal.calories} calories</span>
                      <span>P: {meal.protein}g</span>
                      <span>C: {meal.carbs}g</span>
                      <span>F: {meal.fat}g</span>
                      <span>{meal.quantity} {meal.unit}</span>
                    </div>
                    
                    <p className="text-xs text-gray-400 mt-2">
                      Logged on {new Date(meal.logged_at).toLocaleDateString()} at {new Date(meal.logged_at).toLocaleTimeString()}
                    </p>
                  </div>

                  <div className="flex space-x-2 ml-4">
                    <Button size="small" variant="outline" onClick={() => handleEdit(meal)}>
                      Edit
                    </Button>
                    <Button size="small" variant="danger" onClick={() => handleDelete(meal.id)}>
                      Delete
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No meals found</h3>
            <p className="text-gray-500">Start by logging your first meal!</p>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Page {currentPage} of {totalPages}
            </div>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="small"
                disabled={currentPage <= 1}
                onClick={() => setCurrentPage(prev => prev - 1)}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                size="small"
                disabled={currentPage >= totalPages}
                onClick={() => setCurrentPage(prev => prev + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default MealsPage;