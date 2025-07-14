import { apiService } from './api';
import { 
  AuthResponse, 
  User, 
  LoginFormData, 
  RegisterFormData, 
  ProfileFormData 
} from '../types';

class AuthService {
  // Login user
  async login(data: LoginFormData): Promise<AuthResponse> {
    const response = await apiService.post<AuthResponse>('/api/auth/login', data);
    
    if (response.success && response.data) {
      // Store token and user data
      apiService.setToken(response.data.access_token);
      localStorage.setItem('mealmate_user', JSON.stringify(response.data.user));
      return response.data;
    }
    
    throw new Error(response.message || 'Login failed');
  }

  // Register new user
  async register(data: RegisterFormData): Promise<AuthResponse> {
    const response = await apiService.post<AuthResponse>('/api/auth/register', data);
    
    if (response.success && response.data) {
      // Store token and user data
      apiService.setToken(response.data.access_token);
      localStorage.setItem('mealmate_user', JSON.stringify(response.data.user));
      return response.data;
    }
    
    throw new Error(response.message || 'Registration failed');
  }

  // Logout user
  logout(): void {
    apiService.clearToken();
  }

  // Get current user profile
  async getProfile(): Promise<User> {
    const response = await apiService.get<User>('/api/auth/profile');
    
    if (response.success && response.data) {
      // Update stored user data
      localStorage.setItem('mealmate_user', JSON.stringify(response.data));
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to get profile');
  }

  // Update user profile
  async updateProfile(data: ProfileFormData): Promise<User> {
    const response = await apiService.put<User>('/api/auth/profile', data);
    
    if (response.success && response.data) {
      // Update stored user data
      localStorage.setItem('mealmate_user', JSON.stringify(response.data));
      return response.data;
    }
    
    throw new Error(response.message || 'Failed to update profile');
  }

  // Change password
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    const response = await apiService.post('/api/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    });
    
    if (!response.success) {
      throw new Error(response.message || 'Failed to change password');
    }
  }

  // Delete account
  async deleteAccount(): Promise<void> {
    const response = await apiService.delete('/api/auth/delete-account');
    
    if (response.success) {
      this.logout();
    } else {
      throw new Error(response.message || 'Failed to delete account');
    }
  }

  // Get stored user data
  getCurrentUser(): User | null {
    const userData = localStorage.getItem('mealmate_user');
    return userData ? JSON.parse(userData) : null;
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = localStorage.getItem('mealmate_token');
    const user = this.getCurrentUser();
    return !!(token && user);
  }

  // Check if user is admin
  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.is_admin || false;
  }

  // Get stored token
  getToken(): string | null {
    return localStorage.getItem('mealmate_token');
  }
}

export const authService = new AuthService();
export default authService;