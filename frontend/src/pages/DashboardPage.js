/**
 * User dashboard page - main interface for authenticated users.
 * Displays user profile, resume upload, and personalized content.
 */

import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import ResumeUpload from '../components/ResumeUpload';
import JobList from '../components/JobList';

const DashboardPage = () => {
  const { user, fetchUserProfile } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    // Fetch fresh user data when dashboard loads
    if (!user) {
      fetchUserProfile();
    }
  }, [user, fetchUserProfile]);

  /**
   * Render tab content based on active tab
   */
  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="tab-content">
            <h2>Dashboard Overview</h2>
            <div className="dashboard-stats">
              <div className="stat-card">
                <h3>Profile Status</h3>
                <p>{user ? 'Active' : 'Loading...'}</p>
              </div>
              <div className="stat-card">
                <h3>Account Type</h3>
                <p>{user?.role || 'N/A'}</p>
              </div>
              <div className="stat-card">
                <h3>Member Since</h3>
                <p>{user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}</p>
              </div>
            </div>
            
            <div className="recent-activity">
              <h3>Quick Actions</h3>
              <div className="action-buttons">
                <button 
                  onClick={() => setActiveTab('resume')}
                  className="btn btn-primary"
                >
                  Upload Resume
                </button>
                <button 
                  onClick={() => setActiveTab('jobs')}
                  className="btn btn-secondary"
                >
                  Browse Jobs
                </button>
              </div>
            </div>
          </div>
        );

      case 'resume':
        return (
          <div className="tab-content">
            <h2>Resume Management</h2>
            <ResumeUpload />
          </div>
        );

      case 'jobs':
        return (
          <div className="tab-content">
            <h2>Job Opportunities</h2>
            <JobList />
          </div>
        );

      case 'profile':
        return (
          <div className="tab-content">
            <h2>Profile Settings</h2>
            <div className="profile-info">
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={user?.email || ''} disabled />
              </div>
              <div className="form-group">
                <label>Role</label>
                <input type="text" value={user?.role || ''} disabled />
              </div>
              <div className="form-group">
                <label>Account Status</label>
                <input type="text" value="Active" disabled />
              </div>
            </div>
          </div>
        );

      default:
        return <div>Tab not found</div>;
    }
  };

  return (
    <div className="container">
      <div className="dashboard">
        <div className="dashboard-header">
          <h1>Welcome to Your Dashboard</h1>
          <p>Hi {user?.email}, here's what's happening with your job search</p>
        </div>

        {/* Dashboard Navigation Tabs */}
        <div className="dashboard-nav">
          <button
            className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </button>
          <button
            className={`tab-button ${activeTab === 'resume' ? 'active' : ''}`}
            onClick={() => setActiveTab('resume')}
          >
            Resume
          </button>
          <button
            className={`tab-button ${activeTab === 'jobs' ? 'active' : ''}`}
            onClick={() => setActiveTab('jobs')}
          >
            Jobs
          </button>
          <button
            className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => setActiveTab('profile')}
          >
            Profile
          </button>
        </div>

        {/* Tab Content */}
        <div className="dashboard-content">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
