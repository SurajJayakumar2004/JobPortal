/**
 * Comprehensive Employer Dashboard - Main interface for employer users
 * Provides access to all employer-specific features and management tools
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../components/Toast';
import ErrorBoundary from '../components/ErrorBoundary';

// Import employer-specific components
import EmployerProfile from '../components/employer/EmployerProfile';
import JobPostingManager from '../components/employer/JobPostingManager';
import JobListingDashboard from '../components/employer/JobListingDashboard';
import CandidateManager from '../components/employer/CandidateManager';
import AIRecommendations from '../components/employer/AIRecommendations';
import ApplicationTracker from '../components/employer/ApplicationTracker';
import SecuritySettings from '../components/employer/SecuritySettings';
import dataService from '../services/dataService';

const EmployerDashboard = () => {
  const { user } = useAuth();
  const { showWarning } = useToast();
  const [activeTab, setActiveTab] = useState('overview');
  const [companyProfile, setCompanyProfile] = useState(null);
  const [dashboardStats, setDashboardStats] = useState({
    activeJobs: 0,
    totalApplications: 0,
    newApplications: 0,
    interviewsScheduled: 0,
    hiredCandidates: 0
  });

  useEffect(() => {
    // Check if user is an employer
    if (user?.role !== 'employer') {
      showWarning('Access denied. This dashboard is for employers only.');
      return;
    }
    
    // Initialize employer dashboard data
    initializeDashboard();
  }, [user]);

  const initializeDashboard = async () => {
    try {
      // Fetch dashboard statistics from data service
      const stats = await dataService.getJobStatistics();
      setDashboardStats({
        activeJobs: stats.active_jobs,
        totalApplications: stats.total_applications,
        newApplications: Math.floor(stats.total_applications * 0.2), // Simulate 20% new applications
        interviewsScheduled: Math.floor(stats.total_applications * 0.1), // Simulate 10% interviews
        hiredCandidates: Math.floor(stats.total_applications * 0.05) // Simulate 5% hired
      });
    } catch (error) {
      console.error('Failed to initialize employer dashboard:', error);
      // Fallback to default values
      setDashboardStats({
        activeJobs: 0,
        totalApplications: 0,
        newApplications: 0,
        interviewsScheduled: 0,
        hiredCandidates: 0
      });
    }
  };

  const tabConfig = [
    { id: 'overview', label: 'Dashboard Overview', icon: '📊' },
    { id: 'profile', label: 'Company Profile', icon: '🏢' },
    { id: 'jobs', label: 'Job Management', icon: '💼' },
    { id: 'candidates', label: 'Candidates', icon: '👥' },
    { id: 'ai-recommendations', label: 'AI Matching', icon: '🤖' },
    { id: 'ats', label: 'Application Tracking', icon: '📋' },
    { id: 'security', label: 'Security Settings', icon: '🔒' }
  ];

  const renderOverview = () => (
    <div className="employer-overview">
      <div className="overview-header">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Welcome back, {companyProfile?.name || 'Employer'}!
        </h2>
        <p className="text-gray-600 mb-8">
          Here's a summary of your hiring activities and platform performance.
        </p>
      </div>

      {/* Key Metrics */}
      <div className="metrics-grid grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <div className="metric-card bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <span className="text-blue-600 text-xl">💼</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Active Jobs</h3>
              <p className="text-2xl font-bold text-gray-900">{dashboardStats.activeJobs}</p>
            </div>
          </div>
        </div>

        <div className="metric-card bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <span className="text-green-600 text-xl">📝</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Total Applications</h3>
              <p className="text-2xl font-bold text-gray-900">{dashboardStats.totalApplications}</p>
            </div>
          </div>
        </div>

        <div className="metric-card bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <span className="text-yellow-600 text-xl">🔔</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">New Applications</h3>
              <p className="text-2xl font-bold text-gray-900">{dashboardStats.newApplications}</p>
            </div>
          </div>
        </div>

        <div className="metric-card bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <span className="text-purple-600 text-xl">🗓️</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Interviews Scheduled</h3>
              <p className="text-2xl font-bold text-gray-900">{dashboardStats.interviewsScheduled}</p>
            </div>
          </div>
        </div>

        <div className="metric-card bg-white p-6 rounded-lg shadow-md">
          <div className="flex items-center">
            <div className="p-3 bg-indigo-100 rounded-lg">
              <span className="text-indigo-600 text-xl">✅</span>
            </div>
            <div className="ml-4">
              <h3 className="text-sm font-medium text-gray-500">Hired</h3>
              <p className="text-2xl font-bold text-gray-900">{dashboardStats.hiredCandidates}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions bg-white p-6 rounded-lg shadow-md mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => setActiveTab('jobs')}
            className="flex items-center p-4 bg-indigo-50 hover:bg-indigo-100 rounded-lg transition-colors"
          >
            <span className="text-2xl mr-3">➕</span>
            <div className="text-left">
              <h4 className="font-medium text-gray-900">Post New Job</h4>
              <p className="text-sm text-gray-600">Create a new job listing</p>
            </div>
          </button>

          <button
            onClick={() => setActiveTab('candidates')}
            className="flex items-center p-4 bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
          >
            <span className="text-2xl mr-3">👥</span>
            <div className="text-left">
              <h4 className="font-medium text-gray-900">Review Applications</h4>
              <p className="text-sm text-gray-600">Check new candidate applications</p>
            </div>
          </button>

          <button
            onClick={() => setActiveTab('ai-recommendations')}
            className="flex items-center p-4 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors"
          >
            <span className="text-2xl mr-3">🤖</span>
            <div className="text-left">
              <h4 className="font-medium text-gray-900">AI Recommendations</h4>
              <p className="text-sm text-gray-600">View AI-matched candidates</p>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="recent-activity bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-green-500 mr-3">✅</span>
            <div>
              <p className="text-sm font-medium">New application received for "Senior Developer"</p>
              <p className="text-xs text-gray-500">2 hours ago</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-blue-500 mr-3">📝</span>
            <div>
              <p className="text-sm font-medium">Job posting "Marketing Manager" was published</p>
              <p className="text-xs text-gray-500">5 hours ago</p>
            </div>
          </div>
          <div className="flex items-center p-3 bg-gray-50 rounded-lg">
            <span className="text-purple-500 mr-3">🤖</span>
            <div>
              <p className="text-sm font-medium">AI recommended 3 new candidates for "UX Designer"</p>
              <p className="text-xs text-gray-500">1 day ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'profile':
        return <EmployerProfile companyProfile={companyProfile} setCompanyProfile={setCompanyProfile} />;
      case 'jobs':
        return <JobPostingManager />;
      case 'candidates':
        return <CandidateManager />;
      case 'ai-recommendations':
        return <AIRecommendations />;
      case 'ats':
        return <ApplicationTracker />;
      case 'security':
        return <SecuritySettings />;
      default:
        return renderOverview();
    }
  };

  if (user?.role !== 'employer') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h1>
          <p className="text-gray-600">This dashboard is only available to employer accounts.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="employer-dashboard min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Enhanced Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-2 overflow-x-auto bg-white rounded-2xl shadow-sm p-2">
              {tabConfig.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center whitespace-nowrap py-3 px-4 rounded-xl font-semibold text-sm transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-lg transform scale-105'
                      : 'text-gray-600 hover:text-gray-800 hover:bg-gray-50'
                  }`}
                >
                  <span className="mr-2 text-base">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <ErrorBoundary componentName={`EmployerDashboard-${activeTab}`}>
          {renderTabContent()}
        </ErrorBoundary>
      </div>
    </div>
  );
};

export default EmployerDashboard;
