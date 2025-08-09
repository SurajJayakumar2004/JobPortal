/**
 * Personalized Student Career Insights Component
 * 
 * Displays comprehensive career insights including professional insights,
 * career recommendations, skill breakdown, suggested career paths,
 * and priority skills to develop - all personalized for each student.
 */

import React, { useState, useEffect } from 'react';
import { useToast } from '../Toast';

const StudentInsights = ({ studentData, onBack }) => {
  const { showSuccess, showError } = useToast();
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  const tabConfig = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'professional', label: 'Professional Insights', icon: '💼' },
    { id: 'career', label: 'Career Recommendations', icon: '🎯' },
    { id: 'skills', label: 'Skill Breakdown', icon: '🔧' },
    { id: 'paths', label: 'Career Paths', icon: '🛤️' },
    { id: 'priorities', label: 'Priority Skills', icon: '⚡' }
  ];

  useEffect(() => {
    if (studentData && studentData.personalized_insights) {
      setInsights(studentData.personalized_insights);
    }
  }, [studentData]);

  const renderOverview = () => (
    <div className="overview-section">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Personalized Career Overview
        </h2>
        <p className="text-gray-600">
          AI-powered insights tailored specifically for your profile and career goals
        </p>
      </div>

      {insights && (
        <div className="space-y-6">
          {/* Student Profile Summary */}
          <div className="card-modern">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Your Profile Summary</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">
                  {insights.student_profile?.skills?.technical?.length || 0}
                </div>
                <div className="text-gray-600">Technical Skills</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">
                  {insights.student_profile?.experience?.total_years || 0}
                </div>
                <div className="text-gray-600">Years Experience</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">
                  {insights.personalization_score?.toFixed(0) || 'N/A'}%
                </div>
                <div className="text-gray-600">Profile Completeness</div>
              </div>
            </div>
          </div>

          {/* Quick Insights */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                <span className="mr-2">💪</span>
                Top Strengths
              </h4>
              <div className="space-y-2">
                {insights.professional_insights?.strengths?.slice(0, 3).map((strength, index) => (
                  <div key={index} className="flex items-start">
                    <span className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3"></span>
                    <span className="text-sm text-gray-700">{strength}</span>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
                <span className="mr-2">🎯</span>
                Next Steps
              </h4>
              <div className="space-y-2">
                {insights.career_recommendations?.recommended_next_steps?.slice(0, 3).map((step, index) => (
                  <div key={index} className="flex items-start">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3"></span>
                    <span className="text-sm text-gray-700">{step}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card-modern">
            <h4 className="font-semibold text-gray-900 mb-4">Explore Your Insights</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {tabConfig.slice(1).map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className="flex flex-col items-center p-4 bg-gray-50 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  <span className="text-2xl mb-2">{tab.icon}</span>
                  <span className="text-sm font-medium text-gray-700">{tab.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderProfessionalInsights = () => (
    <div className="professional-insights">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Professional Insights</h2>
        <p className="text-gray-600">Personalized analysis of your professional strengths and opportunities</p>
      </div>

      {insights?.professional_insights && (
        <div className="space-y-6">
          {/* Market Position */}
          <div className="card-modern">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Your Market Position</h3>
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-blue-800 font-medium">
                {insights.professional_insights.market_position}
              </p>
            </div>
          </div>

          {/* Strengths and Improvements */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">✅</span>
                Your Strengths
              </h4>
              <div className="space-y-3">
                {insights.professional_insights.strengths?.map((strength, index) => (
                  <div key={index} className="flex items-start p-3 bg-green-50 rounded-lg">
                    <span className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3"></span>
                    <span className="text-gray-700">{strength}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">📈</span>
                Areas for Growth
              </h4>
              <div className="space-y-3">
                {insights.professional_insights.areas_for_improvement?.map((area, index) => (
                  <div key={index} className="flex items-start p-3 bg-yellow-50 rounded-lg">
                    <span className="w-2 h-2 bg-yellow-500 rounded-full mt-2 mr-3"></span>
                    <span className="text-gray-700">{area}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Competitive Advantages */}
          {insights.professional_insights.competitive_advantages?.length > 0 && (
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🏆</span>
                Your Competitive Advantages
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {insights.professional_insights.competitive_advantages.map((advantage, index) => (
                  <div key={index} className="flex items-center p-3 bg-purple-50 rounded-lg">
                    <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                    <span className="text-gray-700">{advantage}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Industry Readiness */}
          {Object.keys(insights.professional_insights.industry_readiness || {}).length > 0 && (
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🏭</span>
                Industry Readiness Assessment
              </h4>
              <div className="space-y-4">
                {Object.entries(insights.professional_insights.industry_readiness).map(([industry, data]) => (
                  <div key={industry} className="border rounded-lg p-4">
                    <div className="flex justify-between items-center mb-3">
                      <h5 className="font-medium text-gray-900">{industry}</h5>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        data.readiness_score >= 70 ? 'bg-green-100 text-green-800' :
                        data.readiness_score >= 50 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {data.readiness_score}% Ready
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="font-medium text-gray-700 mb-1">Matching Skills:</p>
                        <p className="text-gray-600">{data.matching_skills?.join(', ') || 'None identified'}</p>
                      </div>
                      <div>
                        <p className="font-medium text-gray-700 mb-1">Skills to Develop:</p>
                        <p className="text-gray-600">{data.missing_skills?.join(', ') || 'All covered'}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderCareerRecommendations = () => (
    <div className="career-recommendations">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Career Recommendations</h2>
        <p className="text-gray-600">Personalized career guidance based on your profile and goals</p>
      </div>

      {insights?.career_recommendations && (
        <div className="space-y-6">
          {/* Immediate Opportunities */}
          {insights.career_recommendations.immediate_opportunities?.length > 0 && (
            <div className="card-modern">
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🚀</span>
                Immediate Opportunities
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {insights.career_recommendations.immediate_opportunities.map((opportunity, index) => (
                  <div key={index} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <h4 className="font-semibold text-gray-900 mb-2">{opportunity.role}</h4>
                    <p className="text-sm text-gray-600 mb-2">Industry: {opportunity.industry}</p>
                    <p className="text-sm text-gray-700 mb-3">{opportunity.match_reason}</p>
                    {opportunity.required_preparation?.length > 0 && (
                      <div>
                        <p className="text-sm font-medium text-gray-700 mb-1">Preparation needed:</p>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {opportunity.required_preparation.map((prep, prepIndex) => (
                            <li key={prepIndex} className="flex items-start">
                              <span className="w-1 h-1 bg-gray-400 rounded-full mt-2 mr-2"></span>
                              {prep}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Short-term and Long-term Goals */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">📅</span>
                Short-term Goals (6-18 months)
              </h4>
              <div className="space-y-3">
                {insights.career_recommendations.short_term_goals?.map((goal, index) => (
                  <div key={index} className="flex items-start p-3 bg-blue-50 rounded-lg">
                    <span className="w-2 h-2 bg-blue-500 rounded-full mt-2 mr-3"></span>
                    <span className="text-gray-700">{goal}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🎯</span>
                Long-term Vision (2-5 years)
              </h4>
              <div className="space-y-3">
                {insights.career_recommendations.long_term_vision?.map((vision, index) => (
                  <div key={index} className="flex items-start p-3 bg-purple-50 rounded-lg">
                    <span className="w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3"></span>
                    <span className="text-gray-700">{vision}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Growth Trajectory */}
          {insights.career_recommendations.growth_trajectory?.length > 0 && (
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">📈</span>
                Career Growth Trajectory
              </h4>
              <div className="space-y-4">
                {insights.career_recommendations.growth_trajectory.map((trajectory, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-3">{trajectory.industry} Career Path</h5>
                    <div className="flex items-center space-x-4 text-sm">
                      <div className="flex-1 text-center">
                        <div className="bg-green-100 text-green-800 px-3 py-2 rounded-lg">
                          <div className="font-medium">Entry Level</div>
                          <div>{trajectory.entry_level}</div>
                        </div>
                      </div>
                      <div className="text-gray-400">→</div>
                      <div className="flex-1 text-center">
                        <div className="bg-blue-100 text-blue-800 px-3 py-2 rounded-lg">
                          <div className="font-medium">Mid Level</div>
                          <div>{trajectory.mid_level}</div>
                        </div>
                      </div>
                      <div className="text-gray-400">→</div>
                      <div className="flex-1 text-center">
                        <div className="bg-purple-100 text-purple-800 px-3 py-2 rounded-lg">
                          <div className="font-medium">Senior Level</div>
                          <div>{trajectory.senior_level}</div>
                        </div>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mt-3 text-center">{trajectory.timeline}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderSkillBreakdown = () => (
    <div className="skill-breakdown">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Skill Breakdown & Analysis</h2>
        <p className="text-gray-600">Detailed analysis of your current skills and development opportunities</p>
      </div>

      {insights?.skill_breakdown && (
        <div className="space-y-6">
          {/* Current Skills Analysis */}
          <div className="card-modern">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Current Skills Analysis</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {insights.skill_breakdown.current_skills_analysis?.technical_skills_count || 0}
                </div>
                <div className="text-sm text-gray-600">Technical Skills</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {insights.skill_breakdown.current_skills_analysis?.soft_skills_count || 0}
                </div>
                <div className="text-sm text-gray-600">Soft Skills</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {insights.skill_breakdown.current_skills_analysis?.total_skills || 0}
                </div>
                <div className="text-sm text-gray-600">Total Skills</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {insights.skill_breakdown.current_skills_analysis?.strongest_technical_areas?.length || 0}
                </div>
                <div className="text-sm text-gray-600">Strong Areas</div>
              </div>
            </div>

            {/* Top Skills */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Strongest Technical Skills</h4>
                <div className="space-y-2">
                  {insights.skill_breakdown.current_skills_analysis?.strongest_technical_areas?.map((skill, index) => (
                    <div key={index} className="flex items-center p-2 bg-blue-50 rounded">
                      <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
                      <span className="text-gray-700">{skill}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Strongest Soft Skills</h4>
                <div className="space-y-2">
                  {insights.skill_breakdown.current_skills_analysis?.strongest_soft_skills?.map((skill, index) => (
                    <div key={index} className="flex items-center p-2 bg-green-50 rounded">
                      <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                      <span className="text-gray-700">{skill}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Skill Strength and Development Areas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">💪</span>
                Skill Strength Areas
              </h4>
              <div className="space-y-3">
                {insights.skill_breakdown.skill_strength_areas?.map((area, index) => (
                  <div key={index} className="flex items-start p-3 bg-green-50 rounded-lg">
                    <span className="w-2 h-2 bg-green-500 rounded-full mt-2 mr-3"></span>
                    <span className="text-gray-700">{area}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">📚</span>
                Development Areas
              </h4>
              <div className="space-y-3">
                {insights.skill_breakdown.skill_development_areas?.map((area, index) => (
                  <div key={index} className="flex items-start p-3 bg-yellow-50 rounded-lg">
                    <span className="w-2 h-2 bg-yellow-500 rounded-full mt-2 mr-3"></span>
                    <span className="text-gray-700">{area}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Industry Skill Gaps */}
          {Object.keys(insights.skill_breakdown.industry_skill_gaps || {}).length > 0 && (
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🎯</span>
                Industry-Specific Skill Gaps
              </h4>
              <div className="space-y-4">
                {Object.entries(insights.skill_breakdown.industry_skill_gaps).map(([industry, skills]) => (
                  <div key={industry} className="border rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-2">{industry}</h5>
                    <div className="flex flex-wrap gap-2">
                      {skills.map((skill, index) => (
                        <span key={index} className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Learning Path Suggestions */}
          {insights.skill_breakdown.learning_path_suggestions?.length > 0 && (
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🛤️</span>
                Suggested Learning Paths
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {insights.skill_breakdown.learning_path_suggestions.map((path, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <h5 className="font-medium text-gray-900 mb-2">{path.path}</h5>
                    <p className="text-sm text-gray-600 mb-3">Timeline: {path.timeline}</p>
                    <div className="mb-3">
                      <p className="text-sm font-medium text-gray-700 mb-1">Skills to learn:</p>
                      <div className="flex flex-wrap gap-1">
                        {path.skills?.map((skill, skillIndex) => (
                          <span key={skillIndex} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-700 mb-1">Resources:</p>
                      <p className="text-sm text-gray-600">{path.resources?.join(', ')}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderCareerPaths = () => (
    <div className="career-paths">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Suggested Career Paths</h2>
        <p className="text-gray-600">Personalized career progression paths based on your profile</p>
      </div>

      {insights?.suggested_career_paths && (
        <div className="space-y-6">
          {insights.suggested_career_paths.map((path, index) => (
            <div key={index} className="card-modern">
              <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">{path.title}</h3>
                <p className="text-gray-600 mb-3">{path.description}</p>
                {path.personalization_note && (
                  <div className="bg-blue-50 p-3 rounded-lg">
                    <p className="text-blue-800 text-sm">
                      <strong>Personalized Note:</strong> {path.personalization_note}
                    </p>
                  </div>
                )}
              </div>

              <div className="space-y-4">
                {path.stages?.map((stage, stageIndex) => (
                  <div key={stageIndex} className="border rounded-lg p-4">
                    <div className="flex justify-between items-start mb-3">
                      <h4 className="font-medium text-gray-900">{stage.level}</h4>
                      <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                        {stage.salary_range}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="font-medium text-gray-700 mb-2">Typical Roles:</p>
                        <div className="space-y-1">
                          {stage.roles?.map((role, roleIndex) => (
                            <div key={roleIndex} className="flex items-center">
                              <span className="w-1 h-1 bg-gray-400 rounded-full mr-2"></span>
                              <span className="text-gray-600">{role}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      
                      <div>
                        <p className="font-medium text-gray-700 mb-2">Skills Needed:</p>
                        <div className="flex flex-wrap gap-1">
                          {stage.skills_needed?.map((skill, skillIndex) => (
                            <span key={skillIndex} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderPrioritySkills = () => (
    <div className="priority-skills">
      <div className="mb-6">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Priority Skills to Develop</h2>
        <p className="text-gray-600">Strategic skill development plan tailored to your career goals</p>
      </div>

      {insights?.priority_skills_to_develop && (
        <div className="space-y-6">
          {/* Learning Plan Overview */}
          {insights.priority_skills_to_develop.skill_learning_plan?.length > 0 && (
            <div className="card-modern">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Your Learning Plan</h3>
              <div className="space-y-4">
                {insights.priority_skills_to_develop.skill_learning_plan.map((plan, index) => (
                  <div key={index} className="flex items-center p-4 border rounded-lg hover:shadow-md transition-shadow">
                    <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold mr-4">
                      {plan.order}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{plan.skill}</h4>
                      <p className="text-sm text-gray-600">Timeline: {plan.timeline}</p>
                      <p className="text-sm text-gray-600">Approach: {plan.recommended_approach}</p>
                    </div>
                    <div className="flex-shrink-0">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        plan.priority_level === 'High' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {plan.priority_level} Priority
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Priority Categories */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Immediate Priority */}
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🚨</span>
                Immediate Priority (3 months)
              </h4>
              <div className="space-y-3">
                {insights.priority_skills_to_develop.immediate_priority?.map((skill, index) => (
                  <div key={index} className="p-3 bg-red-50 rounded-lg">
                    <h5 className="font-medium text-gray-900 mb-1">{skill.skill}</h5>
                    <p className="text-sm text-gray-600 mb-2">{skill.reason}</p>
                    <p className="text-xs text-gray-500">Time: {skill.learning_time}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Short-term Priority */}
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">⚡</span>
                Short-term (6-12 months)
              </h4>
              <div className="space-y-3">
                {insights.priority_skills_to_develop.short_term_priority?.map((skill, index) => (
                  <div key={index} className="p-3 bg-yellow-50 rounded-lg">
                    <h5 className="font-medium text-gray-900 mb-1">{skill.skill}</h5>
                    <p className="text-sm text-gray-600 mb-2">{skill.reason}</p>
                    <p className="text-xs text-gray-500">Time: {skill.learning_time}</p>
                    {skill.industry_relevance && (
                      <p className="text-xs text-blue-600">Industry: {skill.industry_relevance}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Long-term Priority */}
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🎯</span>
                Long-term (1+ years)
              </h4>
              <div className="space-y-3">
                {insights.priority_skills_to_develop.long_term_priority?.map((skill, index) => (
                  <div key={index} className="p-3 bg-blue-50 rounded-lg">
                    <h5 className="font-medium text-gray-900 mb-1">{skill.skill}</h5>
                    <p className="text-sm text-gray-600 mb-2">{skill.reason}</p>
                    <p className="text-xs text-gray-500">Time: {skill.learning_time}</p>
                    {skill.future_potential && (
                      <p className="text-xs text-purple-600">Potential: {skill.future_potential}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Recommended Certifications */}
          {insights.priority_skills_to_develop.recommended_certifications?.length > 0 && (
            <div className="card-modern">
              <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🏆</span>
                Recommended Certifications
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {insights.priority_skills_to_develop.recommended_certifications.map((cert, index) => (
                  <div key={index} className="flex items-center p-3 bg-purple-50 rounded-lg">
                    <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
                    <span className="text-gray-700">{cert}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return renderOverview();
      case 'professional':
        return renderProfessionalInsights();
      case 'career':
        return renderCareerRecommendations();
      case 'skills':
        return renderSkillBreakdown();
      case 'paths':
        return renderCareerPaths();
      case 'priorities':
        return renderPrioritySkills();
      default:
        return renderOverview();
    }
  };

  if (!insights) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your personalized insights...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="student-insights min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">Your Career Insights</h1>
              <p className="text-gray-600">AI-powered personalized career guidance</p>
            </div>
            <button
              onClick={onBack}
              className="btn-modern-secondary"
            >
              ← Back
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-2 overflow-x-auto bg-white rounded-2xl shadow-sm p-2">
              {tabConfig.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center whitespace-nowrap py-3 px-4 rounded-xl font-semibold text-sm transition-all duration-300 ${
                    activeTab === tab.id
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg transform scale-105'
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
        <div className="tab-content">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
};

export default StudentInsights;
