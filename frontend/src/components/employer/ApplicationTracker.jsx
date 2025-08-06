/**
 * Application Tracker Component - Placeholder
 * Application Tracking System (ATS) functionality
 */

import React from 'react';

const ApplicationTracker = () => {
  return (
    <div className="application-tracker">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Application Tracking System</h2>
      <div className="bg-white p-8 rounded-lg shadow-md text-center">
        <div className="text-6xl mb-4">📋</div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">ATS - Application Tracking</h3>
        <p className="text-gray-600 mb-4">
          Track application progress through hiring stages and manage candidate pipelines.
        </p>
        <div className="text-sm text-gray-500">
          Features include: Stage management, bulk actions, hiring funnel analytics, and workflow automation.
        </div>
      </div>
    </div>
  );
};

export default ApplicationTracker;
