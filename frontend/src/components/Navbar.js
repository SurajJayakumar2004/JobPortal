/**
 * Navigation bar component that provides site-wide navigation
 * and authentication-aware menu items.
 */

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();

  /**
   * Handle user logout
   */
  const handleLogout = () => {
    logout();
    navigate('/');
  };

  /**
   * Get the appropriate home path based on user role
   */
  const getHomePath = () => {
    if (isAuthenticated && user?.role === 'employer') {
      return '/employer';
    }
    return '/';
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        {/* Brand/Logo */}
        <Link to={getHomePath()} className="nav-brand">
          🚀 AI Job Portal
        </Link>

        {/* Navigation Links */}
        <div className="nav-links">
          {/* Show Home link only for non-employers or unauthenticated users */}
          {(!isAuthenticated || user?.role !== 'employer') && (
            <Link to="/" className="nav-link">Home</Link>
          )}
          
          {isAuthenticated ? (
            // Authenticated user menu
            <>
              {user?.role === 'employer' ? (
                <Link to="/employer" className="nav-link">Employer Dashboard</Link>
              ) : (
                <Link to="/dashboard" className="nav-link">Dashboard</Link>
              )}
              <span className="nav-user">Welcome, {user?.email}</span>
              <button onClick={handleLogout} className="nav-link nav-button">
                Logout
              </button>
            </>
          ) : (
            // Guest user menu
            <>
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="nav-link nav-cta">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
