import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/auth';
import { ProfileFormData, ActivityLevel } from '../types';
import Button from '../components/common/Button';
import Input from '../components/common/Input';
import LoadingSpinner from '../components/common/LoadingSpinner';
import toast from 'react-hot-toast';

const ProfilePage: React.FC = () => {
  const { user, updateUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setValue
  } = useForm<ProfileFormData>();

  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    formState: { errors: passwordErrors },
    reset: resetPassword,
    watch
  } = useForm<{
    current_password: string;
    new_password: string;
    confirm_password: string;
  }>();

  const newPassword = watch('new_password');

  useEffect(() => {
    if (user) {
      // Pre-fill form with user data
      setValue('first_name', user.first_name);
      setValue('last_name', user.last_name);
      setValue('email', user.email);
      setValue('age', user.age || undefined);
      setValue('weight', user.weight || undefined);
      setValue('height', user.height || undefined);
      setValue('activity_level', user.activity_level);
      setValue('daily_calorie_goal', user.daily_calorie_goal);
    }
  }, [user, setValue]);

  const onSubmit = async (data: ProfileFormData) => {
    try {
      setLoading(true);
      const updatedUser = await authService.updateProfile(data);
      updateUser(updatedUser);
      toast.success('Profile updated successfully');
    } catch (error: any) {
      toast.error(error.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const onPasswordSubmit = async (data: {
    current_password: string;
    new_password: string;
    confirm_password: string;
  }) => {
    try {
      setLoading(true);
      await authService.changePassword(data.current_password, data.new_password);
      toast.success('Password changed successfully');
      resetPassword();
      setShowPasswordForm(false);
    } catch (error: any) {
      toast.error(error.message || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const calculateBMI = (weight?: number, height?: number) => {
    if (!weight || !height) return null;
    const heightInM = height / 100;
    return (weight / (heightInM * heightInM)).toFixed(1);
  };

  const getBMICategory = (bmi: number) => {
    if (bmi < 18.5) return { text: 'Underweight', color: 'text-blue-600' };
    if (bmi < 25) return { text: 'Normal weight', color: 'text-green-600' };
    if (bmi < 30) return { text: 'Overweight', color: 'text-yellow-600' };
    return { text: 'Obese', color: 'text-red-600' };
  };

  const handleDeleteAccount = async () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      try {
        await authService.deleteAccount();
        toast.success('Account deleted successfully');
      } catch (error: any) {
        toast.error(error.message || 'Failed to delete account');
      }
    }
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  const bmi = calculateBMI(user.weight, user.height);
  const bmiCategory = bmi ? getBMICategory(Number(bmi)) : null;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
        <p className="text-gray-600">Manage your account information and preferences</p>
      </div>

      {/* Profile Overview */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="flex items-center space-x-6">
          <div className="w-20 h-20 bg-primary-600 rounded-full flex items-center justify-center">
            <span className="text-white text-2xl font-bold">
              {user.first_name.charAt(0)}{user.last_name.charAt(0)}
            </span>
          </div>
          
          <div className="flex-1">
            <h2 className="text-xl font-semibold text-gray-900">
              {user.first_name} {user.last_name}
            </h2>
            <p className="text-gray-600">{user.email}</p>
            <p className="text-sm text-gray-500">
              Member since {new Date(user.created_at).toLocaleDateString()}
            </p>
          </div>

          {user.is_admin && (
            <div className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
              Admin
            </div>
          )}
        </div>

        {/* Health Stats */}
        {(user.age || user.weight || user.height) && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Health Overview</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {user.age && (
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{user.age}</div>
                  <div className="text-sm text-gray-500">Years old</div>
                </div>
              )}
              
              {user.weight && (
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{user.weight}</div>
                  <div className="text-sm text-gray-500">kg</div>
                </div>
              )}
              
              {user.height && (
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{user.height}</div>
                  <div className="text-sm text-gray-500">cm</div>
                </div>
              )}
              
              {bmi && (
                <div className="text-center">
                  <div className={`text-2xl font-bold ${bmiCategory?.color}`}>{bmi}</div>
                  <div className="text-sm text-gray-500">BMI - {bmiCategory?.text}</div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Profile Form */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Personal Information</h3>
        
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              {...register('first_name', { required: 'First name is required' })}
              label="First Name"
              error={errors.first_name?.message}
              fullWidth
            />

            <Input
              {...register('last_name', { required: 'Last name is required' })}
              label="Last Name"
              error={errors.last_name?.message}
              fullWidth
            />

            <Input
              {...register('email', {
                required: 'Email is required',
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: 'Invalid email address'
                }
              })}
              label="Email"
              type="email"
              error={errors.email?.message}
              fullWidth
            />

            <Input
              {...register('age', {
                min: { value: 13, message: 'You must be at least 13 years old' },
                max: { value: 120, message: 'Please enter a valid age' }
              })}
              label="Age"
              type="number"
              error={errors.age?.message}
              fullWidth
            />
          </div>

          {/* Physical Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              {...register('weight', {
                min: { value: 20, message: 'Please enter a valid weight' },
                max: { value: 300, message: 'Please enter a valid weight' }
              })}
              label="Weight (kg)"
              type="number"
              step="0.1"
              error={errors.weight?.message}
              fullWidth
            />

            <Input
              {...register('height', {
                min: { value: 100, message: 'Please enter a valid height' },
                max: { value: 250, message: 'Please enter a valid height' }
              })}
              label="Height (cm)"
              type="number"
              error={errors.height?.message}
              fullWidth
            />
          </div>

          {/* Nutrition Goals */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Activity Level
              </label>
              <select
                {...register('activity_level', { required: 'Activity level is required' })}
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 focus:outline-none"
              >
                <option value="sedentary">Sedentary (little/no exercise)</option>
                <option value="light">Light (light exercise 1-3 days/week)</option>
                <option value="moderate">Moderate (moderate exercise 3-5 days/week)</option>
                <option value="active">Active (hard exercise 6-7 days/week)</option>
                <option value="very_active">Very Active (very hard exercise, physical job)</option>
              </select>
              {errors.activity_level && (
                <p className="mt-1 text-sm text-danger-600">{errors.activity_level.message}</p>
              )}
            </div>

            <Input
              {...register('daily_calorie_goal', {
                required: 'Daily calorie goal is required',
                min: { value: 1000, message: 'Daily calorie goal should be at least 1000' },
                max: { value: 5000, message: 'Daily calorie goal should not exceed 5000' }
              })}
              label="Daily Calorie Goal"
              type="number"
              error={errors.daily_calorie_goal?.message}
              fullWidth
            />
          </div>

          <div className="flex justify-end">
            <Button type="submit" loading={loading}>
              Update Profile
            </Button>
          </div>
        </form>
      </div>

      {/* Security Settings */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Security Settings</h3>
        
        {!showPasswordForm ? (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-medium text-gray-900">Password</h4>
                <p className="text-sm text-gray-500">Last changed: Unknown</p>
              </div>
              <Button variant="outline" onClick={() => setShowPasswordForm(true)}>
                Change Password
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handlePasswordSubmit(onPasswordSubmit)} className="space-y-4">
            <Input
              {...registerPassword('current_password', { required: 'Current password is required' })}
              label="Current Password"
              type="password"
              error={passwordErrors.current_password?.message}
              fullWidth
            />

            <Input
              {...registerPassword('new_password', {
                required: 'New password is required',
                minLength: { value: 6, message: 'Password must be at least 6 characters' }
              })}
              label="New Password"
              type="password"
              error={passwordErrors.new_password?.message}
              fullWidth
            />

            <Input
              {...registerPassword('confirm_password', {
                required: 'Please confirm your new password',
                validate: (value) => value === newPassword || 'Passwords do not match'
              })}
              label="Confirm New Password"
              type="password"
              error={passwordErrors.confirm_password?.message}
              fullWidth
            />

            <div className="flex justify-end space-x-3">
              <Button 
                type="button" 
                variant="outline" 
                onClick={() => {
                  setShowPasswordForm(false);
                  resetPassword();
                }}
              >
                Cancel
              </Button>
              <Button type="submit" loading={loading}>
                Change Password
              </Button>
            </div>
          </form>
        )}
      </div>

      {/* Danger Zone */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-red-200">
        <h3 className="text-lg font-semibold text-red-900 mb-4">Danger Zone</h3>
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-red-900">Delete Account</h4>
              <p className="text-sm text-red-700">
                Permanently delete your account and all associated data. This action cannot be undone.
              </p>
            </div>
            <Button variant="danger" onClick={handleDeleteAccount}>
              Delete Account
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;