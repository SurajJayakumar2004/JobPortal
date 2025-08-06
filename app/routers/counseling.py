"""
Career counseling router for AI-powered career guidance.

This module handles all career counseling endpoints including report
generation, skill recommendations, and career path analysis for students.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime
import logging

from app.schemas import (
    CounselingReportOut, CounselingReportCreate, CounselingReport,
    SuccessResponse, UserRole
)
from app.services.counseling_service import CounselingService
from app.utils.dependencies import require_student, get_current_active_user, TokenData

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for counseling reports (replace with database in production)
counseling_reports_db: Dict[str, CounselingReport] = {}
user_reports: Dict[str, List[str]] = {}  # user_id -> [report_ids]

# Import from other modules
from app.routers.resumes import resumes_db, user_resumes
from app.routers.auth import users_db

# Initialize counseling service
counseling_service = CounselingService()


@router.post("/generate", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def generate_counseling_report(
    target_role: Optional[str] = Query(None, description="Target role for career guidance"),
    interests: Optional[str] = Query(None, description="User interests (comma-separated)"),
    current_user: TokenData = Depends(require_student())
):
    """
    Generate a comprehensive AI-powered career counseling report.
    
    This endpoint analyzes the user's resume, skills, and profile to provide
    personalized career guidance including suggested career paths, skill gaps,
    and learning recommendations.
    
    Args:
        target_role: Optional specific role the user is targeting
        interests: Optional user interests (comma-separated)
        current_user: Current authenticated student user
        
    Returns:
        Dict containing generated counseling report and career guidance
        
    Raises:
        HTTPException: If user has no resume or generation fails
    """
    try:
        # Get user's latest resume for analysis
        user_resume_ids = user_resumes.get(current_user.user_id, [])
        if not user_resume_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No resume found. Please upload a resume first for career counseling."
            )
        
        # Get the latest resume
        latest_resume_id = user_resume_ids[-1]
        resume = resumes_db.get(latest_resume_id)
        
        if not resume or not resume.parsed_sections:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume not processed yet. Please wait for resume processing to complete."
            )
        
        # Get user profile information
        user = users_db.get(current_user.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        # Prepare data for counseling service
        user_skills = resume.parsed_sections.skills or []
        user_experience = resume.parsed_sections.experience or []
        
        # Parse interests if provided
        user_interests = []
        if interests:
            user_interests = [interest.strip() for interest in interests.split(',')]
        else:
            # Use interests from profile if available
            user_interests = user.profile.interests or []
        
        # Generate counseling report
        report = await counseling_service.generate_counseling_report(
            user_id=current_user.user_id,
            user_skills=user_skills,
            user_experience=user_experience,
            user_interests=user_interests,
            target_role=target_role
        )
        
        # Store report in database
        counseling_reports_db[report.id] = report
        
        # Update user's report list
        if current_user.user_id not in user_reports:
            user_reports[current_user.user_id] = []
        user_reports[current_user.user_id].append(report.id)
        
        # Create response
        report_out = CounselingReportOut(
            _id=report.id,
            user_id=report.user_id,
            generated_on=report.generated_on,
            skills_summary=report.skills_summary,
            suggested_paths=report.suggested_paths,
            missing_skills=report.missing_skills,
            recommended_resources=report.recommended_resources,
            overall_score=report.overall_score
        )
        
        logger.info(f"Generated counseling report {report.id} for user {current_user.user_id}")
        
        return {
            "success": True,
            "message": "Career counseling report generated successfully",
            "data": {
                "report": report_out.dict(),
                "analysis_summary": {
                    "total_skills_analyzed": len(user_skills),
                    "career_paths_suggested": len(report.suggested_paths),
                    "skill_gaps_identified": len(report.missing_skills),
                    "learning_resources": len(report.recommended_resources),
                    "overall_readiness": f"{report.overall_score:.1f}/100"
                },
                "next_steps": [
                    "Review suggested career paths and their requirements",
                    "Focus on developing missing skills",
                    "Explore recommended learning resources",
                    "Update your resume with new skills as you learn them"
                ]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating counseling report for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating counseling report: {str(e)}"
        )


@router.get("/reports", response_model=Dict[str, Any])
async def get_user_counseling_reports(
    current_user: TokenData = Depends(require_student())
):
    """
    Get all counseling reports for the current user.
    
    Args:
        current_user: Current authenticated student user
        
    Returns:
        Dict containing list of user's counseling reports
    """
    user_report_ids = user_reports.get(current_user.user_id, [])
    
    if not user_report_ids:
        return {
            "success": True,
            "message": "No counseling reports found",
            "data": {
                "reports": [],
                "total": 0,
                "suggestion": "Generate your first career counseling report to get personalized guidance"
            }
        }
    
    # Get report details
    reports_list = []
    for report_id in user_report_ids:
        if report_id in counseling_reports_db:
            report = counseling_reports_db[report_id]
            report_out = CounselingReportOut(
                _id=report.id,
                user_id=report.user_id,
                generated_on=report.generated_on,
                skills_summary=report.skills_summary,
                suggested_paths=report.suggested_paths,
                missing_skills=report.missing_skills,
                recommended_resources=report.recommended_resources,
                overall_score=report.overall_score
            )
            reports_list.append(report_out.dict())
    
    return {
        "success": True,
        "message": f"Found {len(reports_list)} counseling reports",
        "data": {
            "reports": reports_list,
            "total": len(reports_list)
        }
    }


@router.get("/reports/{report_id}", response_model=Dict[str, Any])
async def get_counseling_report_details(
    report_id: str,
    current_user: TokenData = Depends(require_student())
):
    """
    Get detailed information about a specific counseling report.
    
    Args:
        report_id: The ID of the counseling report to retrieve
        current_user: Current authenticated student user
        
    Returns:
        Dict containing detailed counseling report information
        
    Raises:
        HTTPException: If report not found or access denied
    """
    # Check if report exists
    if report_id not in counseling_reports_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Counseling report not found"
        )
    
    report = counseling_reports_db[report_id]
    
    # Check ownership
    if report.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this counseling report"
        )
    
    # Create detailed response
    report_out = CounselingReportOut(
        _id=report.id,
        user_id=report.user_id,
        generated_on=report.generated_on,
        skills_summary=report.skills_summary,
        suggested_paths=report.suggested_paths,
        missing_skills=report.missing_skills,
        recommended_resources=report.recommended_resources,
        overall_score=report.overall_score
    )
    
    return {
        "success": True,
        "message": "Counseling report details retrieved successfully",
        "data": {
            "report": report_out.dict(),
            "insights": {
                "career_readiness_level": _get_readiness_level(report.overall_score),
                "top_strengths": report.skills_summary[:3],
                "priority_skills": report.missing_skills[:5],
                "recommended_focus": _get_focus_recommendation(report)
            }
        }
    }


@router.get("/skill-recommendations", response_model=Dict[str, Any])
async def get_skill_recommendations(
    target_role: str = Query(..., description="Target role for skill recommendations"),
    current_user: TokenData = Depends(require_student())
):
    """
    Get specific skill recommendations for a target role.
    
    This endpoint provides tailored skill recommendations based on the user's
    current skills and a specific target role they're interested in.
    
    Args:
        target_role: The target role to get skill recommendations for
        current_user: Current authenticated student user
        
    Returns:
        Dict containing skill recommendations and learning guidance
        
    Raises:
        HTTPException: If user has no resume
    """
    try:
        # Get user's current skills from latest resume
        user_resume_ids = user_resumes.get(current_user.user_id, [])
        current_skills = []
        
        if user_resume_ids:
            latest_resume_id = user_resume_ids[-1]
            resume = resumes_db.get(latest_resume_id)
            if resume and resume.parsed_sections and resume.parsed_sections.skills:
                current_skills = resume.parsed_sections.skills
        
        # Get skill recommendations
        recommendations = await counseling_service.get_skill_recommendations(
            current_skills=current_skills,
            target_role=target_role
        )
        
        return {
            "success": True,
            "message": f"Skill recommendations generated for {target_role}",
            "data": {
                "target_role": target_role,
                "current_skills": current_skills,
                "recommendations": recommendations,
                "skill_gap_analysis": {
                    "current_skills_count": len(current_skills),
                    "required_skills_count": len(recommendations['required_skills']),
                    "missing_skills_count": len(recommendations['missing_skills']),
                    "skill_coverage": _calculate_skill_coverage(
                        current_skills, recommendations['required_skills']
                    )
                },
                "next_steps": [
                    "Focus on learning the missing required skills first",
                    "Consider the recommended additional skills for competitive advantage",
                    "Look for projects or courses that combine multiple skills",
                    "Update your resume as you develop new skills"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting skill recommendations for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting skill recommendations: {str(e)}"
        )


@router.get("/career-paths", response_model=Dict[str, Any])
async def get_available_career_paths(
    category: Optional[str] = Query(None, description="Filter by career category"),
    current_user: TokenData = Depends(require_student())
):
    """
    Get available career paths and their requirements.
    
    This endpoint returns a list of available career paths with their
    descriptions, requirements, and growth potential information.
    
    Args:
        category: Optional category filter (tech, business, design, etc.)
        current_user: Current authenticated student user
        
    Returns:
        Dict containing available career paths and information
    """
    # Import career paths from service
    from app.services.counseling_service import CAREER_PATHS
    
    career_paths_list = []
    for path_key, path_data in CAREER_PATHS.items():
        # Apply category filter if specified
        if category:
            category_lower = category.lower()
            path_title_lower = path_data['title'].lower()
            path_desc_lower = path_data['description'].lower()
            
            if not (category_lower in path_title_lower or category_lower in path_desc_lower):
                continue
        
        career_path_info = {
            "id": path_key,
            "title": path_data['title'],
            "description": path_data['description'],
            "required_skills": path_data['required_skills'],
            "growth_potential": path_data['growth_potential'],
            "average_salary": path_data['average_salary']
        }
        career_paths_list.append(career_path_info)
    
    return {
        "success": True,
        "message": f"Found {len(career_paths_list)} career paths",
        "data": {
            "career_paths": career_paths_list,
            "total": len(career_paths_list),
            "categories": [
                "Software Engineering",
                "Data Science",
                "Product Management", 
                "Cybersecurity",
                "Cloud Engineering",
                "UI/UX Design",
                "Digital Marketing"
            ]
        }
    }


@router.delete("/reports/{report_id}", response_model=SuccessResponse)
async def delete_counseling_report(
    report_id: str,
    current_user: TokenData = Depends(require_student())
):
    """
    Delete a counseling report.
    
    Args:
        report_id: The ID of the counseling report to delete
        current_user: Current authenticated student user
        
    Returns:
        Success response confirming deletion
        
    Raises:
        HTTPException: If report not found or access denied
    """
    # Check if report exists
    if report_id not in counseling_reports_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Counseling report not found"
        )
    
    report = counseling_reports_db[report_id]
    
    # Check ownership
    if report.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this counseling report"
        )
    
    # Delete report
    del counseling_reports_db[report_id]
    
    # Remove from user's report list
    if current_user.user_id in user_reports:
        user_reports[current_user.user_id] = [
            rid for rid in user_reports[current_user.user_id] 
            if rid != report_id
        ]
    
    return SuccessResponse(
        message="Counseling report deleted successfully"
    )


# Helper functions
def _get_readiness_level(score: float) -> str:
    """Get career readiness level based on score."""
    if score >= 80:
        return "Excellent - You're well-prepared for your target roles"
    elif score >= 60:
        return "Good - Some skill development needed"
    elif score >= 40:
        return "Fair - Focus on building key skills"
    else:
        return "Developing - Significant skill building recommended"


def _get_focus_recommendation(report: CounselingReport) -> str:
    """Get focus recommendation based on report analysis."""
    if len(report.missing_skills) > 5:
        return "Focus on learning the most critical missing skills first"
    elif report.overall_score < 50:
        return "Build foundational skills and gain more experience"
    elif len(report.suggested_paths) > 2:
        return "Explore different career paths to find the best fit"
    else:
        return "Continue developing skills in your chosen career direction"


def _calculate_skill_coverage(current_skills: List[str], required_skills: List[str]) -> float:
    """Calculate skill coverage percentage."""
    if not required_skills:
        return 100.0
    
    current_skills_lower = [skill.lower() for skill in current_skills]
    matched_skills = 0
    
    for req_skill in required_skills:
        if any(req_skill.lower() in curr_skill for curr_skill in current_skills_lower):
            matched_skills += 1
    
    return (matched_skills / len(required_skills)) * 100
