"""
Student Insights API router.

This router handles personalized career insights, recommendations,
and skill analysis for students based on their resume data and preferences.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import List, Optional
import logging
from datetime import datetime

from app.services.student_insights_service import StudentInsightsService
from app.services.resume_parser import ResumeParserService
from app.utils.dependencies import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/student-insights", tags=["Student Insights"])

# Initialize services
student_insights_service = StudentInsightsService()
resume_parser_service = ResumeParserService()


@router.post("/analyze-resume")
async def analyze_student_resume(
    file: UploadFile = File(...),
    preferred_industries: Optional[str] = Form(None),
    career_goals: Optional[str] = Form(None),
    target_salary_range: Optional[str] = Form(None),
    current_user = Depends(get_current_user)
):
    """
    Analyze a student's resume and generate personalized career insights.
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.docx', '.doc')):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and Word documents are supported"
            )
        
        # Save uploaded file
        file_path = await resume_parser_service.save_uploaded_file(file)
        
        # Parse resume
        parsed_resume_data = await resume_parser_service.parse_resume_file(
            file_path, file.filename
        )
        
        # Extract parsed sections
        parsed_sections = parsed_resume_data.get('parsed_sections')
        if not parsed_sections:
            raise HTTPException(
                status_code=400,
                detail="Could not extract meaningful content from resume"
            )
        
        # Process preferences
        industries_list = []
        if preferred_industries:
            industries_list = [industry.strip() for industry in preferred_industries.split(',')]
        
        # Generate personalized insights
        insights = await student_insights_service.generate_personalized_insights(
            student_id=current_user.get('id', 'anonymous'),
            parsed_resume=parsed_sections,
            preferred_industries=industries_list,
            career_goals=career_goals,
            target_salary_range=target_salary_range
        )
        
        # Combine resume analysis with personalized insights
        response = {
            'success': True,
            'resume_analysis': {
                'parsed_sections': parsed_resume_data.get('parsed_sections').__dict__,
                'ai_feedback': parsed_resume_data.get('ai_feedback').__dict__ if parsed_resume_data.get('ai_feedback') else None
            },
            'personalized_insights': insights,
            'analysis_timestamp': datetime.utcnow().isoformat(),
            'filename': file.filename
        }
        
        logger.info(f"Generated personalized insights for student {current_user.get('id')}")
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing student resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing resume: {str(e)}"
        )


@router.post("/quick-assessment")
async def quick_career_assessment(
    skills: List[str],
    experience_years: int = 0,
    education_level: str = "bachelor",
    preferred_industries: Optional[List[str]] = None,
    career_goals: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Generate quick career insights based on user-provided information.
    """
    try:
        # Create a mock parsed resume structure from provided data
        from app.schemas import ParsedResumeSection
        
        mock_resume = ParsedResumeSection(
            summary=[f"Professional with {experience_years} years of experience"],
            experience=[f"Professional experience: {experience_years} years"] if experience_years > 0 else [],
            education=[f"{education_level.title()} degree"],
            skills=skills,
            projects=None,
            certifications=None
        )
        
        # Generate insights
        insights = await student_insights_service.generate_personalized_insights(
            student_id=current_user.get('id', 'anonymous'),
            parsed_resume=mock_resume,
            preferred_industries=preferred_industries or [],
            career_goals=career_goals,
            target_salary_range=None
        )
        
        response = {
            'success': True,
            'personalized_insights': insights,
            'assessment_type': 'quick_assessment',
            'analysis_timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Generated quick assessment for student {current_user.get('id')}")
        return response
        
    except Exception as e:
        logger.error(f"Error in quick career assessment: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating career assessment: {str(e)}"
        )


@router.get("/skill-recommendations/{target_role}")
async def get_skill_recommendations(
    target_role: str,
    current_skills: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Get skill recommendations for a specific target role.
    """
    try:
        current_skills_list = []
        if current_skills:
            current_skills_list = [skill.strip() for skill in current_skills.split(',')]
        
        # Use counseling service for skill recommendations
        recommendations = await student_insights_service.counseling_service.get_skill_recommendations(
            current_skills=current_skills_list,
            target_role=target_role
        )
        
        # Enhance with personalized learning suggestions
        enhanced_recommendations = {
            'target_role': target_role,
            'current_skills': current_skills_list,
            'skill_analysis': recommendations,
            'personalized_learning_plan': _generate_learning_plan(
                recommendations.get('missing_skills', []),
                target_role
            ),
            'estimated_timeline': _estimate_learning_timeline(
                recommendations.get('missing_skills', [])
            )
        }
        
        logger.info(f"Generated skill recommendations for role: {target_role}")
        return enhanced_recommendations
        
    except Exception as e:
        logger.error(f"Error getting skill recommendations: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting skill recommendations: {str(e)}"
        )


@router.get("/career-paths")
async def get_personalized_career_paths(
    industry: Optional[str] = None,
    experience_level: str = "entry",
    current_user = Depends(get_current_user)
):
    """
    Get personalized career paths based on industry and experience level.
    """
    try:
        # Use the industry paths from student insights service
        industry_paths = student_insights_service.industry_paths
        
        if industry and industry.lower() in industry_paths:
            industry_data = industry_paths[industry.lower()]
            
            # Get appropriate roles for experience level
            if experience_level == 'entry':
                current_roles = industry_data['entry_level']
                next_roles = industry_data['mid_level']
            elif experience_level == 'mid':
                current_roles = industry_data['mid_level']
                next_roles = industry_data['senior_level']
            else:
                current_roles = industry_data['senior_level']
                next_roles = ['Executive Leadership', 'C-Suite Positions']
            
            career_path = {
                'industry': industry,
                'current_level': experience_level,
                'current_opportunities': current_roles,
                'next_level_opportunities': next_roles,
                'key_skills_needed': industry_data['key_skills'],
                'development_recommendations': _get_development_recommendations(
                    experience_level, industry_data['key_skills']
                )
            }
        else:
            # Provide general career path guidance
            career_path = {
                'general_guidance': True,
                'current_level': experience_level,
                'development_focus': _get_general_development_focus(experience_level),
                'skill_priorities': student_insights_service.skill_priorities['high_demand']
            }
        
        logger.info(f"Generated career paths for industry: {industry}, level: {experience_level}")
        return career_path
        
    except Exception as e:
        logger.error(f"Error getting career paths: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting career paths: {str(e)}"
        )


@router.get("/market-insights")
async def get_market_insights(
    skills: Optional[str] = None,
    industry: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """
    Get current market insights and trends relevant to the student.
    """
    try:
        skills_list = []
        if skills:
            skills_list = [skill.strip() for skill in skills.split(',')]
        
        # Generate market insights
        insights = {
            'high_demand_skills': student_insights_service.skill_priorities['high_demand'],
            'emerging_skills': student_insights_service.skill_priorities['emerging'],
            'industry_trends': _get_industry_trends(industry),
            'skill_market_analysis': _analyze_skill_market_value(skills_list),
            'salary_trends': _get_salary_trends(industry),
            'job_market_outlook': _get_job_market_outlook(industry)
        }
        
        logger.info(f"Generated market insights for industry: {industry}")
        return insights
        
    except Exception as e:
        logger.error(f"Error getting market insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting market insights: {str(e)}"
        )


# Helper functions
def _generate_learning_plan(missing_skills: List[str], target_role: str) -> List[dict]:
    """Generate a personalized learning plan for missing skills."""
    learning_plan = []
    
    for i, skill in enumerate(missing_skills[:5]):  # Top 5 skills
        plan_item = {
            'skill': skill,
            'priority': 'High' if i < 2 else 'Medium',
            'estimated_time': '2-4 weeks' if skill.lower() in ['excel', 'communication'] else '1-3 months',
            'recommended_resources': _get_skill_resources(skill),
            'assessment_method': 'Project-based' if 'programming' in skill.lower() else 'Certification'
        }
        learning_plan.append(plan_item)
    
    return learning_plan


def _estimate_learning_timeline(missing_skills: List[str]) -> dict:
    """Estimate timeline for learning missing skills."""
    quick_skills = ['excel', 'communication', 'teamwork']
    medium_skills = ['sql', 'data analysis', 'project management']
    complex_skills = ['programming', 'machine learning', 'cloud computing']
    
    quick_count = sum(1 for skill in missing_skills if any(q in skill.lower() for q in quick_skills))
    medium_count = sum(1 for skill in missing_skills if any(m in skill.lower() for m in medium_skills))
    complex_count = sum(1 for skill in missing_skills if any(c in skill.lower() for c in complex_skills))
    
    total_weeks = (quick_count * 2) + (medium_count * 6) + (complex_count * 12)
    
    return {
        'total_estimated_weeks': total_weeks,
        'total_estimated_months': round(total_weeks / 4, 1),
        'quick_skills': quick_count,
        'medium_skills': medium_count,
        'complex_skills': complex_count,
        'recommendation': 'Focus on 1-2 skills at a time for best results'
    }


def _get_skill_resources(skill: str) -> List[str]:
    """Get recommended resources for learning a specific skill."""
    skill_lower = skill.lower()
    
    if 'programming' in skill_lower or 'python' in skill_lower:
        return ['Codecademy', 'freeCodeCamp', 'Python.org tutorial']
    elif 'sql' in skill_lower:
        return ['SQLBolt', 'W3Schools SQL', 'DataCamp SQL']
    elif 'excel' in skill_lower:
        return ['Microsoft Excel Help', 'ExcelJet', 'Coursera Excel courses']
    elif 'communication' in skill_lower:
        return ['Toastmasters', 'Coursera Communication courses', 'LinkedIn Learning']
    else:
        return ['Coursera', 'edX', 'LinkedIn Learning', 'YouTube tutorials']


def _get_development_recommendations(experience_level: str, key_skills: List[str]) -> List[str]:
    """Get development recommendations based on experience level."""
    if experience_level == 'entry':
        return [
            f"Focus on building foundational skills: {', '.join(key_skills[:3])}",
            "Gain practical experience through internships or projects",
            "Build a professional portfolio showcasing your abilities"
        ]
    elif experience_level == 'mid':
        return [
            "Develop leadership and mentoring skills",
            "Specialize in a particular domain or technology",
            "Build cross-functional collaboration experience"
        ]
    else:
        return [
            "Focus on strategic thinking and business acumen",
            "Develop executive leadership capabilities",
            "Build industry network and thought leadership"
        ]


def _get_general_development_focus(experience_level: str) -> List[str]:
    """Get general development focus areas by experience level."""
    if experience_level == 'entry':
        return [
            "Build strong technical foundation",
            "Develop professional communication skills",
            "Gain hands-on experience through projects"
        ]
    elif experience_level == 'mid':
        return [
            "Develop specialized expertise",
            "Build leadership and team management skills",
            "Focus on business impact and results"
        ]
    else:
        return [
            "Strategic leadership development",
            "Industry expertise and thought leadership",
            "Organizational and cultural transformation"
        ]


def _get_industry_trends(industry: str) -> dict:
    """Get current trends for a specific industry."""
    trends = {
        'technology': {
            'hot_topics': ['AI/ML', 'Cloud Computing', 'Cybersecurity', 'DevOps'],
            'growth_areas': ['Data Science', 'Full-Stack Development', 'Cloud Architecture'],
            'outlook': 'Very positive with continued high demand'
        },
        'business': {
            'hot_topics': ['Digital Transformation', 'Data Analytics', 'Remote Work'],
            'growth_areas': ['Business Analytics', 'Project Management', 'Digital Marketing'],
            'outlook': 'Stable with emphasis on digital skills'
        },
        'healthcare': {
            'hot_topics': ['Telemedicine', 'Health Informatics', 'Personalized Medicine'],
            'growth_areas': ['Healthcare IT', 'Clinical Data Analysis', 'Patient Care Technology'],
            'outlook': 'Strong growth driven by aging population and technology'
        }
    }
    
    return trends.get(industry.lower() if industry else 'technology', trends['technology'])


def _analyze_skill_market_value(skills: List[str]) -> dict:
    """Analyze the market value of a set of skills."""
    high_value_skills = ['python', 'machine learning', 'cloud computing', 'data science', 'javascript']
    medium_value_skills = ['sql', 'excel', 'project management', 'communication']
    
    analysis = {
        'high_value_skills': [skill for skill in skills if any(hv in skill.lower() for hv in high_value_skills)],
        'medium_value_skills': [skill for skill in skills if any(mv in skill.lower() for mv in medium_value_skills)],
        'total_market_score': 0,
        'recommendations': []
    }
    
    # Calculate market score
    analysis['total_market_score'] = (len(analysis['high_value_skills']) * 10 + 
                                    len(analysis['medium_value_skills']) * 5)
    
    # Generate recommendations
    if analysis['total_market_score'] < 20:
        analysis['recommendations'].append("Consider developing high-demand technical skills")
    if not analysis['high_value_skills']:
        analysis['recommendations'].append("Add at least one high-value skill like Python or Cloud Computing")
    
    return analysis


def _get_salary_trends(industry: str) -> dict:
    """Get salary trends for an industry."""
    return {
        'average_growth': '3-5% annually',
        'high_demand_premium': '10-20% above average',
        'geographic_variation': 'Significant differences between major cities and rural areas',
        'remote_work_impact': 'Increasing opportunities for remote positions'
    }


def _get_job_market_outlook(industry: str) -> dict:
    """Get job market outlook for an industry."""
    return {
        'overall_growth': 'Positive',
        'automation_impact': 'Some roles being automated, new roles emerging',
        'skill_demand_shift': 'Increasing demand for digital and analytical skills',
        'recommendation': 'Focus on skills that complement automation rather than compete with it'
    }
