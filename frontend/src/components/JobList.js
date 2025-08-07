/**
 * Job listings component that fetches and displays available jobs.
 * Provides filtering, skill matching, and navigation to detailed job views.
 */

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import dataService from '../services/dataService';
import resumeAnalyzer from '../services/resumeAnalyzer';
import careerCounseling from '../services/careerCounseling';
import { getStatusErrorMessage } from '../utils/errorHandler';

const JobList = () => {
  const { user } = useAuth();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [userSkills, setUserSkills] = useState([]);
  const [skillMatches, setSkillMatches] = useState({});
  const [showResumeUpload, setShowResumeUpload] = useState(false);
  const [uploadingResume, setUploadingResume] = useState(false);
  const [resumeAnalysis, setResumeAnalysis] = useState(null);
  const [careerAnalysis, setCareerAnalysis] = useState(null);
  const [showCareerAnalysis, setShowCareerAnalysis] = useState(false);
  const [filters, setFilters] = useState({
    search: '',
    location: '',
    experience_level: '',
    employment_type: '',
    showRecommended: false
  });

  /**
   * Fetch jobs from data service and analyze skill matches
   */
  useEffect(() => {
    fetchJobs();
    loadUserSkills();
  }, [filters]);

  /**
   * Load user skills from profile or resume data
   */
  const loadUserSkills = () => {
    if (user && user.profile) {
      // Extract skills from user profile if available
      const skills = user.profile.skills || [];
      setUserSkills(skills);
    }
  };

  /**
   * Calculate skill match percentage between user and job
   */
  // Handle resume upload and analysis
  const handleResumeUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setUploadingResume(true);
    
    try {
      const analysis = await resumeAnalyzer.analyzeResume(file);
      
      if (analysis.success) {
        setResumeAnalysis(analysis);
        setUserSkills(analysis.skills);
        
        // Generate career counseling feedback
        const allJobs = await dataService.getAllJobs();
        const matchResults = allJobs.map(job => {
          const jobSkills = job.required_skills || [];
          const matchingSkills = analysis.skills.filter(candidateSkill =>
            jobSkills.some(jobSkill =>
              candidateSkill.toLowerCase().includes(jobSkill.toLowerCase()) ||
              jobSkill.toLowerCase().includes(candidateSkill.toLowerCase())
            )
          );
          const missingSkills = jobSkills.filter(jobSkill =>
            !analysis.skills.some(candidateSkill =>
              candidateSkill.toLowerCase().includes(jobSkill.toLowerCase()) ||
              jobSkill.toLowerCase().includes(candidateSkill.toLowerCase())
            )
          );
          const matchPercentage = jobSkills.length > 0 
            ? Math.round((matchingSkills.length / jobSkills.length) * 100)
            : 0;

          return {
            ...job,
            matchPercentage,
            matchingSkills,
            missingSkills,
            totalRequiredSkills: jobSkills.length
          };
        });

        const counselingFeedback = careerCounseling.generateCareerCounselingFeedback(analysis, matchResults);
        setCareerAnalysis(counselingFeedback);
        setShowCareerAnalysis(true);
        
        // Show success message
        alert(`Resume analyzed successfully! Found ${analysis.totalSkillsFound} skills and generated career guidance.`);
      } else {
        alert(analysis.error || 'Failed to analyze resume');
      }
    } catch (error) {
      console.error('Resume upload error:', error);
      alert('Failed to analyze resume. Please try again.');
    } finally {
      setUploadingResume(false);
      event.target.value = ''; // Reset file input
    }
  };

  // Toggle resume upload section
  const toggleResumeUpload = () => {
    setShowResumeUpload(!showResumeUpload);
  };

  // Calculate skill match percentage
  const calculateSkillMatch = (jobSkills, candidateSkills) => {
    if (!jobSkills || !candidateSkills || jobSkills.length === 0) return 0;
    
    const matchingSkills = jobSkills.filter(skill => 
      candidateSkills.some(candidateSkill => 
        candidateSkill.toLowerCase().includes(skill.toLowerCase()) ||
        skill.toLowerCase().includes(candidateSkill.toLowerCase())
      )
    );
    
    return Math.round((matchingSkills.length / jobSkills.length) * 100);
  };

  /**
   * Fetch jobs from the data service
   */
  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError('');
      
      let allJobs = await dataService.getAllJobs();
      
      // Apply filters
      let filteredJobs = allJobs.filter(job => {
        // Search filter
        if (filters.search) {
          const searchTerm = filters.search.toLowerCase();
          const matchesSearch = 
            job.title.toLowerCase().includes(searchTerm) ||
            job.description.toLowerCase().includes(searchTerm) ||
            job.company_name.toLowerCase().includes(searchTerm) ||
            (job.required_skills && job.required_skills.some(skill => 
              skill.toLowerCase().includes(searchTerm)
            ));
          if (!matchesSearch) return false;
        }

        // Location filter
        if (filters.location) {
          const locationTerm = filters.location.toLowerCase();
          if (!job.location.toLowerCase().includes(locationTerm)) return false;
        }

        // Experience level filter
        if (filters.experience_level) {
          if (job.experience_level !== filters.experience_level) return false;
        }

        // Employment type filter
        if (filters.employment_type) {
          if (job.employment_type !== filters.employment_type) return false;
        }

        return true;
      });

      // Calculate skill matches for each job
      const matchData = {};
      filteredJobs.forEach(job => {
        const matchPercentage = calculateSkillMatch(job.required_skills, userSkills);
        matchData[job._id] = {
          percentage: matchPercentage,
          matchingSkills: getMatchingSkills(job.required_skills, userSkills),
          missingSkills: getMissingSkills(job.required_skills, userSkills)
        };
      });

      setSkillMatches(matchData);

      // Sort jobs by relevance if user has skills
      if (userSkills.length > 0 && filters.showRecommended) {
        filteredJobs.sort((a, b) => {
          const matchA = matchData[a._id]?.percentage || 0;
          const matchB = matchData[b._id]?.percentage || 0;
          return matchB - matchA;
        });
      }

      setJobs(filteredJobs);
    } catch (error) {
      console.error('Failed to fetch jobs:', error);
      setError(getStatusErrorMessage(error, 'Failed to load jobs. Please try again.'));
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Get skills that match between job requirements and user skills
   */
  const getMatchingSkills = (jobSkills, candidateSkills) => {
    if (!jobSkills || !candidateSkills) return [];
    
    const jobSkillsLower = jobSkills.map(skill => skill.toLowerCase().trim());
    const candidateSkillsLower = candidateSkills.map(skill => skill.toLowerCase().trim());
    
    return jobSkills.filter(jobSkill => 
      candidateSkillsLower.some(candidateSkill => 
        candidateSkill.includes(jobSkill.toLowerCase()) || 
        jobSkill.toLowerCase().includes(candidateSkill) ||
        candidateSkill === jobSkill.toLowerCase()
      )
    );
  };

  /**
   * Get skills that are required but missing from user profile
   */
  const getMissingSkills = (jobSkills, candidateSkills) => {
    if (!jobSkills || !candidateSkills) return jobSkills || [];
    
    const matchingSkills = getMatchingSkills(jobSkills, candidateSkills);
    return jobSkills.filter(skill => !matchingSkills.includes(skill));
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
      showRecommended: false
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
        <div className="filter-header">
          <h3>Find Your Perfect Job</h3>
          {user && userSkills.length > 0 && (
            <div className="user-skills-summary">
              <p>Your Skills: {userSkills.slice(0, 3).join(', ')} 
                {userSkills.length > 3 && ` +${userSkills.length - 3} more`}
              </p>
            </div>
          )}
        </div>

        {/* Resume Upload Section */}
        {user && (
          <div className="resume-upload-section">
            <div className="resume-upload-header">
              <button 
                onClick={toggleResumeUpload}
                className="btn btn-outline-primary btn-sm"
              >
                📄 {userSkills.length > 0 ? 'Update Resume' : 'Upload Resume for Skill Analysis'}
              </button>
              {userSkills.length > 0 && (
                <span className="skills-count">({userSkills.length} skills detected)</span>
              )}
            </div>
            
            {showResumeUpload && (
              <div className="resume-upload-form">
                <div className="upload-instructions">
                  <p>Upload your resume to automatically detect your skills and get personalized job recommendations.</p>
                  <p><small>Supported formats: PDF, DOC, DOCX, TXT</small></p>
                </div>
                
                <div className="file-upload-wrapper">
                  <input
                    type="file"
                    id="resume-upload"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleResumeUpload}
                    disabled={uploadingResume}
                    className="file-input"
                  />
                  <label htmlFor="resume-upload" className="file-label">
                    {uploadingResume ? (
                      <span>📊 Analyzing Resume...</span>
                    ) : (
                      <span>📁 Choose Resume File</span>
                    )}
                  </label>
                </div>

                {resumeAnalysis && (
                  <div className="resume-analysis-results">
                    <h4>✅ Analysis Complete</h4>
                    <p><strong>Skills Found:</strong> {resumeAnalysis.totalSkillsFound}</p>
                    <div className="detected-skills">
                      {resumeAnalysis.skills.slice(0, 8).map((skill, index) => (
                        <span key={index} className="skill-tag matching">{skill}</span>
                      ))}
                      {resumeAnalysis.skills.length > 8 && (
                        <span className="skill-tag more">+{resumeAnalysis.skills.length - 8} more</span>
                      )}
                    </div>
                    
                    {/* Career Analysis Button */}
                    <div className="career-analysis-toggle" style={{ marginTop: '15px' }}>
                      <button 
                        onClick={() => setShowCareerAnalysis(!showCareerAnalysis)}
                        className="btn btn-primary btn-sm"
                      >
                        🎓 {showCareerAnalysis ? 'Hide' : 'View'} Career Counseling Analysis
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Career Counseling Analysis Section */}
        {careerAnalysis && showCareerAnalysis && (
          <div className="career-counseling-section" style={{
            backgroundColor: '#f8fafc',
            border: '2px solid #e2e8f0',
            borderRadius: '12px',
            padding: '24px',
            marginBottom: '24px',
            boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
          }}>
            <h3 style={{ 
              color: '#1a365d', 
              marginBottom: '20px',
              display: 'flex',
              alignItems: 'center',
              fontSize: '1.25rem',
              fontWeight: 'bold'
            }}>
              🎓 Career Counseling Analysis
            </h3>
            
            <div style={{ 
              display: 'grid', 
              gridTemplateColumns: window.innerWidth > 1024 ? '1fr 1fr' : '1fr',
              gap: '24px'
            }}>
              {/* Professional Insights */}
              <div>
                <h4 style={{ 
                  color: '#2d3748', 
                  marginBottom: '12px',
                  fontWeight: '600',
                  display: 'flex',
                  alignItems: 'center'
                }}>
                  💡 Professional Insights
                </h4>
                <div style={{ marginBottom: '20px' }}>
                  {careerAnalysis.insights.map((insight, index) => (
                    <div key={index} style={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      marginBottom: '8px'
                    }}>
                      <span style={{ color: '#3182ce', marginRight: '8px', marginTop: '2px' }}>•</span>
                      <span style={{ color: '#2d3748', fontSize: '0.9rem' }}>{insight}</span>
                    </div>
                  ))}
                </div>

                <h4 style={{ 
                  color: '#2d3748', 
                  marginBottom: '12px',
                  fontWeight: '600'
                }}>
                  📊 Skill Breakdown
                </h4>
                <div style={{
                  backgroundColor: 'white',
                  border: '1px solid #e2e8f0',
                  borderRadius: '8px',
                  padding: '16px'
                }}>
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: '1fr 1fr',
                    gap: '12px',
                    fontSize: '0.9rem'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#718096' }}>Technical Skills:</span>
                      <span style={{ fontWeight: '600', color: '#3182ce' }}>{careerAnalysis.skillBreakdown.technical}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#718096' }}>Soft Skills:</span>
                      <span style={{ fontWeight: '600', color: '#3182ce' }}>{careerAnalysis.skillBreakdown.soft}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#718096' }}>Frameworks:</span>
                      <span style={{ fontWeight: '600', color: '#3182ce' }}>{careerAnalysis.skillBreakdown.frameworks}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#718096' }}>Cloud Skills:</span>
                      <span style={{ fontWeight: '600', color: '#3182ce' }}>{careerAnalysis.skillBreakdown.cloud}</span>
                    </div>
                  </div>
                  <div style={{ 
                    marginTop: '12px', 
                    paddingTop: '12px', 
                    borderTop: '1px solid #e2e8f0'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: '600' }}>
                      <span style={{ color: '#4a5568' }}>Market Alignment:</span>
                      <span style={{ 
                        color: careerAnalysis.marketAlignment >= 80 ? '#38a169' :
                               careerAnalysis.marketAlignment >= 60 ? '#d69e2e' : '#e53e3e'
                      }}>
                        {careerAnalysis.marketAlignment}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Career Recommendations */}
              <div>
                <h4 style={{ 
                  color: '#2d3748', 
                  marginBottom: '12px',
                  fontWeight: '600'
                }}>
                  🚀 Career Recommendations
                </h4>
                <div style={{ marginBottom: '20px' }}>
                  {careerAnalysis.recommendations.map((recommendation, index) => (
                    <div key={index} style={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      marginBottom: '8px'
                    }}>
                      <span style={{ color: '#38a169', marginRight: '8px', marginTop: '2px' }}>✓</span>
                      <span style={{ color: '#2d3748', fontSize: '0.9rem' }}>{recommendation}</span>
                    </div>
                  ))}
                </div>

                <h4 style={{ 
                  color: '#2d3748', 
                  marginBottom: '12px',
                  fontWeight: '600'
                }}>
                  🎯 Suggested Career Paths
                </h4>
                <div style={{ 
                  display: 'flex', 
                  flexWrap: 'wrap', 
                  gap: '8px',
                  marginBottom: '20px'
                }}>
                  {careerAnalysis.careerPaths.map((path, index) => (
                    <span
                      key={index}
                      style={{
                        display: 'inline-flex',
                        padding: '6px 12px',
                        backgroundColor: '#ebf8ff',
                        color: '#2c5282',
                        borderRadius: '16px',
                        fontSize: '0.85rem',
                        fontWeight: '500',
                        border: '1px solid #bee3f8'
                      }}
                    >
                      {path}
                    </span>
                  ))}
                </div>

                {careerAnalysis.topSkillGaps.length > 0 && (
                  <div>
                    <h4 style={{ 
                      color: '#2d3748', 
                      marginBottom: '12px',
                      fontWeight: '600'
                    }}>
                      📚 Priority Skills to Develop
                    </h4>
                    <div style={{ 
                      display: 'flex', 
                      flexWrap: 'wrap', 
                      gap: '8px'
                    }}>
                      {careerAnalysis.topSkillGaps.map((skill, index) => (
                        <span
                          key={index}
                          style={{
                            display: 'inline-flex',
                            padding: '6px 12px',
                            backgroundColor: '#fef5e7',
                            color: '#c05621',
                            borderRadius: '16px',
                            fontSize: '0.85rem',
                            fontWeight: '500',
                            border: '1px solid #fbd38d'
                          }}
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Action Items Dashboard */}
            <div style={{
              marginTop: '24px',
              padding: '16px',
              backgroundColor: 'white',
              borderRadius: '8px',
              border: '1px solid #e2e8f0'
            }}>
              <h4 style={{ 
                color: '#2d3748', 
                marginBottom: '12px',
                fontWeight: '600'
              }}>
                📋 Next Steps
              </h4>
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: window.innerWidth > 768 ? '1fr 1fr 1fr' : '1fr',
                gap: '16px',
                fontSize: '0.9rem'
              }}>
                <div style={{
                  textAlign: 'center',
                  padding: '12px',
                  backgroundColor: '#ebf8ff',
                  borderRadius: '8px'
                }}>
                  <div style={{ fontSize: '2rem', marginBottom: '8px' }}>🎯</div>
                  <div style={{ fontWeight: '600', color: '#2c5282' }}>Focus Areas</div>
                  <div style={{ color: '#3182ce', marginTop: '4px' }}>
                    {careerAnalysis.topSkillGaps.length > 0 
                      ? `Learn ${careerAnalysis.topSkillGaps[0]}` 
                      : 'Maintain current skills'
                    }
                  </div>
                </div>
                <div style={{
                  textAlign: 'center',
                  padding: '12px',
                  backgroundColor: '#f0fff4',
                  borderRadius: '8px'
                }}>
                  <div style={{ fontSize: '2rem', marginBottom: '8px' }}>💼</div>
                  <div style={{ fontWeight: '600', color: '#276749' }}>Job Readiness</div>
                  <div style={{ color: '#38a169', marginTop: '4px' }}>
                    {careerAnalysis.marketAlignment >= 70 ? 'Apply Now' : 'Skill Building Phase'}
                  </div>
                </div>
                <div style={{
                  textAlign: 'center',
                  padding: '12px',
                  backgroundColor: '#faf5ff',
                  borderRadius: '8px'
                }}>
                  <div style={{ fontSize: '2rem', marginBottom: '8px' }}>📈</div>
                  <div style={{ fontWeight: '600', color: '#553c9a' }}>Career Growth</div>
                  <div style={{ color: '#805ad5', marginTop: '4px' }}>
                    {careerAnalysis.careerPaths[0] || 'Explore Options'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
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

          {user && userSkills.length > 0 && (
            <div className="filter-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="showRecommended"
                  checked={filters.showRecommended}
                  onChange={(e) => setFilters({...filters, showRecommended: e.target.checked})}
                />
                Show Recommended Jobs
              </label>
            </div>
          )}

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
          {filters.showRecommended && userSkills.length > 0 && (
            <p className="results-subtitle">Sorted by skill match relevance</p>
          )}
        </div>

        {jobs.length === 0 ? (
          <div className="no-jobs">
            <p>No jobs found matching your criteria.</p>
            <p>Try adjusting your filters or check back later for new opportunities.</p>
          </div>
        ) : (
          <div className="jobs-grid">
            {jobs.map((job) => {
              const matchData = skillMatches[job._id] || { percentage: 0, matchingSkills: [], missingSkills: [] };
              
              return (
                <div key={job._id} className="job-card">
                  <div className="job-header">
                    <h4 className="job-title">
                      <Link to={`/jobs/${job._id}`}>
                        {job.title}
                      </Link>
                    </h4>
                    <div className="job-company">
                      {job.company_name || 'Company Name'}
                    </div>
                    
                    {/* Skill Match Indicator */}
                    {user && userSkills.length > 0 && (
                      <div className="skill-match-indicator">
                        <div className={`match-score ${
                          matchData.percentage >= 70 ? 'high-match' :
                          matchData.percentage >= 40 ? 'medium-match' : 'low-match'
                        }`}>
                          <span className="match-percentage">{matchData.percentage}% Match</span>
                          <div className="match-bar">
                            <div 
                              className="match-fill" 
                              style={{ width: `${matchData.percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    )}
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
                      {job.salary_range && (
                        <span className="job-salary">
                          💰 {job.salary_range}
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

                    {/* Skill Analysis */}
                    {user && userSkills.length > 0 && matchData.percentage > 0 && (
                      <div className="skill-analysis">
                        {matchData.matchingSkills.length > 0 && (
                          <div className="matching-skills">
                            <strong>✅ Your Matching Skills:</strong>
                            <div className="skills-tags">
                              {matchData.matchingSkills.slice(0, 3).map((skill, index) => (
                                <span key={index} className="skill-tag matching">{skill}</span>
                              ))}
                              {matchData.matchingSkills.length > 3 && (
                                <span className="skill-tag more">
                                  +{matchData.matchingSkills.length - 3} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                        
                        {matchData.missingSkills.length > 0 && (
                          <div className="missing-skills">
                            <strong>📚 Skills to Learn:</strong>
                            <div className="skills-tags">
                              {matchData.missingSkills.slice(0, 3).map((skill, index) => (
                                <span key={index} className="skill-tag missing">{skill}</span>
                              ))}
                              {matchData.missingSkills.length > 3 && (
                                <span className="skill-tag more">
                                  +{matchData.missingSkills.length - 3} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* All Required Skills */}
                    {job.required_skills && job.required_skills.length > 0 && (
                      <div className="job-skills">
                        <strong>Required Skills:</strong>
                        <div className="skills-tags">
                          {job.required_skills.slice(0, 4).map((skill, index) => (
                            <span 
                              key={index} 
                              className={`skill-tag ${
                                user && matchData.matchingSkills.includes(skill) ? 'matching' : 'neutral'
                              }`}
                            >
                              {skill}
                            </span>
                          ))}
                          {job.required_skills.length > 4 && (
                            <span className="skill-tag more">
                              +{job.required_skills.length - 4} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    <div className="job-footer">
                      <div className="job-date">
                        Posted: {formatDate(job.posted_at)}
                      </div>
                      <Link to={`/jobs/${job._id}`} className="btn btn-primary btn-sm">
                        View Details
                      </Link>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default JobList;
