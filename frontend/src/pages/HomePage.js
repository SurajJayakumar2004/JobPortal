/**
 * Homepage component that serves as the landing page.
 * Displays job listings and provides entry point to the application.
 * Automatically redirects employers to their dashboard.
 */

import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import JobList from '../components/JobList';

const HomePage = () => {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  // Redirect employers to their dashboard
  useEffect(() => {
    if (isAuthenticated && user?.role === 'employer') {
      navigate('/employer');
    }
  }, [isAuthenticated, user, navigate]);

  return (
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h1>AI-Powered Job Portal</h1>
            <p>
              Find your dream job with the help of artificial intelligence. 
              Get personalized resume feedback, smart job matching, and career guidance.
            </p>
            <div className="hero-actions">
              {isAuthenticated ? (
                // Show dashboard link for authenticated job seekers (employers are redirected)
                <Link to="/dashboard" className="btn btn-primary">
                  Go to Dashboard
                </Link>
              ) : (
                <>
                  <Link to="/register" className="btn btn-primary">
                    Get Started
                  </Link>
                  <Link to="/login" className="btn btn-secondary">
                    Sign In
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="container">
          <h2>Why Choose Our AI Job Portal?</h2>
          <div className="features-grid">
            <div className="feature">
              <h3>🤖 AI Resume Analysis</h3>
              <p>Get instant feedback on your resume with our AI-powered analysis engine.</p>
            </div>
            <div className="feature">
              <h3>🎯 Smart Job Matching</h3>
              <p>Find jobs that perfectly match your skills and career goals.</p>
            </div>
            <div className="feature">
              <h3>💼 Career Counseling</h3>
              <p>Receive personalized career guidance from our AI counselor.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Job Listings Section */}
      <section className="job-listings">
        <div className="container">
          <h2>Latest Job Opportunities</h2>
          <JobList />
        </div>
      </section>
    </div>
  );
};

export default HomePage;
