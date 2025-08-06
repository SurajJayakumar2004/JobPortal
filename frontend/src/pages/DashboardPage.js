import React from 'react';
import { useAuth } from '../contexts/AuthContext';

const DashboardPage = () => {
  const { user } = useAuth();

  return (
    <div className="dashboard-page">
      <div className="container">
        <h1>Welcome to your Dashboard, {user?.full_name}!</h1>
        <div className="dashboard-grid">
          <div className="dashboard-card">
            <h3>🎯 Job Recommendations</h3>
            <p>AI-powered job matching based on your profile</p>
          </div>
          <div className="dashboard-card">
            <h3>📄 Resume Analysis</h3>
            <p>Get AI insights on your resume</p>
          </div>
          <div className="dashboard-card">
            <h3>💼 Applications</h3>
            <p>Track your job applications</p>
          </div>
          <div className="dashboard-card">
            <h3>🎓 Career Counseling</h3>
            <p>Get personalized career guidance</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
