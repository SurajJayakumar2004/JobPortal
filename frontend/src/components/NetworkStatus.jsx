import React from 'react';
import { useNetworkStatus } from '../hooks/useNetworkStatus';

const NetworkStatus = () => {
  const { isOnline, isSlowConnection } = useNetworkStatus();

  if (isOnline && !isSlowConnection) {
    return null; // Don't show anything when connection is good
  }

  return (
    <div className={`fixed top-0 left-0 right-0 z-50 ${
      !isOnline ? 'bg-red-500' : 'bg-yellow-500'
    } text-white text-center py-2 px-4 text-sm`}>
      <div className="flex items-center justify-center space-x-2">
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          {!isOnline ? (
            // Offline icon
            <path fillRule="evenodd" d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.367zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z" clipRule="evenodd" />
          ) : (
            // Slow connection icon
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          )}
        </svg>
        <span>
          {!isOnline ? (
            'You are currently offline. Some features may not be available.'
          ) : (
            'Slow connection detected. Some features may load slowly.'
          )}
        </span>
      </div>
    </div>
  );
};

export default NetworkStatus;
