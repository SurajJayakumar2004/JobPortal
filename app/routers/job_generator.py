"""
Job Generation Router - Handles job posting creation and personalized career insights.

This router provides endpoints for generating job descriptions from structured data
and creating personalized recommendations for students.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Optional
import logging
from datetime import datetime

from app.services.job_generator_service import JobGeneratorService
from app.services.matching_service import MatchingService
from app.utils.dependencies import get_current_user
from app.schemas import User, Job, JobStatus

# Import jobs database from jobs router
from app.routers.jobs import jobs_db, employer_jobs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Job Generation"])

# Initialize services
job_generator = JobGeneratorService()
matching_service = MatchingService()

# Sample job data from the user's request
SAMPLE_JOB_DATA = [
    {
        "jobTitle": "Junior Python Developer",
        "industry": "Technology",
        "skillKeywords": [
            "Python", "Basic Algorithms and Data Structures", "Version Control (Git/GitHub)",
            "Debugging", "REST APIs", "Unit Testing", "SQL", "Problem Solving",
            "Communication", "Basic Object-Oriented Programming", "HTML/CSS (basic)",
            "Code Documentation"
        ],
        "requiredCertifications": [
            "Python Institute PCEP – Certified Entry-Level Python Programmer",
            "Microsoft Certified: Azure Fundamentals",
            "AWS Certified Cloud Practitioner"
        ]
    },
    {
        "jobTitle": "UX/UI Designer",
        "industry": "Technology",
        "skillKeywords": [
            "User Research", "Wireframing", "Prototyping", "Visual Design",
            "Interaction Design", "User Testing", "Design Thinking", "Figma",
            "Adobe XD", "Sketch", "Typography", "Color Theory", "Communication",
            "Collaboration", "Information Architecture", "Responsive Design"
        ],
        "requiredCertifications": [
            "NN/g UX Certification",
            "Certified Usability Analyst (CUA)",
            "Adobe Certified Expert (ACE)"
        ]
    },
    {
        "jobTitle": "Product Manager",
        "industry": "Technology",
        "skillKeywords": [
            "Product Lifecycle Management", "Roadmapping", "Agile Methodology",
            "Scrum", "User Story Writing", "Market Research", "Stakeholder Management",
            "Requirements Gathering", "Business Analysis", "Data-Driven Decision Making",
            "Prioritization", "Communication", "Leadership", "Problem Solving",
            "Wireframing (basic)"
        ],
        "requiredCertifications": [
            "Certified Scrum Product Owner (CSPO)",
            "Pragmatic Institute Certified",
            "Project Management Professional (PMP)"
        ]
    },
    {
        "jobTitle": "Senior DevOps Engineer",
        "industry": "Technology",
        "skillKeywords": [
            "CI/CD Pipelines", "Infrastructure as Code (IaC)", "Kubernetes",
            "Docker", "AWS / Azure / Google Cloud", "Ansible", "Terraform",
            "Linux Administration", "Scripting (Python, Bash)", "Monitoring and Logging",
            "Networking", "Security Best Practices", "Automation", "Problem Solving",
            "Collaboration"
        ],
        "requiredCertifications": [
            "AWS Certified DevOps Engineer – Professional",
            "Certified Kubernetes Administrator (CKA)",
            "Microsoft Certified: Azure DevOps Engineer Expert",
            "HashiCorp Certified: Terraform Associate"
        ]
    },
    {
        "jobTitle": "Digital Marketing Specialist",
        "industry": "Marketing",
        "skillKeywords": [
            "SEO", "SEM", "Content Marketing", "Social Media Marketing",
            "Google Analytics", "Google Ads", "Email Marketing",
            "Conversion Rate Optimization", "Copywriting", "Data Analysis",
            "Campaign Management", "Communication", "Creativity", "A/B Testing",
            "Marketing Automation"
        ],
        "requiredCertifications": [
            "Google Ads Certification",
            "Google Analytics Individual Qualification (GAIQ)",
            "HubSpot Content Marketing Certification",
            "Facebook Blueprint Certification"
        ]
    },
    {
        "jobTitle": "Data Scientist",
        "industry": "Technology",
        "skillKeywords": [
            "Python", "R", "SQL", "Machine Learning", "Deep Learning",
            "Statistics", "Data Visualization", "Tableau", "Pandas",
            "NumPy", "Scikit-learn", "TensorFlow", "Big Data",
            "Problem Solving", "Communication"
        ],
        "requiredCertifications": [
            "Certified Analytics Professional (CAP)",
            "TensorFlow Developer Certificate",
            "Microsoft Certified: Azure Data Scientist Associate"
        ]
    },
    {
        "jobTitle": "Registered Nurse",
        "industry": "Healthcare",
        "skillKeywords": [
            "Patient Care", "Medical Records Management", "Electronic Health Records (EHR)",
            "Patient Assessment", "Medication Administration", "IV Therapy",
            "Wound Care", "Critical Thinking", "Compassion", "Teamwork"
        ],
        "requiredCertifications": [
            "NCLEX-RN",
            "Basic Life Support (BLS)",
            "Advanced Cardiovascular Life Support (ACLS)"
        ]
    },
    {
        "jobTitle": "Data Engineer",
        "industry": "Technology",
        "skillKeywords": [
            "Python", "Java", "SQL", "ETL Processes", "Big Data (Hadoop, Spark)",
            "Data Pipeline Development", "Cloud Platforms (AWS, GCP, Azure)",
            "Data Warehousing", "NoSQL Databases", "Scripting", "Automation",
            "Problem Solving"
        ],
        "requiredCertifications": [
            "Google Professional Data Engineer",
            "AWS Certified Big Data – Specialty",
            "Microsoft Certified: Azure Data Engineer Associate"
        ]
    },
    {
        "jobTitle": "Cybersecurity Analyst",
        "industry": "Technology",
        "skillKeywords": [
            "Network Security", "Threat Analysis", "SIEM Tools", "Incident Response",
            "Risk Assessment", "Firewalls", "Encryption", "Penetration Testing",
            "Compliance Standards", "Security Monitoring", "Communication"
        ],
        "requiredCertifications": [
            "Certified Information Systems Security Professional (CISSP)",
            "Certified Ethical Hacker (CEH)",
            "CompTIA Security+"
        ]
    },
    {
        "jobTitle": "Cloud Architect",
        "industry": "Technology",
        "skillKeywords": [
            "Cloud Infrastructure Design", "AWS", "Azure", "Google Cloud Platform",
            "Networking", "Security Architecture", "Cost Optimization",
            "DevOps Practices", "Automation", "Scripting", "Communication",
            "Problem Solving"
        ],
        "requiredCertifications": [
            "AWS Certified Solutions Architect – Professional",
            "Microsoft Certified: Azure Solutions Architect Expert",
            "Google Professional Cloud Architect"
        ]
    }
]


@router.get("/generate-sample-jobs")
async def generate_sample_jobs():
    """
    Generate sample job postings from predefined job data.
    
    Returns:
        List[Dict]: Generated job postings with complete descriptions
    """
    try:
        generated_jobs = []
        
        for job_data in SAMPLE_JOB_DATA:
            logger.info(f"Generating job description for: {job_data['jobTitle']}")
            job_posting = job_generator.generate_job_description(job_data)
            generated_jobs.append(job_posting)
        
        logger.info(f"Successfully generated {len(generated_jobs)} job postings")
        return {
            "success": True,
            "count": len(generated_jobs),
            "jobs": generated_jobs
        }
        
    except Exception as e:
        logger.error(f"Error generating sample jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate jobs: {str(e)}")


@router.post("/generate-job")
async def generate_single_job(job_data: Dict):
    """
    Generate a single job posting from provided job data.
    
    Args:
        job_data: Dictionary containing jobTitle, industry, skillKeywords, requiredCertifications
        
    Returns:
        Dict: Generated job posting with complete description
    """
    try:
        # Validate required fields
        required_fields = ["jobTitle", "industry", "skillKeywords"]
        for field in required_fields:
            if field not in job_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        logger.info(f"Generating job description for: {job_data['jobTitle']}")
        job_posting = job_generator.generate_job_description(job_data)
        
        return {
            "success": True,
            "job": job_posting
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate job: {str(e)}")


@router.post("/personalized-insights")
async def get_personalized_insights(
    request_data: Dict,
    current_user: User = Depends(get_current_user)
):
    """
    Generate personalized career insights for a student based on their resume and target job.
    
    Args:
        request_data: Contains student_resume and target_job_data
        current_user: Current authenticated user
        
    Returns:
        Dict: Personalized insights including career recommendations and skill gaps
    """
    try:
        # Validate request data
        if "student_resume" not in request_data or "target_job_data" not in request_data:
            raise HTTPException(
                status_code=400, 
                detail="Missing student_resume or target_job_data in request"
            )
        
        student_resume = request_data["student_resume"]
        target_job_data = request_data["target_job_data"]
        
        logger.info(f"Generating personalized insights for user: {current_user.email}")
        
        # Generate personalized insights
        insights = job_generator.generate_personalized_insights(student_resume, target_job_data)
        
        # Also get skill gap analysis from matching service
        student_skills = student_resume.get("skills", [])
        job_requirements = target_job_data.get("skillKeywords", [])
        skill_gap_analysis = matching_service.calculate_skill_gap_score(student_skills, job_requirements)
        
        # Combine insights
        comprehensive_insights = {
            **insights,
            "detailed_skill_gap": skill_gap_analysis,
            "user_profile": {
                "name": current_user.username,
                "email": current_user.email,
                "experience_level": student_resume.get("experience_level", "Entry Level")
            },
            "target_job": {
                "title": target_job_data.get("jobTitle", ""),
                "industry": target_job_data.get("industry", "")
            }
        }
        
        return {
            "success": True,
            "insights": comprehensive_insights
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating personalized insights: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate insights: {str(e)}"
        )


@router.post("/career-path-analysis")
async def analyze_career_path(
    request_data: Dict,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze career paths and provide detailed recommendations for a student.
    
    Args:
        request_data: Contains student profile and career interests
        current_user: Current authenticated user
        
    Returns:
        Dict: Detailed career path analysis with timelines and recommendations
    """
    try:
        student_profile = request_data.get("student_profile", {})
        career_interests = request_data.get("career_interests", [])
        
        logger.info(f"Analyzing career paths for user: {current_user.email}")
        
        # Get student skills and experience
        student_skills = student_profile.get("skills", [])
        experience_level = student_profile.get("experience_level", "Entry Level")
        preferred_industry = student_profile.get("preferred_industry", "Technology")
        
        # Generate career paths for each interest
        career_analyses = []
        
        for interest in career_interests:
            # Find matching job data from our sample
            matching_job = next(
                (job for job in SAMPLE_JOB_DATA if job["jobTitle"].lower() == interest.lower()),
                None
            )
            
            if matching_job:
                # Generate personalized insights for this career path
                insights = job_generator.generate_personalized_insights(student_profile, matching_job)
                
                career_analyses.append({
                    "career_title": interest,
                    "industry": matching_job["industry"],
                    "match_score": len([s for s in student_skills if s in matching_job["skillKeywords"]]) / len(matching_job["skillKeywords"]) * 100,
                    "insights": insights,
                    "job_data": matching_job
                })
        
        # Sort by match score
        career_analyses.sort(key=lambda x: x["match_score"], reverse=True)
        
        return {
            "success": True,
            "student_name": current_user.username,
            "analysis_date": "2025-08-07",
            "career_analyses": career_analyses,
            "recommendations": {
                "top_match": career_analyses[0] if career_analyses else None,
                "focus_areas": ["Skill Development", "Portfolio Building", "Networking"],
                "next_steps": [
                    "Complete skills assessment for top career match",
                    "Build portfolio projects demonstrating key skills",
                    "Connect with professionals in target industry"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing career path: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze career path: {str(e)}"
        )


@router.get("/available-careers")
async def get_available_careers():
    """
    Get list of available career options with basic information.
    
    Returns:
        List[Dict]: Available career options from sample job data
    """
    try:
        careers = []
        
        for job_data in SAMPLE_JOB_DATA:
            career_info = {
                "title": job_data["jobTitle"],
                "industry": job_data["industry"],
                "key_skills": job_data["skillKeywords"][:5],  # Top 5 skills
                "experience_level": job_generator._determine_experience_level(job_data["jobTitle"]),
                "certifications_count": len(job_data["requiredCertifications"])
            }
            careers.append(career_info)
        
        return {
            "success": True,
            "count": len(careers),
            "careers": careers
        }
        
    except Exception as e:
        logger.error(f"Error fetching available careers: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch careers: {str(e)}"
        )


@router.post("/skill-development-plan")
async def create_skill_development_plan(
    request_data: Dict,
    current_user: User = Depends(get_current_user)
):
    """
    Create a personalized skill development plan for a student.
    
    Args:
        request_data: Contains target job and current skills
        current_user: Current authenticated user
        
    Returns:
        Dict: Detailed skill development plan with timeline and resources
    """
    try:
        target_job_title = request_data.get("target_job_title", "")
        current_skills = request_data.get("current_skills", [])
        time_commitment = request_data.get("time_commitment", "10-15 hours/week")
        
        # Find target job data
        target_job = next(
            (job for job in SAMPLE_JOB_DATA if job["jobTitle"].lower() == target_job_title.lower()),
            None
        )
        
        if not target_job:
            raise HTTPException(status_code=404, detail="Target job not found")
        
        logger.info(f"Creating skill development plan for {target_job_title}")
        
        # Analyze skill gaps
        required_skills = target_job["skillKeywords"]
        missing_skills = [skill for skill in required_skills if skill not in current_skills]
        
        # Get prioritized skill development plan
        prioritized_skills = job_generator._prioritize_skill_development(missing_skills, target_job_title)
        
        # Get learning resources
        learning_resources = job_generator._suggest_learning_resources(missing_skills)
        
        # Calculate timeline
        timeline_info = job_generator._estimate_readiness_timeline(len(missing_skills), "Entry Level")
        
        development_plan = {
            "target_job": target_job_title,
            "student_name": current_user.username,
            "current_skill_count": len(current_skills),
            "required_skill_count": len(required_skills),
            "skills_to_develop": len(missing_skills),
            "skill_match_percentage": ((len(required_skills) - len(missing_skills)) / len(required_skills)) * 100,
            "prioritized_skills": prioritized_skills,
            "learning_resources": learning_resources,
            "timeline": timeline_info,
            "weekly_commitment": time_commitment,
            "estimated_cost": "$200-500",  # Estimated for courses and materials
            "success_metrics": [
                "Complete 2-3 portfolio projects",
                "Obtain relevant certifications",
                "Build professional network",
                "Practice technical interviews"
            ]
        }
        
        return {
            "success": True,
            "development_plan": development_plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating skill development plan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create development plan: {str(e)}"
        )


@router.get("/job-market-insights")
async def get_job_market_insights():
    """
    Get insights about the job market based on available positions.
    
    Returns:
        Dict: Job market analysis and trends
    """
    try:
        # Analyze job market from sample data
        industry_distribution = {}
        skill_frequency = {}
        experience_levels = {}
        
        for job in SAMPLE_JOB_DATA:
            # Count industries
            industry = job["industry"]
            industry_distribution[industry] = industry_distribution.get(industry, 0) + 1
            
            # Count skills
            for skill in job["skillKeywords"]:
                skill_frequency[skill] = skill_frequency.get(skill, 0) + 1
            
            # Count experience levels
            exp_level = job_generator._determine_experience_level(job["jobTitle"])
            experience_levels[exp_level] = experience_levels.get(exp_level, 0) + 1
        
        # Get top skills
        top_skills = sorted(skill_frequency.items(), key=lambda x: x[1], reverse=True)[:10]
        
        market_insights = {
            "total_jobs_analyzed": len(SAMPLE_JOB_DATA),
            "industry_distribution": industry_distribution,
            "top_in_demand_skills": [{"skill": skill, "demand_count": count} for skill, count in top_skills],
            "experience_level_distribution": experience_levels,
            "growth_industries": ["Technology", "Healthcare", "Marketing"],
            "emerging_skills": ["Machine Learning", "Cloud Computing", "Cybersecurity"],
            "recommendations": [
                "Technology sector has the highest number of opportunities",
                "Python and Communication are the most demanded skills",
                "Cloud skills (AWS, Azure) are increasingly valuable",
                "Healthcare offers stable career opportunities"
            ],
            "analysis_date": "2025-08-07"
        }
        
        return {
            "success": True,
            "market_insights": market_insights
        }
        
    except Exception as e:
        logger.error(f"Error generating market insights: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate market insights: {str(e)}"
        )


@router.post("/save-sample-jobs-to-database")
async def save_sample_jobs_to_database(
    current_user: User = Depends(get_current_user)
):
    """
    Generate sample job postings and save them to the main jobs database.
    This makes them visible in the main job listings.
    
    Returns:
        Dict: Status of job creation and list of created job IDs
    """
    try:
        created_jobs = []
        
        # Use a system employer ID for generated jobs
        system_employer_id = "system-generated"
        
        for job_data in SAMPLE_JOB_DATA:
            logger.info(f"Creating database job for: {job_data['jobTitle']}")
            
            # Generate the complete job posting
            job_posting = job_generator.generate_job_description(job_data)
            
            # Create a proper Job object for the database
            job_id = job_posting["id"]
            
            # Convert generated job to database format
            job = Job(
                _id=job_id,  # Use _id as per existing pattern
                employer_id=system_employer_id,
                title=job_posting["title"],
                description=job_posting["description"],
                required_skills=job_posting["requirements"],
                location=job_posting["location"],
                experience_level=job_posting.get("experience_level", "Mid Level"),
                employment_type=job_posting.get("employment_type", "Full-time"),
                salary_range=f"${job_posting.get('salary_min', 50000)}-${job_posting.get('salary_max', 80000)}",
                company_name=job_posting["company"],
                status=JobStatus.OPEN,
                posted_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Save to main jobs database
            jobs_db[job_id] = job
            
            # Add to employer's job list
            if system_employer_id not in employer_jobs:
                employer_jobs[system_employer_id] = []
            employer_jobs[system_employer_id].append(job_id)
            
            created_jobs.append({
                "id": job_id,
                "title": job.title,
                "company": job.company_name
            })
        
        logger.info(f"Successfully created {len(created_jobs)} jobs in database")
        
        return {
            "success": True,
            "message": f"Successfully created {len(created_jobs)} sample jobs",
            "created_jobs": created_jobs,
            "total_jobs_in_database": len(jobs_db)
        }
        
    except Exception as e:
        logger.error(f"Error saving jobs to database: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save jobs to database: {str(e)}"
        )
