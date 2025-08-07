/**
 * AI Matching API Service
 * Handles communication with the Python backend for AI-powered job matching and candidate screening
 */

import axios from 'axios';

// Backend API base URL (adjust based on your backend configuration)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class AIMatchingAPI {
  constructor() {
    this.api = axios.create({
      baseURL: `${API_BASE_URL}/api`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get AI-ranked candidates for a specific job
   * @param {string} jobId - The job ID to get candidates for
   * @returns {Promise<Object>} AI-ranked candidates with match scores
   */
  async getCandidatesForJob(jobId) {
    try {
      console.log(`Fetching AI-ranked candidates for job: ${jobId}`);
      const response = await this.api.get(`/jobs/${jobId}/candidates`);
      return response.data;
    } catch (error) {
      console.error('Error fetching candidates for job:', error);
      // Return mock data for development
      return this.getMockCandidatesForJob(jobId);
    }
  }

  /**
   * Get job recommendations for a candidate
   * @param {string} candidateId - The candidate ID
   * @returns {Promise<Object>} AI-recommended jobs for the candidate
   */
  async getJobRecommendationsForCandidate(candidateId) {
    try {
      const response = await this.api.get(`/candidates/${candidateId}/job-recommendations`);
      return response.data;
    } catch (error) {
      console.error('Error fetching job recommendations:', error);
      return this.getMockJobRecommendations();
    }
  }

  /**
   * Analyze skill gaps for a candidate against job requirements
   * @param {string} candidateId - The candidate ID
   * @param {string} jobId - The job ID to analyze against
   * @returns {Promise<Object>} Skill gap analysis
   */
  async analyzeSkillGap(candidateId, jobId) {
    try {
      const response = await this.api.post(`/analysis/skill-gap`, {
        candidate_id: candidateId,
        job_id: jobId
      });
      return response.data;
    } catch (error) {
      console.error('Error analyzing skill gap:', error);
      return this.getMockSkillGapAnalysis();
    }
  }

  /**
   * Upload and parse resume for AI analysis
   * @param {File} resumeFile - The resume file to upload
   * @returns {Promise<Object>} Parsed resume data with AI feedback
   */
  async uploadAndParseResume(resumeFile) {
    try {
      const formData = new FormData();
      formData.append('resume_file', resumeFile);

      const response = await this.api.post('/resumes/upload-and-parse', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading and parsing resume:', error);
      throw error;
    }
  }

  /**
   * Get AI insights for a job posting
   * @param {string} jobId - The job ID
   * @returns {Promise<Object>} AI insights and analytics for the job
   */
  async getJobInsights(jobId) {
    try {
      const response = await this.api.get(`/jobs/${jobId}/ai-insights`);
      return response.data;
    } catch (error) {
      console.error('Error fetching job insights:', error);
      return this.getMockJobInsights(jobId);
    }
  }

  /**
   * Get overall matching statistics for an employer
   * @returns {Promise<Object>} Matching statistics and insights
   */
  async getEmployerMatchingStats() {
    try {
      const response = await this.api.get('/employers/matching-stats');
      return response.data;
    } catch (error) {
      console.error('Error fetching employer matching stats:', error);
      return this.getMockEmployerStats();
    }
  }

  /**
   * Batch process multiple resumes for a job
   * @param {string} jobId - The job ID
   * @param {Array<string>} candidateIds - Array of candidate IDs to process
   * @returns {Promise<Object>} Batch processing results
   */
  async batchProcessCandidates(jobId, candidateIds) {
    try {
      const response = await this.api.post('/jobs/batch-process-candidates', {
        job_id: jobId,
        candidate_ids: candidateIds
      });
      return response.data;
    } catch (error) {
      console.error('Error batch processing candidates:', error);
      throw error;
    }
  }

  // Mock data methods for development/fallback
  getMockCandidatesForJob(jobId) {
    return {
      success: true,
      data: {
        job_id: jobId,
        job_title: "Senior Software Engineer",
        total_candidates: 12,
        average_match_score: 78.5,
        candidates: [
          {
            user_id: "candidate_1",
            user_name: "Alex Johnson",
            user_email: "alex.johnson@email.com",
            resume_id: "resume_1",
            match_score: 92.5,
            matching_skills: ["Python", "React", "AWS", "Machine Learning", "PostgreSQL"],
            missing_skills: ["Kubernetes", "GraphQL"],
            experience_level: "senior",
            location: "San Francisco, CA",
            years_experience: 6,
            summary: "Experienced full-stack developer with strong ML background",
            key_achievements: [
              "Led development of ML recommendation system",
              "Reduced API response time by 40%",
              "Mentored 5 junior developers"
            ]
          },
          {
            user_id: "candidate_2",
            user_name: "Sarah Chen",
            user_email: "sarah.chen@email.com",
            resume_id: "resume_2",
            match_score: 87.3,
            matching_skills: ["Python", "Django", "AWS", "Docker", "Redis"],
            missing_skills: ["React", "Machine Learning", "Kubernetes"],
            experience_level: "mid",
            location: "Seattle, WA",
            years_experience: 4,
            summary: "Backend specialist with cloud infrastructure expertise",
            key_achievements: [
              "Architected microservices platform",
              "Improved system reliability to 99.9%",
              "Led AWS migration project"
            ]
          },
          {
            user_id: "candidate_3",
            user_name: "Michael Rodriguez",
            user_email: "michael.rodriguez@email.com",
            resume_id: "resume_3",
            match_score: 82.1,
            matching_skills: ["JavaScript", "React", "Node.js", "MongoDB"],
            missing_skills: ["Python", "AWS", "Machine Learning", "PostgreSQL"],
            experience_level: "mid",
            location: "Austin, TX",
            years_experience: 3,
            summary: "Frontend-focused developer with full-stack capabilities",
            key_achievements: [
              "Built responsive web applications",
              "Optimized frontend performance by 60%",
              "Implemented modern UI/UX designs"
            ]
          },
          {
            user_id: "candidate_4",
            user_name: "Emily Park",
            user_email: "emily.park@email.com",
            resume_id: "resume_4",
            match_score: 79.8,
            matching_skills: ["Python", "Machine Learning", "TensorFlow", "SQL"],
            missing_skills: ["React", "AWS", "Docker", "Kubernetes"],
            experience_level: "entry",
            location: "New York, NY",
            years_experience: 2,
            summary: "Data science background transitioning to software engineering",
            key_achievements: [
              "Developed predictive models",
              "Published ML research paper",
              "Built data visualization dashboards"
            ]
          }
        ]
      }
    };
  }

  getMockJobRecommendations() {
    return {
      success: true,
      data: {
        total_recommendations: 8,
        recommendations: [
          {
            job: {
              _id: "job_1",
              title: "Machine Learning Engineer",
              company_name: "TechCorp",
              location: "San Francisco, CA",
              salary_range: "$130,000 - $180,000"
            },
            match_score: 94.2,
            matching_skills: ["Python", "TensorFlow", "AWS", "Docker"]
          },
          {
            job: {
              _id: "job_2",
              title: "Senior Backend Developer",
              company_name: "StartupXYZ",
              location: "Remote",
              salary_range: "$120,000 - $160,000"
            },
            match_score: 88.7,
            matching_skills: ["Python", "PostgreSQL", "Redis", "API Development"]
          }
        ]
      }
    };
  }

  getMockSkillGapAnalysis() {
    return {
      success: true,
      data: {
        skill_coverage: 73.2,
        gap_score: 26.8,
        critical_gaps: 2,
        matching_skills_count: 8,
        missing_skills_count: 3,
        matching_skills: ["Python", "React", "SQL", "Git", "Agile"],
        missing_skills: ["Kubernetes", "GraphQL", "Microservices"],
        recommendations: [
          "Focus on learning Kubernetes for container orchestration",
          "Consider GraphQL for modern API development",
          "Gain experience with microservices architecture"
        ]
      }
    };
  }

  getMockJobInsights(jobId) {
    return {
      success: true,
      data: {
        job_id: jobId,
        application_trends: {
          total_applications: 45,
          applications_this_week: 12,
          application_rate: "2.1 per day",
          trending_up: true
        },
        candidate_quality: {
          average_match_score: 76.3,
          high_quality_candidates: 18,
          candidates_above_80_percent: 12
        },
        skill_demand: {
          most_common_skills: ["Python", "React", "SQL", "AWS"],
          rare_skills: ["Kubernetes", "GraphQL", "Rust"],
          skill_gap_frequency: {
            "Kubernetes": 67,
            "Machine Learning": 43,
            "GraphQL": 38
          }
        },
        recommendations: [
          "Consider making Kubernetes optional to increase candidate pool",
          "High-quality candidates are actively applying",
          "Your salary range is competitive for this market"
        ]
      }
    };
  }

  getMockEmployerStats() {
    return {
      success: true,
      data: {
        total_jobs_posted: 8,
        total_applications: 156,
        average_match_score: 74.2,
        successful_hires: 3,
        time_to_hire: "18 days",
        top_performing_jobs: [
          {
            job_id: "job_1",
            title: "Senior Developer",
            applications: 23,
            avg_match_score: 82.1
          },
          {
            job_id: "job_2", 
            title: "Product Manager",
            applications: 31,
            avg_match_score: 79.8
          }
        ],
        candidate_source_analysis: {
          direct_applications: 45,
          ai_recommendations: 32,
          referrals: 18,
          job_boards: 61
        },
        skill_trends: {
          most_in_demand: ["Python", "React", "AWS", "Machine Learning"],
          emerging_skills: ["Rust", "GraphQL", "Kubernetes", "WebAssembly"],
          skill_gaps: ["DevOps", "Cloud Architecture", "Data Engineering"]
        }
      }
    };
  }

  // ====== AI ANALYSIS ENDPOINTS ======
  
  /**
   * Perform skill gap analysis between candidate and job
   * @param {string} candidateId - ID of the candidate
   * @param {string} jobId - ID of the job
   * @returns {Promise<Object>} Skill gap analysis results
   */
  async analyzeSkillGap(candidateId, jobId) {
    try {
      const response = await this.api.post(`/ai/skill-gap?candidate_id=${candidateId}&job_id=${jobId}`);
      return response.data;
    } catch (error) {
      console.error('Error analyzing skill gap:', error);
      
      // Mock fallback data
      return {
        success: true,
        message: "Skill gap analysis completed (demo mode)",
        data: {
          candidate_id: candidateId,
          job_id: jobId,
          skill_coverage: 76.5,
          matching_skills: ['JavaScript', 'React', 'Node.js', 'Git'],
          missing_skills: ['AWS', 'Docker', 'Kubernetes', 'TypeScript'],
          critical_gaps: 2,
          recommendations: [
            'Consider learning AWS to better match this role',
            'Docker and containerization skills would be valuable',
            'Strong foundation in web development - highlight these skills'
          ],
          improvement_areas: ['Cloud Computing', 'DevOps', 'Modern JavaScript']
        }
      };
    }
  }

  /**
   * Get AI-powered insights about a candidate
   * @param {string} candidateId - ID of the candidate
   * @returns {Promise<Object>} Candidate insights and recommendations
   */
  async getCandidateInsights(candidateId) {
    try {
      const response = await this.api.get(`/ai/candidate-insights/${candidateId}`);
      return response.data;
    } catch (error) {
      console.error('Error getting candidate insights:', error);
      
      // Mock fallback data
      return {
        success: true,
        message: "Candidate insights generated (demo mode)",
        data: {
          candidate_id: candidateId,
          profile_strength: {
            overall_score: 82.5,
            skills_diversity: 15,
            experience_relevance: 78.0,
            ats_compatibility: 85.2
          },
          market_fit: {
            in_demand_skills: ['Python', 'React', 'JavaScript'],
            emerging_skills: ['Kubernetes', 'GraphQL'],
            skill_gaps: ['Machine Learning', 'DevOps', 'Cloud Architecture']
          },
          career_recommendations: [
            'Consider developing cloud computing skills',
            'Your profile shows strong technical foundation',
            'Focus on building a portfolio of projects'
          ],
          job_match_potential: {
            best_fit_roles: ['Software Developer', 'Full Stack Engineer'],
            salary_range_estimate: '$70,000 - $95,000',
            location_opportunities: ['San Francisco', 'Seattle', 'Remote']
          }
        }
      };
    }
  }

  /**
   * Get current job market trends and analytics
   * @returns {Promise<Object>} Market trends data
   */
  async getMarketTrends() {
    try {
      const response = await this.api.get('/ai/market-trends');
      return response.data;
    } catch (error) {
      console.error('Error getting market trends:', error);
      
      // Mock fallback data
      return {
        success: true,
        message: "Market trends retrieved (demo mode)",
        data: {
          skill_demand: {
            most_in_demand: [
              { skill: "Python", demand_score: 95, growth: "+15%" },
              { skill: "JavaScript", demand_score: 92, growth: "+12%" },
              { skill: "React", demand_score: 88, growth: "+20%" },
              { skill: "AWS", demand_score: 85, growth: "+25%" },
              { skill: "Machine Learning", demand_score: 82, growth: "+30%" }
            ],
            emerging_skills: [
              { skill: "Rust", demand_score: 45, growth: "+150%" },
              { skill: "GraphQL", demand_score: 52, growth: "+80%" },
              { skill: "Kubernetes", demand_score: 68, growth: "+60%" }
            ]
          },
          job_categories: {
            highest_demand: [
              { category: "Software Engineering", openings: 15420, growth: "+18%" },
              { category: "Data Science", openings: 8950, growth: "+35%" },
              { category: "Product Management", openings: 6780, growth: "+22%" }
            ]
          },
          salary_trends: {
            software_engineer: {
              entry_level: "$75,000 - $95,000",
              mid_level: "$95,000 - $130,000",
              senior_level: "$130,000 - $180,000",
              trend: "+8% YoY"
            },
            data_scientist: {
              entry_level: "$85,000 - $110,000",
              mid_level: "$110,000 - $150,000",
              senior_level: "$150,000 - $200,000",
              trend: "+12% YoY"
            }
          },
          remote_work: {
            percentage_remote: 65,
            hybrid_percentage: 25,
            on_site_percentage: 10,
            trend: "Increasing remote opportunities"
          },
          hiring_timeline: {
            average_time_to_hire: "21 days",
            interview_rounds: "3-4 rounds",
            response_time: "5-7 days"
          }
        }
      };
    }
  }

  /**
   * Get optimization suggestions for a job posting
   * @param {string} jobId - ID of the job to optimize
   * @returns {Promise<Object>} Job optimization suggestions
   */
  async optimizeJobPosting(jobId) {
    try {
      const response = await this.api.post(`/ai/optimize-job-posting?job_id=${jobId}`);
      return response.data;
    } catch (error) {
      console.error('Error optimizing job posting:', error);
      
      // Mock fallback data
      return {
        success: true,
        message: "Job optimization analysis completed (demo mode)",
        data: {
          job_id: jobId,
          current_performance: {
            applications_received: 12,
            average_match_score: 74.2,
            time_since_posted: "5 days"
          },
          title_optimization: {
            current_title: "Software Developer",
            suggestions: [
              "Consider adding seniority level for clarity",
              "Include key technology stack in title",
              "Keep title under 60 characters for better visibility"
            ],
            optimized_examples: [
              "Senior Software Developer - Python/React",
              "Software Developer (Remote) - TechCorp"
            ]
          },
          description_optimization: {
            readability_score: 78,
            suggestions: [
              "Add bullet points for better readability",
              "Include company culture information",
              "Specify remote work options clearly"
            ]
          },
          requirements_optimization: {
            total_requirements: 8,
            suggestions: [
              "Consider marking some skills as 'nice-to-have'",
              "Add years of experience for each technology",
              "Include soft skills requirements"
            ]
          },
          ats_optimization: {
            ats_score: 85,
            suggestions: [
              "Good keyword usage for ATS systems",
              "Consider adding industry-specific terms"
            ]
          }
        }
      };
    }
  }
}

// Export singleton instance
const aiMatchingAPI = new AIMatchingAPI();
export default aiMatchingAPI;
