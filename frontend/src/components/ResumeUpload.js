/**
 * Resume upload component with AI analysis and feedback display.
 * Critical component that handles file upload and shows AI insights.
 */

import React, { useState } from 'react';
import { resumeAPI } from '../services/api';
import { getStatusErrorMessage } from '../utils/errorHandler';

const ResumeUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [error, setError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState(false);

  /**
   * Handle file selection
   */
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    
    if (!file) {
      setSelectedFile(null);
      return;
    }

    // Validate file type
    const allowedTypes = ['.pdf', '.docx', '.doc'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
      setError('Please select a PDF, DOC, or DOCX file');
      setSelectedFile(null);
      return;
    }

    // Validate file size (10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      setError('File size must be less than 10MB');
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
    setError('');
    setFeedback(null);
    setUploadSuccess(false);
  };

  /**
   * Handle file upload and processing
   */
  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError('');
    setFeedback(null);

    try {
      // Upload resume to backend for AI analysis
      const response = await resumeAPI.uploadResume(selectedFile);
      
      // Extract feedback data from response
      const data = response.data;
      setFeedback(data);
      setUploadSuccess(true);
      
      console.log('Resume upload successful:', data);
    } catch (error) {
      console.error('Resume upload failed:', error);
      setError(getStatusErrorMessage(error));
    } finally {
      setLoading(false);
    }
  };

  /**
   * Render AI feedback results
   */
  const renderFeedback = () => {
    if (!feedback) return null;

    return (
      <div className="feedback-results">
        <h3>🤖 AI Analysis Results</h3>
        
        {/* ATS Score */}
        {feedback.ats_score && (
          <div className="feedback-section">
            <h4>ATS Compatibility Score</h4>
            <div className="score-display">
              <span className="score">{feedback.ats_score}%</span>
              <div className="score-bar">
                <div 
                  className="score-fill" 
                  style={{ width: `${feedback.ats_score}%` }}
                ></div>
              </div>
            </div>
            <p className="score-description">
              {feedback.ats_score >= 80 ? 'Excellent ATS compatibility!' :
               feedback.ats_score >= 60 ? 'Good ATS compatibility with room for improvement.' :
               'Consider optimizing your resume for ATS systems.'}
            </p>
          </div>
        )}

        {/* Skills Analysis */}
        {feedback.skills && feedback.skills.length > 0 && (
          <div className="feedback-section">
            <h4>Skills Identified</h4>
            <div className="skills-list">
              {feedback.skills.map((skill, index) => (
                <span key={index} className="skill-tag">{skill}</span>
              ))}
            </div>
          </div>
        )}

        {/* Skill Gaps */}
        {feedback.skill_gaps && feedback.skill_gaps.length > 0 && (
          <div className="feedback-section">
            <h4>Skill Gaps to Address</h4>
            <ul className="gaps-list">
              {feedback.skill_gaps.map((gap, index) => (
                <li key={index}>{gap}</li>
              ))}
            </ul>
          </div>
        )}

        {/* AI Suggestions */}
        {feedback.suggestions && feedback.suggestions.length > 0 && (
          <div className="feedback-section">
            <h4>💡 AI Recommendations</h4>
            <ul className="suggestions-list">
              {feedback.suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Overall Summary */}
        {feedback.summary && (
          <div className="feedback-section">
            <h4>Summary</h4>
            <p>{feedback.summary}</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="resume-upload">
      <div className="upload-section">
        <h3>📄 Upload Your Resume</h3>
        <p>Upload your resume to get AI-powered feedback and insights</p>

        {/* File Input */}
        <div className="file-input-container">
          <input
            type="file"
            id="resume-file"
            accept=".pdf,.doc,.docx"
            onChange={handleFileSelect}
            className="file-input"
          />
          <label htmlFor="resume-file" className="file-input-label">
            {selectedFile ? selectedFile.name : 'Choose Resume File'}
          </label>
        </div>

        {/* File Info */}
        {selectedFile && (
          <div className="file-info">
            <p>Selected: {selectedFile.name}</p>
            <p>Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
        )}

        {/* Upload Button */}
        <button
          onClick={handleUpload}
          disabled={!selectedFile || loading}
          className="btn btn-primary upload-button"
        >
          {loading ? 'Analyzing Resume...' : 'Upload & Analyze'}
        </button>

        {/* Error Display */}
        {error && <div className="error-message">{error}</div>}

        {/* Success Message */}
        {uploadSuccess && !loading && (
          <div className="success-message">
            Resume uploaded and analyzed successfully!
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="loading-state">
            <p>🔄 Our AI is analyzing your resume...</p>
            <p>This may take a few moments.</p>
          </div>
        )}
      </div>

      {/* AI Feedback Display */}
      {renderFeedback()}
    </div>
  );
};

export default ResumeUpload;
