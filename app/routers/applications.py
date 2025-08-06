from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional

from app.schemas import APIResponse, UserRole, ApplicationStatus
from app.services.application_service import ApplicationService
from app.services.job_service import JobService
from app.utils.dependencies import get_current_active_user

router = APIRouter(tags=["applications"])


@router.get("/my-applications", response_model=APIResponse)
def get_my_applications(
    skip: int = Query(0, ge=0, description="Number of applications to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of applications to return"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get applications for the current user (job seekers only)
    """
    try:
        # Check if user is a job seeker
        if current_user.get("role") != UserRole.JOB_SEEKER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only job seekers can view their applications"
            )
        
        # Get user's applications
        applications = ApplicationService.get_applications_by_job_seeker(
            current_user["id"], skip=skip, limit=limit
        )
        
        total_count = ApplicationService.count_applications_by_job_seeker(
            current_user["id"]
        )
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(applications)} application(s)",
            data={
                "applications": applications,
                "pagination": {
                    "total_count": total_count,
                    "returned_count": len(applications),
                    "skip": skip,
                    "limit": limit,
                    "has_more": (skip + len(applications)) < total_count
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve applications. Please try again."
        )


@router.get("/job/{job_id}", response_model=APIResponse)
def get_job_applications(
    job_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[ApplicationStatus] = Query(None, description="Filter by application status"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get applications for a specific job (employers only - must own the job)
    """
    try:
        # Check if user is an employer
        if current_user.get("role") != UserRole.EMPLOYER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only employers can view job applications"
            )
        
        # Verify job exists and belongs to the current employer
        job = JobService.get_job_by_id(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        if job["employer_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view applications for your own job postings"
            )
        
        # Get applications for the job
        applications = ApplicationService.get_applications_by_job(
            job_id, skip=skip, limit=limit, status_filter=status_filter
        )
        
        total_count = ApplicationService.count_applications_by_job(
            job_id, status_filter=status_filter
        )
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(applications)} application(s) for job",
            data={
                "applications": applications,
                "job": {
                    "id": job["id"],
                    "title": job["title"],
                    "company_name": job["company_name"]
                },
                "pagination": {
                    "total_count": total_count,
                    "returned_count": len(applications),
                    "skip": skip,
                    "limit": limit,
                    "has_more": (skip + len(applications)) < total_count
                },
                "filters": {
                    "status_filter": status_filter
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve job applications. Please try again."
        )


@router.get("/employer-applications", response_model=APIResponse)
def get_employer_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status_filter: Optional[ApplicationStatus] = Query(None, description="Filter by application status"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get all applications for jobs posted by the current employer
    """
    try:
        # Check if user is an employer
        if current_user.get("role") != UserRole.EMPLOYER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only employers can view applications"
            )
        
        # Get all applications for this employer's jobs
        applications = ApplicationService.get_applications_by_employer(
            current_user["id"], skip=skip, limit=limit, status_filter=status_filter
        )
        
        total_count = ApplicationService.count_applications_by_employer(
            current_user["id"], status_filter=status_filter
        )
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(applications)} application(s)",
            data={
                "applications": applications,
                "pagination": {
                    "total_count": total_count,
                    "returned_count": len(applications),
                    "skip": skip,
                    "limit": limit,
                    "has_more": (skip + len(applications)) < total_count
                },
                "filters": {
                    "status_filter": status_filter
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve applications. Please try again."
        )


@router.get("/{application_id}", response_model=APIResponse)
def get_application_details(
    application_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get details of a specific application
    """
    try:
        # Get application
        application = ApplicationService.get_application_by_id(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Check permissions
        if current_user["role"] == UserRole.JOB_SEEKER:
            # Job seekers can only view their own applications
            if application["job_seeker_id"] != current_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view your own applications"
                )
        elif current_user["role"] == UserRole.EMPLOYER:
            # Employers can only view applications for their jobs
            job = JobService.get_job_by_id(application["job_id"])
            if not job or job["employer_id"] != current_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only view applications for your own job postings"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Add job details to application
        job = JobService.get_job_by_id(application["job_id"])
        if job:
            application["job_title"] = job["title"]
            application["company_name"] = job["company_name"]
            application["job_location"] = job["location"]
        
        return APIResponse(
            success=True,
            message="Application details retrieved successfully",
            data={
                "application": application
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve application details. Please try again."
        )


@router.put("/{application_id}/status", response_model=APIResponse)
def update_application_status(
    application_id: int,
    new_status: ApplicationStatus,
    notes: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Update application status (employers only)
    """
    try:
        # Check if user is an employer
        if current_user.get("role") != UserRole.EMPLOYER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only employers can update application status"
            )
        
        # Get application
        application = ApplicationService.get_application_by_id(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Verify employer owns the job
        job = JobService.get_job_by_id(application["job_id"])
        if not job or job["employer_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update applications for your own job postings"
            )
        
        # Update application status
        updated_application = ApplicationService.update_application_status(
            application_id, new_status, notes
        )
        
        return APIResponse(
            success=True,
            message="Application status updated successfully",
            data={
                "application": updated_application,
                "changes": {
                    "status": new_status,
                    "notes": notes
                }
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update application status. Please try again."
        )


@router.delete("/{application_id}", response_model=APIResponse)
def delete_application(
    application_id: int,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Delete an application (job seekers can delete their own applications)
    """
    try:
        # Check if user is a job seeker
        if current_user.get("role") != UserRole.JOB_SEEKER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only job seekers can delete applications"
            )
        
        # Get application
        application = ApplicationService.get_application_by_id(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Check if user owns this application
        if application["job_seeker_id"] != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own applications"
            )
        
        # Delete application
        ApplicationService.delete_application(application_id)
        
        return APIResponse(
            success=True,
            message="Application deleted successfully",
            data={
                "deleted_application_id": application_id
            }
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete application. Please try again."
        )