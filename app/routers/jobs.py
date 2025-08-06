from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
import logging

from app.schemas import JobCreate, JobResponse, JobUpdate, APIResponse, UserRole, ApplicationCreate
from app.services.job_service import JobService
from app.services.application_service import ApplicationService
from app.config import app_data
from app.utils.dependencies import (
    get_current_active_user, 
    get_current_employer, 
    get_current_user_optional
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    current_user: Dict[str, Any] = Depends(get_current_employer)
):
    """
    Create a new job posting (employers only)
    
    Args:
        job_data (JobCreate): Job creation data
        current_user: Current authenticated employer
        
    Returns:
        APIResponse: Success response with job data
        
    Raises:
        HTTPException: If job creation fails
    """
    try:
        job = JobService.create_job(job_data, current_user["id"])
        
        return APIResponse(
            success=True,
            message="Job created successfully",
            data={
                "job": job,
                "next_steps": [
                    "Job is now live and visible to job seekers",
                    "You can edit or deactivate the job anytime",
                    "Check applications in the applications section"
                ]
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create job. Please try again."
        )


@router.get("/", response_model=APIResponse)
async def list_jobs(
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of jobs to return"),
    search: Optional[str] = Query(None, description="Search term for job title or company"),
    location: Optional[str] = Query(None, description="Filter by location"),
    job_type: Optional[str] = Query(None, description="Filter by job type"),
    active_only: bool = Query(True, description="Show only active jobs"),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    List all available jobs with filtering and pagination
    
    Args:
        skip: Number of jobs to skip (pagination)
        limit: Number of jobs to return (pagination)
        search: Search term for job title or company name
        location: Filter by job location
        job_type: Filter by job type
        active_only: Show only active jobs
        current_user: Optional current user (for personalization)
        
    Returns:
        APIResponse: List of jobs matching criteria
    """
    try:
        filters = {
            "search": search,
            "location": location,
            "job_type": job_type,
            "active_only": active_only
        }
        
        jobs = JobService.get_jobs(skip=skip, limit=limit, filters=filters)
        total_count = JobService.count_jobs(filters=filters)
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(jobs)} jobs",
            data={
                "jobs": jobs,
                "pagination": {
                    "total_count": total_count,
                    "returned_count": len(jobs),
                    "skip": skip,
                    "limit": limit,
                    "has_more": (skip + len(jobs)) < total_count
                },
                "filters_applied": {k: v for k, v in filters.items() if v is not None}
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve jobs. Please try again."
        )


@router.get("/{job_id}", response_model=APIResponse)
async def get_job_details(
    job_id: int,
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Get details for a specific job
    
    Args:
        job_id (int): Job ID
        current_user: Optional current user (for personalization)
        
    Returns:
        APIResponse: Job details
        
    Raises:
        HTTPException: If job not found
    """
    job = JobService.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Add additional context based on user role
    additional_data = {}
    if current_user:
        if current_user["role"] == UserRole.EMPLOYER and current_user["id"] == job["employer_id"]:
            # If employer viewing their own job, add application statistics
            additional_data["is_owner"] = True
            additional_data["applications_count"] = job.get("applications_count", 0)
        elif current_user["role"] == UserRole.JOB_SEEKER:
            # If job seeker, add application status if they applied
            from app.services.application_service import ApplicationService
            application = ApplicationService.get_application_by_job_and_user(
                job_id, current_user["id"]
            )
            additional_data["user_applied"] = application is not None
            if application:
                additional_data["application_status"] = application["status"]
    
    return APIResponse(
        success=True,
        message="Job details retrieved successfully",
        data={
            "job": job,
            **additional_data
        }
    )


@router.put("/{job_id}", response_model=APIResponse)
async def update_job(
    job_id: int,
    job_update: JobUpdate,
    current_user: Dict[str, Any] = Depends(get_current_employer)
):
    """
    Update a job posting (job owner only)
    
    Args:
        job_id (int): Job ID to update
        job_update (JobUpdate): Job update data
        current_user: Current authenticated employer
        
    Returns:
        APIResponse: Success response with updated job data
        
    Raises:
        HTTPException: If job not found or user not authorized
    """
    job = JobService.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job["employer_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own job postings"
        )
    
    try:
        updated_job = JobService.update_job(job_id, job_update)
        
        return APIResponse(
            success=True,
            message="Job updated successfully",
            data={
                "job": updated_job
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update job. Please try again."
        )


@router.delete("/{job_id}", response_model=APIResponse)
async def delete_job(
    job_id: int,
    current_user: Dict[str, Any] = Depends(get_current_employer)
):
    """
    Delete a job posting (job owner only)
    
    Args:
        job_id (int): Job ID to delete
        current_user: Current authenticated employer
        
    Returns:
        APIResponse: Success confirmation
        
    Raises:
        HTTPException: If job not found or user not authorized
    """
    job = JobService.get_job_by_id(job_id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job["employer_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own job postings"
        )
    
    try:
        JobService.delete_job(job_id)
        
        return APIResponse(
            success=True,
            message="Job deleted successfully",
            data={
                "deleted_job_id": job_id
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete job. Please try again."
        )


@router.get("/employer/{employer_id}", response_model=APIResponse)
async def get_employer_jobs(
    employer_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    active_only: bool = Query(True),
    current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)
):
    """
    Get all jobs posted by a specific employer
    
    Args:
        employer_id (int): Employer ID
        skip: Number of jobs to skip
        limit: Number of jobs to return
        active_only: Show only active jobs
        current_user: Optional current user
        
    Returns:
        APIResponse: List of employer's jobs
    """
    try:
        jobs = JobService.get_jobs_by_employer(
            employer_id=employer_id,
            skip=skip,
            limit=limit,
            active_only=active_only
        )
        
        total_count = JobService.count_jobs_by_employer(
            employer_id=employer_id,
            active_only=active_only
        )
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(jobs)} jobs for employer",
            data={
                "jobs": jobs,
                "employer_id": employer_id,
                "pagination": {
                    "total_count": total_count,
                    "returned_count": len(jobs),
                    "skip": skip,
                    "limit": limit,
                    "has_more": (skip + len(jobs)) < total_count
                }
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employer jobs. Please try again."
        )


@router.post("/{job_id}/apply", response_model=APIResponse)
def apply_to_job(
    job_id: int,
    application_data: ApplicationCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Apply to a job (job seekers only)
    
    This endpoint allows job seekers to submit applications for job postings.
    """
    try:
        # Check if user is a job seeker
        if current_user.get("role") != UserRole.JOB_SEEKER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only job seekers can apply to jobs"
            )
        
        # Verify the job exists and is active
        job = JobService.get_job_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        if not job.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This job is no longer accepting applications"
            )
        
        # Create the application
        application = ApplicationService.create_application(
            application_data, 
            current_user["id"]
        )
        
        return APIResponse(
            success=True,
            message="Application submitted successfully",
            data={
                "application": {
                    "id": application["id"],
                    "job_id": application["job_id"],
                    "job_title": job["title"],
                    "company_name": job["company_name"],
                    "status": application["status"],
                    "applied_at": application["applied_at"],
                    "cover_letter": application["cover_letter"]
                },
                "next_steps": [
                    "Your application has been submitted to the employer",
                    "You will be notified of any status updates",
                    "You can track your application status in your dashboard"
                ]
            }
        )
        
    except ValueError as e:
        # Handle specific application errors
        if "already applied" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already applied to this job"
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit application. Please try again."
        )


# AI-powered job matching and recommendation endpoints

@router.get("/{job_id}/match-candidates", response_model=APIResponse)
async def get_job_candidate_matches(
    job_id: int,
    top_n: int = Query(default=10, le=50, description="Number of top candidates to return"),
    current_user: Dict[str, Any] = Depends(get_current_employer)
):
    """Get AI-powered candidate matches for a specific job."""
    try:
        # Get job details
        job = JobService.get_job_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Check if employer owns this job
        if job["employer_id"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get all resumes (candidates) from app_data
        candidates = []
        for resume in app_data.get("resumes", []):
            if resume.get("parsing_result", {}).get("success"):
                candidate_data = {
                    "id": resume["user_id"],
                    "resume_id": resume["id"],
                    "skills": resume["parsing_result"].get("skills", {}),
                    "experience_years": resume["parsing_result"].get("experience_years"),
                    "education": resume["parsing_result"].get("education", []),
                    "text": resume["parsing_result"].get("text", ""),
                    "contact_info": resume["parsing_result"].get("contact_info", {})
                }
                candidates.append(candidate_data)
        
        if not candidates:
            return APIResponse(
                success=True,
                message="No candidates found for matching",
                data={"matches": []}
            )
        
        # Use AI matching service
        from app.services.matching_service import job_matching_service
        
        job_data = {
            "id": job["id"],
            "title": job["title"],
            "description": job["description"],
            "requirements": job.get("requirements", ""),
            "location": job.get("location", ""),
            "salary_range": job.get("salary_range", "")
        }
        
        # Get ranked candidates
        ranked_candidates = job_matching_service.rank_candidates_for_job(candidates, job_data)
        
        # Format response
        matches = []
        for match in ranked_candidates[:top_n]:
            candidate = match["candidate_data"]
            match_details = match["match_details"]
            
            matches.append({
                "candidate_id": candidate["id"],
                "resume_id": candidate["resume_id"],
                "match_score": match["match_score"],
                "contact_info": candidate.get("contact_info", {}),
                "experience_years": candidate.get("experience_years"),
                "education_count": len(candidate.get("education", [])),
                "skill_match": match_details.get("skill_match", 0),
                "experience_match": match_details.get("experience_match", 0),
                "education_match": match_details.get("education_match", 0),
                "matching_skills": match_details.get("matching_skills", {}),
                "missing_skills": match_details.get("missing_skills", {}),
                "job_level": match_details.get("job_level", "unknown")
            })
        
        return APIResponse(
            success=True,
            message=f"Found {len(matches)} candidate matches",
            data={
                "job_id": job_id,
                "job_title": job["title"],
                "matches": matches,
                "total_candidates_analyzed": len(candidates),
                "matching_criteria": {
                    "skills_weight": "40%",
                    "experience_weight": "25%",
                    "text_similarity_weight": "20%",
                    "education_weight": "15%"
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job matches: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to find candidate matches")


@router.get("/recommendations", response_model=APIResponse)
async def get_job_recommendations(
    top_n: int = Query(default=10, le=50, description="Number of job recommendations"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get AI-powered job recommendations for the current user."""
    try:
        # Only job seekers can get recommendations
        if current_user.get("role") != UserRole.JOB_SEEKER:
            raise HTTPException(status_code=403, detail="Only job seekers can get recommendations")
        
        # Get user's resume data
        user_resumes = [
            resume for resume in app_data.get("resumes", [])
            if resume["user_id"] == current_user["id"] and resume.get("parsing_result", {}).get("success")
        ]
        
        if not user_resumes:
            raise HTTPException(
                status_code=404, 
                detail="Please upload a resume first to get job recommendations"
            )
        
        # Use the most recent resume
        latest_resume = max(user_resumes, key=lambda x: x.get("upload_timestamp", ""))
        parsing_result = latest_resume["parsing_result"]
        
        candidate_data = {
            "skills": parsing_result.get("skills", {}),
            "experience_years": parsing_result.get("experience_years"),
            "education": parsing_result.get("education", []),
            "text": parsing_result.get("text", ""),
            "contact_info": parsing_result.get("contact_info", {})
        }
        
        # Get all active jobs
        jobs = [job for job in JobService.get_all_jobs() if job.get("is_active", True)]
        
        if not jobs:
            return APIResponse(
                success=True,
                message="No active jobs available for recommendations",
                data={"recommendations": []}
            )
        
        # Use AI matching service for recommendations
        from app.services.matching_service import job_matching_service
        
        job_recommendations = job_matching_service.recommend_jobs_for_candidate(
            candidate_data, jobs, top_n
        )
        
        # Format response
        recommendations = []
        for rec in job_recommendations:
            job = rec["job_data"]
            match_details = rec["match_details"]
            
            recommendations.append({
                "job_id": job["id"],
                "title": job["title"],
                "company": job.get("company", ""),
                "location": job.get("location", ""),
                "salary_range": job.get("salary_range", ""),
                "employment_type": job.get("employment_type", ""),
                "match_score": rec["match_score"],
                "skill_match": match_details.get("skill_match", 0),
                "experience_match": match_details.get("experience_match", 0),
                "education_match": match_details.get("education_match", 0),
                "matching_skills": match_details.get("matching_skills", {}),
                "missing_skills": match_details.get("missing_skills", {}),
                "job_level": match_details.get("job_level", "unknown"),
                "recommendation_reason": _generate_recommendation_reason(match_details)
            })
        
        return APIResponse(
            success=True,
            message=f"Found {len(recommendations)} job recommendations",
            data={
                "recommendations": recommendations,
                "user_profile": {
                    "skills_count": sum(len(skills) for skills in candidate_data["skills"].values()),
                    "experience_years": candidate_data.get("experience_years"),
                    "education_count": len(candidate_data.get("education", []))
                },
                "resume_id": latest_resume["id"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get job recommendations")


def _generate_recommendation_reason(match_details: dict) -> str:
    """Generate a human-readable recommendation reason."""
    reasons = []
    
    skill_match = match_details.get("skill_match", 0)
    experience_match = match_details.get("experience_match", 0)
    
    if skill_match > 80:
        reasons.append("Strong skill alignment")
    elif skill_match > 60:
        reasons.append("Good skill match")
    
    if experience_match > 80:
        reasons.append("Perfect experience level")
    elif experience_match > 60:
        reasons.append("Suitable experience")
    
    matching_skills = match_details.get("matching_skills", {})
    if matching_skills:
        skill_count = sum(len(skills) for skills in matching_skills.values())
        if skill_count > 0:
            reasons.append(f"Matches {skill_count} required skills")
    
    if not reasons:
        reasons.append("Potential career growth opportunity")
    
    return " • ".join(reasons)