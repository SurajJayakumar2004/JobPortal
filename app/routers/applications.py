"""
Job application management router.

This module handles all application-related endpoints including applying
to jobs, viewing application status, and managing applications for both
students and employers.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging

from app.schemas import (
    ApplicationCreate, ApplicationUpdate, ApplicationOut, Application,
    ApplicationStatus, SuccessResponse, UserRole
)
from app.utils.dependencies import (
    get_current_active_user, require_student, 
    require_employer, TokenData
)

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage (replace with database in production)
applications_db: Dict[str, Application] = {}
user_applications: Dict[str, List[str]] = {}  # user_id -> [application_ids]
job_applications: Dict[str, List[str]] = {}  # job_id -> [application_ids]

# Import from other modules (these would be from database in production)
from app.routers.jobs import jobs_db
from app.routers.resumes import resumes_db, user_resumes
from app.routers.auth import users_db


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def apply_to_job(
    application_data: ApplicationCreate,
    current_user: TokenData = Depends(require_student())
):
    """
    Apply to a job posting.
    
    This endpoint allows students to apply to job postings using their
    uploaded resume and optional cover letter.
    
    Args:
        application_data: Application data including job_id, resume_id, cover_letter
        current_user: Current authenticated student user
        
    Returns:
        Dict containing application confirmation and details
        
    Raises:
        HTTPException: If job not found, resume not found, or already applied
    """
    # Validate job exists and is open
    if application_data.job_id not in jobs_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    job = jobs_db[application_data.job_id]
    if job.status != "open":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job is no longer accepting applications"
        )
    
    # Validate resume exists and belongs to user
    if application_data.resume_id not in resumes_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    resume = resumes_db[application_data.resume_id]
    if resume.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Resume does not belong to current user"
        )
    
    # Check if user has already applied to this job
    if _user_has_applied_to_job(current_user.user_id, application_data.job_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied to this job"
        )
    
    try:
        # Generate application ID
        application_id = str(uuid.uuid4())
        
        # Create application
        application = Application(
            _id=application_id,
            job_id=application_data.job_id,
            user_id=current_user.user_id,
            resume_id=application_data.resume_id,
            status=ApplicationStatus.APPLIED,
            cover_letter=application_data.cover_letter,
            applied_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store in database
        applications_db[application_id] = application
        
        # Update user applications
        if current_user.user_id not in user_applications:
            user_applications[current_user.user_id] = []
        user_applications[current_user.user_id].append(application_id)
        
        # Update job applications
        if application_data.job_id not in job_applications:
            job_applications[application_data.job_id] = []
        job_applications[application_data.job_id].append(application_id)
        
        # Create response
        application_out = ApplicationOut(
            _id=application_id,
            job_id=application.job_id,
            user_id=application.user_id,
            resume_id=application.resume_id,
            status=application.status,
            cover_letter=application.cover_letter,
            applied_at=application.applied_at,
            updated_at=application.updated_at
        )
        
        logger.info(f"User {current_user.user_id} applied to job {application_data.job_id}")
        
        return {
            "success": True,
            "message": "Application submitted successfully",
            "data": {
                "application": application_out.dict(),
                "job_info": {
                    "title": job.title,
                    "company": job.company_name,
                    "location": job.location
                },
                "next_steps": [
                    "Your application has been submitted",
                    "Employers will review and rank applications using AI",
                    "You'll be notified of any status updates"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error creating application for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting application: {str(e)}"
        )


@router.get("/", response_model=Dict[str, Any])
async def get_user_applications(
    status_filter: Optional[ApplicationStatus] = Query(None, description="Filter by application status"),
    skip: int = Query(0, ge=0, description="Number of applications to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of applications to return"),
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Get applications for the current user.
    
    For students: Returns their job applications
    For employers: Returns applications to their job postings
    
    Args:
        status_filter: Optional filter by application status
        skip: Number of applications to skip for pagination
        limit: Maximum number of applications to return
        current_user: Current authenticated user
        
    Returns:
        Dict containing list of applications and pagination info
    """
    try:
        if current_user.role == UserRole.STUDENT:
            return await _get_student_applications(
                current_user.user_id, status_filter, skip, limit
            )
        elif current_user.role == UserRole.EMPLOYER:
            return await _get_employer_applications(
                current_user.user_id, status_filter, skip, limit
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role"
            )
            
    except Exception as e:
        logger.error(f"Error getting applications for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving applications"
        )


@router.get("/{application_id}", response_model=Dict[str, Any])
async def get_application_details(
    application_id: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific application.
    
    Args:
        application_id: The ID of the application to retrieve
        current_user: Current authenticated user
        
    Returns:
        Dict containing detailed application information
        
    Raises:
        HTTPException: If application not found or access denied
    """
    # Check if application exists
    if application_id not in applications_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    application = applications_db[application_id]
    
    # Check access permissions
    if current_user.role == UserRole.STUDENT:
        if application.user_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this application"
            )
    elif current_user.role == UserRole.EMPLOYER:
        job = jobs_db.get(application.job_id)
        if not job or job.employer_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this application"
            )
    
    # Get related information
    job = jobs_db.get(application.job_id)
    resume = resumes_db.get(application.resume_id)
    user = users_db.get(application.user_id)
    
    # Create detailed response
    response_data = {
        "application": ApplicationOut(
            _id=application_id,
            job_id=application.job_id,
            user_id=application.user_id,
            resume_id=application.resume_id,
            status=application.status,
            cover_letter=application.cover_letter,
            applied_at=application.applied_at,
            updated_at=application.updated_at,
            match_score=application.match_score,
            notes=application.notes
        ).dict()
    }
    
    # Add job information
    if job:
        response_data["job_info"] = {
            "title": job.title,
            "company": job.company_name,
            "location": job.location,
            "employment_type": job.employment_type
        }
    
    # Add user information (for employers)
    if current_user.role == UserRole.EMPLOYER and user:
        response_data["candidate_info"] = {
            "name": user.profile.name,
            "email": user.email,
            "skills": user.profile.skills,
            "location": user.profile.location
        }
    
    # Add resume information
    if resume:
        response_data["resume_info"] = {
            "filename": resume.filename,
            "upload_date": resume.upload_date,
            "ai_feedback_score": resume.ai_feedback.ats_score if resume.ai_feedback else None
        }
    
    return {
        "success": True,
        "message": "Application details retrieved successfully",
        "data": response_data
    }


@router.put("/{application_id}/status", response_model=Dict[str, Any])
async def update_application_status(
    application_id: str,
    status_update: ApplicationUpdate,
    current_user: TokenData = Depends(require_employer())
):
    """
    Update the status of a job application (employer only).
    
    This endpoint allows employers to update application status
    (reviewed, shortlisted, interviewed, rejected, hired).
    
    Args:
        application_id: The ID of the application to update
        status_update: New status and optional notes
        current_user: Current authenticated employer user
        
    Returns:
        Dict containing updated application information
        
    Raises:
        HTTPException: If application not found or access denied
    """
    # Check if application exists
    if application_id not in applications_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    application = applications_db[application_id]
    
    # Check if employer owns the job
    job = jobs_db.get(application.job_id)
    if not job or job.employer_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this application"
        )
    
    # Update application
    application.status = status_update.status
    if status_update.notes:
        application.notes = status_update.notes
    application.updated_at = datetime.utcnow()
    
    # Save changes
    applications_db[application_id] = application
    
    # Create response
    application_out = ApplicationOut(
        _id=application_id,
        job_id=application.job_id,
        user_id=application.user_id,
        resume_id=application.resume_id,
        status=application.status,
        cover_letter=application.cover_letter,
        applied_at=application.applied_at,
        updated_at=application.updated_at,
        match_score=application.match_score,
        notes=application.notes
    )
    
    logger.info(f"Application {application_id} status updated to {status_update.status} by employer {current_user.user_id}")
    
    return {
        "success": True,
        "message": f"Application status updated to {status_update.status}",
        "data": {
            "application": application_out.dict(),
            "status_history": _get_status_history(application_id)
        }
    }


@router.delete("/{application_id}", response_model=SuccessResponse)
async def withdraw_application(
    application_id: str,
    current_user: TokenData = Depends(require_student())
):
    """
    Withdraw a job application (student only).
    
    Args:
        application_id: The ID of the application to withdraw
        current_user: Current authenticated student user
        
    Returns:
        Success response confirming withdrawal
        
    Raises:
        HTTPException: If application not found or access denied
    """
    # Check if application exists
    if application_id not in applications_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    
    application = applications_db[application_id]
    
    # Check ownership
    if application.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this application"
        )
    
    # Check if application can be withdrawn
    if application.status in [ApplicationStatus.HIRED, ApplicationStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot withdraw application with status: {application.status}"
        )
    
    # Remove application
    del applications_db[application_id]
    
    # Remove from user applications
    if current_user.user_id in user_applications:
        user_applications[current_user.user_id] = [
            app_id for app_id in user_applications[current_user.user_id]
            if app_id != application_id
        ]
    
    # Remove from job applications
    if application.job_id in job_applications:
        job_applications[application.job_id] = [
            app_id for app_id in job_applications[application.job_id]
            if app_id != application_id
        ]
    
    return SuccessResponse(
        message="Application withdrawn successfully"
    )


# Helper functions
def _user_has_applied_to_job(user_id: str, job_id: str) -> bool:
    """Check if user has already applied to a specific job."""
    user_app_ids = user_applications.get(user_id, [])
    for app_id in user_app_ids:
        if app_id in applications_db:
            app = applications_db[app_id]
            if app.job_id == job_id:
                return True
    return False


async def _get_student_applications(
    user_id: str,
    status_filter: Optional[ApplicationStatus],
    skip: int,
    limit: int
) -> Dict[str, Any]:
    """Get applications for a student user."""
    user_app_ids = user_applications.get(user_id, [])
    
    # Filter applications
    filtered_apps = []
    for app_id in user_app_ids:
        if app_id in applications_db:
            app = applications_db[app_id]
            if not status_filter or app.status == status_filter:
                filtered_apps.append(app)
    
    # Sort by applied date (newest first)
    filtered_apps.sort(key=lambda x: x.applied_at, reverse=True)
    
    # Apply pagination
    total_applications = len(filtered_apps)
    paginated_apps = filtered_apps[skip:skip + limit]
    
    # Create detailed response
    app_list = []
    for app in paginated_apps:
        # Get job info
        job = jobs_db.get(app.job_id)
        
        app_data = ApplicationOut(
            _id=app.id,
            job_id=app.job_id,
            user_id=app.user_id,
            resume_id=app.resume_id,
            status=app.status,
            cover_letter=app.cover_letter,
            applied_at=app.applied_at,
            updated_at=app.updated_at,
            match_score=app.match_score,
            notes=app.notes
        ).dict()
        
        if job:
            app_data["job_info"] = {
                "title": job.title,
                "company": job.company_name,
                "location": job.location,
                "employment_type": job.employment_type
            }
        
        app_list.append(app_data)
    
    return {
        "success": True,
        "message": f"Found {total_applications} applications",
        "data": {
            "applications": app_list,
            "pagination": {
                "total": total_applications,
                "skip": skip,
                "limit": limit,
                "has_more": skip + limit < total_applications
            },
            "status_filter": status_filter
        }
    }


async def _get_employer_applications(
    employer_id: str,
    status_filter: Optional[ApplicationStatus],
    skip: int,
    limit: int
) -> Dict[str, Any]:
    """Get applications for an employer's job postings."""
    # Get employer's jobs
    employer_job_ids = []
    for job_id, job in jobs_db.items():
        if job.employer_id == employer_id:
            employer_job_ids.append(job_id)
    
    # Get applications for employer's jobs
    employer_apps = []
    for job_id in employer_job_ids:
        job_app_ids = job_applications.get(job_id, [])
        for app_id in job_app_ids:
            if app_id in applications_db:
                app = applications_db[app_id]
                if not status_filter or app.status == status_filter:
                    employer_apps.append(app)
    
    # Sort by applied date (newest first)
    employer_apps.sort(key=lambda x: x.applied_at, reverse=True)
    
    # Apply pagination
    total_applications = len(employer_apps)
    paginated_apps = employer_apps[skip:skip + limit]
    
    # Create detailed response
    app_list = []
    for app in paginated_apps:
        # Get related info
        job = jobs_db.get(app.job_id)
        user = users_db.get(app.user_id)
        
        app_data = ApplicationOut(
            _id=app.id,
            job_id=app.job_id,
            user_id=app.user_id,
            resume_id=app.resume_id,
            status=app.status,
            cover_letter=app.cover_letter,
            applied_at=app.applied_at,
            updated_at=app.updated_at,
            match_score=app.match_score,
            notes=app.notes
        ).dict()
        
        if job:
            app_data["job_info"] = {
                "title": job.title,
                "location": job.location
            }
        
        if user:
            app_data["candidate_info"] = {
                "name": user.profile.name,
                "email": user.email,
                "skills": user.profile.skills[:5]  # Show top 5 skills
            }
        
        app_list.append(app_data)
    
    return {
        "success": True,
        "message": f"Found {total_applications} applications",
        "data": {
            "applications": app_list,
            "pagination": {
                "total": total_applications,
                "skip": skip,
                "limit": limit,
                "has_more": skip + limit < total_applications
            },
            "status_filter": status_filter
        }
    }


def _get_status_history(application_id: str) -> List[Dict[str, Any]]:
    """Get status change history for an application."""
    # In a real implementation, this would return actual status history
    # For now, return a placeholder
    return [
        {
            "status": "applied",
            "timestamp": datetime.utcnow().isoformat(),
            "notes": "Application submitted"
        }
    ]
