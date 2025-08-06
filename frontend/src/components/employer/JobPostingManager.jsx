/**
 * Job Posting Manager Component
 * Handles creation, editing, cloning, and management of job postings
 */

import React, { useState, useEffect } from 'react';
import { useToast } from '../Toast';
import { getStatusErrorMessage } from '../../utils/errorHandler';

const JobPostingManager = () => {
  const { showSuccess, showError, showInfo } = useToast();
  const [activeView, setActiveView] = useState('list'); // 'list', 'create', 'edit'
  const [jobs, setJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: {
      type: 'remote', // 'remote', 'onsite', 'hybrid'
      city: '',
      state: '',
      country: ''
    },
    employment: {
      type: 'full-time', // 'full-time', 'part-time', 'contract', 'internship'
      duration: '', // for contracts
      startDate: ''
    },
    salary: {
      min: '',
      max: '',
      currency: 'USD',
      period: 'annually' // 'annually', 'monthly', 'hourly'
    },
    requirements: {
      experience: '',
      skills: [],
      education: '',
      certifications: []
    },
    responsibilities: '',
    benefits: '',
    applicationDeadline: '',
    visibility: 'public', // 'public', 'private', 'draft'
    assessments: [],
    socialSharing: {
      linkedin: false,
      twitter: false,
      facebook: false
    },
    publishSchedule: {
      immediate: true,
      scheduledDate: ''
    }
  });

  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    try {
      setIsLoading(true);
      // API call to fetch employer's jobs
      // const response = await jobsAPI.getEmployerJobs();
      // setJobs(response.data);
      
      // Mock data for now
      setJobs([
        {
          id: 1,
          title: 'Senior Software Engineer',
          status: 'active',
          applications: 23,
          views: 145,
          createdAt: '2024-01-15',
          deadline: '2024-02-15'
        },
        {
          id: 2,
          title: 'Product Manager',
          status: 'draft',
          applications: 0,
          views: 0,
          createdAt: '2024-01-20',
          deadline: '2024-03-01'
        }
      ]);
    } catch (error) {
      showError('Failed to load job postings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (section, field, value) => {
    if (section) {
      setFormData(prev => ({
        ...prev,
        [section]: {
          ...prev[section],
          [field]: value
        }
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }));
    }
  };

  const handleSkillsChange = (skills) => {
    setFormData(prev => ({
      ...prev,
      requirements: {
        ...prev.requirements,
        skills: skills.split(',').map(skill => skill.trim()).filter(skill => skill)
      }
    }));
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
        ...formData,
        visibility: isDraft ? 'draft' : formData.visibility
      };

      // API call to create/update job
      // const response = selectedJob 
      //   ? await jobsAPI.updateJob(selectedJob.id, jobData)
      //   : await jobsAPI.createJob(jobData);

      showSuccess(isDraft ? 'Job saved as draft' : 'Job posted successfully!');
      setActiveView('list');
      loadJobs();
      resetForm();
    } catch (error) {
      const errorMessage = getStatusErrorMessage(error);
      showError(`Failed to save job: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClone = (job) => {
    setFormData({
      ...job,
      title: `${job.title} (Copy)`,
      visibility: 'draft'
    });
    setSelectedJob(null);
    setActiveView('create');
    showInfo('Job cloned. Make your changes and save.');
  };

  const handleEdit = (job) => {
    setSelectedJob(job);
    setFormData(job);
    setActiveView('edit');
  };

  const handleDelete = async (jobId) => {
    if (!window.confirm('Are you sure you want to delete this job posting?')) {
      return;
    }

    try {
      // API call to delete job
      // await jobsAPI.deleteJob(jobId);
      showSuccess('Job posting deleted successfully');
      loadJobs();
    } catch (error) {
      showError('Failed to delete job posting');
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      location: { type: 'remote', city: '', state: '', country: '' },
      employment: { type: 'full-time', duration: '', startDate: '' },
      salary: { min: '', max: '', currency: 'USD', period: 'annually' },
      requirements: { experience: '', skills: [], education: '', certifications: [] },
      responsibilities: '',
      benefits: '',
      applicationDeadline: '',
      visibility: 'public',
      assessments: [],
      socialSharing: { linkedin: false, twitter: false, facebook: false },
      publishSchedule: { immediate: true, scheduledDate: '' }
    });
    setSelectedJob(null);
  };

  const renderJobList = () => (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Job Postings</h2>
        <button
          onClick={() => {
            resetForm();
            setActiveView('create');
          }}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
        >
          + Create New Job
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Job Title
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Applications
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Views
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Deadline
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {jobs.map((job) => (
                <tr key={job.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{job.title}</div>
                    <div className="text-sm text-gray-500">Created: {job.createdAt}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      job.status === 'active' ? 'bg-green-100 text-green-800' :
                      job.status === 'draft' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {job.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {job.applications}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {job.views}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {job.deadline}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => handleEdit(job)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleClone(job)}
                      className="text-green-600 hover:text-green-900"
                    >
                      Clone
                    </button>
                    <button
                      onClick={() => handleDelete(job.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );

  const renderJobForm = () => (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          {selectedJob ? 'Edit Job Posting' : 'Create New Job Posting'}
        </h2>
        <button
          onClick={() => setActiveView('list')}
          className="text-gray-600 hover:text-gray-900"
        >
          ← Back to List
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        {/* Basic Information */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Title *
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => handleInputChange(null, 'title', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="e.g., Senior Software Engineer"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Job Description *
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => handleInputChange(null, 'description', e.target.value)}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Describe the role, responsibilities, and what makes this position unique..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Key Responsibilities
              </label>
              <textarea
                value={formData.responsibilities}
                onChange={(e) => handleInputChange(null, 'responsibilities', e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="List the main responsibilities and duties..."
              />
            </div>
          </div>
        </div>

        {/* Location & Employment */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Location & Employment Details</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Work Type
              </label>
              <select
                value={formData.location.type}
                onChange={(e) => handleInputChange('location', 'type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="remote">Remote</option>
                <option value="onsite">On-site</option>
                <option value="hybrid">Hybrid</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Employment Type
              </label>
              <select
                value={formData.employment.type}
                onChange={(e) => handleInputChange('employment', 'type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="full-time">Full-time</option>
                <option value="part-time">Part-time</option>
                <option value="contract">Contract</option>
                <option value="internship">Internship</option>
              </select>
            </div>

            {formData.location.type !== 'remote' && (
              <>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    City
                  </label>
                  <input
                    type="text"
                    value={formData.location.city}
                    onChange={(e) => handleInputChange('location', 'city', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="City"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Country
                  </label>
                  <input
                    type="text"
                    value={formData.location.country}
                    onChange={(e) => handleInputChange('location', 'country', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    placeholder="Country"
                  />
                </div>
              </>
            )}
          </div>
        </div>

        {/* Salary & Compensation */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Salary & Compensation</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Salary
              </label>
              <input
                type="number"
                value={formData.salary.min}
                onChange={(e) => handleInputChange('salary', 'min', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="50000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Maximum Salary
              </label>
              <input
                type="number"
                value={formData.salary.max}
                onChange={(e) => handleInputChange('salary', 'max', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="80000"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Period
              </label>
              <select
                value={formData.salary.period}
                onChange={(e) => handleInputChange('salary', 'period', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="annually">Annually</option>
                <option value="monthly">Monthly</option>
                <option value="hourly">Hourly</option>
              </select>
            </div>
          </div>
        </div>

        {/* Requirements */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Requirements & Qualifications</h3>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Required Skills (comma-separated)
              </label>
              <input
                type="text"
                value={formData.requirements.skills.join(', ')}
                onChange={(e) => handleSkillsChange(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="JavaScript, React, Node.js, MongoDB"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Experience Level
              </label>
              <input
                type="text"
                value={formData.requirements.experience}
                onChange={(e) => handleInputChange('requirements', 'experience', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="3-5 years of experience in software development"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Education Requirements
              </label>
              <input
                type="text"
                value={formData.requirements.education}
                onChange={(e) => handleInputChange('requirements', 'education', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
                placeholder="Bachelor's degree in Computer Science or related field"
              />
            </div>
          </div>
        </div>

        {/* Application Settings */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Application Settings</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Application Deadline
              </label>
              <input
                type="date"
                value={formData.applicationDeadline}
                onChange={(e) => handleInputChange(null, 'applicationDeadline', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Visibility
              </label>
              <select
                value={formData.visibility}
                onChange={(e) => handleInputChange(null, 'visibility', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="public">Public</option>
                <option value="private">Private</option>
                <option value="draft">Draft</option>
              </select>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end space-x-4">
          <button
            onClick={() => handleSave(true)}
            disabled={isLoading}
            className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50"
          >
            Save as Draft
          </button>
          <button
            onClick={() => handleSave(false)}
            disabled={isLoading}
            className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
          >
            {isLoading ? 'Publishing...' : 'Publish Job'}
          </button>
        </div>
      </div>
    </div>
  );

  switch (activeView) {
    case 'create':
    case 'edit':
      return renderJobForm();
    default:
      return renderJobList();
  }
};

export default JobPostingManager;
