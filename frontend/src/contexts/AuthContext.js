/**
 * Authentication context for managing user authentication state
 * throughout the application.
 */

import React, { createContext, useContext, useState, useEffect } from 'react';
import { userAPI } from '../services/api';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check if user is authenticated on app load
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token and get user profile
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, []);

  /**
   * Fetch user profile data from API
   */
  const fetchUserProfile = async () => {
    try {
      const response = await userAPI.getProfile();
      const { data } = response.data; // Backend wraps response in { success: true, data: {...} }
      setUser(data.user);
      setIsAuthenticated(true);
      
      // Check if we need to redirect employer on app load
      if (data.user?.role === 'employer' && window.location.pathname === '/') {
        window.location.href = '/employer';
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      localStorage.removeItem('token');
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Login user and store authentication token
   * @param {string} token - JWT token from login response
   * @param {Object} userData - User data from login response
   */
  const login = (token, userData) => {
    localStorage.setItem('token', token);
    setUser(userData);
    setIsAuthenticated(true);
  };

  /**
   * Check if user should be redirected based on their role
   * @param {Object} userData - User data
   * @returns {string} - Redirect path based on user role
   */
  const getDefaultRedirectPath = (userData) => {
    if (userData?.role === 'employer') {
      return '/employer';
    }
    return '/dashboard';
  };

  /**
   * Logout user and clear authentication data
   */
  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    fetchUserProfile,
    getDefaultRedirectPath,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
