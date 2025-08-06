/**
 * API service for employer-specific operations.
 * Handles all HTTP requests to employer endpoints.
 */

const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Get authorization headers with current token
 */
const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

/**
 * Generic API request handler with error handling
 */
const apiRequest = async (url, options = {}) => {
  try {
    const response = await fetch(`${BASE_URL}${url}`, {
      headers: getAuthHeaders(),
      ...options
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API request failed for ${url}:`, error);
    throw error;
  }
};

/**
 * Employer Profile API methods
 */
export const employerProfileAPI = {
  /**
   * Get employer profile
   */
  getProfile: async () => {
    return apiRequest('/employers/profile');
  },

  /**
   * Update employer profile
   */
  updateProfile: async (profileData) => {
    return apiRequest('/employers/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    });
  },

  /**
   * Upload company logo
   */
  uploadLogo: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = localStorage.getItem('token');
    const response = await fetch(`${BASE_URL}/employers/upload-logo`, {
      method: 'POST',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` })
      },
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || errorData.message || `HTTP ${response.status}`);
    }

    return await response.json();
  }
};

/**
 * Employer Dashboard API methods
 */
export const employerDashboardAPI = {
  /**
   * Get dashboard overview data
   */
  getDashboard: async () => {
    return apiRequest('/employers/dashboard');
  },

  /**
   * Get employer analytics
   */
  getAnalytics: async (period = '30d') => {
    return apiRequest(`/employers/analytics?period=${period}`);
  }
};

/**
 * Employer Jobs API methods
 */
export const employerJobsAPI = {
  /**
   * Get all jobs for the employer
   */
  getJobs: async (params = {}) => {
    const queryParams = new URLSearchParams();
    
    if (params.status) queryParams.append('status', params.status);
    if (params.skip) queryParams.append('skip', params.skip);
    if (params.limit) queryParams.append('limit', params.limit);
    
    const url = `/employers/jobs${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return apiRequest(url);
  },

  /**
   * Create new job posting
   */
  createJob: async (jobData) => {
    return apiRequest('/jobs', {
      method: 'POST',
      body: JSON.stringify(jobData)
    });
  },

  /**
   * Update existing job
   */
  updateJob: async (jobId, jobData) => {
    return apiRequest(`/jobs/${jobId}`, {
      method: 'PUT',
      body: JSON.stringify(jobData)
    });
  },

  /**
   * Delete job posting
   */
  deleteJob: async (jobId) => {
    return apiRequest(`/jobs/${jobId}`, {
      method: 'DELETE'
    });
  },

  /**
   * Get job details
   */
  getJobDetails: async (jobId) => {
    return apiRequest(`/jobs/${jobId}`);
  },

  /**
   * Get candidates for a job
   */
  getJobCandidates: async (jobId) => {
    return apiRequest(`/jobs/${jobId}/candidates`);
  }
};

/**
 * General Jobs API methods (for listing public jobs)
 */
export const jobsAPI = {
  /**
   * Get all public job listings
   */
  getJobs: async (params = {}) => {
    const queryParams = new URLSearchParams();
    
    if (params.skip) queryParams.append('skip', params.skip);
    if (params.limit) queryParams.append('limit', params.limit);
    if (params.location) queryParams.append('location', params.location);
    if (params.experience_level) queryParams.append('experience_level', params.experience_level);
    if (params.employment_type) queryParams.append('employment_type', params.employment_type);
    if (params.skills) queryParams.append('skills', params.skills);
    
    const url = `/jobs${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return apiRequest(url);
  }
};

/**
 * Industry and dropdown data
 */
export const INDUSTRIES = [
  'Technology',
  'Healthcare',
  'Finance',
  'Education',
  'Manufacturing',
  'Retail',
  'Consulting',
  'Real Estate',
  'Media & Entertainment',
  'Transportation',
  'Energy',
  'Government',
  'Non-profit',
  'Other'
];

export const COMPANY_SIZES = [
  '1-10 employees',
  '11-50 employees',
  '51-200 employees',
  '201-1000 employees',
  '1001-5000 employees',
  '5000+ employees'
];

export const EMPLOYMENT_TYPES = [
  'Full-time',
  'Part-time',
  'Contract',
  'Temporary',
  'Internship',
  'Remote'
];

export const EXPERIENCE_LEVELS = [
  'Entry Level',
  'Mid Level',
  'Senior Level',
  'Executive Level'
];

export const JOB_STATUSES = [
  'open',
  'closed',
  'draft',
  'paused'
];

/**
 * Utility functions
 */
export const formatSalaryRange = (min, max) => {
  if (!min || !max) return 'Salary not specified';
  return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
};

export const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

export const formatDateTime = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const getStatusColor = (status) => {
  const colors = {
    'open': 'bg-green-100 text-green-800',
    'closed': 'bg-red-100 text-red-800',
    'draft': 'bg-gray-100 text-gray-800',
    'paused': 'bg-yellow-100 text-yellow-800'
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
};

const employerAPIExports = {
  employerProfileAPI,
  employerDashboardAPI,
  employerJobsAPI,
  jobsAPI,
  INDUSTRIES,
  COMPANY_SIZES,
  EMPLOYMENT_TYPES,
  EXPERIENCE_LEVELS,
  JOB_STATUSES,
  formatSalaryRange,
  formatDate,
  formatDateTime,
  getStatusColor
};

export default employerAPIExports;
