/**
 * Security Settings Component - Placeholder
 * Account security and access management
 */

import React from 'react';

const SecuritySettings = () => {
  return (
    <div className="security-settings">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Security Settings</h2>
        <p className="text-gray-600">Manage account security and access controls</p>
      </div>
      <div className="card-modern text-center py-16">
        <div className="text-6xl mb-6">🔒</div>
        <h3 className="text-xl font-semibold text-gray-900 mb-4">Security & Access</h3>
        <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
          Manage account security, multi-factor authentication, and team access controls.
          Keep your company data safe with enterprise-grade security features.
        </p>
        <div className="bg-gray-50 rounded-lg p-6 max-w-3xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-700">
            <div className="flex items-center">
              <span className="mr-2">🔐</span>
              Multi-factor authentication
            </div>
            <div className="flex items-center">
              <span className="mr-2">👥</span>
              Role management
            </div>
            <div className="flex items-center">
              <span className="mr-2">📝</span>
              Audit logs
            </div>
            <div className="flex items-center">
              <span className="mr-2">✅</span>
              Compliance controls
            </div>
          </div>
        </div>
        <div className="mt-8">
          <button className="btn-modern-primary">
            <span className="mr-2">🚀</span>
            Coming Soon
          </button>
        </div>
      </div>
    </div>
  );
};

export default SecuritySettings;
