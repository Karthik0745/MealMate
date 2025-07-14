import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { ApiResponse, ApiError } from '../types';

class ApiService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
    
    this.api = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('mealmate_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle errors globally
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        // Handle 401 errors by clearing token and redirecting to login
        if (error.response?.status === 401) {
          localStorage.removeItem('mealmate_token');
          localStorage.removeItem('mealmate_user');
          window.location.href = '/login';
        }
        return Promise.reject(this.formatError(error));
      }
    );
  }

  private formatError(error: AxiosError): ApiError {
    if (error.response?.data) {
      const data = error.response.data as any;
      return {
        message: data.message || 'An error occurred',
        errors: data.errors,
        status: error.response.status,
      };
    }
    
    if (error.request) {
      return {
        message: 'Network error - please check your connection',
        status: 0,
      };
    }
    
    return {
      message: error.message || 'An unexpected error occurred',
    };
  }

  // Generic GET request
  async get<T>(url: string, params?: any): Promise<ApiResponse<T>> {
    const response = await this.api.get(url, { params });
    return response.data;
  }

  // Generic POST request
  async post<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.api.post(url, data);
    return response.data;
  }

  // Generic PUT request
  async put<T>(url: string, data?: any): Promise<ApiResponse<T>> {
    const response = await this.api.put(url, data);
    return response.data;
  }

  // Generic DELETE request
  async delete<T>(url: string): Promise<ApiResponse<T>> {
    const response = await this.api.delete(url);
    return response.data;
  }

  // File upload
  async upload<T>(url: string, formData: FormData): Promise<ApiResponse<T>> {
    const response = await this.api.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Download file
  async download(url: string): Promise<Blob> {
    const response = await this.api.get(url, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Set auth token
  setToken(token: string): void {
    localStorage.setItem('mealmate_token', token);
  }

  // Clear auth token
  clearToken(): void {
    localStorage.removeItem('mealmate_token');
    localStorage.removeItem('mealmate_user');
  }

  // Get base URL for file URLs
  getFileUrl(path: string): string {
    return `${this.baseURL}${path}`;
  }
}

// Create and export singleton instance
export const apiService = new ApiService();
export default apiService;