/**
 * API service layer for communicating with the FastAPI backend.
 * Contains configured axios instance and all API call functions.
 */

import axios from 'axios';
import { logError, retryApiCall } from '../utils/errorHandler';

// Configure axios instance with base URL
// Create axios instance with base configuration
const api = axios.create({
  baseURL: 'http://localhost:8001',
  timeout: 30000, // Increased timeout for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add authentication token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('API Request:', config.method?.toUpperCase(), config.url, 'Token:', token ? 'Present' : 'None');
    return config;
  },
  (error) => {
    logError(error, 'API Request Interceptor');
    return Promise.reject(error);
  }
);

// Response interceptor to handle authentication errors and retries
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    logError(error, 'API Response', {
      url: originalRequest?.url,
      method: originalRequest?.method,
      status: error.response?.status
    });
    
    // Handle authentication errors
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Clear auth data
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // Redirect to login only if not already on auth pages
      const currentPath = window.location.pathname;
      if (currentPath !== '/login' && currentPath !== '/register') {
        window.location.href = '/login';
      }
    }
    
    // Handle rate limiting with exponential backoff
    if (error.response?.status === 429 && !originalRequest._retryCount) {
      originalRequest._retryCount = 0;
      
      const retryAfter = error.response.headers['retry-after'] || 1;
      await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      
      originalRequest._retryCount++;
      if (originalRequest._retryCount < 3) {
        return api(originalRequest);
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API calls
export const authAPI = {
  /**
   * Register a new user (legacy endpoint)
   * @param {Object} userData - User registration data
   * @param {string} userData.email - User email
   * @param {string} userData.password - User password
   * @param {string} userData.role - User role (student/employer)
   */
  register: (userData) => api.post('/api/auth/register', userData),

  /**
   * Register a new employer with organization details
   * @param {Object} employerData - Employer registration data
   * @param {string} employerData.full_name - Employer's full name
   * @param {string} employerData.organization_name - Organization name
   * @param {string} employerData.organization_email - Organization email
   * @param {string} employerData.phone_number - Phone number
   * @param {string} employerData.password - Password
   */
  registerEmployer: (employerData) => api.post('/api/auth/register/employer', employerData),

  /**
   * Register a new student with personal details
   * @param {Object} studentData - Student registration data
   * @param {string} studentData.email - Student email
   * @param {string} studentData.full_name - Student's full name
   * @param {string} studentData.phone_number - Phone number (optional)
   * @param {string} studentData.password - Password
   */
  registerStudent: (studentData) => api.post('/api/auth/register/student', studentData),

  /**
   * Login user with email and password
   * @param {Object} credentials - Login credentials
   * @param {string} credentials.username - User email (username)
   * @param {string} credentials.password - User password
   */
  login: (credentials) => {
    return api.post('/api/auth/login', {
      email: credentials.username, // Backend expects 'email' field
      password: credentials.password
    });
  },
};

// User API calls
export const userAPI = {
  /**
   * Get current user profile data
   * Requires authentication token
   */
  getProfile: () => api.get('/api/auth/me'),
};

// Resume API calls
export const resumeAPI = {
  /**
   * Upload resume file for AI parsing and analysis
   * @param {File} file - Resume file (.pdf or .docx)
   */
  uploadResume: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return api.post('/api/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * Get AI feedback for a specific resume
   * @param {string} resumeId - Resume ID
   */
  getFeedback: (resumeId) => api.get(`/api/resumes/${resumeId}/feedback`),
};

// Jobs API calls
export const jobsAPI = {
  /**
   * Get all available jobs (public endpoint)
   * @param {Object} params - Query parameters for filtering
   */
  getJobs: (params = {}) => api.get('/api/jobs', { params }),

  /**
   * Get specific job details by ID
   * @param {string} jobId - Job ID
   */
  getJobById: (jobId) => api.get(`/api/jobs/${jobId}`),

  /**
   * Create a new job posting (employer only)
   * @param {Object} jobData - Job posting data
   */
  createJob: (jobData) => api.post('/api/jobs', jobData),

  /**
   * Get candidates for a specific job (employer only)
   * @param {string} jobId - Job ID
   */
  getJobCandidates: (jobId) => api.get(`/api/jobs/${jobId}/candidates`),
};

// Export the configured axios instance as default
export default api;
