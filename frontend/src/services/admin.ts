import { apiService } from './api';
import { AdminStats, AdminUser, Category, PaginatedResponse } from '../types';

interface GetUsersParams {
  page?: number;
  per_page?: number;
  search?: string;
}

interface CreateCategoryData {
  name: string;
  color: string;
}

class AdminService {
  async getStats(): Promise<AdminStats> {
    const response = await apiService.get('/admin/stats');
    return response.data;
  }

  async getUsers(params: GetUsersParams = {}): Promise<PaginatedResponse<AdminUser>> {
    const response = await apiService.get('/admin/users', {
      params: {
        page: params.page || 1,
        per_page: params.per_page || 10,
        search: params.search
      }
    });
    return response.data;
  }

  async toggleUserStatus(userId: number, isActive: boolean): Promise<{ message: string }> {
    const response = await apiService.put(`/admin/users/${userId}/status`, {
      is_active: isActive
    });
    return response.data;
  }

  async deleteUser(userId: number): Promise<{ message: string }> {
    const response = await apiService.delete(`/admin/users/${userId}`);
    return response.data;
  }

  async getCategories(): Promise<Category[]> {
    const response = await apiService.get('/admin/categories');
    return response.data;
  }

  async createCategory(data: CreateCategoryData): Promise<Category> {
    const response = await apiService.post('/admin/categories', data);
    return response.data;
  }

  async updateCategory(categoryId: number, data: Partial<CreateCategoryData>): Promise<Category> {
    const response = await apiService.put(`/admin/categories/${categoryId}`, data);
    return response.data;
  }

  async deleteCategory(categoryId: number): Promise<{ message: string }> {
    const response = await apiService.delete(`/admin/categories/${categoryId}`);
    return response.data;
  }

  async getUserDetails(userId: number): Promise<AdminUser> {
    const response = await apiService.get(`/admin/users/${userId}`);
    return response.data;
  }

  async getUserMeals(userId: number, params: { page?: number; per_page?: number } = {}) {
    const response = await apiService.get(`/admin/users/${userId}/meals`, {
      params: {
        page: params.page || 1,
        per_page: params.per_page || 10
      }
    });
    return response.data;
  }

  async getSystemHealth(): Promise<{
    status: 'healthy' | 'warning' | 'error';
    database: boolean;
    api: boolean;
    uptime: number;
  }> {
    const response = await apiService.get('/admin/health');
    return response.data;
  }

  async exportUserData(format: 'csv' | 'json' = 'csv'): Promise<Blob> {
    const response = await apiService.get('/admin/export/users', {
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  }

  async exportMealData(format: 'csv' | 'json' = 'csv'): Promise<Blob> {
    const response = await apiService.get('/admin/export/meals', {
      params: { format },
      responseType: 'blob'
    });
    return response.data;
  }

  async getActivityLogs(params: { 
    page?: number; 
    per_page?: number; 
    user_id?: number; 
    action?: string;
    date_from?: string;
    date_to?: string;
  } = {}) {
    const response = await apiService.get('/admin/activity-logs', { params });
    return response.data;
  }

  async bulkDeleteUsers(userIds: number[]): Promise<{ deleted_count: number; message: string }> {
    const response = await apiService.post('/admin/users/bulk-delete', {
      user_ids: userIds
    });
    return response.data;
  }

  async sendSystemNotification(data: {
    title: string;
    message: string;
    type: 'info' | 'warning' | 'error' | 'success';
    target: 'all' | 'active' | number[];
  }): Promise<{ message: string }> {
    const response = await apiService.post('/admin/notifications', data);
    return response.data;
  }
}

export const adminService = new AdminService();