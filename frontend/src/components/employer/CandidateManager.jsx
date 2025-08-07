/**
 * Candidate Manager Component - Enhanced
 * Handles candidate profiles, applications, and screening with AI-powered matching
 */

import React, { useState, useEffect } from 'react';
import { useToast } from '../Toast';
import dataService from '../../services/dataService';

const CandidateManager = () => {
  const [candidates, setCandidates] = useState([]);
  const [filteredCandidates, setFilteredCandidates] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState({
    skills: '',
    experience: '',
    location: '',
    availability: 'all'
  });
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const { showSuccess, showError } = useToast();

  useEffect(() => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    loadCandidates();
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    filterCandidates();
  }, [candidates, filters]);

  const loadCandidates = async () => {
    try {
      setIsLoading(true);
      // Load candidates from data service
      const candidatesData = await dataService.getAllCandidates();
      // Map data structure to match component expectations
      const formattedCandidates = candidatesData.map(candidate => ({
        id: candidate.user_id,
        name: candidate.user_name,
        email: candidate.user_email,
        phone: candidate.phone || '+1 (555) 000-0000',
        location: candidate.location,
        skills: candidate.skills,
        experience_level: candidate.experience_level,
        years_experience: candidate.years_experience,
        education: candidate.education,
        current_position: candidate.current_position,
        salary_expectation: candidate.salary_expectation,
        availability: candidate.availability,
        resume_summary: candidate.resume_summary,
        languages: candidate.languages || ['English'],
        certifications: candidate.certifications || [],
        portfolio_url: candidate.portfolio,
        linkedin_url: candidate.linkedin,
        github_url: candidate.github_url || '',
        applied_jobs: Math.floor(Math.random() * 10) + 1, // Random for demo
        last_active: new Date().toISOString().split('T')[0],
        match_score: candidate.match_score || 85.0
      }));
      setCandidates(formattedCandidates);
    } catch (error) {
      console.error('Error loading candidates:', error);
      showError('Failed to load candidates');
    } finally {
      setIsLoading(false);
    }
  };

  const filterCandidates = () => {
    let filtered = candidates;

    if (filters.skills) {
      const skillsArray = filters.skills.toLowerCase().split(',').map(s => s.trim());
      filtered = filtered.filter(candidate =>
        skillsArray.some(skill =>
          candidate.skills.some(candidateSkill =>
            candidateSkill.toLowerCase().includes(skill)
          )
        )
      );
    }

    if (filters.experience) {
      filtered = filtered.filter(candidate =>
        candidate.experience_level === filters.experience
      );
    }

    if (filters.location) {
      filtered = filtered.filter(candidate =>
        candidate.location.toLowerCase().includes(filters.location.toLowerCase())
      );
    }

    if (filters.availability !== 'all') {
      filtered = filtered.filter(candidate =>
        candidate.availability === filters.availability
      );
    }

    setFilteredCandidates(filtered);
  };

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  const handleContactCandidate = (candidate) => {
    showSuccess(`Contact information for ${candidate.name} has been noted. You can reach them at ${candidate.email}`);
  };

  const handleViewProfile = (candidate) => {
    setSelectedCandidate(candidate);
    setShowDetails(true);
  };

  const handleDownloadResume = (candidate) => {
    showSuccess(`Resume download initiated for ${candidate.name}`);
    // In production, this would trigger an actual download
  };

  const getAvailabilityText = (availability) => {
    switch (availability) {
      case 'immediately': return 'Available immediately';
      case '2_weeks': return 'Available in 2 weeks';
      case '1_month': return 'Available in 1 month';
      default: return 'Not specified';
    }
  };

  const getMatchScoreColor = (score) => {
    if (score >= 90) return 'bg-green-100 text-green-800';
    if (score >= 80) return 'bg-blue-100 text-blue-800';
    if (score >= 70) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  if (showDetails && selectedCandidate) {
    return (
      <div className="bg-white rounded-lg shadow-md">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">Candidate Profile</h2>
            <button
              onClick={() => setShowDetails(false)}
              className="text-gray-600 hover:text-gray-900"
            >
              ← Back to Candidates
            </button>
          </div>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Profile */}
            <div className="lg:col-span-2 space-y-6">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900">{selectedCandidate.name}</h3>
                  <p className="text-gray-600">{selectedCandidate.current_position}</p>
                  <p className="text-gray-500">{selectedCandidate.location}</p>
                  <div className="flex items-center mt-2">
                    <span className="text-sm font-medium text-gray-600 mr-2">Match Score:</span>
                    <div className={`px-3 py-1 rounded-full text-sm font-bold ${getMatchScoreColor(selectedCandidate.match_score)}`}>
                      {selectedCandidate.match_score}%
                    </div>
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleContactCandidate(selectedCandidate)}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
                  >
                    Contact
                  </button>
                  <button
                    onClick={() => handleDownloadResume(selectedCandidate)}
                    className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
                  >
                    Download Resume
                  </button>
                </div>
              </div>

              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Summary</h4>
                <p className="text-gray-700">{selectedCandidate.resume_summary}</p>
              </div>

              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Skills</h4>
                <div className="flex flex-wrap gap-2">
                  {selectedCandidate.skills.map((skill, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-indigo-100 text-indigo-800 rounded-full text-sm"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>

              <div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">Certifications</h4>
                <ul className="list-disc list-inside text-gray-700">
                  {selectedCandidate.certifications.map((cert, index) => (
                    <li key={index}>{cert}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">Contact Information</h4>
                <div className="space-y-2 text-sm">
                  <p><span className="font-medium">Email:</span> {selectedCandidate.email}</p>
                  <p><span className="font-medium">Phone:</span> {selectedCandidate.phone}</p>
                  <p><span className="font-medium">Location:</span> {selectedCandidate.location}</p>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">Experience</h4>
                <div className="space-y-2 text-sm">
                  <p><span className="font-medium">Level:</span> {selectedCandidate.experience_level}</p>
                  <p><span className="font-medium">Years:</span> {selectedCandidate.years_experience} years</p>
                  <p><span className="font-medium">Education:</span> {selectedCandidate.education}</p>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">Preferences</h4>
                <div className="space-y-2 text-sm">
                  <p><span className="font-medium">Salary:</span> {selectedCandidate.salary_expectation}</p>
                  <p><span className="font-medium">Availability:</span> {getAvailabilityText(selectedCandidate.availability)}</p>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-3">Links</h4>
                <div className="space-y-2">
                  <a href={selectedCandidate.portfolio_url} target="_blank" rel="noopener noreferrer" className="block text-indigo-600 hover:text-indigo-800 text-sm">Portfolio</a>
                  <a href={selectedCandidate.linkedin_url} target="_blank" rel="noopener noreferrer" className="block text-indigo-600 hover:text-indigo-800 text-sm">LinkedIn</a>
                  <a href={selectedCandidate.github_url} target="_blank" rel="noopener noreferrer" className="block text-indigo-600 hover:text-indigo-800 text-sm">GitHub</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900">Candidate Database</h2>
        <p className="text-gray-600 mt-1">Browse and filter through available candidates with AI-powered matching</p>
      </div>

      {/* Filters */}
      <div className="p-6 border-b border-gray-200 bg-gray-50">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Skills</label>
            <input
              type="text"
              value={filters.skills}
              onChange={(e) => handleFilterChange('skills', e.target.value)}
              placeholder="e.g., JavaScript, React"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Experience Level</label>
            <select
              value={filters.experience}
              onChange={(e) => handleFilterChange('experience', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Levels</option>
              <option value="entry">Entry Level</option>
              <option value="mid">Mid Level</option>
              <option value="senior">Senior Level</option>
              <option value="executive">Executive</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Location</label>
            <input
              type="text"
              value={filters.location}
              onChange={(e) => handleFilterChange('location', e.target.value)}
              placeholder="City, State"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Availability</label>
            <select
              value={filters.availability}
              onChange={(e) => handleFilterChange('availability', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All</option>
              <option value="immediately">Immediately</option>
              <option value="2_weeks">2 Weeks</option>
              <option value="1_month">1 Month</option>
            </select>
          </div>
        </div>
      </div>

      {/* Candidates List */}
      <div className="p-6">
        {isLoading ? (
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : (
          <>
            <div className="mb-4 text-sm text-gray-600">
              Showing {filteredCandidates.length} of {candidates.length} candidates
            </div>

            <div className="space-y-4">
              {filteredCandidates.map((candidate) => (
                <div key={candidate.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center mb-2">
                        <h3 className="text-lg font-semibold text-gray-900 mr-3">{candidate.name}</h3>
                        <div className={`px-3 py-1 rounded-full text-sm font-bold ${getMatchScoreColor(candidate.match_score)}`}>
                          {candidate.match_score}% match
                        </div>
                      </div>
                      
                      <p className="text-gray-600 mb-1">{candidate.current_position}</p>
                      <p className="text-gray-500 text-sm mb-2">{candidate.location} • {getAvailabilityText(candidate.availability)}</p>
                      
                      <div className="mb-3">
                        <div className="flex flex-wrap gap-1">
                          {candidate.skills.slice(0, 5).map((skill, index) => (
                            <span
                              key={index}
                              className="inline-flex px-2 py-1 text-xs bg-indigo-100 text-indigo-800 rounded-md"
                            >
                              {skill}
                            </span>
                          ))}
                          {candidate.skills.length > 5 && (
                            <span className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-md">
                              +{candidate.skills.length - 5} more
                            </span>
                          )}
                        </div>
                      </div>

                      <p className="text-sm text-gray-600 line-clamp-2">{candidate.resume_summary}</p>
                    </div>
                    
                    <div className="ml-6 flex flex-col space-y-2">
                      <button
                        onClick={() => handleViewProfile(candidate)}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-sm"
                      >
                        View Profile
                      </button>
                      <button
                        onClick={() => handleContactCandidate(candidate)}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 text-sm"
                      >
                        Contact
                      </button>
                      <button
                        onClick={() => handleDownloadResume(candidate)}
                        className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 text-sm"
                      >
                        Resume
                      </button>
                    </div>
                  </div>
                </div>
              ))}

              {filteredCandidates.length === 0 && (
                <div className="text-center py-8">
                  <div className="text-gray-400 text-5xl mb-4">👥</div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">No candidates found</h3>
                  <p className="text-gray-600">
                    Try adjusting your filters to see more candidates.
                  </p>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default CandidateManager;
