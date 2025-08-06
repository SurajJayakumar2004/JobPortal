/**
 * Job listings component that fetches and displays available jobs.
 * Provides filtering and navigation to detailed job views.
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { jobsAPI } from '../services/api';
import { getStatusErrorMessage } from '../utils/errorHandler';

const JobList = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    search: '',
    location: '',
    experience_level: '',
    employment_type: '',
  });

  /**
   * Fetch jobs from API on component mount and when filters change
   */
  useEffect(() => {
    fetchJobs();
  }, [filters]);

  /**
   * Fetch jobs from the backend API
   */
  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Build query parameters from filters
      const params = {};
      Object.keys(filters).forEach(key => {
        if (filters[key]) {
          params[key] = filters[key];
        }
      });

      const response = await jobsAPI.getJobs(params);
      setJobs(response.data || []);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
      setError(getStatusErrorMessage(error, 'Failed to load jobs. Please try again.'));
    } finally {
      setLoading(false);
    }
  };

  /**
   * Handle filter changes
   */
  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
    });
  };

  /**
   * Clear all filters
   */
  const clearFilters = () => {
    setFilters({
      search: '',
      location: '',
      experience_level: '',
      employment_type: '',
    });
  };

  /**
   * Format date for display
   */
  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="job-list">
        <div className="loading">
          <p>Loading job opportunities...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="job-list">
        <div className="error-message">
          {error}
          <button onClick={fetchJobs} className="btn btn-secondary">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="job-list">
      {/* Job Filters */}
      <div className="job-filters">
        <h3>Filter Jobs</h3>
        <div className="filters-grid">
          <div className="filter-group">
            <input
              type="text"
              name="search"
              placeholder="Search jobs..."
              value={filters.search}
              onChange={handleFilterChange}
              className="filter-input"
            />
          </div>

          <div className="filter-group">
            <input
              type="text"
              name="location"
              placeholder="Location"
              value={filters.location}
              onChange={handleFilterChange}
              className="filter-input"
            />
          </div>

          <div className="filter-group">
            <select
              name="experience_level"
              value={filters.experience_level}
              onChange={handleFilterChange}
              className="filter-select"
            >
              <option value="">Experience Level</option>
              <option value="entry">Entry Level</option>
              <option value="mid">Mid Level</option>
              <option value="senior">Senior Level</option>
              <option value="lead">Lead</option>
              <option value="executive">Executive</option>
            </select>
          </div>

          <div className="filter-group">
            <select
              name="employment_type"
              value={filters.employment_type}
              onChange={handleFilterChange}
              className="filter-select"
            >
              <option value="">Employment Type</option>
              <option value="full-time">Full Time</option>
              <option value="part-time">Part Time</option>
              <option value="contract">Contract</option>
              <option value="internship">Internship</option>
            </select>
          </div>

          <div className="filter-group">
            <button onClick={clearFilters} className="btn btn-secondary">
              Clear Filters
            </button>
          </div>
        </div>
      </div>

      {/* Job Results */}
      <div className="job-results">
        <div className="results-header">
          <h3>
            {jobs.length} Job{jobs.length !== 1 ? 's' : ''} Found
          </h3>
        </div>

        {jobs.length === 0 ? (
          <div className="no-jobs">
            <p>No jobs found matching your criteria.</p>
            <p>Try adjusting your filters or check back later for new opportunities.</p>
          </div>
        ) : (
          <div className="jobs-grid">
            {jobs.map((job) => (
              <div key={job.id} className="job-card">
                <div className="job-header">
                  <h4 className="job-title">
                    <Link to={`/jobs/${job.id}`}>
                      {job.title}
                    </Link>
                  </h4>
                  <div className="job-company">
                    {job.company || 'Company Name'}
                  </div>
                </div>

                <div className="job-details">
                  <div className="job-info">
                    {job.location && (
                      <span className="job-location">📍 {job.location}</span>
                    )}
                    {job.experience_level && (
                      <span className="job-experience">
                        👤 {job.experience_level}
                      </span>
                    )}
                    {job.employment_type && (
                      <span className="job-type">
                        💼 {job.employment_type}
                      </span>
                    )}
                  </div>

                  <div className="job-description">
                    <p>
                      {job.description 
                        ? job.description.substring(0, 150) + '...'
                        : 'No description available.'
                      }
                    </p>
                  </div>

                  {job.required_skills && job.required_skills.length > 0 && (
                    <div className="job-skills">
                      <strong>Skills:</strong>
                      <div className="skills-tags">
                        {job.required_skills.slice(0, 3).map((skill, index) => (
                          <span key={index} className="skill-tag">{skill}</span>
                        ))}
                        {job.required_skills.length > 3 && (
                          <span className="skill-tag more">
                            +{job.required_skills.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="job-footer">
                    <div className="job-date">
                      Posted: {formatDate(job.created_at)}
                    </div>
                    <Link to={`/jobs/${job.id}`} className="btn btn-primary btn-sm">
                      View Details
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default JobList;
