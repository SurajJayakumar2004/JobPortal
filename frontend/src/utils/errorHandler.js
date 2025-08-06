/**
 * Utility functions for handling API errors consistently.
 */

/**
 * Parse API error response into a user-friendly string message
 * @param {Object} error - Axios error object
 * @param {string} defaultMessage - Default error message if parsing fails
 * @returns {string} - Parsed error message
 */
export const parseErrorMessage = (error, defaultMessage = 'An error occurred. Please try again.') => {
  // Handle network errors
  if (!error.response) {
    if (error.code === 'ECONNABORTED') {
      return 'Request timed out. Please check your connection and try again.';
    }
    if (error.code === 'ERR_NETWORK') {
      return 'Network error. Please check your internet connection.';
    }
    if (error.message === 'Network Error') {
      return 'Unable to connect to server. Please try again later.';
    }
    return 'Connection error. Please check your internet connection.';
  }

  const errorData = error.response.data;

  // Handle FastAPI validation errors (array of error objects)
  if (Array.isArray(errorData.detail)) {
    return errorData.detail
      .map(err => {
        if (typeof err === 'object' && err.msg) {
          return err.msg;
        }
        if (typeof err === 'string') {
          return err;
        }
        return 'Validation error';
      })
      .join(', ');
  }

  // Handle single string error messages
  if (typeof errorData.detail === 'string') {
    return errorData.detail;
  }

  if (typeof errorData.message === 'string') {
    return errorData.message;
  }

  if (typeof errorData === 'string') {
    return errorData;
  }

  return defaultMessage;
};

/**
 * Handle common HTTP status codes with appropriate messages
 * @param {Object} error - Axios error object
 * @returns {string} - Status-specific error message
 */
export const getStatusErrorMessage = (error) => {
  // Handle network errors first
  if (!error.response) {
    return parseErrorMessage(error);
  }

  const status = error.response?.status;

  switch (status) {
    case 400:
      return parseErrorMessage(error, 'Invalid request. Please check your input.');
    case 401:
      return 'Authentication failed. Please log in again.';
    case 403:
      return 'You do not have permission to perform this action.';
    case 404:
      return 'The requested resource was not found.';
    case 409:
      return parseErrorMessage(error, 'A conflict occurred. This resource may already exist.');
    case 422:
      return parseErrorMessage(error, 'Invalid data provided. Please check your input.');
    case 429:
      return 'Too many requests. Please try again later.';
    case 500:
      return 'Server error. Please try again later.';
    case 502:
      return 'Bad gateway. The server is temporarily unavailable.';
    case 503:
      return 'Service unavailable. Please try again later.';
    case 504:
      return 'Gateway timeout. The request took too long to process.';
    default:
      return parseErrorMessage(error);
  }
};

/**
 * Enhanced error logger for debugging and monitoring
 * @param {Object} error - Error object
 * @param {string} context - Context where error occurred
 * @param {Object} additionalData - Additional data to log
 */
export const logError = (error, context = 'Unknown', additionalData = {}) => {
  const errorDetails = {
    context,
    timestamp: new Date().toISOString(),
    message: error.message,
    stack: error.stack,
    response: error.response ? {
      status: error.response.status,
      statusText: error.response.statusText,
      data: error.response.data
    } : null,
    request: error.config ? {
      url: error.config.url,
      method: error.config.method,
      data: error.config.data
    } : null,
    ...additionalData
  };

  console.group(`🚨 Error in ${context}`);
  console.error('Error details:', errorDetails);
  console.groupEnd();

  // In production, you might want to send this to an error monitoring service
  // like Sentry, LogRocket, or your own logging endpoint
};

/**
 * Retry mechanism for failed requests
 * @param {Function} apiCall - The API call function to retry
 * @param {number} maxRetries - Maximum number of retries
 * @param {number} delay - Delay between retries in milliseconds
 * @returns {Promise} - Promise that resolves with the successful response
 */
export const retryApiCall = async (apiCall, maxRetries = 3, delay = 1000) => {
  let lastError;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await apiCall();
    } catch (error) {
      lastError = error;
      
      // Don't retry on client errors (4xx) except 408 (timeout)
      if (error.response?.status >= 400 && error.response?.status < 500 && error.response?.status !== 408) {
        throw error;
      }

      if (attempt < maxRetries) {
        console.warn(`API call failed (attempt ${attempt}/${maxRetries}). Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
        delay *= 2; // Exponential backoff
      }
    }
  }

  throw lastError;
};

/**
 * Check if error is recoverable (user can retry)
 * @param {Object} error - Error object
 * @returns {boolean} - Whether the error is recoverable
 */
export const isRecoverableError = (error) => {
  if (!error.response) {
    return true; // Network errors are usually recoverable
  }

  const status = error.response.status;
  
  // Server errors and timeouts are recoverable
  if (status >= 500 || status === 408 || status === 429) {
    return true;
  }

  return false;
};

/**
 * Create a standardized error boundary component helper
 * @param {string} componentName - Name of the component for error tracking
 * @returns {Object} - Error boundary state and methods
 */
export const createErrorBoundary = (componentName) => {
  return {
    getDerivedStateFromError: (error) => ({
      hasError: true,
      error: error,
      errorInfo: {
        componentName,
        timestamp: new Date().toISOString()
      }
    }),
    
    componentDidCatch: (error, errorInfo) => {
      logError(error, `Error Boundary: ${componentName}`, {
        errorInfo,
        componentStack: errorInfo.componentStack
      });
    }
  };
};
