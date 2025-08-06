import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const HomePage = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="home-page">
      <div className="hero-section">
        <div className="container">
          <h1>AI-Powered Job Portal</h1>
          <p>Find your dream job with intelligent resume screening and career counseling</p>
          
          {!isAuthenticated ? (
            <div className="hero-actions">
              <Link to="/register" className="btn btn-primary">Get Started</Link>
              <Link to="/login" className="btn btn-secondary">Sign In</Link>
            </div>
          ) : (
            <div className="hero-actions">
              <Link 
                to={user?.role === 'employer' ? '/employer-dashboard' : '/dashboard'} 
                className="btn btn-primary"
              >
                Go to Dashboard
              </Link>
            </div>
          )}
        </div>
      </div>

      <div className="features-section">
        <div className="container">
          <h2>AI-Powered Features</h2>
          <div className="features-grid">
            <div className="feature-card">
              <h3>🤖 Smart Resume Screening</h3>
              <p>AI analyzes resumes and matches candidates with relevant job openings</p>
            </div>
            <div className="feature-card">
              <h3>💼 Intelligent Job Matching</h3>
              <p>Find the perfect job match based on your skills and experience</p>
            </div>
            <div className="feature-card">
              <h3>🎯 Career Counseling</h3>
              <p>Get personalized career guidance and skill recommendations</p>
            </div>
            <div className="feature-card">
              <h3>📊 Analytics Dashboard</h3>
              <p>Track your applications and get insights on your job search</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
