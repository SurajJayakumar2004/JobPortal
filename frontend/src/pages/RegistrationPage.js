/**
 * User registration page with role-specific forms for creating new accounts.
 * Handles both employer and student registration with appropriate fields.
 */

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authAPI } from '../services/api';
import { getStatusErrorMessage } from '../utils/errorHandler';

const RegistrationPage = () => {
  const [formData, setFormData] = useState({
    // Common fields
    role: 'student', // Default role
    password: '',
    confirmPassword: '',
    
    // Student fields
    email: '',
    full_name: '',
    phone_number: '',
    
    // Employer fields
    employer_full_name: '',
    organization_name: '',
    organization_email: '',
    employer_phone_number: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  /**
   * Handle form input changes
   */
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear error when user starts typing
    if (error) setError('');
  };

  /**
   * Handle role selection change
   */
  const handleRoleChange = (e) => {
    const newRole = e.target.value;
    setFormData({
      ...formData,
      role: newRole,
      // Clear form data when switching roles
      email: '',
      full_name: '',
      phone_number: '',
      employer_full_name: '',
      organization_name: '',
      organization_email: '',
      employer_phone_number: '',
      password: '',
      confirmPassword: ''
    });
    setError('');
  };

  /**
   * Validate form data before submission
   */
  const validateForm = () => {
    if (!formData.password || !formData.confirmPassword) {
      setError('Password fields are required');
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }

    if (formData.password.length < 8) {
      setError('Password must be at least 8 characters long');
      return false;
    }

    if (formData.role === 'student') {
      if (!formData.email || !formData.full_name) {
        setError('Email and full name are required for students');
        return false;
      }
      
      // Basic email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.email)) {
        setError('Please enter a valid email address');
        return false;
      }
    } else if (formData.role === 'employer') {
      if (!formData.employer_full_name || !formData.organization_name || 
          !formData.organization_email || !formData.employer_phone_number) {
        setError('All employer fields are required');
        return false;
      }
      
      // Basic email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(formData.organization_email)) {
        setError('Please enter a valid organization email address');
        return false;
      }
      
      // Basic phone validation
      const phoneRegex = /^[\+]?[\d\s\-\(\)]+$/;
      if (!phoneRegex.test(formData.employer_phone_number)) {
        setError('Please enter a valid phone number');
        return false;
      }
    }

    return true;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setLoading(true);
    setError('');

    try {
      let response;
      
      if (formData.role === 'employer') {
        // Use employer-specific registration endpoint
        response = await authAPI.registerEmployer({
          full_name: formData.employer_full_name,
          organization_name: formData.organization_name,
          organization_email: formData.organization_email,
          phone_number: formData.employer_phone_number,
          password: formData.password
        });
      } else {
        // Use student registration endpoint
        response = await authAPI.registerStudent({
          email: formData.email,
          full_name: formData.full_name,
          phone_number: formData.phone_number || null,
          password: formData.password
        });
      }

      setSuccess(`${formData.role === 'employer' ? 'Employer' : 'Student'} registration successful! Please log in.`);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error) {
      console.error('Registration error:', error);
      setError(getStatusErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="auth-form">
        <h1>Create Your Account</h1>
        <p>Join our AI-powered job portal and accelerate your career</p>

        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <form onSubmit={handleSubmit}>
          {/* Role Selection */}
          <div className="form-group">
            <label htmlFor="role">I am a:</label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleRoleChange}
              className="form-select"
            >
              <option value="student">Student/Job Seeker</option>
              <option value="employer">Employer/Recruiter</option>
            </select>
          </div>

          {/* Student Fields */}
          {formData.role === 'student' && (
            <>
              <div className="form-group">
                <label htmlFor="full_name">Full Name *</label>
                <input
                  type="text"
                  id="full_name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  placeholder="Enter your full name"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="email">Email Address *</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="Enter your email address"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="phone_number">Phone Number (Optional)</label>
                <input
                  type="tel"
                  id="phone_number"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  placeholder="Enter your phone number"
                />
              </div>
            </>
          )}

          {/* Employer Fields */}
          {formData.role === 'employer' && (
            <>
              <div className="form-group">
                <label htmlFor="employer_full_name">Full Name *</label>
                <input
                  type="text"
                  id="employer_full_name"
                  name="employer_full_name"
                  value={formData.employer_full_name}
                  onChange={handleChange}
                  placeholder="Enter your full name"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="organization_name">Organization Name *</label>
                <input
                  type="text"
                  id="organization_name"
                  name="organization_name"
                  value={formData.organization_name}
                  onChange={handleChange}
                  placeholder="Enter your organization name"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="organization_email">Organization Email ID *</label>
                <input
                  type="email"
                  id="organization_email"
                  name="organization_email"
                  value={formData.organization_email}
                  onChange={handleChange}
                  placeholder="Enter your organization email"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="employer_phone_number">Phone Number *</label>
                <input
                  type="tel"
                  id="employer_phone_number"
                  name="employer_phone_number"
                  value={formData.employer_phone_number}
                  onChange={handleChange}
                  placeholder="Enter your phone number"
                  required
                />
              </div>
            </>
          )}

          {/* Common Password Fields */}
          <div className="form-group">
            <label htmlFor="password">Password *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Create a password (min. 8 characters)"
              required
              minLength={8}
            />
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">Confirm Password *</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="Confirm your password"
              required
              minLength={8}
            />
          </div>

          <button type="submit" disabled={loading} className="auth-button">
            {loading ? 'Creating Account...' : `Create ${formData.role === 'employer' ? 'Employer' : 'Student'} Account`}
          </button>
        </form>

        <div className="auth-links">
          <p>
            Already have an account? <Link to="/login">Sign in here</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegistrationPage;
