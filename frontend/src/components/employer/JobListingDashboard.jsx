/**
 * Job Listing Dashboard Component
 * Provides overview and management of all job postings with filtering and sorting
 */

import React, { useState, useEffect } from 'react';
import { useToast } from '../Toast';

const JobListingDashboard = () => {
  const { showSuccess, showError } = useToast();
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState({
    status: 'all',
    dateRange: 'all',
    sortBy: 'created_desc'
  });
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadJobs();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [jobs, filters, searchTerm]);

  const loadJobs = async () => {
    try {
      setIsLoading(true);
      // API call to fetch detailed job listings
      // const response = await jobsAPI.getEmployerJobsDetailed();
      // setJobs(response.data);
      
      // Mock data for demonstration
      const mockJobs = [
        {
          id: 1,
          title: 'Senior Software Engineer',
          status: 'active',
          applications: 23,
          views: 145,
          createdAt: '2024-01-15T10:00:00Z',
          updatedAt: '2024-01-16T14:30:00Z',
          deadline: '2024-02-15',
          location: { type: 'remote', city: '', country: '' },
          employment: { type: 'full-time' },
          salary: { min: 80000, max: 120000, currency: 'USD', period: 'annually' },
          lastActivity: '2024-01-20T09:15:00Z',
          performance: {
            clickRate: 12.5,
            applicationRate: 4.2,
            qualityScore: 8.7
          }
        },
        {
          id: 2,
          title: 'Product Manager',
          status: 'paused',
          applications: 8,
          views: 67,
          createdAt: '2024-01-10T15:20:00Z',
          updatedAt: '2024-01-18T11:45:00Z',
          deadline: '2024-03-01',
          location: { type: 'hybrid', city: 'San Francisco', country: 'USA' },
          employment: { type: 'full-time' },
          salary: { min: 90000, max: 130000, currency: 'USD', period: 'annually' },
          lastActivity: '2024-01-19T16:30:00Z',
          performance: {
            clickRate: 8.9,
            applicationRate: 2.1,
            qualityScore: 7.3
          }
        },
        {
          id: 3,
          title: 'UX Designer',
          status: 'draft',
          applications: 0,
          views: 0,
          createdAt: '2024-01-20T09:00:00Z',
          updatedAt: '2024-01-20T09:00:00Z',
          deadline: '2024-02-28',
          location: { type: 'onsite', city: 'New York', country: 'USA' },
          employment: { type: 'full-time' },
          salary: { min: 70000, max: 100000, currency: 'USD', period: 'annually' },
          lastActivity: '2024-01-20T09:00:00Z',
          performance: {
            clickRate: 0,
            applicationRate: 0,
            qualityScore: 0
          }
        },
        {
          id: 4,
          title: 'Marketing Intern',
          status: 'closed',
          applications: 45,
          views: 234,
          createdAt: '2023-12-01T10:00:00Z',
          updatedAt: '2024-01-05T16:00:00Z',
          deadline: '2024-01-05',
          location: { type: 'hybrid', city: 'Austin', country: 'USA' },
          employment: { type: 'internship' },
          salary: { min: 20, max: 25, currency: 'USD', period: 'hourly' },
          lastActivity: '2024-01-05T16:00:00Z',
          performance: {
            clickRate: 15.2,
            applicationRate: 6.8,
            qualityScore: 9.1
          }
        }
      ];
      
      setJobs(mockJobs);
    } catch (error) {
      showError('Failed to load job listings');
    } finally {
      setIsLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...jobs];

    // Apply status filter
    if (filters.status !== 'all') {
      filtered = filtered.filter(job => job.status === filters.status);
    }

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(job =>
        job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.location.city.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply date range filter
    const now = new Date();
    if (filters.dateRange !== 'all') {
      const days = {
        'week': 7,
        'month': 30,
        'quarter': 90
      };
      const cutoffDate = new Date(now.getTime() - (days[filters.dateRange] * 24 * 60 * 60 * 1000));
      filtered = filtered.filter(job => new Date(job.createdAt) >= cutoffDate);
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (filters.sortBy) {
        case 'created_desc':
          return new Date(b.createdAt) - new Date(a.createdAt);
        case 'created_asc':
          return new Date(a.createdAt) - new Date(b.createdAt);
        case 'title_asc':
          return a.title.localeCompare(b.title);
        case 'title_desc':
          return b.title.localeCompare(a.title);
        case 'applications_desc':
          return b.applications - a.applications;
        case 'applications_asc':
          return a.applications - b.applications;
        case 'views_desc':
          return b.views - a.views;
        case 'views_asc':
          return a.views - b.views;
        default:
          return 0;
      }
    });

    setFilteredJobs(filtered);
  };

  const handleStatusChange = async (jobId, newStatus) => {
    try {
      // API call to update job status
      // await jobsAPI.updateJobStatus(jobId, newStatus);
      
      setJobs(prevJobs =>
        prevJobs.map(job =>
          job.id === jobId ? { ...job, status: newStatus } : job
        )
      );
      
      showSuccess(`Job ${newStatus === 'active' ? 'activated' : newStatus === 'paused' ? 'paused' : 'updated'} successfully`);
    } catch (error) {
      showError('Failed to update job status');
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'closed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatSalary = (salary) => {
    const { min, max, currency, period } = salary;
    const periodText = period === 'annually' ? '/year' : period === 'monthly' ? '/month' : '/hour';
    
    if (min && max) {
      return `${currency} ${min.toLocaleString()} - ${max.toLocaleString()} ${periodText}`;
    } else if (min) {
      return `${currency} ${min.toLocaleString()}+ ${periodText}`;
    }
    return 'Not specified';
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
        <span className="ml-2">Loading job listings...</span>
      </div>
    );
  }

  return (
    <div className="job-listing-dashboard">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Job Listing Dashboard</h2>
        <div className="text-sm text-gray-600">
          {filteredJobs.length} of {jobs.length} jobs
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <span className="text-green-600 text-xl">✅</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Active Jobs</h3>
              <p className="text-2xl font-bold text-gray-900">
                {jobs.filter(job => job.status === 'active').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <span className="text-blue-600 text-xl">👁️</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Views</h3>
              <p className="text-2xl font-bold text-gray-900">
                {jobs.reduce((sum, job) => sum + job.views, 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <span className="text-purple-600 text-xl">📝</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Applications</h3>
              <p className="text-2xl font-bold text-gray-900">
                {jobs.reduce((sum, job) => sum + job.applications, 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <span className="text-yellow-600 text-xl">📊</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Avg. Performance</h3>
              <p className="text-2xl font-bold text-gray-900">
                {jobs.length > 0 ? 
                  (jobs.reduce((sum, job) => sum + job.performance.qualityScore, 0) / jobs.length).toFixed(1)
                  : '0'
                }
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Search */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by title or location..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={filters.status}
              onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="paused">Paused</option>
              <option value="draft">Draft</option>
              <option value="closed">Closed</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
            <select
              value={filters.dateRange}
              onChange={(e) => setFilters(prev => ({ ...prev, dateRange: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Time</option>
              <option value="week">Last Week</option>
              <option value="month">Last Month</option>
              <option value="quarter">Last Quarter</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
            <select
              value={filters.sortBy}
              onChange={(e) => setFilters(prev => ({ ...prev, sortBy: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="created_desc">Newest First</option>
              <option value="created_asc">Oldest First</option>
              <option value="title_asc">Title A-Z</option>
              <option value="title_desc">Title Z-A</option>
              <option value="applications_desc">Most Applications</option>
              <option value="applications_asc">Least Applications</option>
              <option value="views_desc">Most Views</option>
              <option value="views_asc">Least Views</option>
            </select>
          </div>
        </div>
      </div>

      {/* Job Listings Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Job Details
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Performance
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Applications
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Dates
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredJobs.map((job) => (
                <tr key={job.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <div className="text-sm font-medium text-gray-900">{job.title}</div>
                      <div className="text-sm text-gray-500">
                        {job.location.type === 'remote' ? 'Remote' : 
                         `${job.location.city}, ${job.location.country} (${job.location.type})`}
                      </div>
                      <div className="text-sm text-gray-500">{formatSalary(job.salary)}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <select
                      value={job.status}
                      onChange={(e) => handleStatusChange(job.id, e.target.value)}
                      className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border-0 ${getStatusColor(job.status)}`}
                    >
                      <option value="active">Active</option>
                      <option value="paused">Paused</option>
                      <option value="draft">Draft</option>
                      <option value="closed">Closed</option>
                    </select>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col text-sm">
                      <div className="text-gray-900">{job.views} views</div>
                      <div className="text-gray-500">
                        {job.performance.clickRate.toFixed(1)}% click rate
                      </div>
                      <div className="text-gray-500">
                        Quality: {job.performance.qualityScore.toFixed(1)}/10
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col text-sm">
                      <div className="text-lg font-semibold text-gray-900">{job.applications}</div>
                      <div className="text-gray-500">
                        {job.performance.applicationRate.toFixed(1)}% rate
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col text-sm">
                      <div className="text-gray-900">Created: {formatDate(job.createdAt)}</div>
                      <div className="text-gray-500">Deadline: {formatDate(job.deadline)}</div>
                      <div className="text-gray-500">Updated: {formatDate(job.updatedAt)}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex flex-col space-y-1">
                      <button className="text-indigo-600 hover:text-indigo-900 text-left">
                        View Details
                      </button>
                      <button className="text-green-600 hover:text-green-900 text-left">
                        Edit
                      </button>
                      <button className="text-blue-600 hover:text-blue-900 text-left">
                        View Applications
                      </button>
                      <button className="text-purple-600 hover:text-purple-900 text-left">
                        Analytics
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredJobs.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500 text-lg">No jobs found matching your criteria</div>
            <p className="text-gray-400 mt-2">Try adjusting your filters or search terms</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobListingDashboard;
