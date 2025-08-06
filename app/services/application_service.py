from typing import Optional, Dict, Any, List
from datetime import datetime
from app.schemas import ApplicationCreate, ApplicationStatus
from app.services.job_service import JobService

# In-memory database simulation (replace with actual database in later phases)
applications_db: Dict[int, Dict[str, Any]] = {}
application_id_counter = 1


class ApplicationService:
    """Service for job application management"""
    
    @staticmethod
    def create_application(application_data: ApplicationCreate, job_seeker_id: int) -> Dict[str, Any]:
        """
        Create a new job application
        
        Args:
            application_data (ApplicationCreate): Application data
            job_seeker_id (int): ID of the job seeker applying
            
        Returns:
            dict: Created application data
            
        Raises:
            ValueError: If job not found or application already exists
        """
        global application_id_counter
        
        # Check if job exists
        job = JobService.get_job_by_id(application_data.job_id)
        if not job:
            raise ValueError("Job not found")
        
        # Check if user already applied to this job
        existing_application = ApplicationService.get_application_by_job_and_user(
            application_data.job_id, job_seeker_id
        )
        if existing_application:
            raise ValueError("You have already applied to this job")
        
        # Create application record
        application_record = {
            "id": application_id_counter,
            "job_id": application_data.job_id,
            "job_seeker_id": job_seeker_id,
            "cover_letter": application_data.cover_letter,
            "status": ApplicationStatus.PENDING,
            "applied_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "notes": "",
            "resume_id": application_data.resume_id if hasattr(application_data, 'resume_id') else None
        }
        
        # Store application
        applications_db[application_id_counter] = application_record
        application_id_counter += 1
        
        # Increment job's applications count
        JobService.increment_applications_count(application_data.job_id)
        
        return application_record
    
    @staticmethod
    def get_application_by_id(application_id: int) -> Optional[Dict[str, Any]]:
        """
        Get application by ID
        
        Args:
            application_id (int): Application ID
            
        Returns:
            dict or None: Application data if found, None otherwise
        """
        return applications_db.get(application_id)
    
    @staticmethod
    def get_application_by_job_and_user(job_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get application by job ID and user ID
        
        Args:
            job_id (int): Job ID
            user_id (int): User ID
            
        Returns:
            dict or None: Application data if found, None otherwise
        """
        for app in applications_db.values():
            if app["job_id"] == job_id and app["job_seeker_id"] == user_id:
                return app
        return None
    
    @staticmethod
    def get_applications_by_job_seeker(
        job_seeker_id: int, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get applications by job seeker
        
        Args:
            job_seeker_id (int): Job seeker ID
            skip (int): Number of applications to skip
            limit (int): Maximum number of applications to return
            
        Returns:
            list: List of applications
        """
        applications = [
            app for app in applications_db.values() 
            if app["job_seeker_id"] == job_seeker_id
        ]
        
        # Sort by application date (newest first)
        applications.sort(key=lambda x: x["applied_at"], reverse=True)
        
        # Add job details to each application
        for app in applications:
            job = JobService.get_job_by_id(app["job_id"])
            if job:
                app["job_title"] = job["title"]
                app["company_name"] = job["company_name"]
                app["job_location"] = job["location"]
        
        # Apply pagination
        return applications[skip:skip + limit]
    
    @staticmethod
    def count_applications_by_job_seeker(job_seeker_id: int) -> int:
        """
        Count applications by job seeker
        
        Args:
            job_seeker_id (int): Job seeker ID
            
        Returns:
            int: Number of applications
        """
        return len([
            app for app in applications_db.values() 
            if app["job_seeker_id"] == job_seeker_id
        ])
    
    @staticmethod
    def get_applications_by_job(
        job_id: int, 
        skip: int = 0, 
        limit: int = 10,
        status_filter: Optional[ApplicationStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Get applications for a specific job
        
        Args:
            job_id (int): Job ID
            skip (int): Number of applications to skip
            limit (int): Maximum number of applications to return
            status_filter (ApplicationStatus): Filter by status
            
        Returns:
            list: List of applications
        """
        applications = [
            app for app in applications_db.values() 
            if app["job_id"] == job_id
        ]
        
        # Apply status filter
        if status_filter:
            applications = [
                app for app in applications 
                if app["status"] == status_filter
            ]
        
        # Sort by application date (newest first)
        applications.sort(key=lambda x: x["applied_at"], reverse=True)
        
        # Apply pagination
        return applications[skip:skip + limit]
    
    @staticmethod
    def count_applications_by_job(job_id: int, status_filter: Optional[ApplicationStatus] = None) -> int:
        """
        Count applications for a specific job
        
        Args:
            job_id (int): Job ID
            status_filter (ApplicationStatus): Filter by status
            
        Returns:
            int: Number of applications
        """
        applications = [
            app for app in applications_db.values() 
            if app["job_id"] == job_id
        ]
        
        if status_filter:
            applications = [
                app for app in applications 
                if app["status"] == status_filter
            ]
        
        return len(applications)
    
    @staticmethod
    def get_applications_by_employer(
        employer_id: int, 
        skip: int = 0, 
        limit: int = 10,
        status_filter: Optional[ApplicationStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all applications for jobs posted by an employer
        
        Args:
            employer_id (int): Employer ID
            skip (int): Number of applications to skip
            limit (int): Maximum number of applications to return
            status_filter (ApplicationStatus): Filter by status
            
        Returns:
            list: List of applications
        """
        # Get all jobs by this employer
        employer_jobs = JobService.get_jobs_by_employer(employer_id, active_only=False)
        job_ids = [job["id"] for job in employer_jobs]
        
        # Get applications for these jobs
        applications = [
            app for app in applications_db.values() 
            if app["job_id"] in job_ids
        ]
        
        # Apply status filter
        if status_filter:
            applications = [
                app for app in applications 
                if app["status"] == status_filter
            ]
        
        # Sort by application date (newest first)
        applications.sort(key=lambda x: x["applied_at"], reverse=True)
        
        # Add job details to each application
        for app in applications:
            job = JobService.get_job_by_id(app["job_id"])
            if job:
                app["job_title"] = job["title"]
                app["company_name"] = job["company_name"]
                app["job_location"] = job["location"]
        
        # Apply pagination
        return applications[skip:skip + limit]
    
    @staticmethod
    def count_applications_by_employer(employer_id: int, status_filter: Optional[ApplicationStatus] = None) -> int:
        """
        Count applications for all jobs posted by an employer
        
        Args:
            employer_id (int): Employer ID
            status_filter (ApplicationStatus): Filter by status
            
        Returns:
            int: Number of applications
        """
        # Get all jobs by this employer
        employer_jobs = JobService.get_jobs_by_employer(employer_id, active_only=False)
        job_ids = [job["id"] for job in employer_jobs]
        
        # Get applications for these jobs
        applications = [
            app for app in applications_db.values() 
            if app["job_id"] in job_ids
        ]
        
        if status_filter:
            applications = [
                app for app in applications 
                if app["status"] == status_filter
            ]
        
        return len(applications)
    
    @staticmethod
    def update_application_status(
        application_id: int, 
        new_status: ApplicationStatus, 
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update application status
        
        Args:
            application_id (int): Application ID
            new_status (ApplicationStatus): New status
            notes (str): Optional notes
            
        Returns:
            dict: Updated application data
            
        Raises:
            ValueError: If application not found
        """
        if application_id not in applications_db:
            raise ValueError("Application not found")
        
        application = applications_db[application_id]
        application["status"] = new_status
        application["updated_at"] = datetime.utcnow()
        
        if notes:
            application["notes"] = notes
        
        return application
    
    @staticmethod
    def delete_application(application_id: int) -> bool:
        """
        Delete an application
        
        Args:
            application_id (int): Application ID
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            ValueError: If application not found
        """
        if application_id not in applications_db:
            raise ValueError("Application not found")
        
        application = applications_db[application_id]
        job_id = application["job_id"]
        
        # Delete application
        del applications_db[application_id]
        
        # Decrement job's applications count
        JobService.decrement_applications_count(job_id)
        
        return True
    
    @staticmethod
    def get_application_statistics(job_id: Optional[int] = None, employer_id: Optional[int] = None) -> Dict[str, int]:
        """
        Get application statistics
        
        Args:
            job_id (int): Optional job ID to filter by
            employer_id (int): Optional employer ID to filter by
            
        Returns:
            dict: Statistics by status
        """
        applications = list(applications_db.values())
        
        # Filter by job
        if job_id:
            applications = [app for app in applications if app["job_id"] == job_id]
        
        # Filter by employer
        if employer_id:
            employer_jobs = JobService.get_jobs_by_employer(employer_id, active_only=False)
            job_ids = [job["id"] for job in employer_jobs]
            applications = [app for app in applications if app["job_id"] in job_ids]
        
        # Count by status
        stats = {
            "total": len(applications),
            "pending": 0,
            "reviewed": 0,
            "shortlisted": 0,
            "rejected": 0,
            "hired": 0
        }
        
        for app in applications:
            status = app["status"]
            if status == ApplicationStatus.PENDING:
                stats["pending"] += 1
            elif status == ApplicationStatus.REVIEWED:
                stats["reviewed"] += 1
            elif status == ApplicationStatus.SHORTLISTED:
                stats["shortlisted"] += 1
            elif status == ApplicationStatus.REJECTED:
                stats["rejected"] += 1
            elif status == ApplicationStatus.HIRED:
                stats["hired"] += 1
        
        return stats
    
    @staticmethod
    def get_all_applications() -> List[Dict[str, Any]]:
        """
        Get all applications (for development/testing purposes)
        
        Returns:
            list: List of all applications
        """
        return list(applications_db.values())


# Create some default applications for testing
def create_default_applications():
    """Create default applications for testing purposes"""
    try:
        # Only create if no applications exist and there are jobs
        if applications_db or not JobService.get_all_jobs():
            return
        
        # Sample applications (job seeker ID 2 applying to various jobs)
        jobs = JobService.get_all_jobs()
        if len(jobs) >= 2:
            # Application 1: Job seeker 2 applies to first job
            app1 = ApplicationCreate(
                job_id=jobs[0]["id"],
                cover_letter="I am very interested in this Senior Python Developer position. I have 6 years of experience with Python and have worked extensively with FastAPI and React. I believe my skills would be a great fit for your team."
            )
            ApplicationService.create_application(app1, job_seeker_id=2)
            
            # Application 2: Job seeker 2 applies to second job
            app2 = ApplicationCreate(
                job_id=jobs[1]["id"],
                cover_letter="I am excited about the Frontend Developer opportunity. I have been working with React and TypeScript for the past 4 years and have experience with state management and testing frameworks."
            )
            ApplicationService.create_application(app2, job_seeker_id=2)
        
        print("✅ Default applications created successfully")
        
    except Exception as e:
        print(f"ℹ️ Could not create default applications: {e}")


# Initialize default applications
create_default_applications()
