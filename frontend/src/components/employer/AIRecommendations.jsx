/**
 * AI-Powered Candidate Matching & Recommendations Component
 * Provides intelligent candidate screening, job matching, and hiring insights
 */

import React, { useState, useEffect } from 'react';
import { useToast } from '../Toast';
import dataService from '../../services/dataService';
import aiMatchingAPI from '../../services/aiMatchingAPI';

const AIRecommendations = () => {
  const { showSuccess, showError, showInfo } = useToast();
  const [activeTab, setActiveTab] = useState('candidates');
  const [isLoading, setIsLoading] = useState(false);
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [employerStats, setEmployerStats] = useState(null);
  const [jobInsights, setJobInsights] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);
  const [skillGapAnalysis, setSkillGapAnalysis] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setIsLoading(true);
    try {
      // Load jobs
      const jobsData = await dataService.getAllJobs();
      const openJobs = jobsData.filter(job => job.status === 'open');
      setJobs(openJobs);
      
      if (openJobs.length > 0) {
        setSelectedJob(openJobs[0]);
        await loadCandidatesForJob(openJobs[0]._id);
      }

      // Load employer statistics
      const stats = await aiMatchingAPI.getEmployerMatchingStats();
      setEmployerStats(stats.data);

    } catch (error) {
      console.error('Error loading initial data:', error);
      showError('Failed to load AI recommendations data');
    } finally {
      setIsLoading(false);
    }
  };

  const loadCandidatesForJob = async (jobId) => {
    if (!jobId) return;
    
    setIsLoading(true);
    try {
      const response = await aiMatchingAPI.getCandidatesForJob(jobId);
      setCandidates(response.data.candidates || []);
      
      // Load job insights
      const insights = await aiMatchingAPI.getJobInsights(jobId);
      setJobInsights(insights.data);
      
      showInfo(`Found ${response.data.candidates?.length || 0} AI-matched candidates`);
    } catch (error) {
      console.error('Error loading candidates:', error);
      showError('Failed to load AI-matched candidates');
    } finally {
      setIsLoading(false);
    }
  };

  const handleJobChange = async (jobId) => {
    const job = jobs.find(j => j._id === jobId);
    setSelectedJob(job);
    await loadCandidatesForJob(jobId);
  };

  const analyzeSkillGap = async (candidate) => {
    if (!selectedJob || !candidate) return;
    
    setIsLoading(true);
    try {
      const analysis = await aiMatchingAPI.analyzeSkillGap(candidate.user_id, selectedJob._id);
      setSkillGapAnalysis(analysis.data);
      setSelectedCandidate(candidate);
      showSuccess('Skill gap analysis completed');
    } catch (error) {
      console.error('Error analyzing skill gap:', error);
      showError('Failed to analyze skill gap');
    } finally {
      setIsLoading(false);
    }
  };

  const getMatchScoreColor = (score) => {
    if (score >= 90) return 'bg-gradient-to-r from-green-400 to-green-600';
    if (score >= 80) return 'bg-gradient-to-r from-blue-400 to-blue-600';
    if (score >= 70) return 'bg-gradient-to-r from-yellow-400 to-yellow-600';
    if (score >= 60) return 'bg-gradient-to-r from-orange-400 to-orange-600';
    return 'bg-gradient-to-r from-red-400 to-red-600';
  };

  const getMatchScoreLabel = (score) => {
    if (score >= 90) return 'Excellent Match';
    if (score >= 80) return 'Strong Match';
    if (score >= 70) return 'Good Match';
    if (score >= 60) return 'Fair Match';
    return 'Weak Match';
  };

  const renderCandidateMatching = () => (
    <div className="ai-candidate-matching">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">AI-Powered Candidate Matching</h2>
        <p className="text-gray-600">Advanced machine learning algorithms rank candidates by job compatibility</p>
      </div>

      {/* Job Selection */}
      <div className="card-modern mb-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <span className="mr-2">🎯</span>
          Select Job for AI Analysis
        </h3>
        
        {jobs.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">📋</div>
            <p className="text-gray-600">No open jobs available for AI matching</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {jobs.map((job) => (
              <div
                key={job._id}
                onClick={() => handleJobChange(job._id)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${
                  selectedJob?._id === job._id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-semibold text-gray-900">{job.title}</h4>
                    <p className="text-sm text-gray-600">{job.company_name}</p>
                    <p className="text-xs text-gray-500 flex items-center mt-1">
                      <span className="mr-1">📍</span>
                      {job.location}
                    </p>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-indigo-600">{job.applications_count || 0}</div>
                    <div className="text-xs text-gray-500">Applications</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* AI-Matched Candidates */}
      {selectedJob && (
        <div className="card-modern">
          <div className="flex justify-between items-center mb-6">
            <div>
              <h3 className="text-xl font-semibold text-gray-900 flex items-center">
                <span className="mr-2">🤖</span>
                AI-Ranked Candidates for "{selectedJob.title}"
              </h3>
              <p className="text-gray-600 mt-1">Candidates ranked by machine learning compatibility score</p>
            </div>
            <button
              onClick={() => loadCandidatesForJob(selectedJob._id)}
              className="btn-modern-secondary flex items-center"
              disabled={isLoading}
            >
              <span className="mr-2">🔄</span>
              Refresh Analysis
            </button>
          </div>

          {isLoading ? (
            <div className="loading-container py-12">
              <div className="loading-spinner"></div>
              <div className="loading-text">Running AI analysis...</div>
            </div>
          ) : candidates.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-6xl mb-4">🔍</div>
              <h4 className="text-lg font-semibold text-gray-900 mb-2">No Candidates Found</h4>
              <p className="text-gray-600">No applications have been received for this job yet.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {candidates.map((candidate, index) => (
                <div key={candidate.user_id} className="candidate-match-card border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow duration-200">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center">
                      <div className="w-12 h-12 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mr-4">
                        <span className="text-xl font-bold text-indigo-600">#{index + 1}</span>
                      </div>
                      <div>
                        <h4 className="text-lg font-semibold text-gray-900">{candidate.user_name}</h4>
                        <p className="text-gray-600">{candidate.user_email}</p>
                        <p className="text-sm text-gray-500 mt-1">{candidate.location} • {candidate.years_experience} years exp.</p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <div className={`px-4 py-2 rounded-full text-white font-bold text-sm ${getMatchScoreColor(candidate.match_score)}`}>
                        {candidate.match_score.toFixed(1)}% Match
                      </div>
                      <p className="text-xs text-gray-500 mt-1">{getMatchScoreLabel(candidate.match_score)}</p>
                    </div>
                  </div>

                  <div className="mb-4">
                    <p className="text-gray-700 text-sm leading-relaxed">{candidate.summary}</p>
                  </div>

                  {/* Skills Analysis */}
                  <div className="mb-4">
                    <div className="flex flex-wrap gap-2 mb-2">
                      <span className="text-sm font-medium text-gray-700">Matching Skills:</span>
                      {candidate.matching_skills.slice(0, 5).map((skill, idx) => (
                        <span key={idx} className="inline-flex px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                          ✓ {skill}
                        </span>
                      ))}
                      {candidate.matching_skills.length > 5 && (
                        <span className="inline-flex px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                          +{candidate.matching_skills.length - 5} more
                        </span>
                      )}
                    </div>
                    
                    {candidate.missing_skills.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        <span className="text-sm font-medium text-gray-700">Missing Skills:</span>
                        {candidate.missing_skills.slice(0, 3).map((skill, idx) => (
                          <span key={idx} className="inline-flex px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
                            ✗ {skill}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Key Achievements */}
                  {candidate.key_achievements && (
                    <div className="mb-4">
                      <span className="text-sm font-medium text-gray-700 block mb-2">Key Achievements:</span>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {candidate.key_achievements.slice(0, 2).map((achievement, idx) => (
                          <li key={idx} className="flex items-start">
                            <span className="mr-2">•</span>
                            {achievement}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex space-x-3 pt-4 border-t border-gray-100">
                    <button className="btn-modern-primary text-sm flex-1">
                      <span className="mr-1">👁️</span>
                      View Full Profile
                    </button>
                    <button
                      onClick={() => analyzeSkillGap(candidate)}
                      className="btn-modern-secondary text-sm flex-1"
                    >
                      <span className="mr-1">📊</span>
                      Skill Gap Analysis
                    </button>
                    <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200">
                      <span className="mr-1">�</span>
                      Contact
                    </button>
                    <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-200">
                      <span className="mr-1">⭐</span>
                      Shortlist
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderJobInsights = () => (
    <div className="job-insights">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Job Insights & Analytics</h2>
        <p className="text-gray-600">AI-powered insights about your job postings and hiring trends</p>
      </div>

      {selectedJob && jobInsights && (
        <div className="space-y-6">
          {/* Application Trends */}
          <div className="card-modern">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <span className="mr-2">📈</span>
              Application Trends
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-indigo-600">{jobInsights.application_trends.total_applications}</div>
                <div className="text-sm text-gray-600">Total Applications</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{jobInsights.application_trends.applications_this_week}</div>
                <div className="text-sm text-gray-600">This Week</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{jobInsights.application_trends.application_rate}</div>
                <div className="text-sm text-gray-600">Daily Rate</div>
              </div>
              <div className="text-center">
                <div className={`text-2xl font-bold ${jobInsights.application_trends.trending_up ? 'text-green-600' : 'text-red-600'}`}>
                  {jobInsights.application_trends.trending_up ? '↗️' : '↘️'}
                </div>
                <div className="text-sm text-gray-600">Trend</div>
              </div>
            </div>
          </div>

          {/* Candidate Quality */}
          <div className="card-modern">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <span className="mr-2">⭐</span>
              Candidate Quality Analysis
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{jobInsights.candidate_quality.average_match_score}%</div>
                <div className="text-sm text-gray-600">Average Match Score</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{jobInsights.candidate_quality.high_quality_candidates}</div>
                <div className="text-sm text-gray-600">High Quality Candidates</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{jobInsights.candidate_quality.candidates_above_80_percent}</div>
                <div className="text-sm text-gray-600">Above 80% Match</div>
              </div>
            </div>
          </div>

          {/* AI Recommendations */}
          <div className="card-modern">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <span className="mr-2">💡</span>
              AI Recommendations
            </h3>
            <div className="space-y-3">
              {jobInsights.recommendations.map((recommendation, index) => (
                <div key={index} className="flex items-start p-3 bg-blue-50 rounded-lg">
                  <span className="mr-3 text-blue-600">💡</span>
                  <p className="text-gray-700">{recommendation}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderEmployerStats = () => (
    <div className="employer-stats">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Hiring Analytics Dashboard</h2>
        <p className="text-gray-600">Comprehensive overview of your hiring performance and trends</p>
      </div>

      {employerStats && (
        <div className="space-y-6">
          {/* Overview Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="card-modern text-center">
              <div className="text-3xl font-bold text-indigo-600">{employerStats.total_jobs_posted}</div>
              <div className="text-gray-600 mt-2">Jobs Posted</div>
            </div>
            <div className="card-modern text-center">
              <div className="text-3xl font-bold text-green-600">{employerStats.total_applications}</div>
              <div className="text-gray-600 mt-2">Total Applications</div>
            </div>
            <div className="card-modern text-center">
              <div className="text-3xl font-bold text-purple-600">{employerStats.average_match_score}%</div>
              <div className="text-gray-600 mt-2">Avg Match Score</div>
            </div>
            <div className="card-modern text-center">
              <div className="text-3xl font-bold text-orange-600">{employerStats.successful_hires}</div>
              <div className="text-gray-600 mt-2">Successful Hires</div>
            </div>
          </div>

          {/* Top Performing Jobs */}
          <div className="card-modern">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <span className="mr-2">🏆</span>
              Top Performing Jobs
            </h3>
            <div className="space-y-4">
              {employerStats.top_performing_jobs.map((job, index) => (
                <div key={job.job_id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <div className="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center mr-4">
                      <span className="text-indigo-600 font-bold">#{index + 1}</span>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{job.title}</h4>
                      <p className="text-sm text-gray-600">{job.applications} applications</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-green-600">{job.avg_match_score}%</div>
                    <div className="text-xs text-gray-500">Avg Match</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Skill Trends */}
          <div className="card-modern">
            <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
              <span className="mr-2">📊</span>
              Market Skill Trends
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Most In-Demand</h4>
                <div className="space-y-2">
                  {employerStats.skill_trends.most_in_demand.map((skill, index) => (
                    <div key={index} className="flex items-center">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                      <span className="text-sm text-gray-700">{skill}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Emerging Skills</h4>
                <div className="space-y-2">
                  {employerStats.skill_trends.emerging_skills.map((skill, index) => (
                    <div key={index} className="flex items-center">
                      <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                      <span className="text-sm text-gray-700">{skill}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Common Gaps</h4>
                <div className="space-y-2">
                  {employerStats.skill_trends.skill_gaps.map((skill, index) => (
                    <div key={index} className="flex items-center">
                      <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                      <span className="text-sm text-gray-700">{skill}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderSkillGapAnalysis = () => (
    <div className="skill-gap-analysis">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Skill Gap Analysis</h2>
        <p className="text-gray-600">Detailed analysis of candidate skill alignment with job requirements</p>
      </div>

      {selectedCandidate && skillGapAnalysis && (
        <div className="space-y-6">
          <div className="card-modern">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-semibold text-gray-900">{selectedCandidate.user_name}</h3>
                <p className="text-gray-600">vs. {selectedJob?.title}</p>
              </div>
              <button
                onClick={() => {
                  setSelectedCandidate(null);
                  setSkillGapAnalysis(null);
                }}
                className="btn-modern-secondary"
              >
                ← Back to Candidates
              </button>
            </div>

            {/* Skill Coverage Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">{skillGapAnalysis.skill_coverage.toFixed(1)}%</div>
                <div className="text-gray-600">Skill Coverage</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-red-600">{skillGapAnalysis.gap_score.toFixed(1)}%</div>
                <div className="text-gray-600">Skill Gap</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-600">{skillGapAnalysis.critical_gaps}</div>
                <div className="text-gray-600">Critical Gaps</div>
              </div>
            </div>

            {/* Skill Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="mr-2">✅</span>
                  Matching Skills ({skillGapAnalysis.matching_skills_count})
                </h4>
                <div className="space-y-2">
                  {skillGapAnalysis.matching_skills.map((skill, index) => (
                    <div key={index} className="flex items-center p-2 bg-green-50 rounded">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                      <span className="text-gray-700">{skill}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="mr-2">❌</span>
                  Missing Skills ({skillGapAnalysis.missing_skills_count})
                </h4>
                <div className="space-y-2">
                  {skillGapAnalysis.missing_skills.map((skill, index) => (
                    <div key={index} className="flex items-center p-2 bg-red-50 rounded">
                      <span className="w-2 h-2 bg-red-500 rounded-full mr-3"></span>
                      <span className="text-gray-700">{skill}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Recommendations */}
            {skillGapAnalysis.recommendations && (
              <div className="mt-8">
                <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                  <span className="mr-2">💡</span>
                  Training Recommendations
                </h4>
                <div className="space-y-3">
                  {skillGapAnalysis.recommendations.map((recommendation, index) => (
                    <div key={index} className="p-3 bg-blue-50 rounded-lg">
                      <p className="text-gray-700">{recommendation}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {(!selectedCandidate || !skillGapAnalysis) && (
        <div className="card-modern text-center py-16">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Select a Candidate for Analysis</h3>
          <p className="text-gray-600">Choose a candidate from the AI Matching tab to see detailed skill gap analysis</p>
        </div>
      )}
    </div>
  );

  return (
    <div className="ai-recommendations">
      {/* Tab Navigation */}
      <div className="mb-8">
        <nav className="flex space-x-1 bg-gray-100 rounded-lg p-1">
          {[
            { id: 'candidates', label: 'AI Candidate Matching', icon: '🤖' },
            { id: 'insights', label: 'Job Insights', icon: '📊' },
            { id: 'analytics', label: 'Hiring Analytics', icon: '📈' },
            { id: 'skillgap', label: 'Skill Gap Analysis', icon: '🎯' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center px-4 py-2 rounded-md font-medium text-sm transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-white text-indigo-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'candidates' && renderCandidateMatching()}
      {activeTab === 'insights' && renderJobInsights()}
      {activeTab === 'analytics' && renderEmployerStats()}
      {activeTab === 'skillgap' && renderSkillGapAnalysis()}
    </div>
  );
};

export default AIRecommendations;
