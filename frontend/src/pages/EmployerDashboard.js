import React from 'react';

const EmployerDashboard = () => {
  return (
    <div className="employer-dashboard">
      <div className="container">
        <h1>Employer Dashboard</h1>
        <div className="dashboard-grid">
          <div className="dashboard-card">
            <h3>📋 Job Postings</h3>
            <p>Manage your job listings</p>
          </div>
          <div className="dashboard-card">
            <h3>🤖 AI Candidate Matching</h3>
            <p>Find the best candidates with AI</p>
          </div>
          <div className="dashboard-card">
            <h3>📊 Analytics</h3>
            <p>View application analytics</p>
          </div>
          <div className="dashboard-card">
            <h3>💬 Communication</h3>
            <p>Communicate with candidates</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmployerDashboard;
