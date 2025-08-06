import { useState, useEffect } from 'react';

/**
 * Custom hook to track network status and connection quality
 * @returns {Object} Network status information
 */
export const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [connectionSpeed, setConnectionSpeed] = useState('unknown');
  const [isSlowConnection, setIsSlowConnection] = useState(false);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Monitor connection speed if supported
    if ('connection' in navigator) {
      const connection = navigator.connection;
      
      const updateConnectionInfo = () => {
        setConnectionSpeed(connection.effectiveType || 'unknown');
        setIsSlowConnection(connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g');
      };

      updateConnectionInfo();
      connection.addEventListener('change', updateConnectionInfo);

      return () => {
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
        connection.removeEventListener('change', updateConnectionInfo);
      };
    }

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return {
    isOnline,
    connectionSpeed,
    isSlowConnection
  };
};

/**
 * Custom hook for retrying failed operations
 * @param {Function} operation - The operation to retry
 * @param {number} maxRetries - Maximum number of retries
 * @param {number} delay - Delay between retries
 * @returns {Object} Retry state and methods
 */
export const useRetry = (operation, maxRetries = 3, delay = 1000) => {
  const [isRetrying, setIsRetrying] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [lastError, setLastError] = useState(null);

  const retry = async () => {
    if (retryCount >= maxRetries) {
      return Promise.reject(new Error('Maximum retry attempts exceeded'));
    }

    setIsRetrying(true);
    setRetryCount(prev => prev + 1);

    try {
      await new Promise(resolve => setTimeout(resolve, delay * retryCount));
      const result = await operation();
      setIsRetrying(false);
      setRetryCount(0);
      setLastError(null);
      return result;
    } catch (error) {
      setLastError(error);
      setIsRetrying(false);
      throw error;
    }
  };

  const reset = () => {
    setRetryCount(0);
    setLastError(null);
    setIsRetrying(false);
  };

  return {
    retry,
    reset,
    isRetrying,
    retryCount,
    canRetry: retryCount < maxRetries,
    lastError
  };
};

/**
 * Custom hook for handling loading states with error recovery
 * @param {Function} asyncOperation - The async operation to manage
 * @returns {Object} Loading state and methods
 */
export const useAsyncOperation = (asyncOperation) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const execute = async (...args) => {
    try {
      setLoading(true);
      setError(null);
      const result = await asyncOperation(...args);
      setData(result);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setLoading(false);
    setError(null);
    setData(null);
  };

  return {
    execute,
    reset,
    loading,
    error,
    data
  };
};
