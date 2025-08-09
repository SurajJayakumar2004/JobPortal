/**
 * Student Insights API Service
 * 
 * Handles API calls for personalized student career insights,
 * resume analysis, and skill recommendations.
 */

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for file uploads
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

const studentInsightsAPI = {
  /**
   * Analyze a student's resume and generate personalized insights
   */
  analyzeResume: async (formData) => {
    try {
      const response = await apiClient.post('/api/student-insights/analyze-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error analyzing resume:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Failed to analyze resume. Please try again.'
      );
    }
  },

  /**
   * Generate quick career assessment based on user inputs
   */
  quickAssessment: async (assessmentData) => {
    try {
      const response = await apiClient.post('/api/student-insights/quick-assessment', assessmentData);
      return response.data;
    } catch (error) {
      console.error('Error in quick assessment:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Failed to generate career assessment. Please try again.'
      );
    }
  },

  /**
   * Get skill recommendations for a target role
   */
  getSkillRecommendations: async (targetRole, currentSkills = '') => {
    try {
      const params = { current_skills: currentSkills };
      const response = await apiClient.get(`/api/student-insights/skill-recommendations/${encodeURIComponent(targetRole)}`, { params });
      return response.data;
    } catch (error) {
      console.error('Error getting skill recommendations:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Failed to get skill recommendations. Please try again.'
      );
    }
  },

  /**
   * Get personalized career paths
   */
  getCareerPaths: async (industry = '', experienceLevel = 'entry') => {
    try {
      const params = { 
        industry: industry,
        experience_level: experienceLevel 
      };
      const response = await apiClient.get('/api/student-insights/career-paths', { params });
      return response.data;
    } catch (error) {
      console.error('Error getting career paths:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Failed to get career paths. Please try again.'
      );
    }
  },

  /**
   * Get market insights and trends
   */
  getMarketInsights: async (skills = '', industry = '') => {
    try {
      const params = { 
        skills: skills,
        industry: industry 
      };
      const response = await apiClient.get('/api/student-insights/market-insights', { params });
      return response.data;
    } catch (error) {
      console.error('Error getting market insights:', error);
      throw new Error(
        error.response?.data?.detail || 
        'Failed to get market insights. Please try again.'
      );
    }
  },

  /**
   * Generate mock personalized insights for demo purposes
   */
  generateMockInsights: async (userData) => {
    // This creates realistic mock data for demonstration
    return new Promise((resolve) => {
      setTimeout(() => {
        const mockInsights = {
          success: true,
          personalized_insights: {
            student_id: userData.id || 'demo_student',
            generated_on: new Date().toISOString(),
            student_profile: {
              skills: {
                technical: userData.skills?.technical || ['JavaScript', 'Python', 'React', 'SQL'],
                soft: userData.skills?.soft || ['Communication', 'Problem Solving', 'Teamwork'],
                tools: userData.skills?.tools || ['Git', 'VS Code', 'Excel'],
                languages: userData.skills?.languages || ['English', 'Spanish']
              },
              experience: {
                work_experience: userData.experience?.work || ['Software Development Intern at TechCorp'],
                internships: userData.experience?.internships || ['Summer Internship 2023'],
                projects: userData.experience?.projects || ['E-commerce Website', 'Data Analysis Dashboard'],
                total_years: userData.experience?.years || 1
              },
              education: {
                degrees: userData.education?.degrees || ['Bachelor of Science in Computer Science'],
                certifications: userData.education?.certifications || ['AWS Cloud Practitioner'],
                gpa: userData.education?.gpa || 3.7,
                relevant_coursework: userData.education?.coursework || ['Data Structures', 'Algorithms', 'Database Systems']
              },
              experience_level: userData.experience?.level || 'junior'
            },
            professional_insights: {
              strengths: [
                'Strong technical foundation with 4 technical skills identified',
                'Well-developed soft skills including Communication, Problem Solving, Teamwork',
                'Practical experience through 1 internship(s)',
                'Professional certifications: AWS Cloud Practitioner'
              ],
              areas_for_improvement: [
                'Consider obtaining additional industry-relevant certifications',
                'Expand technical skill set with emerging technologies'
              ],
              market_position: 'Competitive entry-level candidate with good preparation for the job market',
              competitive_advantages: [
                'High-demand skills: JavaScript, Python, SQL',
                'Multilingual abilities: English, Spanish'
              ],
              industry_readiness: {
                Technology: {
                  readiness_score: 78.5,
                  matching_skills: ['programming', 'problem-solving'],
                  missing_skills: ['version control', 'testing']
                }
              },
              recommendations: [
                'Focus on developing 2-3 additional technical skills relevant to your target industry',
                'Build a portfolio with 2-3 personal projects to demonstrate your skills'
              ]
            },
            career_recommendations: {
              immediate_opportunities: [
                {
                  role: 'Junior Software Developer',
                  industry: 'Technology',
                  match_reason: 'Aligns with your junior-level profile and Technology interest',
                  required_preparation: ['Build coding portfolio', 'Practice coding interviews', 'Learn additional frameworks']
                },
                {
                  role: 'Frontend Developer',
                  industry: 'Technology',
                  match_reason: 'Your JavaScript and React skills are well-suited for this role',
                  required_preparation: ['Master modern frontend frameworks', 'Learn UI/UX principles']
                }
              ],
              short_term_goals: [
                'Transition to a full-time role with increased responsibilities',
                'Specialize in a particular technology stack or domain',
                'Build leadership experience through project management',
                'Expand professional network through industry events'
              ],
              long_term_vision: [
                'Progress to Software Engineer or similar role in Technology',
                'Develop expertise in emerging technologies like AI/ML'
              ],
              recommended_next_steps: [
                'Build a portfolio with personal projects',
                'Apply for internships to gain practical experience'
              ],
              growth_trajectory: [
                {
                  industry: 'Technology',
                  entry_level: 'Junior Software Developer',
                  mid_level: 'Software Engineer',
                  senior_level: 'Senior Software Engineer',
                  timeline: 'Typically 2-3 years between levels with consistent skill development'
                }
              ]
            },
            skill_breakdown: {
              current_skills_analysis: {
                technical_skills_count: 4,
                soft_skills_count: 3,
                strongest_technical_areas: ['JavaScript', 'Python', 'React'],
                strongest_soft_skills: ['Communication', 'Problem Solving', 'Teamwork'],
                total_skills: 7
              },
              skill_strength_areas: [
                'High-demand technical skills: JavaScript, Python, SQL',
                'Strong soft skill foundation with 3 identified skills'
              ],
              skill_development_areas: [
                'Missing high-demand skills: machine learning, cloud computing'
              ],
              industry_skill_gaps: {
                Technology: ['version control', 'testing', 'databases']
              },
              skill_recommendations: [
                'Develop 2-3 additional programming languages or frameworks',
                'Consider learning data analysis or database management skills',
                'Explore cloud computing platforms (AWS, Azure, or GCP)'
              ],
              learning_path_suggestions: [
                {
                  path: 'Full-Stack Development',
                  skills: ['HTML/CSS', 'JavaScript', 'React', 'Node.js', 'Databases'],
                  timeline: '3-6 months',
                  resources: ['freeCodeCamp', 'The Odin Project', 'Codecademy']
                }
              ]
            },
            suggested_career_paths: [
              {
                title: 'Software Development Career Path',
                description: 'Progress from junior developer to senior engineer or architect',
                stages: [
                  {
                    level: 'Entry (0-2 years)',
                    roles: ['Junior Developer', 'Software Developer I'],
                    skills_needed: ['Programming fundamentals', 'Version control', 'Testing'],
                    salary_range: '$50,000 - $75,000'
                  },
                  {
                    level: 'Mid (2-5 years)',
                    roles: ['Software Engineer', 'Full Stack Developer'],
                    skills_needed: ['Advanced programming', 'System design', 'Database management'],
                    salary_range: '$75,000 - $120,000'
                  },
                  {
                    level: 'Senior (5+ years)',
                    roles: ['Senior Engineer', 'Tech Lead', 'Software Architect'],
                    skills_needed: ['Leadership', 'Architecture design', 'Mentoring'],
                    salary_range: '$120,000 - $200,000+'
                  }
                ],
                personalization_note: 'Your JavaScript, Python skills provide a strong foundation for this path'
              }
            ],
            priority_skills_to_develop: {
              immediate_priority: [
                {
                  skill: 'Programming Fundamentals',
                  reason: 'Essential foundation for technology careers',
                  learning_time: '2-3 months',
                  resources: ['Codecademy', 'freeCodeCamp', 'Python.org tutorial']
                }
              ],
              short_term_priority: [
                {
                  skill: 'Version Control',
                  reason: 'Key requirement for Technology industry',
                  learning_time: '3-6 months',
                  industry_relevance: 'Technology'
                },
                {
                  skill: 'Cloud Computing',
                  reason: 'High market demand across industries',
                  learning_time: '3-6 months',
                  market_demand: 'High'
                }
              ],
              long_term_priority: [
                {
                  skill: 'Machine Learning',
                  reason: 'Emerging technology with future growth potential',
                  learning_time: '6-12 months',
                  future_potential: 'High'
                }
              ],
              skill_learning_plan: [
                {
                  order: 1,
                  skill: 'Programming Fundamentals',
                  timeline: '2-3 months',
                  priority_level: 'High',
                  recommended_approach: 'Hands-on coding with projects and practice problems'
                },
                {
                  order: 2,
                  skill: 'Version Control',
                  timeline: '3-6 months',
                  priority_level: 'High',
                  recommended_approach: 'Practice with Git through real projects'
                }
              ],
              recommended_certifications: ['AWS Cloud Practitioner', 'Google IT Support Certificate']
            },
            personalization_score: 85.0
          },
          analysis_timestamp: new Date().toISOString(),
          filename: userData.filename || 'demo_resume.pdf'
        };
        
        resolve(mockInsights);
      }, 2000); // Simulate API delay
    });
  }
};

export default studentInsightsAPI;
