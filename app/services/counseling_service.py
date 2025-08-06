"""
AI-powered career counseling service.

This service provides intelligent career guidance by analyzing user skills,
experience, and interests to suggest career paths, identify skill gaps,
and recommend learning resources.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import random

from app.schemas import (
    CounselingReportOut, CounselingReport, CareerPath,
    ParsedResumeSection
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Career paths database (in production, this would be a comprehensive database)
CAREER_PATHS = {
    'software_engineering': {
        'title': 'Software Engineer',
        'description': 'Design, develop, and maintain software applications and systems',
        'required_skills': ['programming', 'problem-solving', 'software design', 'testing'],
        'growth_potential': 'High - Growing field with excellent career progression',
        'average_salary': '$70,000 - $150,000'
    },
    'data_science': {
        'title': 'Data Scientist',
        'description': 'Analyze complex data to help businesses make informed decisions',
        'required_skills': ['python', 'statistics', 'machine learning', 'data visualization'],
        'growth_potential': 'Very High - High demand across industries',
        'average_salary': '$80,000 - $180,000'
    },
    'product_management': {
        'title': 'Product Manager',
        'description': 'Guide product development from conception to launch',
        'required_skills': ['strategy', 'communication', 'market research', 'project management'],
        'growth_potential': 'High - Leadership track with executive potential',
        'average_salary': '$90,000 - $200,000'
    },
    'cybersecurity': {
        'title': 'Cybersecurity Specialist',
        'description': 'Protect organizations from digital threats and security breaches',
        'required_skills': ['security protocols', 'risk assessment', 'incident response', 'networking'],
        'growth_potential': 'Very High - Critical need across all industries',
        'average_salary': '$75,000 - $160,000'
    },
    'cloud_engineering': {
        'title': 'Cloud Engineer',
        'description': 'Design and manage cloud infrastructure and services',
        'required_skills': ['aws', 'azure', 'docker', 'kubernetes', 'devops'],
        'growth_potential': 'Very High - Cloud adoption accelerating',
        'average_salary': '$85,000 - $170,000'
    },
    'ui_ux_design': {
        'title': 'UI/UX Designer',
        'description': 'Create user-friendly interfaces and experiences for digital products',
        'required_skills': ['design thinking', 'figma', 'user research', 'prototyping'],
        'growth_potential': 'High - Growing importance of user experience',
        'average_salary': '$60,000 - $130,000'
    },
    'digital_marketing': {
        'title': 'Digital Marketing Specialist',
        'description': 'Develop and execute online marketing strategies',
        'required_skills': ['seo', 'social media', 'analytics', 'content marketing'],
        'growth_potential': 'High - Digital transformation driving demand',
        'average_salary': '$45,000 - $100,000'
    }
}

# High-demand skills across industries
HIGH_DEMAND_SKILLS = [
    'python', 'javascript', 'react', 'sql', 'aws', 'machine learning',
    'project management', 'data analysis', 'communication', 'problem solving',
    'agile', 'git', 'docker', 'api development', 'cloud computing'
]

# Learning resources database
LEARNING_RESOURCES = {
    'programming': [
        'Codecademy - Interactive Programming Courses',
        'freeCodeCamp - Free Coding Bootcamp',
        'LeetCode - Coding Interview Practice'
    ],
    'data_science': [
        'Coursera - Data Science Specialization',
        'Kaggle Learn - Free Data Science Courses',
        'DataCamp - Interactive Data Science Learning'
    ],
    'cloud': [
        'AWS Training and Certification',
        'Azure Learning Paths',
        'Google Cloud Skills Boost'
    ],
    'design': [
        'Figma Academy - Design System Training',
        'Coursera - UI/UX Design Courses',
        'YouTube - Design Tutorial Channels'
    ],
    'general': [
        'LinkedIn Learning - Professional Development',
        'Udemy - Comprehensive Course Library',
        'YouTube - Free Educational Content'
    ]
}


class CounselingService:
    """Service for generating AI-powered career counseling reports."""
    
    def __init__(self):
        """Initialize the counseling service."""
        pass
    
    async def generate_counseling_report(
        self,
        user_id: str,
        user_skills: List[str],
        user_experience: List[str],
        user_interests: Optional[List[str]] = None,
        target_role: Optional[str] = None
    ) -> CounselingReport:
        """
        Generate a comprehensive career counseling report.
        
        Args:
            user_id: The user's ID
            user_skills: List of user's current skills
            user_experience: List of user's experience entries
            user_interests: Optional list of user's interests
            target_role: Optional specific role the user is targeting
            
        Returns:
            CounselingReport: Generated counseling report
        """
        try:
            # Analyze current skills and experience
            skills_analysis = self._analyze_skills(user_skills)
            experience_level = self._determine_experience_level(user_experience)
            
            # Generate career path suggestions
            suggested_paths = self._suggest_career_paths(
                user_skills, user_interests, target_role, experience_level
            )
            
            # Identify skill gaps
            missing_skills = self._identify_skill_gaps(user_skills, suggested_paths)
            
            # Generate learning recommendations
            recommended_resources = self._recommend_learning_resources(
                missing_skills, suggested_paths
            )
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(
                user_skills, user_experience, missing_skills
            )
            
            # Create counseling report
            report = CounselingReport(
                _id=f"report_{user_id}_{int(datetime.utcnow().timestamp())}",
                user_id=user_id,
                generated_on=datetime.utcnow(),
                skills_summary=skills_analysis['summary'],
                suggested_paths=suggested_paths,
                missing_skills=missing_skills,
                recommended_resources=recommended_resources,
                overall_score=overall_score
            )
            
            logger.info(f"Generated counseling report for user {user_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating counseling report for user {user_id}: {str(e)}")
            raise ValueError(f"Error generating counseling report: {str(e)}")
    
    def _analyze_skills(self, user_skills: List[str]) -> Dict[str, List[str]]:
        """Analyze and categorize user skills."""
        skills_lower = [skill.lower() for skill in user_skills]
        
        categories = {
            'technical': [],
            'soft': [],
            'high_demand': [],
            'summary': []
        }
        
        # Categorize technical skills
        technical_keywords = [
            'python', 'java', 'javascript', 'react', 'sql', 'aws', 'docker',
            'kubernetes', 'git', 'api', 'database', 'cloud', 'machine learning'
        ]
        
        for skill in user_skills:
            skill_lower = skill.lower()
            if any(keyword in skill_lower for keyword in technical_keywords):
                categories['technical'].append(skill)
            
            if skill_lower in [s.lower() for s in HIGH_DEMAND_SKILLS]:
                categories['high_demand'].append(skill)
        
        # Identify soft skills
        soft_skills_keywords = [
            'communication', 'leadership', 'teamwork', 'problem solving',
            'project management', 'time management', 'analytical'
        ]
        
        for skill in user_skills:
            skill_lower = skill.lower()
            if any(keyword in skill_lower for keyword in soft_skills_keywords):
                categories['soft'].append(skill)
        
        # Create summary
        categories['summary'] = [
            f"Technical Skills: {len(categories['technical'])} identified",
            f"Soft Skills: {len(categories['soft'])} identified",
            f"High-Demand Skills: {len(categories['high_demand'])} identified",
            f"Total Skills: {len(user_skills)}"
        ]
        
        return categories
    
    def _determine_experience_level(self, experience_entries: List[str]) -> str:
        """Determine experience level from experience entries."""
        if not experience_entries:
            return 'entry'
        
        # Simple heuristics based on experience content
        experience_text = ' '.join(experience_entries).lower()
        
        if any(keyword in experience_text for keyword in ['senior', 'lead', 'principal', 'manager']):
            return 'senior'
        elif any(keyword in experience_text for keyword in ['mid', 'intermediate', '3+', '4+', '5+']):
            return 'mid'
        else:
            return 'entry'
    
    def _suggest_career_paths(
        self,
        user_skills: List[str],
        user_interests: Optional[List[str]],
        target_role: Optional[str],
        experience_level: str
    ) -> List[CareerPath]:
        """Suggest relevant career paths based on user profile."""
        suggested_paths = []
        skills_lower = [skill.lower() for skill in user_skills]
        interests_lower = [interest.lower() for interest in (user_interests or [])]
        
        # Score each career path based on skill match
        path_scores = {}
        
        for path_key, path_data in CAREER_PATHS.items():
            score = 0
            
            # Score based on required skills match
            required_skills = path_data['required_skills']
            for required_skill in required_skills:
                if any(required_skill.lower() in user_skill for user_skill in skills_lower):
                    score += 2
            
            # Bonus for interest match
            if any(interest in path_data['title'].lower() or 
                   interest in path_data['description'].lower() 
                   for interest in interests_lower):
                score += 1
            
            # Bonus for target role match
            if target_role and target_role.lower() in path_data['title'].lower():
                score += 3
            
            path_scores[path_key] = score
        
        # Sort paths by score and select top 3-5
        sorted_paths = sorted(path_scores.items(), key=lambda x: x[1], reverse=True)
        
        for path_key, score in sorted_paths[:5]:
            if score > 0:  # Only include paths with some relevance
                path_data = CAREER_PATHS[path_key]
                career_path = CareerPath(
                    title=path_data['title'],
                    description=path_data['description'],
                    required_skills=path_data['required_skills'],
                    growth_potential=path_data['growth_potential'],
                    average_salary=path_data['average_salary']
                )
                suggested_paths.append(career_path)
        
        # If no relevant paths found, suggest some general high-growth paths
        if not suggested_paths:
            default_paths = ['software_engineering', 'data_science', 'digital_marketing']
            for path_key in default_paths:
                path_data = CAREER_PATHS[path_key]
                career_path = CareerPath(
                    title=path_data['title'],
                    description=path_data['description'],
                    required_skills=path_data['required_skills'],
                    growth_potential=path_data['growth_potential'],
                    average_salary=path_data['average_salary']
                )
                suggested_paths.append(career_path)
        
        return suggested_paths[:3]  # Return top 3 suggestions
    
    def _identify_skill_gaps(
        self,
        user_skills: List[str],
        suggested_paths: List[CareerPath]
    ) -> List[str]:
        """Identify missing skills for suggested career paths."""
        user_skills_lower = [skill.lower() for skill in user_skills]
        missing_skills = set()
        
        # Collect required skills from all suggested paths
        for path in suggested_paths:
            for required_skill in path.required_skills:
                # Check if user has this skill
                if not any(required_skill.lower() in user_skill.lower() 
                          for user_skill in user_skills_lower):
                    missing_skills.add(required_skill.title())
        
        # Add high-demand skills that are missing
        for high_demand_skill in HIGH_DEMAND_SKILLS[:10]:  # Top 10 high-demand skills
            if not any(high_demand_skill.lower() in user_skill.lower() 
                      for user_skill in user_skills_lower):
                missing_skills.add(high_demand_skill.title())
        
        # Limit to most important gaps
        return list(missing_skills)[:8]
    
    def _recommend_learning_resources(
        self,
        missing_skills: List[str],
        suggested_paths: List[CareerPath]
    ) -> List[str]:
        """Recommend learning resources based on missing skills and career paths."""
        resources = []
        
        # Map missing skills to resource categories
        skill_categories = {
            'programming': ['python', 'java', 'javascript', 'react', 'programming'],
            'data_science': ['machine learning', 'data analysis', 'statistics', 'python'],
            'cloud': ['aws', 'azure', 'docker', 'kubernetes', 'cloud computing'],
            'design': ['figma', 'ui', 'ux', 'design thinking', 'prototyping']
        }
        
        # Find relevant resource categories
        relevant_categories = set()
        for skill in missing_skills:
            skill_lower = skill.lower()
            for category, keywords in skill_categories.items():
                if any(keyword in skill_lower for keyword in keywords):
                    relevant_categories.add(category)
        
        # Add resources for relevant categories
        for category in relevant_categories:
            if category in LEARNING_RESOURCES:
                resources.extend(LEARNING_RESOURCES[category][:2])  # Top 2 per category
        
        # Add general resources
        resources.extend(LEARNING_RESOURCES['general'][:2])
        
        # Remove duplicates and limit
        unique_resources = list(dict.fromkeys(resources))  # Preserve order
        return unique_resources[:6]
    
    def _calculate_overall_score(
        self,
        user_skills: List[str],
        user_experience: List[str],
        missing_skills: List[str]
    ) -> float:
        """Calculate overall career readiness score."""
        score = 0.0
        
        # Base score from number of skills
        skill_score = min(len(user_skills) * 5, 40)  # Max 40 points for skills
        score += skill_score
        
        # Experience score
        experience_score = min(len(user_experience) * 10, 30)  # Max 30 points for experience
        score += experience_score
        
        # High-demand skills bonus
        high_demand_count = sum(
            1 for skill in user_skills
            if any(hd_skill.lower() in skill.lower() for hd_skill in HIGH_DEMAND_SKILLS)
        )
        high_demand_score = min(high_demand_count * 3, 15)  # Max 15 points
        score += high_demand_score
        
        # Penalty for missing critical skills
        gap_penalty = min(len(missing_skills) * 2, 15)  # Max 15 point penalty
        score -= gap_penalty
        
        # Ensure score is between 0 and 100
        return max(0.0, min(100.0, score))
    
    async def get_skill_recommendations(
        self,
        current_skills: List[str],
        target_role: str
    ) -> Dict[str, List[str]]:
        """Get specific skill recommendations for a target role."""
        target_lower = target_role.lower()
        current_skills_lower = [skill.lower() for skill in current_skills]
        
        # Find matching career path
        matching_path = None
        for path_data in CAREER_PATHS.values():
            if any(keyword in target_lower for keyword in path_data['title'].lower().split()):
                matching_path = path_data
                break
        
        if not matching_path:
            return {
                'required_skills': [],
                'recommended_skills': HIGH_DEMAND_SKILLS[:5],
                'missing_skills': []
            }
        
        # Identify missing required skills
        missing_required = []
        for req_skill in matching_path['required_skills']:
            if not any(req_skill.lower() in curr_skill for curr_skill in current_skills_lower):
                missing_required.append(req_skill.title())
        
        # Recommend additional beneficial skills
        additional_skills = [
            skill for skill in HIGH_DEMAND_SKILLS[:10]
            if skill not in current_skills_lower and skill not in missing_required
        ]
        
        return {
            'required_skills': matching_path['required_skills'],
            'recommended_skills': additional_skills[:5],
            'missing_skills': missing_required
        }
