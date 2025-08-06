"""
Employer-specific API endpoints.

This module handles employer profile management, company information,
job analytics, and other employer-specific functionality.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime, timedelta
import logging

from app.schemas import UserRole
from app.utils.dependencies import get_current_active_user, require_employer, TokenData

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage (replace with database in production)
employer_profiles: Dict[str, Dict[str, Any]] = {}
employer_analytics: Dict[str, Dict[str, Any]] = {}

# Import from other modules
from app.routers.auth import users_db
from app.routers.jobs import jobs_db, employer_jobs


@router.get("/profile", response_model=Dict[str, Any])
async def get_employer_profile(
    current_user: TokenData = Depends(require_employer())
):
    """
    Get the current employer's company profile.
    
    Returns:
        Dict containing employer profile information
    """
    try:
        profile = employer_profiles.get(current_user.user_id, {})
        
        # If no profile exists, create a default one
        if not profile:
            user = users_db.get(current_user.user_id)
            profile = {
                "company_name": user.profile.name if user else "",
                "industry": "",
                "company_size": "",
                "website": "",
                "description": "",
                "location": {
                    "address": "",
                    "city": "",
                    "state": "",
                    "country": "",
                    "postal_code": ""
                },
                "contact": {
                    "phone": "",
                    "email": user.email if user else "",
                    "linkedin": ""
                },
                "culture": {
                    "values": [],
                    "benefits": [],
                    "work_environment": ""
                },
                "logo_url": "",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            employer_profiles[current_user.user_id] = profile
        
        return {
            "success": True,
            "message": "Employer profile retrieved successfully",
            "data": {"profile": profile}
        }
        
    except Exception as e:
        logger.error(f"Error getting employer profile for {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving profile: {str(e)}"
        )


@router.put("/profile", response_model=Dict[str, Any])
async def update_employer_profile(
    profile_data: Dict[str, Any],
    current_user: TokenData = Depends(require_employer())
):
    """
    Update the current employer's company profile.
    
    Args:
        profile_data: Updated profile information
        current_user: Current authenticated employer user
        
    Returns:
        Dict containing updated profile information
    """
    try:
        # Get existing profile or create new one
        existing_profile = employer_profiles.get(current_user.user_id, {})
        
        # Update profile with new data
        updated_profile = {**existing_profile, **profile_data}
        updated_profile["updated_at"] = datetime.utcnow().isoformat()
        
        # If this is a new profile, set created_at
        if "created_at" not in updated_profile:
            updated_profile["created_at"] = datetime.utcnow().isoformat()
        
        # Save updated profile
        employer_profiles[current_user.user_id] = updated_profile
        
        logger.info(f"Updated employer profile for {current_user.user_id}")
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "data": {"profile": updated_profile}
        }
        
    except Exception as e:
        logger.error(f"Error updating employer profile for {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating profile: {str(e)}"
        )


@router.get("/dashboard", response_model=Dict[str, Any])
async def get_employer_dashboard(
    current_user: TokenData = Depends(require_employer())
):
    """
    Get employer dashboard overview with statistics and metrics.
    
    Returns:
        Dict containing dashboard statistics and recent activity
    """
    try:
        # Get employer's jobs
        employer_job_ids = employer_jobs.get(current_user.user_id, [])
        employer_job_list = [jobs_db[job_id] for job_id in employer_job_ids if job_id in jobs_db]
        
        # Calculate statistics
        total_jobs = len(employer_job_list)
        active_jobs = len([job for job in employer_job_list if job.status == "open"])
        closed_jobs = len([job for job in employer_job_list if job.status == "closed"])
        draft_jobs = len([job for job in employer_job_list if job.status == "draft"])
        
        # Calculate total applications (placeholder)
        total_applications = 0  # Would come from applications database
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_jobs = [
            job for job in employer_job_list 
            if job.posted_at > thirty_days_ago
        ]
        
        # Top performing jobs (by applications)
        top_jobs = sorted(employer_job_list, key=lambda x: x.posted_at, reverse=True)[:5]
        
        dashboard_data = {
            "statistics": {
                "total_jobs": total_jobs,
                "active_jobs": active_jobs,
                "closed_jobs": closed_jobs,
                "draft_jobs": draft_jobs,
                "total_applications": total_applications,
                "avg_applications_per_job": total_applications / max(total_jobs, 1)
            },
            "recent_activity": {
                "jobs_posted_last_30_days": len(recent_jobs),
                "recent_jobs": [
                    {
                        "id": job.id,
                        "title": job.title,
                        "status": job.status,
                        "posted_at": job.posted_at.isoformat(),
                        "applications_count": 0  # Placeholder
                    }
                    for job in recent_jobs[:5]
                ]
            },
            "top_performing_jobs": [
                {
                    "id": job.id,
                    "title": job.title,
                    "status": job.status,
                    "posted_at": job.posted_at.isoformat(),
                    "applications_count": 0  # Placeholder
                }
                for job in top_jobs
            ],
            "quick_actions": [
                {"action": "post_job", "label": "Post New Job", "count": None},
                {"action": "review_applications", "label": "Review Applications", "count": total_applications},
                {"action": "manage_jobs", "label": "Manage Jobs", "count": active_jobs},
                {"action": "view_analytics", "label": "View Analytics", "count": None}
            ]
        }
        
        return {
            "success": True,
            "message": "Dashboard data retrieved successfully",
            "data": dashboard_data
        }
        
    except Exception as e:
        logger.error(f"Error getting employer dashboard for {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving dashboard: {str(e)}"
        )


@router.get("/jobs", response_model=Dict[str, Any])
async def get_employer_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of jobs to return"),
    current_user: TokenData = Depends(require_employer())
):
    """
    Get all jobs posted by the current employer.
    
    Args:
        status: Optional status filter
        skip: Number of jobs to skip for pagination
        limit: Maximum number of jobs to return
        current_user: Current authenticated employer user
        
    Returns:
        Dict containing list of employer's jobs
    """
    try:
        # Get employer's jobs
        employer_job_ids = employer_jobs.get(current_user.user_id, [])
        employer_job_list = [jobs_db[job_id] for job_id in employer_job_ids if job_id in jobs_db]
        
        # Apply status filter
        if status:
            employer_job_list = [job for job in employer_job_list if job.status == status]
        
        # Sort by posted date (newest first)
        employer_job_list.sort(key=lambda x: x.posted_at, reverse=True)
        
        # Apply pagination
        total_jobs = len(employer_job_list)
        paginated_jobs = employer_job_list[skip:skip + limit]
        
        # Format job data
        jobs_data = []
        for job in paginated_jobs:
            job_data = {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "status": job.status,
                "location": job.location,
                "employment_type": job.employment_type,
                "salary_range": job.salary_range,
                "required_skills": job.required_skills,
                "posted_at": job.posted_at.isoformat(),
                "updated_at": job.updated_at.isoformat(),
                "applications_count": 0,  # Placeholder
                "views_count": 0  # Placeholder
            }
            jobs_data.append(job_data)
        
        return {
            "success": True,
            "message": f"Retrieved {len(jobs_data)} jobs",
            "data": {
                "jobs": jobs_data,
                "pagination": {
                    "total": total_jobs,
                    "skip": skip,
                    "limit": limit,
                    "has_more": skip + limit < total_jobs
                },
                "summary": {
                    "total_jobs": total_jobs,
                    "status_filter": status
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting employer jobs for {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving jobs: {str(e)}"
        )


@router.get("/analytics", response_model=Dict[str, Any])
async def get_employer_analytics(
    period: str = Query("30d", description="Analytics period: 7d, 30d, 90d"),
    current_user: TokenData = Depends(require_employer())
):
    """
    Get analytics data for the employer's job postings.
    
    Args:
        period: Time period for analytics (7d, 30d, 90d)
        current_user: Current authenticated employer user
        
    Returns:
        Dict containing analytics data
    """
    try:
        # Calculate date range
        days_map = {"7d": 7, "30d": 30, "90d": 90}
        days = days_map.get(period, 30)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get employer's jobs
        employer_job_ids = employer_jobs.get(current_user.user_id, [])
        employer_job_list = [jobs_db[job_id] for job_id in employer_job_ids if job_id in jobs_db]
        
        # Filter jobs by date range
        period_jobs = [job for job in employer_job_list if job.posted_at >= start_date]
        
        # Calculate analytics (placeholder data)
        analytics_data = {
            "period": period,
            "date_range": {
                "start": start_date.isoformat(),
                "end": datetime.utcnow().isoformat()
            },
            "overview": {
                "jobs_posted": len(period_jobs),
                "total_applications": 0,  # Placeholder
                "total_views": 0,  # Placeholder
                "avg_applications_per_job": 0,  # Placeholder
                "response_rate": 0.0  # Placeholder
            },
            "job_performance": [
                {
                    "job_id": job.id,
                    "title": job.title,
                    "posted_at": job.posted_at.isoformat(),
                    "applications": 0,  # Placeholder
                    "views": 0,  # Placeholder
                    "conversion_rate": 0.0  # Placeholder
                }
                for job in period_jobs[:10]  # Top 10 jobs
            ],
            "trends": {
                "applications_over_time": [],  # Placeholder
                "views_over_time": [],  # Placeholder
                "popular_skills": [],  # Placeholder
                "application_sources": []  # Placeholder
            }
        }
        
        return {
            "success": True,
            "message": f"Analytics data for {period} retrieved successfully",
            "data": analytics_data
        }
        
    except Exception as e:
        logger.error(f"Error getting employer analytics for {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving analytics: {str(e)}"
        )


@router.post("/upload-logo", response_model=Dict[str, Any])
async def upload_company_logo(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(require_employer())
):
    """
    Upload company logo for the employer profile.
    
    Args:
        file: Logo image file
        current_user: Current authenticated employer user
        
    Returns:
        Dict containing upload success status and logo URL
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed."
            )
        
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size is 5MB."
            )
        
        # Generate unique filename
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        unique_filename = f"logo_{current_user.user_id}_{uuid.uuid4().hex}.{file_extension}"
        
        # In production, save to cloud storage (S3, etc.)
        # For now, simulate upload
        logo_url = f"/uploads/logos/{unique_filename}"
        
        # Update employer profile with logo URL
        if current_user.user_id in employer_profiles:
            employer_profiles[current_user.user_id]["logo_url"] = logo_url
            employer_profiles[current_user.user_id]["updated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Uploaded logo for employer {current_user.user_id}: {unique_filename}")
        
        return {
            "success": True,
            "message": "Logo uploaded successfully",
            "data": {
                "logo_url": logo_url,
                "filename": unique_filename
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading logo for employer {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading logo: {str(e)}"
        )
