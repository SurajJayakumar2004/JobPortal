"""
AI-powered Career Counseling endpoints providing personalized career guidance,
skill gap analysis, and career path recommendations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from app.schemas import APIResponse, UserRole
from app.utils.dependencies import get_current_user
from app.services.counseling_service import career_counseling_service
from app.config import app_data
import logging

router = APIRouter(prefix="/counseling", tags=["career_counseling"])
logger = logging.getLogger(__name__)

@router.get("/career-assessment", response_model=APIResponse)
async def get_career_assessment(current_user: dict = Depends(get_current_user)):
    """Get comprehensive AI-powered career assessment and recommendations."""
    try:
        # Only job seekers can get career assessments
        if current_user.get("role") != UserRole.JOB_SEEKER:
            raise HTTPException(
                status_code=403, 
                detail="Only job seekers can access career counseling services"
            )
        
        # Get user's resume data
        user_resumes = [
            resume for resume in app_data.get("resumes", [])
            if resume["user_id"] == current_user["id"] and resume.get("parsing_result", {}).get("success")
        ]
        
        if not user_resumes:
            raise HTTPException(
                status_code=404, 
                detail="Please upload a resume first to get career assessment"
            )
        
        # Use the most recent resume
        latest_resume = max(user_resumes, key=lambda x: x.get("upload_timestamp", ""))
        parsing_result = latest_resume["parsing_result"]
        
        # Prepare candidate data
        candidate_data = {
            "skills": parsing_result.get("skills", {}),
            "experience_years": parsing_result.get("experience_years"),
            "education": parsing_result.get("education", []),
            "text": parsing_result.get("text", ""),
            "contact_info": parsing_result.get("contact_info", {}),
            "skill_score": parsing_result.get("skill_score", 0),
            "sentiment": parsing_result.get("sentiment", {})
        }
        
        # Get AI-powered career recommendations
        recommendations = career_counseling_service.get_career_recommendations(candidate_data)
        
        return APIResponse(
            success=True,
            message="Career assessment completed successfully",
            data={
                "assessment": recommendations,
                "resume_info": {
                    "resume_id": latest_resume["id"],
                    "filename": latest_resume["original_filename"],
                    "upload_date": latest_resume["upload_timestamp"]
                },
                "assessment_timestamp": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting career assessment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate career assessment")

@router.get("/skill-gap-analysis", response_model=APIResponse)
async def get_skill_gap_analysis(
    target_domain: str = Query(description="Target career domain (e.g., software_development, data_science)"),
    target_level: str = Query(description="Target career level (e.g., entry_level, mid_level, senior_level)"),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed skill gap analysis for a specific career path."""
    try:
        # Only job seekers can get skill gap analysis
        if current_user.get("role") != UserRole.JOB_SEEKER:
            raise HTTPException(
                status_code=403, 
                detail="Only job seekers can access skill gap analysis"
            )
        
        # Validate target parameters
        valid_domains = ["software_development", "data_science", "devops_cloud", "product_management", "cybersecurity"]
        valid_levels = ["entry_level", "mid_level", "senior_level", "management", "specialist"]
        
        if target_domain not in valid_domains:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid domain. Valid options: {', '.join(valid_domains)}"
            )
        
        if target_level not in valid_levels:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid level. Valid options: {', '.join(valid_levels)}"
            )
        
        # Get user's resume data
        user_resumes = [
            resume for resume in app_data.get("resumes", [])
            if resume["user_id"] == current_user["id"] and resume.get("parsing_result", {}).get("success")
        ]
        
        if not user_resumes:
            raise HTTPException(
                status_code=404, 
                detail="Please upload a resume first to get skill gap analysis"
            )
        
        # Use the most recent resume
        latest_resume = max(user_resumes, key=lambda x: x.get("upload_timestamp", ""))
        parsing_result = latest_resume["parsing_result"]
        
        candidate_skills = parsing_result.get("skills", {})
        
        # Perform skill gap analysis
        skill_gaps = career_counseling_service.analyze_skill_gaps(
            candidate_skills, target_domain, target_level
        )
        
        # Generate learning path
        learning_path = career_counseling_service.generate_learning_path(skill_gaps, timeframe_months=6)
        
        return APIResponse(
            success=True,
            message="Skill gap analysis completed successfully",
            data={
                "target_career": {
                    "domain": target_domain.replace("_", " ").title(),
                    "level": target_level.replace("_", " ").title()
                },
                "current_skills": candidate_skills,
                "skill_gap_analysis": skill_gaps,
                "learning_path": learning_path,
                "summary": {
                    "total_skill_gap": skill_gaps.get("total_skill_gap", 0),
                    "readiness_percentage": skill_gaps.get("readiness_score", 0),
                    "estimated_learning_time": f"{len(learning_path) * 6} months" if learning_path else "0 months",
                    "priority_areas": skill_gaps.get("priority_areas", [])
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting skill gap analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate skill gap analysis")

@router.get("/learning-path", response_model=APIResponse)
async def get_personalized_learning_path(
    timeframe_months: int = Query(default=6, ge=1, le=24, description="Learning timeframe in months"),
    current_user: dict = Depends(get_current_user)
):
    """Get a personalized learning path based on current skills and career goals."""
    try:
        # Only job seekers can get learning paths
        if current_user.get("role") != UserRole.JOB_SEEKER:
            raise HTTPException(
                status_code=403, 
                detail="Only job seekers can access learning path recommendations"
            )
        
        # Get user's resume data
        user_resumes = [
            resume for resume in app_data.get("resumes", [])
            if resume["user_id"] == current_user["id"] and resume.get("parsing_result", {}).get("success")
        ]
        
        if not user_resumes:
            raise HTTPException(
                status_code=404, 
                detail="Please upload a resume first to get learning path"
            )
        
        # Use the most recent resume
        latest_resume = max(user_resumes, key=lambda x: x.get("upload_timestamp", ""))
        parsing_result = latest_resume["parsing_result"]
        
        candidate_data = {
            "skills": parsing_result.get("skills", {}),
            "experience_years": parsing_result.get("experience_years"),
            "education": parsing_result.get("education", [])
        }
        
        # Identify current career domain and level
        current_domain = career_counseling_service.identify_career_domain(
            candidate_data["skills"], candidate_data.get("experience_years")
        )
        current_level = career_counseling_service.assess_current_level(
            candidate_data["skills"], 
            candidate_data.get("experience_years"),
            candidate_data.get("education")
        )
        
        # Determine next level for progression
        level_progression = ["entry_level", "mid_level", "senior_level", "management", "specialist"]
        current_index = level_progression.index(current_level) if current_level in level_progression else 0
        next_level = level_progression[min(current_index + 1, len(level_progression) - 1)]
        
        # Analyze skill gaps for next level
        skill_gaps = career_counseling_service.analyze_skill_gaps(
            candidate_data["skills"], current_domain, next_level
        )
        
        # Generate learning path
        learning_path = career_counseling_service.generate_learning_path(skill_gaps, timeframe_months)
        
        return APIResponse(
            success=True,
            message="Personalized learning path generated successfully",
            data={
                "current_profile": {
                    "domain": current_domain.replace("_", " ").title(),
                    "level": current_level.replace("_", " ").title(),
                    "skills_count": sum(len(skills) for skills in candidate_data["skills"].values())
                },
                "target_profile": {
                    "domain": current_domain.replace("_", " ").title(),
                    "level": next_level.replace("_", " ").title()
                },
                "learning_path": learning_path,
                "timeline": {
                    "total_months": timeframe_months,
                    "phases": len(learning_path),
                    "estimated_hours": sum(phase.get("estimated_hours", 0) for phase in learning_path)
                },
                "recommendations": [
                    "Follow the learning path in sequential order",
                    "Practice each skill with hands-on projects",
                    "Seek feedback and mentorship opportunities",
                    "Update your resume as you acquire new skills"
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating learning path: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate learning path")

@router.get("/industry-insights", response_model=APIResponse)
async def get_industry_insights(
    domain: str = Query(description="Career domain for insights"),
    current_user: dict = Depends(get_current_user)
):
    """Get industry insights and trends for a specific career domain."""
    try:
        # Validate domain
        valid_domains = ["software_development", "data_science", "devops_cloud", "product_management", "cybersecurity"]
        
        if domain not in valid_domains:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid domain. Valid options: {', '.join(valid_domains)}"
            )
        
        # Get industry trends from counseling service
        industry_info = career_counseling_service.industry_trends.get(domain, {})
        
        # Get career paths for the domain
        career_paths = career_counseling_service.career_paths.get(domain, {})
        
        return APIResponse(
            success=True,
            message="Industry insights retrieved successfully",
            data={
                "domain": domain.replace("_", " ").title(),
                "market_outlook": {
                    "growth_rate": industry_info.get("growth_rate", "moderate"),
                    "market_demand": industry_info.get("market_demand", "moderate"),
                    "salary_range": industry_info.get("avg_salary_range", "varies")
                },
                "trending_skills": industry_info.get("hot_skills", []),
                "career_progression": career_paths,
                "insights": [
                    "Stay updated with latest technology trends",
                    "Build a strong professional network",
                    "Contribute to open source projects",
                    "Obtain relevant certifications",
                    "Develop both technical and soft skills"
                ],
                "job_market_tips": [
                    "Tailor your resume for each application",
                    "Showcase projects that demonstrate your skills",
                    "Prepare for technical interviews",
                    "Highlight your problem-solving abilities",
                    "Demonstrate continuous learning mindset"
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting industry insights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get industry insights")

@router.get("/career-domains", response_model=APIResponse)
async def get_available_career_domains(current_user: dict = Depends(get_current_user)):
    """Get list of available career domains and levels for analysis."""
    return APIResponse(
        success=True,
        message="Available career domains and levels retrieved",
        data={
            "domains": [
                {
                    "id": "software_development",
                    "name": "Software Development",
                    "description": "Building software applications and systems"
                },
                {
                    "id": "data_science",
                    "name": "Data Science",
                    "description": "Analyzing data to extract business insights"
                },
                {
                    "id": "devops_cloud",
                    "name": "DevOps & Cloud",
                    "description": "Managing infrastructure and deployment pipelines"
                },
                {
                    "id": "product_management",
                    "name": "Product Management",
                    "description": "Guiding product development and strategy"
                },
                {
                    "id": "cybersecurity",
                    "name": "Cybersecurity",
                    "description": "Protecting systems and data from threats"
                }
            ],
            "levels": [
                {
                    "id": "entry_level",
                    "name": "Entry Level",
                    "description": "0-2 years of experience"
                },
                {
                    "id": "mid_level",
                    "name": "Mid Level",
                    "description": "2-5 years of experience"
                },
                {
                    "id": "senior_level",
                    "name": "Senior Level",
                    "description": "5+ years of experience"
                },
                {
                    "id": "management",
                    "name": "Management",
                    "description": "Leading teams and projects"
                },
                {
                    "id": "specialist",
                    "name": "Specialist",
                    "description": "Deep expertise in specific areas"
                }
            ]
        }
    )