/**
 * Communication Center Component - Placeholder
 * Handles messaging and interview scheduling
 */

import React from 'react';

const CommunicationCenter = () => {
  return (
    <div className="communication-center">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Communication Center</h2>
      <div className="bg-white p-8 rounded-lg shadow-md text-center">
        <div className="text-6xl mb-4">💬</div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Communication & Scheduling</h3>
        <p className="text-gray-600 mb-4">
          Manage candidate communications, interview scheduling, and message templates.
        </p>
        <div className="text-sm text-gray-500">
          Features include: In-platform messaging, interview scheduling, calendar integration, and template management.
        </div>
      </div>
    </div>
  );
};

export default CommunicationCenter;
