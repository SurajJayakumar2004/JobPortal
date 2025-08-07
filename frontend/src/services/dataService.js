/**
 * Data Service for handling jobs and candidates data
 * This service provides methods to interact with JSON data files
 */

import jobsData from '../data/jobs.json';
import candidatesData from '../data/candidates.json';

class DataService {
  constructor() {
    // Load data from localStorage if available, otherwise use JSON files
    this.initializeData();
  }

  initializeData() {
    // Try to load data from localStorage first
    const savedJobs = localStorage.getItem('jobPortal_jobs');
    const savedCandidates = localStorage.getItem('jobPortal_candidates');
    
    if (savedJobs) {
      try {
        this.jobs = JSON.parse(savedJobs);
      } catch (error) {
        console.warn('Failed to parse saved jobs data, using default data:', error);
        this.jobs = [...jobsData];
      }
    } else {
      // First time loading, use data from JSON files
      this.jobs = [...jobsData];
      this.saveJobsToLocalStorage();
    }

    if (savedCandidates) {
      try {
        this.candidates = JSON.parse(savedCandidates);
      } catch (error) {
        console.warn('Failed to parse saved candidates data, using default data:', error);
        this.candidates = [...candidatesData];
      }
    } else {
      // First time loading, use data from JSON files
      this.candidates = [...candidatesData];
      this.saveCandidatesToLocalStorage();
    }

    this.nextJobId = this.getNextJobId();
  }

  // Save jobs to localStorage
  saveJobsToLocalStorage() {
    try {
      localStorage.setItem('jobPortal_jobs', JSON.stringify(this.jobs));
    } catch (error) {
      console.error('Failed to save jobs to localStorage:', error);
    }
  }

  // Save candidates to localStorage
  saveCandidatesToLocalStorage() {
    try {
      localStorage.setItem('jobPortal_candidates', JSON.stringify(this.candidates));
    } catch (error) {
      console.error('Failed to save candidates to localStorage:', error);
    }
  }

  // Generate next available job ID
  getNextJobId() {
    const maxId = Math.max(...this.jobs.map(job => parseInt(job._id)), 0);
    return (maxId + 1).toString();
  }

  // Job-related methods
  getAllJobs() {
    return new Promise((resolve) => {
      // Simulate API delay
      setTimeout(() => {
        resolve([...this.jobs]);
      }, 500);
    });
  }

  getJobById(jobId) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const job = this.jobs.find(job => job._id === jobId);
        if (job) {
          resolve({ ...job });
        } else {
          reject(new Error('Job not found'));
        }
      }, 300);
    });
  }

  createJob(jobData) {
    return new Promise((resolve) => {
      setTimeout(() => {
        const newJob = {
          _id: this.nextJobId,
          ...jobData,
          applications_count: 0,
          posted_at: new Date().toISOString(),
          status: jobData.status || 'draft'
        };
        
        this.jobs.unshift(newJob); // Add to beginning of array
        this.nextJobId = (parseInt(this.nextJobId) + 1).toString();
        
        // Save to localStorage
        this.saveJobsToLocalStorage();
        
        resolve({
          success: true,
          data: { job: newJob },
          message: 'Job created successfully'
        });
      }, 800);
    });
  }

  updateJob(jobId, updatedData) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const jobIndex = this.jobs.findIndex(job => job._id === jobId);
        if (jobIndex !== -1) {
          this.jobs[jobIndex] = {
            ...this.jobs[jobIndex],
            ...updatedData,
            updated_at: new Date().toISOString()
          };
          
          // Save to localStorage
          this.saveJobsToLocalStorage();
          
          resolve({
            success: true,
            data: { job: this.jobs[jobIndex] },
            message: 'Job updated successfully'
          });
        } else {
          reject(new Error('Job not found'));
        }
      }, 600);
    });
  }

  deleteJob(jobId) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const jobIndex = this.jobs.findIndex(job => job._id === jobId);
        if (jobIndex !== -1) {
          const deletedJob = this.jobs.splice(jobIndex, 1)[0];
          
          // Save to localStorage after deletion
          this.saveJobsToLocalStorage();
          
          resolve({
            success: true,
            data: { job: deletedJob },
            message: 'Job deleted successfully'
          });
        } else {
          reject(new Error('Job not found'));
        }
      }, 400);
    });
  }

  // Candidate-related methods
  getCandidatesForJob(jobId) {
    return new Promise((resolve) => {
      setTimeout(() => {
        // Get job to match candidates based on skills
        const job = this.jobs.find(j => j._id === jobId);
        if (!job) {
          resolve([]);
          return;
        }

        // Filter and score candidates based on job requirements
        const jobSkills = job.required_skills || [];
        const matchedCandidates = this.candidates
          .map(candidate => {
            // Calculate match score based on skill overlap
            const candidateSkills = candidate.skills || [];
            const skillMatches = jobSkills.filter(skill => 
              candidateSkills.some(candidateSkill => 
                candidateSkill.toLowerCase().includes(skill.toLowerCase()) ||
                skill.toLowerCase().includes(candidateSkill.toLowerCase())
              )
            ).length;
            
            const matchScore = jobSkills.length > 0 
              ? Math.round((skillMatches / jobSkills.length) * 100)
              : 50;

            return {
              ...candidate,
              match_score: Math.min(matchScore + Math.random() * 20, 100) // Add some variance
            };
          })
          .filter(candidate => candidate.match_score > 60) // Only show candidates with >60% match
          .sort((a, b) => b.match_score - a.match_score) // Sort by match score
          .slice(0, 10); // Limit to top 10 candidates

        resolve(matchedCandidates);
      }, 700);
    });
  }

  getAllCandidates() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([...this.candidates]);
      }, 500);
    });
  }

  getCandidateById(candidateId) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const candidate = this.candidates.find(c => c.user_id === candidateId);
        if (candidate) {
          resolve({ ...candidate });
        } else {
          reject(new Error('Candidate not found'));
        }
      }, 300);
    });
  }

  // Search and filter methods
  searchJobs(filters = {}) {
    return new Promise((resolve) => {
      setTimeout(() => {
        let filteredJobs = [...this.jobs];

        // Apply filters
        if (filters.title) {
          filteredJobs = filteredJobs.filter(job =>
            job.title.toLowerCase().includes(filters.title.toLowerCase())
          );
        }

        if (filters.location) {
          filteredJobs = filteredJobs.filter(job =>
            job.location.toLowerCase().includes(filters.location.toLowerCase())
          );
        }

        if (filters.experience_level) {
          filteredJobs = filteredJobs.filter(job =>
            job.experience_level === filters.experience_level
          );
        }

        if (filters.employment_type) {
          filteredJobs = filteredJobs.filter(job =>
            job.employment_type === filters.employment_type
          );
        }

        if (filters.status) {
          filteredJobs = filteredJobs.filter(job =>
            job.status === filters.status
          );
        }

        resolve(filteredJobs);
      }, 400);
    });
  }

  searchCandidates(filters = {}) {
    return new Promise((resolve) => {
      setTimeout(() => {
        let filteredCandidates = [...this.candidates];

        if (filters.skills) {
          const skillKeywords = filters.skills.toLowerCase().split(',').map(s => s.trim());
          filteredCandidates = filteredCandidates.filter(candidate =>
            skillKeywords.some(keyword =>
              candidate.skills.some(skill =>
                skill.toLowerCase().includes(keyword)
              )
            )
          );
        }

        if (filters.experience) {
          filteredCandidates = filteredCandidates.filter(candidate =>
            candidate.experience_level === filters.experience
          );
        }

        if (filters.location) {
          filteredCandidates = filteredCandidates.filter(candidate =>
            candidate.location.toLowerCase().includes(filters.location.toLowerCase())
          );
        }

        resolve(filteredCandidates);
      }, 400);
    });
  }

  // Statistics and analytics
  getJobStatistics() {
    return new Promise((resolve) => {
      setTimeout(() => {
        const stats = {
          total_jobs: this.jobs.length,
          active_jobs: this.jobs.filter(job => job.status === 'open').length,
          draft_jobs: this.jobs.filter(job => job.status === 'draft').length,
          closed_jobs: this.jobs.filter(job => job.status === 'closed').length,
          total_applications: this.jobs.reduce((sum, job) => sum + (job.applications_count || 0), 0),
          avg_applications_per_job: this.jobs.length > 0 
            ? Math.round(this.jobs.reduce((sum, job) => sum + (job.applications_count || 0), 0) / this.jobs.length)
            : 0
        };
        resolve(stats);
      }, 300);
    });
  }

  // Utility methods
  incrementApplicationCount(jobId) {
    const job = this.jobs.find(j => j._id === jobId);
    if (job) {
      job.applications_count = (job.applications_count || 0) + 1;
      // Save to localStorage after updating application count
      this.saveJobsToLocalStorage();
    }
  }

  // Reset data to original state (useful for testing or data reset)
  resetToDefaultData() {
    this.jobs = [...jobsData];
    this.candidates = [...candidatesData];
    this.nextJobId = this.getNextJobId();
    
    // Save reset data to localStorage
    this.saveJobsToLocalStorage();
    this.saveCandidatesToLocalStorage();
    
    return {
      success: true,
      message: 'Data reset to default state'
    };
  }

  // Export data (for backup/persistence)
  exportData() {
    return {
      jobs: this.jobs,
      candidates: this.candidates,
      exported_at: new Date().toISOString()
    };
  }

  // Import data (for restore)
  importData(data) {
    if (data.jobs) {
      this.jobs = [...data.jobs];
      this.nextJobId = this.getNextJobId();
      this.saveJobsToLocalStorage();
    }
    if (data.candidates) {
      this.candidates = [...data.candidates];
      this.saveCandidatesToLocalStorage();
    }
    
    return {
      success: true,
      message: 'Data imported successfully'
    };
  }
}

// Create and export a singleton instance
const dataService = new DataService();
export default dataService;
