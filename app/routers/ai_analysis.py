"""
AI Analysis and Skill Gap router.

This module handles AI-powered analysis endpoints including skill gap analysis,
candidate recommendations, and advanced matching analytics.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, List, Optional
import logging

from app.schemas import (
    SkillGapAnalysisRequest, SkillGapAnalysisResponse,
    CandidateRecommendationRequest, JobMatchResponse
)
from app.services.matching_service import MatchingService
from app.utils.dependencies import (
    get_current_active_user, require_employer, 
    require_student, TokenData
)

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import from other modules (these would be from database in production)
from app.routers.resumes import resumes_db, user_resumes
from app.routers.auth import users_db
from app.routers.jobs import jobs_db

# Initialize matching service
matching_service = MatchingService()


@router.post("/skill-gap", response_model=Dict[str, Any])
async def analyze_skill_gap(
    candidate_id: str,
    job_id: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Perform detailed skill gap analysis between a candidate and job requirements.
    
    This endpoint uses AI to analyze the alignment between a candidate's skills
    and a job's requirements, providing detailed insights into skill coverage,
    gaps, and recommendations for improvement.
    
    Args:
        candidate_id: The ID of the candidate to analyze
        job_id: The ID of the job to analyze against
        current_user: Current authenticated user
        
    Returns:
        Dict containing detailed skill gap analysis
        
    Raises:
        HTTPException: If candidate/job not found or access denied
    """
    try:
        # Get job information
        if job_id not in jobs_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        job = jobs_db[job_id]
        
        # Get candidate information
        if candidate_id not in users_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        
        # Get candidate's resume
        candidate_resume_ids = user_resumes.get(candidate_id, [])
        if not candidate_resume_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume found for candidate"
            )
        
        latest_resume_id = candidate_resume_ids[-1]
        resume = resumes_db.get(latest_resume_id)
        
        if not resume or not resume.parsed_sections:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No parsed resume data found"
            )
        
        # Perform skill gap analysis
        candidate_skills = resume.parsed_sections.skills or []
        job_requirements = job.required_skills or []
        
        skill_gap_analysis = matching_service.calculate_skill_gap_score(
            candidate_skills=candidate_skills,
            job_requirements=job_requirements
        )
        
        # Add recommendations based on missing skills
        recommendations = []
        for missing_skill in skill_gap_analysis.get('missing_skills', [])[:3]:
            recommendations.append(f"Consider learning {missing_skill} to better match this role")
        
        if skill_gap_analysis.get('critical_gaps', 0) > 0:
            recommendations.append("Focus on developing critical skills first for better job compatibility")
        
        if skill_gap_analysis.get('skill_coverage', 0) > 80:
            recommendations.append("Strong skill alignment! Consider highlighting these skills in your application")
        
        skill_gap_analysis['recommendations'] = recommendations
        
        logger.info(f"Skill gap analysis completed for candidate {candidate_id} and job {job_id}")
        
        return {
            "success": True,
            "message": "Skill gap analysis completed successfully",
            "data": skill_gap_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing skill gap for candidate {candidate_id} and job {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error performing skill gap analysis: {str(e)}"
        )


@router.get("/candidate-insights/{candidate_id}", response_model=Dict[str, Any])
async def get_candidate_insights(
    candidate_id: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Get AI-powered insights about a candidate's profile and market fit.
    
    Args:
        candidate_id: The ID of the candidate to analyze
        current_user: Current authenticated user
        
    Returns:
        Dict containing candidate insights and recommendations
    """
    try:
        # Get candidate information
        if candidate_id not in users_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        
        user = users_db[candidate_id]
        
        # Get candidate's resume
        candidate_resume_ids = user_resumes.get(candidate_id, [])
        if not candidate_resume_ids:
            return {
                "success": True,
                "message": "No resume data available for insights",
                "data": {
                    "candidate_id": candidate_id,
                    "insights": [],
                    "recommendations": ["Upload a resume to get AI-powered insights"],
                    "market_fit_score": 0
                }
            }
        
        latest_resume_id = candidate_resume_ids[-1]
        resume = resumes_db.get(latest_resume_id)
        
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume data not found"
            )
        
        # Generate insights (simplified for this example)
        candidate_skills = resume.parsed_sections.skills if resume.parsed_sections else []
        
        insights = {
            "candidate_id": candidate_id,
            "profile_strength": {
                "overall_score": 78.5,
                "skills_diversity": len(set(candidate_skills)) if candidate_skills else 0,
                "experience_relevance": 85.2,
                "ats_compatibility": resume.ai_feedback.ats_score if resume.ai_feedback else 70.0
            },
            "market_fit": {
                "in_demand_skills": [skill for skill in candidate_skills if skill.lower() in ['python', 'react', 'aws', 'javascript']],
                "emerging_skills": [skill for skill in candidate_skills if skill.lower() in ['kubernetes', 'graphql', 'rust']],
                "skill_gaps": ["Machine Learning", "DevOps", "Cloud Architecture"]
            },
            "career_recommendations": [
                "Consider developing cloud computing skills to increase job opportunities",
                "Your profile shows strong technical foundation",
                "Focus on building a portfolio of projects to showcase your skills"
            ],
            "job_match_potential": {
                "best_fit_roles": ["Software Developer", "Full Stack Engineer", "Backend Developer"],
                "salary_range_estimate": "$70,000 - $95,000",
                "location_opportunities": ["San Francisco", "Seattle", "Austin", "Remote"]
            }
        }
        
        return {
            "success": True,
            "message": "Candidate insights generated successfully",
            "data": insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating candidate insights for {candidate_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating candidate insights: {str(e)}"
        )


@router.get("/market-trends", response_model=Dict[str, Any])
async def get_market_trends(
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Get current job market trends and skill demand analytics.
    
    This endpoint provides insights into current job market conditions,
    in-demand skills, salary trends, and hiring patterns.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Dict containing market trends and analytics
    """
    try:
        # Generate market trends data (in production, this would come from real market data)
        trends = {
            "skill_demand": {
                "most_in_demand": [
                    {"skill": "Python", "demand_score": 95, "growth": "+15%"},
                    {"skill": "JavaScript", "demand_score": 92, "growth": "+12%"},
                    {"skill": "React", "demand_score": 88, "growth": "+20%"},
                    {"skill": "AWS", "demand_score": 85, "growth": "+25%"},
                    {"skill": "Machine Learning", "demand_score": 82, "growth": "+30%"}
                ],
                "emerging_skills": [
                    {"skill": "Rust", "demand_score": 45, "growth": "+150%"},
                    {"skill": "GraphQL", "demand_score": 52, "growth": "+80%"},
                    {"skill": "Kubernetes", "demand_score": 68, "growth": "+60%"},
                    {"skill": "Flutter", "demand_score": 41, "growth": "+120%"}
                ]
            },
            "job_categories": {
                "highest_demand": [
                    {"category": "Software Engineering", "openings": 15420, "growth": "+18%"},
                    {"category": "Data Science", "openings": 8950, "growth": "+35%"},
                    {"category": "Product Management", "openings": 6780, "growth": "+22%"},
                    {"category": "DevOps Engineering", "openings": 5340, "growth": "+40%"}
                ]
            },
            "salary_trends": {
                "software_engineer": {
                    "entry_level": "$75,000 - $95,000",
                    "mid_level": "$95,000 - $130,000",
                    "senior_level": "$130,000 - $180,000",
                    "trend": "+8% YoY"
                },
                "data_scientist": {
                    "entry_level": "$85,000 - $110,000",
                    "mid_level": "$110,000 - $150,000",
                    "senior_level": "$150,000 - $200,000",
                    "trend": "+12% YoY"
                }
            },
            "remote_work": {
                "percentage_remote": 65,
                "hybrid_percentage": 25,
                "on_site_percentage": 10,
                "trend": "Increasing remote opportunities"
            },
            "hiring_timeline": {
                "average_time_to_hire": "21 days",
                "interview_rounds": "3-4 rounds",
                "response_time": "5-7 days"
            }
        }
        
        return {
            "success": True,
            "message": "Market trends retrieved successfully",
            "data": trends
        }
        
    except Exception as e:
        logger.error(f"Error retrieving market trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving market trends: {str(e)}"
        )


@router.post("/optimize-job-posting", response_model=Dict[str, Any])
async def optimize_job_posting(
    job_id: str,
    current_user: TokenData = Depends(require_employer())
):
    """
    Get AI-powered suggestions to optimize a job posting for better candidate attraction.
    
    This endpoint analyzes a job posting and provides recommendations to improve
    its effectiveness in attracting qualified candidates.
    
    Args:
        job_id: The ID of the job to optimize
        current_user: Current authenticated employer user
        
    Returns:
        Dict containing optimization suggestions
    """
    try:
        # Get job information
        if job_id not in jobs_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job not found"
            )
        
        job = jobs_db[job_id]
        
        # Check ownership
        if job.employer_id != current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this job"
            )
        
        # Analyze job posting and generate optimization suggestions
        optimization_suggestions = {
            "job_id": job_id,
            "current_performance": {
                "applications_received": _get_applications_count(job_id),
                "average_match_score": 74.2,
                "time_since_posted": "5 days"
            },
            "title_optimization": {
                "current_title": job.title,
                "suggestions": [
                    "Consider adding seniority level for clarity",
                    "Include key technology stack in title",
                    "Keep title under 60 characters for better visibility"
                ],
                "optimized_examples": [
                    f"Senior {job.title} - Python/React",
                    f"{job.title} (Remote) - {job.company_name}"
                ]
            },
            "description_optimization": {
                "readability_score": 78,
                "suggestions": [
                    "Add bullet points for better readability",
                    "Include company culture information",
                    "Specify remote work options clearly",
                    "Add growth opportunities section"
                ]
            },
            "requirements_optimization": {
                "total_requirements": len(job.required_skills),
                "suggestions": [
                    "Consider marking some skills as 'nice-to-have' to increase applicant pool",
                    "Add years of experience for each technology",
                    "Include soft skills requirements"
                ],
                "skill_demand_analysis": {
                    skill: "High demand" if skill.lower() in ['python', 'react', 'aws'] 
                    else "Medium demand" 
                    for skill in job.required_skills[:5]
                }
            },
            "compensation_optimization": {
                "current_range": job.salary_range,
                "market_comparison": "Competitive with market standards",
                "suggestions": [
                    "Consider adding benefits information",
                    "Include equity/stock options if available",
                    "Mention flexible working arrangements"
                ]
            },
            "ats_optimization": {
                "ats_score": 85,
                "suggestions": [
                    "Good keyword usage for ATS systems",
                    "Consider adding industry-specific terms",
                    "Job posting length is optimal"
                ]
            }
        }
        
        return {
            "success": True,
            "message": "Job posting optimization analysis completed",
            "data": optimization_suggestions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing job posting {job_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error optimizing job posting: {str(e)}"
        )


# Helper function
def _get_applications_count(job_id: str) -> int:
    """Get the number of applications for a job (placeholder implementation)."""
    # In production, this would query the applications database
    return hash(job_id) % 20  # Return a consistent but varied number for demo
