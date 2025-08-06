from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional

from app.schemas import APIResponse, UserRole
from app.services.job_service import JobService
from app.services.application_service import ApplicationService
from app.utils.dependencies import get_current_active_user

router = APIRouter(tags=["employers"])


@router.get("/dashboard", response_model=APIResponse)
def get_employer_dashboard(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get employer dashboard statistics and overview
    """
    try:
        # Check if user is an employer
        if current_user.get("role") != UserRole.EMPLOYER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only employers can access the employer dashboard"
            )
        
        employer_id = current_user["id"]
        
        # Get job statistics
        total_jobs = JobService.count_jobs_by_employer(employer_id, active_only=False)
        active_jobs = JobService.count_jobs_by_employer(employer_id, active_only=True)
        
        # Get application statistics
        app_stats = ApplicationService.get_application_statistics(employer_id=employer_id)
        
        # Get recent applications
        recent_applications = ApplicationService.get_applications_by_employer(
            employer_id, skip=0, limit=5
        )
        
        # Get recent jobs
        recent_jobs = JobService.get_jobs_by_employer(
            employer_id, skip=0, limit=5, active_only=False
        )
        
        return APIResponse(
            success=True,
            message="Employer dashboard data retrieved successfully",
            data={
                "employer": {
                    "id": current_user["id"],
                    "email": current_user["email"],
                    "full_name": current_user["full_name"]
                },
                "statistics": {
                    "jobs": {
                        "total": total_jobs,
                        "active": active_jobs,
                        "inactive": total_jobs - active_jobs
                    },
                    "applications": app_stats
                },
                "recent_activity": {
                    "applications": recent_applications,
                    "jobs": recent_jobs
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employer dashboard. Please try again."
        )


@router.get("/profile", response_model=APIResponse)
def get_employer_profile(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """
    Get employer profile information
    """
    try:
        # Check if user is an employer
        if current_user.get("role") != UserRole.EMPLOYER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only employers can access this endpoint"
            )
        
        # Return employer profile (would be expanded with more details in real implementation)
        profile = {
            "id": current_user["id"],
            "email": current_user["email"],
            "full_name": current_user["full_name"],
            "role": current_user["role"],
            "company_name": "TechCorp Inc.",  # This would come from database
            "company_description": "A leading technology company focused on innovation",
            "industry": "Technology",
            "company_size": "100-500 employees",
            "location": "San Francisco, CA",
            "website": "https://techcorp.com",
            "created_at": "2025-01-01T00:00:00",
            "is_verified": True
        }
        
        return APIResponse(
            success=True,
            message="Employer profile retrieved successfully",
            data={
                "profile": profile
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve employer profile. Please try again."
        )