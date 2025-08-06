import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          Job Portal AI
        </Link>
        
        <div className="nav-menu">
          {!isAuthenticated ? (
            <div className="nav-links">
              <Link to="/login" className="nav-link">Login</Link>
              <Link to="/register" className="nav-link btn-primary">Register</Link>
            </div>
          ) : (
            <div className="nav-links">
              <span className="nav-user">Welcome, {user?.full_name}</span>
              <Link 
                to={user?.role === 'employer' ? '/employer-dashboard' : '/dashboard'} 
                className="nav-link"
              >
                Dashboard
              </Link>
              <button onClick={handleLogout} className="nav-link btn-secondary">
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
