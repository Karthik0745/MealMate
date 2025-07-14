import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../contexts/AuthContext';
import { RegisterFormData, ActivityLevel } from '../types';
import Button from '../components/common/Button';
import Input from '../components/common/Input';

const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const { register: registerUser, isAuthenticated, isLoading } = useAuth();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
    watch
  } = useForm<RegisterFormData>();

  const password = watch('password');

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate]);

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setIsSubmitting(true);
      await registerUser(data);
      // Navigation will be handled by the useEffect above
    } catch (error: any) {
      // Set form errors if available
      if (error.errors) {
        Object.keys(error.errors).forEach((key) => {
          setError(key as keyof RegisterFormData, {
            type: 'server',
            message: error.errors[key][0]
          });
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto w-16 h-16 bg-primary-600 rounded-full flex items-center justify-center mb-4">
            <span className="text-white font-bold text-2xl">M</span>
          </div>
          <h2 className="text-3xl font-extrabold text-gray-900">
            Join MealMate
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Create your account and start tracking your nutrition journey
          </p>
        </div>

        {/* Registration Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)}>
          <div className="bg-white p-6 rounded-lg shadow space-y-6">
            {/* Account Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Account Information</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Input
                  {...register('first_name', {
                    required: 'First name is required'
                  })}
                  label="First Name"
                  placeholder="Enter your first name"
                  error={errors.first_name?.message}
                  fullWidth
                />

                <Input
                  {...register('last_name', {
                    required: 'Last name is required'
                  })}
                  label="Last Name"
                  placeholder="Enter your last name"
                  error={errors.last_name?.message}
                  fullWidth
                />

                <Input
                  {...register('username', {
                    required: 'Username is required',
                    minLength: {
                      value: 3,
                      message: 'Username must be at least 3 characters'
                    },
                    pattern: {
                      value: /^[a-zA-Z0-9_]+$/,
                      message: 'Username can only contain letters, numbers, and underscores'
                    }
                  })}
                  label="Username"
                  placeholder="Choose a username"
                  error={errors.username?.message}
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
                  placeholder="Enter your email"
                  error={errors.email?.message}
                  fullWidth
                />

                <Input
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 6,
                      message: 'Password must be at least 6 characters'
                    }
                  })}
                  label="Password"
                  type="password"
                  placeholder="Create a password"
                  error={errors.password?.message}
                  fullWidth
                />

                <Input
                  {...register('confirm_password', {
                    required: 'Please confirm your password',
                    validate: (value) => value === password || 'Passwords do not match'
                  })}
                  label="Confirm Password"
                  type="password"
                  placeholder="Confirm your password"
                  error={errors.confirm_password?.message}
                  fullWidth
                />
              </div>
            </div>

            {/* Optional Profile Information */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Profile Information
                <span className="text-sm font-normal text-gray-500 ml-2">(Optional)</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Input
                  {...register('age', {
                    min: {
                      value: 13,
                      message: 'You must be at least 13 years old'
                    },
                    max: {
                      value: 120,
                      message: 'Please enter a valid age'
                    }
                  })}
                  label="Age"
                  type="number"
                  placeholder="Your age"
                  error={errors.age?.message}
                  fullWidth
                />

                <Input
                  {...register('weight', {
                    min: {
                      value: 20,
                      message: 'Please enter a valid weight'
                    },
                    max: {
                      value: 300,
                      message: 'Please enter a valid weight'
                    }
                  })}
                  label="Weight (kg)"
                  type="number"
                  step="0.1"
                  placeholder="Your weight"
                  error={errors.weight?.message}
                  fullWidth
                />

                <Input
                  {...register('height', {
                    min: {
                      value: 100,
                      message: 'Please enter a valid height'
                    },
                    max: {
                      value: 250,
                      message: 'Please enter a valid height'
                    }
                  })}
                  label="Height (cm)"
                  type="number"
                  placeholder="Your height"
                  error={errors.height?.message}
                  fullWidth
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Activity Level
                  </label>
                  <select
                    {...register('activity_level')}
                    className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 focus:border-primary-500 focus:ring-2 focus:ring-primary-200 focus:outline-none"
                  >
                    <option value="sedentary">Sedentary (little/no exercise)</option>
                    <option value="light">Light (light exercise 1-3 days/week)</option>
                    <option value="moderate">Moderate (moderate exercise 3-5 days/week)</option>
                    <option value="active">Active (hard exercise 6-7 days/week)</option>
                    <option value="very_active">Very Active (very hard exercise, physical job)</option>
                  </select>
                </div>

                <Input
                  {...register('daily_calorie_goal', {
                    min: {
                      value: 1000,
                      message: 'Daily calorie goal should be at least 1000'
                    },
                    max: {
                      value: 5000,
                      message: 'Daily calorie goal should not exceed 5000'
                    }
                  })}
                  label="Daily Calorie Goal"
                  type="number"
                  placeholder="2000"
                  error={errors.daily_calorie_goal?.message}
                  fullWidth
                />
              </div>
            </div>
          </div>

          <Button
            type="submit"
            loading={isSubmitting}
            fullWidth
            size="large"
          >
            Create Account
          </Button>

          <div className="text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <Link
                to="/login"
                className="font-medium text-primary-600 hover:text-primary-500"
              >
                Sign in here
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RegisterPage;