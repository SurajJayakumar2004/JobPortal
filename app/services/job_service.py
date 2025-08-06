from typing import Optional, Dict, Any, List
from datetime import datetime
from app.schemas import JobCreate, JobUpdate, JobType

# In-memory database simulation (replace with actual database in later phases)
jobs_db: Dict[int, Dict[str, Any]] = {}
job_id_counter = 1


class JobService:
    """Service for job management"""
    
    @staticmethod
    def create_job(job_data: JobCreate, employer_id: int) -> Dict[str, Any]:
        """
        Create a new job posting
        
        Args:
            job_data (JobCreate): Job creation data
            employer_id (int): ID of the employer creating the job
            
        Returns:
            dict: Created job data
        """
        global job_id_counter
        
        # Create job record
        job_record = {
            "id": job_id_counter,
            "title": job_data.title,
            "description": job_data.description,
            "company_name": job_data.company_name,
            "location": job_data.location,
            "job_type": job_data.job_type,
            "salary_min": job_data.salary_min,
            "salary_max": job_data.salary_max,
            "requirements": job_data.requirements or [],
            "benefits": job_data.benefits or [],
            "employer_id": employer_id,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "applications_count": 0
        }
        
        # Store job
        jobs_db[job_id_counter] = job_record
        job_id_counter += 1
        
        return job_record
    
    @staticmethod
    def get_job_by_id(job_id: int) -> Optional[Dict[str, Any]]:
        """
        Get job by ID
        
        Args:
            job_id (int): Job ID
            
        Returns:
            dict or None: Job data if found, None otherwise
        """
        return jobs_db.get(job_id)
    
    @staticmethod
    def get_jobs(
        skip: int = 0, 
        limit: int = 10, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get jobs with filtering and pagination
        
        Args:
            skip (int): Number of jobs to skip
            limit (int): Maximum number of jobs to return
            filters (dict): Filters to apply
            
        Returns:
            list: List of jobs matching criteria
        """
        if filters is None:
            filters = {}
        
        jobs = list(jobs_db.values())
        
        # Apply filters
        if filters.get("active_only", True):
            jobs = [job for job in jobs if job.get("is_active", True)]
        
        if filters.get("search"):
            search_term = filters["search"].lower()
            jobs = [
                job for job in jobs 
                if search_term in job["title"].lower() 
                or search_term in job["company_name"].lower()
                or search_term in job["description"].lower()
            ]
        
        if filters.get("location"):
            location_filter = filters["location"].lower()
            jobs = [
                job for job in jobs 
                if location_filter in job["location"].lower()
            ]
        
        if filters.get("job_type"):
            jobs = [
                job for job in jobs 
                if job["job_type"] == filters["job_type"]
            ]
        
        # Sort by creation date (newest first)
        jobs.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        return jobs[skip:skip + limit]
    
    @staticmethod
    def count_jobs(filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count jobs matching filters
        
        Args:
            filters (dict): Filters to apply
            
        Returns:
            int: Number of jobs matching criteria
        """
        if filters is None:
            filters = {}
        
        jobs = list(jobs_db.values())
        
        # Apply same filters as get_jobs but just count
        if filters.get("active_only", True):
            jobs = [job for job in jobs if job.get("is_active", True)]
        
        if filters.get("search"):
            search_term = filters["search"].lower()
            jobs = [
                job for job in jobs 
                if search_term in job["title"].lower() 
                or search_term in job["company_name"].lower()
                or search_term in job["description"].lower()
            ]
        
        if filters.get("location"):
            location_filter = filters["location"].lower()
            jobs = [
                job for job in jobs 
                if location_filter in job["location"].lower()
            ]
        
        if filters.get("job_type"):
            jobs = [
                job for job in jobs 
                if job["job_type"] == filters["job_type"]
            ]
        
        return len(jobs)
    
    @staticmethod
    def get_jobs_by_employer(
        employer_id: int, 
        skip: int = 0, 
        limit: int = 10, 
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get jobs posted by a specific employer
        
        Args:
            employer_id (int): Employer ID
            skip (int): Number of jobs to skip
            limit (int): Maximum number of jobs to return
            active_only (bool): Show only active jobs
            
        Returns:
            list: List of employer's jobs
        """
        jobs = [
            job for job in jobs_db.values() 
            if job["employer_id"] == employer_id
        ]
        
        if active_only:
            jobs = [job for job in jobs if job.get("is_active", True)]
        
        # Sort by creation date (newest first)
        jobs.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        return jobs[skip:skip + limit]
    
    @staticmethod
    def count_jobs_by_employer(employer_id: int, active_only: bool = True) -> int:
        """
        Count jobs posted by a specific employer
        
        Args:
            employer_id (int): Employer ID
            active_only (bool): Count only active jobs
            
        Returns:
            int: Number of jobs
        """
        jobs = [
            job for job in jobs_db.values() 
            if job["employer_id"] == employer_id
        ]
        
        if active_only:
            jobs = [job for job in jobs if job.get("is_active", True)]
        
        return len(jobs)
    
    @staticmethod
    def update_job(job_id: int, job_update: JobUpdate) -> Dict[str, Any]:
        """
        Update a job posting
        
        Args:
            job_id (int): Job ID to update
            job_update (JobUpdate): Update data
            
        Returns:
            dict: Updated job data
            
        Raises:
            ValueError: If job not found
        """
        if job_id not in jobs_db:
            raise ValueError("Job not found")
        
        job = jobs_db[job_id]
        
        # Update fields that are provided
        update_data = job_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                job[field] = value
        
        job["updated_at"] = datetime.utcnow()
        
        return job
    
    @staticmethod
    def delete_job(job_id: int) -> bool:
        """
        Delete a job posting
        
        Args:
            job_id (int): Job ID to delete
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            ValueError: If job not found
        """
        if job_id not in jobs_db:
            raise ValueError("Job not found")
        
        del jobs_db[job_id]
        return True
    
    @staticmethod
    def increment_applications_count(job_id: int):
        """
        Increment the applications count for a job
        
        Args:
            job_id (int): Job ID
        """
        if job_id in jobs_db:
            jobs_db[job_id]["applications_count"] += 1
    
    @staticmethod
    def decrement_applications_count(job_id: int):
        """
        Decrement the applications count for a job
        
        Args:
            job_id (int): Job ID
        """
        if job_id in jobs_db and jobs_db[job_id]["applications_count"] > 0:
            jobs_db[job_id]["applications_count"] -= 1
    
    @staticmethod
    def get_all_jobs() -> List[Dict[str, Any]]:
        """
        Get all jobs (for development/testing purposes)
        
        Returns:
            list: List of all jobs
        """
        return list(jobs_db.values())


# Create some default jobs for testing
def create_default_jobs():
    """Create default jobs for testing purposes"""
    try:
        # Only create if no jobs exist
        if jobs_db:
            return
        
        # Sample jobs
        sample_jobs = [
            {
                "title": "Senior Python Developer",
                "description": "We are looking for an experienced Python developer to join our team. You will be working on scalable web applications using FastAPI and React.",
                "company_name": "TechCorp Inc.",
                "location": "San Francisco, CA",
                "job_type": JobType.FULL_TIME,
                "salary_min": 120000,
                "salary_max": 180000,
                "requirements": [
                    "5+ years of Python experience",
                    "Experience with FastAPI or Django",
                    "Knowledge of React/JavaScript",
                    "Database design experience",
                    "AWS/Docker experience preferred"
                ],
                "benefits": [
                    "Health insurance",
                    "401k matching",
                    "Flexible work hours",
                    "Remote work options"
                ]
            },
            {
                "title": "Frontend Developer - React",
                "description": "Join our frontend team to build amazing user experiences with React and TypeScript.",
                "company_name": "WebSolutions LLC",
                "location": "New York, NY",
                "job_type": JobType.FULL_TIME,
                "salary_min": 90000,
                "salary_max": 130000,
                "requirements": [
                    "3+ years of React experience",
                    "TypeScript proficiency",
                    "CSS/SCSS expertise",
                    "State management (Redux/Zustand)",
                    "Testing frameworks"
                ],
                "benefits": [
                    "Health insurance",
                    "Unlimited PTO",
                    "Professional development budget",
                    "Flexible schedule"
                ]
            },
            {
                "title": "Data Science Intern",
                "description": "Summer internship opportunity to work on machine learning projects and data analysis.",
                "company_name": "DataTech Analytics",
                "location": "Austin, TX",
                "job_type": JobType.INTERNSHIP,
                "salary_min": 25,  # hourly
                "salary_max": 35,  # hourly
                "requirements": [
                    "Currently pursuing degree in Data Science/Statistics/CS",
                    "Python and pandas experience",
                    "Basic ML knowledge",
                    "SQL skills",
                    "Jupyter notebooks"
                ],
                "benefits": [
                    "Mentorship program",
                    "Learning stipend",
                    "Flexible hours",
                    "Potential full-time offer"
                ]
            }
        ]
        
        # Create jobs with employer ID 1 (admin user)
        for job_data in sample_jobs:
            job_create = JobCreate(**job_data)
            JobService.create_job(job_create, employer_id=1)
        
        print("✅ Default jobs created successfully")
        
    except Exception as e:
        print(f"ℹ️ Could not create default jobs: {e}")


# Initialize default jobs
create_default_jobs()
