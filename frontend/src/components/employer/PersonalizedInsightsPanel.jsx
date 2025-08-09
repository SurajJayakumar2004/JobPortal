/**
 * Enhanced AI Recommendations with Personalized Student Insights
 * Provides comprehensive AI-powered candidate matching and personalized career guidance
 */

import React, { useState, useEffect } from 'react';
import { useToast } from '../Toast';
import aiMatchingAPI from '../../services/aiMatchingAPI';

const PersonalizedInsightsPanel = ({ candidate, jobData, onClose }) => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (candidate && jobData) {
      generatePersonalizedInsights();
    }
  }, [candidate, jobData]);

  const generatePersonalizedInsights = async () => {
    try {
      setLoading(true);
      
      // Simulate personalized insights based on candidate and job data
      const studentResume = {
        skills: candidate.skills || [],
        experience_level: candidate.experience_level || 'Entry Level',
        resume_text: candidate.resume_text || '',
        projects: candidate.projects || [],
        gpa: candidate.gpa || 0
      };

      const targetJob = {
        jobTitle: jobData.title,
        industry: jobData.industry || 'Technology',
        skillKeywords: jobData.required_skills || []
      };

      // Calculate skill match
      const matchingSkills = studentResume.skills.filter(skill => 
        targetJob.skillKeywords.includes(skill)
      );
      const missingSkills = targetJob.skillKeywords.filter(skill => 
        !studentResume.skills.includes(skill)
      );
      const skillMatchPercentage = targetJob.skillKeywords.length > 0 ? 
        (matchingSkills.length / targetJob.skillKeywords.length) * 100 : 0;

      // Generate insights
      const personalizedInsights = {
        professional_insights: [
          `${candidate.name} has ${matchingSkills.length} of ${targetJob.skillKeywords.length} required skills for ${targetJob.jobTitle}`,
          `Skill match percentage: ${Math.round(skillMatchPercentage)}%`,
          skillMatchPercentage >= 70 ? 'Strong candidate - well-qualified for this role!' : 
          skillMatchPercentage >= 50 ? 'Good potential - solid foundation for this role' :
          'Development needed - focus on key skills to improve competitiveness',
          `Experience level (${studentResume.experience_level}) ${
            targetJob.jobTitle.includes('Senior') ? 'may need further development for senior roles' :
            targetJob.jobTitle.includes('Junior') ? 'aligns well with entry-level expectations' :
            'is appropriate for this position level'
          }`
        ],
        career_recommendations: [
          'Build portfolio projects demonstrating technical skills',
          'Focus on developing the missing technical competencies',
          skillMatchPercentage < 50 ? 'Consider entry-level positions to gain experience' :
          'Apply to positions matching current skill level',
          'Network with professionals in the target industry',
          'Pursue relevant certifications to strengthen profile'
        ],
        skill_breakdown: {
          matching_skills: matchingSkills,
          missing_skills: missingSkills,
          skill_match_percentage: Math.round(skillMatchPercentage),
          total_skills_required: targetJob.skillKeywords.length,
          candidate_skills_count: studentResume.skills.length
        },
        suggested_career_paths: [
          {
            path_name: `${targetJob.jobTitle} Development Track`,
            steps: [
              `Entry-level ${targetJob.jobTitle}`,
              `${targetJob.jobTitle}`,
              `Senior ${targetJob.jobTitle}`,
              `Lead ${targetJob.jobTitle}`
            ],
            timeline: '2-5 years',
            key_skills_needed: missingSkills.slice(0, 3)
          },
          {
            path_name: 'Alternative Career Path',
            steps: [
              'Related technical role',
              'Specialized position',
              'Team leadership',
              'Management track'
            ],
            timeline: '3-6 years',
            key_skills_needed: ['Leadership', 'Communication', 'Strategic thinking']
          }
        ],
        priority_skills_to_develop: missingSkills.slice(0, 5).map((skill, index) => ({
          skill: skill,
          priority: index < 2 ? 'High' : index < 4 ? 'Medium' : 'Low',
          estimated_learning_time: getEstimatedLearningTime(skill),
          importance_reason: `Essential for ${targetJob.jobTitle} success`
        })),
        learning_timeline: {
          estimated_months: Math.max(2, Math.min(12, missingSkills.length * 2)),
          confidence_level: skillMatchPercentage >= 70 ? 'High' : 
                           skillMatchPercentage >= 50 ? 'Medium' : 'Requires significant effort',
          milestones: generateLearningMilestones(missingSkills.length)
        }
      };

      setInsights(personalizedInsights);
    } catch (error) {
      console.error('Error generating insights:', error);
    } finally {
      setLoading(false);
    }
  };

  const getEstimatedLearningTime = (skill) => {
    const timeEstimates = {
      'Python': '2-3 months',
      'JavaScript': '2-3 months',
      'SQL': '1-2 months',
      'React': '3-4 months',
      'Machine Learning': '4-6 months',
      'AWS': '2-3 months',
      'Git': '2-4 weeks',
      'Communication': 'Ongoing development',
      'Problem Solving': 'Ongoing development'
    };
    return timeEstimates[skill] || '2-3 months';
  };

  const generateLearningMilestones = (skillCount) => {
    const baseMonths = Math.max(2, Math.min(12, skillCount * 2));
    const milestones = [];
    
    for (let i = 1; i <= Math.min(4, skillCount); i++) {
      milestones.push({
        month: Math.round((baseMonths / 4) * i),
        goal: `Master ${i === 1 ? 'first priority skill' : `${i} priority skills`}`,
        deliverable: `Portfolio project showcasing ${i} new skill${i > 1 ? 's' : ''}`
      });
    }
    
    milestones.push({
      month: baseMonths,
      goal: 'Job application readiness',
      deliverable: 'Complete portfolio and updated resume'
    });
    
    return milestones;
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white p-8 rounded-lg max-w-md w-full mx-4">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Generating personalized insights...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 rounded-t-lg">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                Personalized Career Insights
              </h2>
              <p className="text-gray-600">
                AI-generated recommendations for {candidate.name}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        {insights && (
          <div className="p-6 space-y-8">
            {/* Professional Insights */}
            <section>
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">💡</span>
                Professional Insights
              </h3>
              <div className="bg-blue-50 rounded-lg p-4 space-y-2">
                {insights.professional_insights.map((insight, index) => (
                  <p key={index} className="text-blue-800">
                    • {insight}
                  </p>
                ))}
              </div>
            </section>

            {/* Skill Breakdown */}
            <section>
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🎯</span>
                Skill Breakdown Analysis
              </h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-green-50 rounded-lg p-4">
                  <h4 className="font-medium text-green-900 mb-3">Matching Skills ({insights.skill_breakdown.matching_skills.length})</h4>
                  <div className="flex flex-wrap gap-2">
                    {insights.skill_breakdown.matching_skills.map(skill => (
                      <span key={skill} className="px-3 py-1 bg-green-200 text-green-800 text-sm rounded-full">
                        ✓ {skill}
                      </span>
                    ))}
                  </div>
                  <div className="mt-3 text-sm text-green-700">
                    Match Rate: {insights.skill_breakdown.skill_match_percentage}%
                  </div>
                </div>

                <div className="bg-orange-50 rounded-lg p-4">
                  <h4 className="font-medium text-orange-900 mb-3">Skills to Develop ({insights.skill_breakdown.missing_skills.length})</h4>
                  <div className="flex flex-wrap gap-2">
                    {insights.skill_breakdown.missing_skills.map(skill => (
                      <span key={skill} className="px-3 py-1 bg-orange-200 text-orange-800 text-sm rounded-full">
                        📚 {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </section>

            {/* Career Recommendations */}
            <section>
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🚀</span>
                Career Recommendations
              </h3>
              <div className="bg-purple-50 rounded-lg p-4">
                <ul className="space-y-2">
                  {insights.career_recommendations.map((rec, index) => (
                    <li key={index} className="text-purple-800 flex items-start">
                      <span className="mr-2 mt-1">→</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </section>

            {/* Suggested Career Paths */}
            <section>
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🛤️</span>
                Suggested Career Paths
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                {insights.suggested_career_paths.map((path, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <h4 className="font-medium text-gray-900 mb-2">{path.path_name}</h4>
                    <p className="text-sm text-gray-600 mb-3">Timeline: {path.timeline}</p>
                    <div className="space-y-2">
                      {path.steps.map((step, stepIndex) => (
                        <div key={stepIndex} className="flex items-center text-sm">
                          <span className="w-6 h-6 bg-indigo-100 text-indigo-800 rounded-full flex items-center justify-center text-xs mr-3">
                            {stepIndex + 1}
                          </span>
                          {step}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* Priority Skills Development */}
            <section>
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">📈</span>
                Priority Skills to Develop
              </h3>
              <div className="space-y-3">
                {insights.priority_skills_to_develop.map((skillInfo, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h4 className="font-medium text-gray-900">{skillInfo.skill}</h4>
                      <span className={`px-2 py-1 text-xs rounded ${
                        skillInfo.priority === 'High' ? 'bg-red-100 text-red-800' :
                        skillInfo.priority === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {skillInfo.priority} Priority
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-1">
                      Estimated learning time: {skillInfo.estimated_learning_time}
                    </p>
                    <p className="text-sm text-gray-500">
                      {skillInfo.importance_reason}
                    </p>
                  </div>
                ))}
              </div>
            </section>

            {/* Learning Timeline */}
            <section>
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">⏱️</span>
                Learning Timeline & Milestones
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="mb-4">
                  <p className="text-sm text-gray-600">
                    Estimated time to job readiness: <strong>{insights.learning_timeline.estimated_months} months</strong>
                  </p>
                  <p className="text-sm text-gray-600">
                    Confidence level: <strong>{insights.learning_timeline.confidence_level}</strong>
                  </p>
                </div>
                <div className="space-y-3">
                  {insights.learning_timeline.milestones.map((milestone, index) => (
                    <div key={index} className="flex items-center">
                      <div className="w-8 h-8 bg-indigo-100 text-indigo-800 rounded-full flex items-center justify-center text-sm font-medium mr-4">
                        {milestone.month}M
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{milestone.goal}</p>
                        <p className="text-sm text-gray-600">{milestone.deliverable}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </section>
          </div>
        )}
      </div>
    </div>
  );
};

export default PersonalizedInsightsPanel;
