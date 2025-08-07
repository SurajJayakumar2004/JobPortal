/**
 * Job Posting Manager Component
 * Handles creation, editing, cloning, and management of job postings
 */

import React, { useState, useEffect } from 'react';
import { useToast } from '../Toast';
import { getStatusErrorMessage } from '../../utils/errorHandler';
import { jobsAPI } from '../../services/api';
import dataService from '../../services/dataService';

const JobPostingManager = () => {
  const { showSuccess, showError, showInfo } = useToast();
  const [activeView, setActiveView] = useState('list'); // 'list', 'create', 'edit', 'candidates'
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedJobCandidates, setSelectedJobCandidates] = useState([]);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    requirements: '',
    required_skills: '',
    location: '',
    experience_level: 'mid',
    employment_type: 'full-time',
    salary_range: '',
    company_name: '',
    application_deadline: ''
  });

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      setIsLoading(true);
      console.log('Loading jobs from data service...');
      
      // Load jobs from data service
      const jobsData = await dataService.getAllJobs();
      console.log('Loaded jobs:', jobsData.length, 'jobs');
      
      setJobs(jobsData);
    } catch (error) {
      console.error('Error loading jobs:', error);
      showError('Failed to load job postings');
      // Set empty array as fallback
      setJobs([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    await handleSave();
  };

  const handleSave = async (isDraft = false) => {
    try {
      setIsLoading(true);
      
      // Validate required fields
      if (!formData.title || !formData.description) {
        showError('Please fill in required fields (Title and Description)');
        return;
      }

      const jobData = {
        title: formData.title,
        description: formData.description,
        requirements: formData.requirements,
        required_skills: formData.required_skills.split(',').map(skill => skill.trim()).filter(skill => skill),
        location: formData.location,
        experience_level: formData.experience_level,
        employment_type: formData.employment_type,
        salary_range: formData.salary_range,
        company_name: formData.company_name,
        application_deadline: formData.application_deadline,
        status: formData.status || 'draft'
      };

      console.log('Submitting job data:', jobData);

      let response;
      if (selectedJob) {
        // Update existing job
        response = await dataService.updateJob(selectedJob._id, jobData);
      } else {
        // Create new job
        response = await dataService.createJob(jobData);
      }
      
      if (response && response.success) {
        showSuccess(selectedJob ? 'Job updated successfully!' : 'Job created successfully!');
        setActiveView('list');
        loadJobs();
        resetForm();
      } else {
        showError('Failed to save job posting');
      }
    } catch (error) {
      console.error('Job save error:', error);
      const errorMessage = getStatusErrorMessage(error, 'Failed to save job posting');
      showError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const loadJobCandidates = async (jobId) => {
    try {
      setIsLoading(true);
      // Load candidates for specific job from data service
      const candidates = await dataService.getCandidatesForJob(jobId);
      setSelectedJobCandidates(candidates);
    } catch (error) {
      console.error('Error loading candidates:', error);
      showError('Failed to load candidates');
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewCandidates = (job) => {
    setSelectedJob(job);
    setActiveView('candidates');
    loadJobCandidates(job._id);
  };

  const handleClone = (job) => {
    setFormData({
      title: `${job.title} (Copy)`,
      description: job.description,
      requirements: job.requirements || '',
      required_skills: Array.isArray(job.required_skills) ? job.required_skills.join(', ') : job.required_skills || '',
      location: job.location,
      experience_level: job.experience_level,
      employment_type: job.employment_type,
      salary_range: job.salary_range,
      company_name: job.company_name,
      application_deadline: job.application_deadline || '',
      status: 'draft'
    });
    setSelectedJob(null);
    setActiveView('create');
    showInfo('Job cloned. Make your changes and save.');
  };

  const handleEdit = (job) => {
    setSelectedJob(job);
    setFormData({
      title: job.title,
      description: job.description,
      requirements: job.requirements || '',
      required_skills: Array.isArray(job.required_skills) ? job.required_skills.join(', ') : job.required_skills || '',
      location: job.location,
      experience_level: job.experience_level,
      employment_type: job.employment_type,
      salary_range: job.salary_range,
      company_name: job.company_name,
      application_deadline: job.application_deadline || '',
      status: job.status || 'draft'
    });
    setActiveView('edit');
  };

  const handleDelete = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job posting? This action cannot be undone.')) {
      return;
    }

    try {
      setIsLoading(true);
      console.log('Deleting job with ID:', jobId);
      
      const response = await dataService.deleteJob(jobId);
      console.log('Delete response:', response);
      
      if (response && response.success) {
        showSuccess('Job posting deleted successfully');
        // Immediately reload jobs to reflect the change
        await loadJobs();
      } else {
        console.error('Delete failed - no success response:', response);
        showError('Failed to delete job posting');
      }
    } catch (error) {
      console.error('Error deleting job:', error);
      showError(`Failed to delete job posting: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      requirements: '',
      required_skills: '',
      location: '',
      experience_level: 'mid',
      employment_type: 'full-time',
      salary_range: '',
      company_name: '',
      application_deadline: '',
      status: 'draft'
    });
    setSelectedJob(null);
  };

  // Debug function to reset data (for testing)
  const handleResetData = async () => {
    if (!window.confirm('This will reset all job data to the original state. Are you sure? This action cannot be undone.')) {
      return;
    }

    try {
      setIsLoading(true);
      const response = dataService.resetToDefaultData();
      if (response && response.success) {
        showSuccess('Data reset successfully');
        await loadJobs();
      } else {
        showError('Failed to reset data');
      }
    } catch (error) {
      console.error('Error resetting data:', error);
      showError('Failed to reset data');
    } finally {
      setIsLoading(false);
    }
  };

  const renderJobList = () => (
    <div className="job-posting-manager">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">Job Postings</h2>
          <p className="text-gray-600">Manage your job listings and track applications</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => {
              resetForm();
              setActiveView('create');
            }}
            className="btn-modern-primary flex items-center"
          >
            <span className="mr-2 text-lg">✨</span>
            Create New Job
          </button>
          
          {/* Debug reset button - can be removed in production */}
          <button
            onClick={handleResetData}
            className="bg-gray-400 hover:bg-gray-500 text-white px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-200 flex items-center"
            title="Reset all job data to original state (for testing)"
          >
            <span className="mr-1 text-sm">🔄</span>
            Reset Data
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading job postings...</div>
        </div>
      ) : (
        <div className="card-modern">
          {jobs.length === 0 ? (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">📋</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No job postings yet</h3>
              <p className="text-gray-600 mb-6">Create your first job posting to start attracting candidates!</p>
              <button
                onClick={() => {
                  resetForm();
                  setActiveView('create');
                }}
                className="btn-modern-primary"
              >
                <span className="mr-2">+</span>
                Create Your First Job
              </button>
            </div>
          ) : (
            <div className="overflow-hidden">
              <table className="min-w-full">
                <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                  <tr>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                      Job Information
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                      Details
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                      Applications
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                      Posted
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-bold text-gray-600 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-100">
                  {jobs.map((job) => (
                    <tr key={job._id} className="hover:bg-gray-50 transition-colors duration-200">
                      <td className="px-6 py-5">
                        <div>
                          <div className="text-sm font-semibold text-gray-900 mb-1">{job.title}</div>
                          <div className="text-sm text-gray-600 flex items-center">
                            <span className="mr-1">🏢</span>
                            {job.company_name}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <div>
                          <div className="text-sm text-gray-900 flex items-center mb-1">
                            <span className="mr-1">📍</span>
                            {job.location}
                          </div>
                          <div className="text-sm text-gray-600 flex items-center">
                            <span className="mr-1">💼</span>
                            {job.employment_type?.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-5">
                        <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${
                          job.status === 'open' ? 'bg-green-100 text-green-800 border border-green-200' :
                          job.status === 'draft' ? 'bg-yellow-100 text-yellow-800 border border-yellow-200' :
                          'bg-gray-100 text-gray-800 border border-gray-200'
                        }`}>
                          {job.status?.charAt(0).toUpperCase() + job.status?.slice(1)}
                        </span>
                      </td>
                      <td className="px-6 py-5">
                        <button
                          onClick={() => handleViewCandidates(job)}
                          className="flex items-center text-indigo-600 hover:text-indigo-800 font-semibold transition-colors duration-200"
                        >
                          <span className="mr-1">👥</span>
                          {job.applications_count || 0} candidates
                        </button>
                      </td>
                      <td className="px-6 py-5 text-sm text-gray-600">
                        {new Date(job.posted_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })}
                      </td>
                      <td className="px-6 py-5">
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleEdit(job)}
                            className="text-indigo-600 hover:text-indigo-800 font-medium text-sm transition-colors duration-200"
                          >
                            ✏️ Edit
                          </button>
                          <button
                            onClick={() => handleViewCandidates(job)}
                            className="text-green-600 hover:text-green-800 font-medium text-sm transition-colors duration-200"
                          >
                            👁️ View
                          </button>
                          <button
                            onClick={() => handleClone(job)}
                            className="text-blue-600 hover:text-blue-800 font-medium text-sm transition-colors duration-200"
                          >
                            📋 Clone
                          </button>
                          <button
                            onClick={() => handleDelete(job._id)}
                            className="text-red-600 hover:text-red-800 font-medium text-sm transition-colors duration-200"
                          >
                            🗑️ Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderCandidatesView = () => (
    <div className="candidates-view">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Candidates for "{selectedJob?.title}"
          </h2>
          <p className="text-gray-600 flex items-center">
            <span className="mr-2">🤖</span>
            AI-matched candidates ranked by compatibility score
          </p>
        </div>
        <button
          onClick={() => setActiveView('list')}
          className="btn-modern-secondary flex items-center"
        >
          <span className="mr-2">←</span>
          Back to Jobs
        </button>
      </div>

      {isLoading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading candidates...</div>
        </div>
      ) : (
        <div className="space-y-6">
          {selectedJobCandidates.length === 0 ? (
            <div className="card-modern text-center py-16">
              <div className="text-6xl mb-4">👥</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No candidates yet</h3>
              <p className="text-gray-600 mb-6">
                Once candidates apply for this position, they'll appear here with AI-powered match scores.
              </p>
              <div className="flex justify-center space-x-4">
                <button
                  onClick={() => setActiveView('list')}
                  className="btn-modern-secondary"
                >
                  View All Jobs
                </button>
                <button
                  onClick={() => setActiveView('create')}
                  className="btn-modern-primary"
                >
                  Create New Job
                </button>
              </div>
            </div>
          ) : (
            selectedJobCandidates.map((candidate) => (
              <div key={candidate.user_id} className="card-modern candidate-card">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center mb-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mr-4">
                        <span className="text-xl">👤</span>
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {candidate.user_name}
                        </h3>
                        <p className="text-gray-600 text-sm">{candidate.user_email}</p>
                      </div>
                      <div className="flex items-center">
                        <span className="text-sm font-medium text-gray-600 mr-3">Match Score:</span>
                        <div className={`px-4 py-2 rounded-full text-sm font-bold shadow-md ${
                          candidate.match_score >= 90 ? 'bg-gradient-to-r from-green-400 to-green-600 text-white' :
                          candidate.match_score >= 80 ? 'bg-gradient-to-r from-blue-400 to-blue-600 text-white' :
                          candidate.match_score >= 70 ? 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-white' :
                          'bg-gradient-to-r from-gray-400 to-gray-600 text-white'
                        }`}>
                          {candidate.match_score}%
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div className="flex items-center text-sm">
                        <span className="font-medium text-gray-700 mr-2">📍 Location:</span>
                        <span className="text-gray-600">{candidate.location}</span>
                      </div>
                      <div className="flex items-center text-sm">
                        <span className="font-medium text-gray-700 mr-2">💼 Experience:</span>
                        <span className="text-gray-600 capitalize">{candidate.experience_level}</span>
                      </div>
                    </div>

                    <div className="mb-4">
                      <span className="text-sm font-medium text-gray-700 mb-2 block">🛠️ Skills:</span>
                      <div className="flex flex-wrap gap-2">
                        {candidate.skills.slice(0, 8).map((skill, index) => (
                          <span
                            key={index}
                            className="inline-flex px-3 py-1 text-xs bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-800 rounded-full border border-indigo-200"
                          >
                            {skill}
                          </span>
                        ))}
                        {candidate.skills.length > 8 && (
                          <span className="inline-flex px-3 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                            +{candidate.skills.length - 8} more
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="bg-gray-50 rounded-lg p-4">
                      <span className="text-sm font-medium text-gray-700 mb-2 block">📄 Summary:</span>
                      <p className="text-sm text-gray-600 leading-relaxed">{candidate.resume_summary}</p>
                    </div>
                  </div>
                  
                  <div className="ml-6 flex flex-col space-y-3">
                    <button className="btn-modern-primary text-sm">
                      <span className="mr-1">👁️</span>
                      View Profile
                    </button>
                    <button className="btn-modern-secondary text-sm">
                      <span className="mr-1">💬</span>
                      Message
                    </button>
                    <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200">
                      <span className="mr-1">📞</span>
                      Contact
                    </button>
                    <button className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200">
                      <span className="mr-1">📥</span>
                      Download
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );

  const renderJobForm = () => (
    <div className="job-form-container">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            {selectedJob ? 'Edit Job Posting' : 'Create New Job Posting'}
          </h2>
          <p className="text-gray-600">
            {selectedJob ? 'Update your job posting details' : 'Fill out the details to create an attractive job listing'}
          </p>
        </div>
        <button
          onClick={() => setActiveView('list')}
          className="btn-modern-secondary flex items-center"
        >
          <span className="mr-2">←</span>
          Back to List
        </button>
      </div>

      <div className="card-modern employer-form">
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Basic Information Section */}
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
              <span className="mr-2">📝</span>
              Basic Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="form-group">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Title *
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="e.g., Senior Software Engineer"
                />
              </div>

              <div className="form-group">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Company Name *
                </label>
                <input
                  type="text"
                  name="company_name"
                  value={formData.company_name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="e.g., TechCorp Solutions"
                />
              </div>

              <div className="form-group">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location *
                </label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="e.g., San Francisco, CA or Remote"
                />
              </div>

              <div className="form-group">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Employment Type *
                </label>
                <select
                  name="employment_type"
                  value={formData.employment_type}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="">Select Type</option>
                  <option value="full-time">Full Time</option>
                  <option value="part-time">Part Time</option>
                  <option value="contract">Contract</option>
                  <option value="internship">Internship</option>
                </select>
              </div>

              <div className="form-group">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Experience Level
                </label>
                <select
                  name="experience_level"
                  value={formData.experience_level}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="">Select Level</option>
                  <option value="entry">Entry Level</option>
                  <option value="mid">Mid Level</option>
                  <option value="senior">Senior Level</option>
                  <option value="executive">Executive</option>
                </select>
              </div>

              <div className="form-group">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Salary Range
                </label>
                <input
                  type="text"
                  name="salary_range"
                  value={formData.salary_range}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="e.g., $80,000 - $120,000"
                />
              </div>
            </div>
          </div>

          {/* Job Details Section */}
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
              <span className="mr-2">📋</span>
              Job Details
            </h3>
            <div className="space-y-6">
              <div className="form-group">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Job Description *
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  required
                  rows={6}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="Describe the role, responsibilities, and what makes this opportunity exciting..."
                />
              </div>

              <div className="form-group">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Requirements
                </label>
                <textarea
                  name="requirements"
                  value={formData.requirements}
                  onChange={handleInputChange}
                  rows={4}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="List the required qualifications, experience, and skills..."
                />
              </div>

              <div className="form-group">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Required Skills *
                </label>
                <input
                  type="text"
                  name="required_skills"
                  value={formData.required_skills}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="e.g., JavaScript, React, Node.js, Python (separate with commas)"
                />
                <p className="text-sm text-gray-500 mt-2 flex items-center">
                  <span className="mr-1">💡</span>
                  Separate skills with commas. These will be used for AI-powered candidate matching.
                </p>
              </div>
            </div>
          </div>

          {/* Publishing Settings Section */}
          <div>
            <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
              <span className="mr-2">⚙️</span>
              Publishing Settings
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="form-group">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Application Deadline
                </label>
                <input
                  type="date"
                  name="application_deadline"
                  value={formData.application_deadline}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              <div className="form-group">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Status
                </label>
                <select
                  name="status"
                  value={formData.status}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="draft">Draft</option>
                  <option value="open">Open for Applications</option>
                  <option value="closed">Closed</option>
                </select>
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-4 pt-8 border-t border-gray-200">
            <button
              type="button"
              onClick={() => setActiveView('list')}
              className="btn-modern-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="btn-modern-primary flex items-center"
            >
              {isLoading && (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              )}
              <span className="mr-2">{selectedJob ? '✏️' : '✨'}</span>
              {selectedJob ? 'Update Job' : 'Create Job'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  switch (activeView) {
    case 'create':
    case 'edit':
      return renderJobForm();
    case 'candidates':
      return renderCandidatesView();
    default:
      return renderJobList();
  }
};

export default JobPostingManager;
