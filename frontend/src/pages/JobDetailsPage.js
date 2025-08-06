/**
 * Job details page that displays comprehensive information about a specific job.
 * Retrieves job ID from URL parameters and fetches detailed job data.
 */

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { jobsAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const JobDetailsPage = () => {
  const { id } = useParams(); // Get job ID from URL
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  /**
   * Fetch job details on component mount
   */
  useEffect(() => {
    if (id) {
      fetchJobDetails();
    }
  }, [id]);

  /**
   * Fetch detailed job information from API
   */
  const fetchJobDetails = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await jobsAPI.getJobById(id);
      setJob(response.data);
    } catch (error) {
      console.error('Failed to fetch job details:', error);
      if (error.response?.status === 404) {
        setError('Job not found. It may have been removed or the link is invalid.');
      } else {
        setError('Failed to load job details. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle job application (placeholder for future implementation)
   */
  const handleApply = () => {
    if (!isAuthenticated) {
      // Redirect to login with return URL
      navigate(`/login?returnTo=/jobs/${id}`);
      return;
    }
    
    // TODO: Implement job application logic
    alert('Application feature coming soon!');
  };

  /**
   * Format date for display
   */
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  /**
   * Format salary range for display
   */
  const formatSalary = (min, max) => {
    if (!min && !max) return 'Salary not specified';
    if (min && max) return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
    if (min) return `From $${min.toLocaleString()}`;
    if (max) return `Up to $${max.toLocaleString()}`;
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <p>Loading job details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="error-page">
          <h1>Error Loading Job</h1>
          <p>{error}</p>
          <div className="error-actions">
            <button onClick={fetchJobDetails} className="btn btn-primary">
              Try Again
            </button>
            <Link to="/" className="btn btn-secondary">
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="container">
        <div className="error-page">
          <h1>Job Not Found</h1>
          <p>The job you're looking for doesn't exist.</p>
          <Link to="/" className="btn btn-primary">
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="job-details">
        {/* Navigation */}
        <div className="job-nav">
          <button onClick={() => navigate(-1)} className="btn btn-secondary">
            ← Back
          </button>
        </div>

        {/* Job Header */}
        <div className="job-header">
          <div className="job-title-section">
            <h1>{job.title}</h1>
            <div className="job-company">
              <h2>{job.company || 'Company Name'}</h2>
            </div>
          </div>
          
          <div className="job-actions">
            <button onClick={handleApply} className="btn btn-primary btn-large">
              {isAuthenticated ? 'Apply Now' : 'Sign In to Apply'}
            </button>
          </div>
        </div>

        {/* Job Quick Info */}
        <div className="job-quick-info">
          <div className="info-grid">
            {job.location && (
              <div className="info-item">
                <span className="info-label">📍 Location</span>
                <span className="info-value">{job.location}</span>
              </div>
            )}
            
            {job.employment_type && (
              <div className="info-item">
                <span className="info-label">💼 Type</span>
                <span className="info-value">{job.employment_type}</span>
              </div>
            )}
            
            {job.experience_level && (
              <div className="info-item">
                <span className="info-label">👤 Experience</span>
                <span className="info-value">{job.experience_level}</span>
              </div>
            )}
            
            <div className="info-item">
              <span className="info-label">📅 Posted</span>
              <span className="info-value">{formatDate(job.created_at)}</span>
            </div>

            {(job.salary_min || job.salary_max) && (
              <div className="info-item">
                <span className="info-label">💰 Salary</span>
                <span className="info-value">
                  {formatSalary(job.salary_min, job.salary_max)}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Job Content */}
        <div className="job-content">
          {/* Job Description */}
          <section className="job-section">
            <h3>Job Description</h3>
            <div className="job-description">
              {job.description ? (
                <div dangerouslySetInnerHTML={{ 
                  __html: job.description.replace(/\n/g, '<br>') 
                }} />
              ) : (
                <p>No description available for this position.</p>
              )}
            </div>
          </section>

          {/* Required Skills */}
          {job.required_skills && job.required_skills.length > 0 && (
            <section className="job-section">
              <h3>Required Skills</h3>
              <div className="skills-container">
                {job.required_skills.map((skill, index) => (
                  <span key={index} className="skill-tag">{skill}</span>
                ))}
              </div>
            </section>
          )}

          {/* Requirements */}
          {job.requirements && (
            <section className="job-section">
              <h3>Requirements</h3>
              <div className="requirements">
                <div dangerouslySetInnerHTML={{ 
                  __html: job.requirements.replace(/\n/g, '<br>') 
                }} />
              </div>
            </section>
          )}

          {/* Benefits */}
          {job.benefits && (
            <section className="job-section">
              <h3>Benefits</h3>
              <div className="benefits">
                <div dangerouslySetInnerHTML={{ 
                  __html: job.benefits.replace(/\n/g, '<br>') 
                }} />
              </div>
            </section>
          )}

          {/* Company Information */}
          {job.company_info && (
            <section className="job-section">
              <h3>About the Company</h3>
              <div className="company-info">
                <div dangerouslySetInnerHTML={{ 
                  __html: job.company_info.replace(/\n/g, '<br>') 
                }} />
              </div>
            </section>
          )}
        </div>

        {/* Apply Section */}
        <div className="job-apply-section">
          <div className="apply-card">
            <h3>Ready to Apply?</h3>
            <p>Join thousands of professionals who found their dream job through our AI-powered platform.</p>
            <button onClick={handleApply} className="btn btn-primary btn-large">
              {isAuthenticated ? 'Apply for This Position' : 'Sign In to Apply'}
            </button>
            {!isAuthenticated && (
              <p className="apply-note">
                Don't have an account? <Link to="/register">Create one here</Link>
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetailsPage;
