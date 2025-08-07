"""
AI-powered career counseling service.

This service provides intelligent career guidance by analyzing user skills,
experience, and interests to suggest career paths, identify skill gaps,
and recommend learning resources using real job market data.
"""

import logging
import json
import os
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from collections import defaultdict, Counter
import random

from app.schemas import (
    CounselingReportOut, CounselingReport, CareerPath,
    ParsedResumeSection
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Job dataset loading and processing
def load_job_dataset():
    """Load and process the job dataset from JSON file."""
    job_data_path = os.path.join(os.path.dirname(__file__), 'job_data.json')
    try:
        with open(job_data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Job dataset not found at {job_data_path}, using fallback data")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing job dataset: {e}")
        return []

# Load job dataset
JOB_DATASET = load_job_dataset()

# Process job dataset for career paths and skills analysis
def process_job_dataset(job_data: List[Dict]) -> Tuple[Dict, Dict, List[str]]:
    """Process job dataset to extract career paths, skill frequencies, and certifications."""
    career_paths = {}
    skill_frequency = Counter()
    all_certifications = []
    industry_skills = defaultdict(set)
    
    for job in job_data:
        job_title = job.get('jobTitle', '')
        industry = job.get('industry', 'Other')
        skills = job.get('skillKeywords', [])
        certifications = job.get('requiredCertifications', [])
        
        # Create career path entry
        career_key = job_title.lower().replace(' ', '_').replace('/', '_')
        career_paths[career_key] = {
            'title': job_title,
            'description': f"Professional role in {industry} requiring specialized skills and expertise",
            'required_skills': [skill.lower() for skill in skills],
            'industry': industry,
            'certifications': certifications,
            'growth_potential': _determine_growth_potential(job_title, industry),
            'average_salary': _estimate_salary_range(job_title, industry)
        }
        
        # Count skill frequencies
        for skill in skills:
            skill_frequency[skill.lower()] += 1
            industry_skills[industry.lower()].add(skill.lower())
        
        # Collect certifications
        all_certifications.extend(certifications)
    
    return career_paths, dict(skill_frequency), list(set(all_certifications))

def _determine_growth_potential(job_title: str, industry: str) -> str:
    """Determine growth potential based on job title and industry."""
    title_lower = job_title.lower()
    industry_lower = industry.lower()
    
    if 'senior' in title_lower or 'architect' in title_lower or 'manager' in title_lower:
        return 'Very High - Senior level position with leadership opportunities'
    elif industry_lower == 'technology':
        if any(keyword in title_lower for keyword in ['data', 'ai', 'cloud', 'cybersecurity', 'devops']):
            return 'Very High - High-demand technology field with rapid growth'
        else:
            return 'High - Technology sector with good growth prospects'
    elif industry_lower == 'healthcare':
        return 'High - Essential industry with stable growth'
    else:
        return 'Moderate - Steady growth with good opportunities'

def _estimate_salary_range(job_title: str, industry: str) -> str:
    """Estimate salary range based on job title and industry."""
    title_lower = job_title.lower()
    industry_lower = industry.lower()
    
    # Senior/Leadership roles
    if any(keyword in title_lower for keyword in ['senior', 'lead', 'principal', 'architect', 'manager']):
        if industry_lower == 'technology':
            return '$100,000 - $200,000'
        else:
            return '$80,000 - $150,000'
    
    # Technology roles
    elif industry_lower == 'technology':
        if any(keyword in title_lower for keyword in ['data scientist', 'devops', 'cloud']):
            return '$80,000 - $160,000'
        elif 'junior' in title_lower or 'entry' in title_lower:
            return '$50,000 - $80,000'
        else:
            return '$60,000 - $120,000'
    
    # Healthcare
    elif industry_lower == 'healthcare':
        if 'nurse' in title_lower:
            return '$55,000 - $85,000'
        else:
            return '$50,000 - $100,000'
    
    # Marketing
    elif industry_lower == 'marketing':
        return '$45,000 - $90,000'
    
    else:
        return '$40,000 - $80,000'

# Process the loaded dataset
PROCESSED_CAREER_PATHS, SKILL_FREQUENCY, ALL_CERTIFICATIONS = process_job_dataset(JOB_DATASET)

# Get high-demand skills from dataset
HIGH_DEMAND_SKILLS = [skill for skill, count in sorted(SKILL_FREQUENCY.items(), key=lambda x: x[1], reverse=True)[:20]]

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

# Enhanced learning resources based on job market data
LEARNING_RESOURCES = {
    'programming': [
        'Codecademy - Interactive Programming Courses',
        'freeCodeCamp - Free Coding Bootcamp',
        'LeetCode - Coding Interview Practice',
        'Python Institute - Official Python Certification Path'
    ],
    'data_science': [
        'Coursera - Data Science Specialization by Johns Hopkins',
        'Kaggle Learn - Free Data Science Micro-Courses',
        'DataCamp - Interactive Data Science Learning',
        'TensorFlow - Official Machine Learning Tutorials'
    ],
    'cloud': [
        'AWS Training and Certification Portal',
        'Microsoft Azure Learning Paths',
        'Google Cloud Skills Boost',
        'A Cloud Guru - Cloud Technology Training'
    ],
    'design': [
        'Figma Academy - Design System Training',
        'NN/g Nielsen Norman Group - UX Certification',
        'Adobe Creative Cloud Tutorials',
        'Interaction Design Foundation'
    ],
    'cybersecurity': [
        'CompTIA Security+ Training',
        'CISSP Official Study Guide',
        'Certified Ethical Hacker (CEH) Course',
        'Cybrary - Free Cybersecurity Training'
    ],
    'devops': [
        'Kubernetes Official Documentation',
        'Docker Training and Certification',
        'HashiCorp Learn - Terraform Training',
        'Linux Academy - DevOps Learning Paths'
    ],
    'marketing': [
        'Google Ads Certification Program',
        'HubSpot Academy - Free Marketing Courses',
        'Facebook Blueprint Certification',
        'Google Analytics Academy'
    ],
    'healthcare': [
        'Khan Academy - Healthcare and Medicine',
        'Coursera - Healthcare Courses',
        'NCLEX-RN Preparation Resources',
        'Continuing Education for Healthcare Professionals'
    ],
    'general': [
        'LinkedIn Learning - Professional Development',
        'Udemy - Comprehensive Course Library',
        'Coursera - University-Level Courses',
        'edX - Free Online Courses from Top Universities'
    ]
}


class CounselingService:
    """Service for generating AI-powered career counseling reports using real job market data."""
    
    def __init__(self):
        """Initialize the counseling service with job market data."""
        self.job_dataset = JOB_DATASET  # Add the raw job dataset
        self.career_paths = PROCESSED_CAREER_PATHS if PROCESSED_CAREER_PATHS else CAREER_PATHS
        self.skill_frequency = SKILL_FREQUENCY
        self.high_demand_skills = HIGH_DEMAND_SKILLS if HIGH_DEMAND_SKILLS else [
            'python', 'javascript', 'sql', 'communication', 'problem solving'
        ]
        logger.info(f"Initialized counseling service with {len(self.career_paths)} career paths")
    
    async def generate_counseling_report(
        self,
        user_id: str,
        user_skills: List[str],
        user_experience: List[str],
        user_interests: Optional[List[str]] = None,
        target_role: Optional[str] = None
    ) -> CounselingReport:
        """
        Generate a comprehensive career counseling report using job market data.
        
        Args:
            user_id: The user's ID
            user_skills: List of user's current skills
            user_experience: List of user's experience entries
            user_interests: Optional list of user's interests
            target_role: Optional specific role the user is targeting
            
        Returns:
            CounselingReport: Generated counseling report with market insights
        """
        try:
            # Analyze current skills against market data
            skills_analysis = self._analyze_skills_against_market(user_skills)
            experience_level = self._determine_experience_level(user_experience)
            
            # Generate career path suggestions based on real job data
            suggested_paths = self._suggest_career_paths_from_dataset(
                user_skills, user_interests, target_role, experience_level
            )
            
            # Identify skill gaps using market demand data
            missing_skills = self._identify_skill_gaps_from_dataset(user_skills, suggested_paths, target_role)
            
            # Generate learning recommendations with certifications
            recommended_resources = self._recommend_learning_resources_enhanced(
                missing_skills, suggested_paths
            )
            
            # Calculate market-adjusted score
            overall_score = self._calculate_market_adjusted_score(
                user_skills, user_experience, missing_skills
            )
            
            # Convert complex skill gap analysis to simple strings for schema compatibility
            simplified_missing_skills = []
            for gap_info in missing_skills:
                for skill_info in gap_info.get('missing_skills', []):
                    skill_name = skill_info.get('skill', str(skill_info))
                    priority = skill_info.get('priority', 'Medium')
                    demand = skill_info.get('demand_percentage', 0)
                    simplified_missing_skills.append(f"{skill_name} ({priority} priority, {demand}% market demand)")
            
            # Convert complex learning resources to simple strings
            simplified_resources = []
            for resource_info in recommended_resources:
                for priority_resource in resource_info.get('priority_resources', []):
                    skill = priority_resource.get('skill', 'Unknown')
                    courses = priority_resource.get('courses', [])
                    if courses:
                        simplified_resources.append(f"{skill}: {courses[0]}")
            
            # Create enhanced counseling report
            report = CounselingReport(
                _id=f"report_{user_id}_{int(datetime.utcnow().timestamp())}",
                user_id=user_id,
                generated_on=datetime.utcnow(),
                skills_summary=skills_analysis['summary'],
                suggested_paths=suggested_paths,
                missing_skills=simplified_missing_skills[:10],  # Limit to top 10
                recommended_resources=simplified_resources[:8],   # Limit to top 8
                overall_score=overall_score
            )
            
            logger.info(f"Generated market-based counseling report for user {user_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating counseling report for user {user_id}: {str(e)}")
            raise ValueError(f"Error generating counseling report: {str(e)}")
    
    def _analyze_skills_against_market(self, user_skills: List[str]) -> Dict[str, Any]:
        """Analyze user skills against current job market demands."""
        skills_lower = [skill.lower().strip() for skill in user_skills]
        market_analysis = {
            'technical': [],
            'soft': [],
            'high_demand': [],
            'market_value': [],
            'certifiable': [],
            'skill_demand_scores': {},
            'in_demand_skills': [],
            'emerging_skills': [],
            'skill_market_frequency': {},
            'recommendations': [],
            'summary': []
        }
        
        # Count skill frequency across all job postings
        skill_counts = {}
        total_jobs = len(self.job_dataset)
        
        for job in self.job_dataset:
            job_skills = [skill.lower().strip() for skill in job.get('skillKeywords', [])]
            for skill in job_skills:
                skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Calculate demand scores for user skills
        for user_skill in skills_lower:
            # Direct match
            if user_skill in skill_counts:
                demand_score = (skill_counts[user_skill] / total_jobs) * 100
                market_analysis['skill_demand_scores'][user_skill] = round(demand_score, 1)
            else:
                # Partial match
                partial_matches = []
                for market_skill, count in skill_counts.items():
                    if user_skill in market_skill or market_skill in user_skill:
                        if len(user_skill) > 2 and len(market_skill) > 2:  # Avoid short false matches
                            partial_matches.append((market_skill, count))
                
                if partial_matches:
                    # Use highest matching skill count
                    best_match = max(partial_matches, key=lambda x: x[1])
                    demand_score = (best_match[1] / total_jobs) * 100
                    market_analysis['skill_demand_scores'][user_skill] = round(demand_score, 1)
                else:
                    market_analysis['skill_demand_scores'][user_skill] = 0.0
        
        # Categorize based on market data and existing logic
        for skill in user_skills:
            skill_lower = skill.lower()
            
            # Check if skill appears in job dataset
            market_frequency = self.skill_frequency.get(skill_lower, 0)
            
            # High-demand skills from dataset
            if skill_lower in self.high_demand_skills:
                market_analysis['high_demand'].append(skill)
                
            # Market value based on frequency in job postings
            if market_frequency > 3:  # Appears in multiple job types
                market_analysis['market_value'].append(f"{skill} (appears in {market_frequency} job types)")
            
            # Technical skills identification (enhanced with dataset)
            technical_indicators = ['python', 'java', 'sql', 'cloud', 'api', 'machine learning', 
                                  'docker', 'kubernetes', 'terraform', 'figma', 'tableau']
            if any(indicator in skill_lower for indicator in technical_indicators):
                market_analysis['technical'].append(skill)
            
            # Soft skills
            soft_indicators = ['communication', 'leadership', 'teamwork', 'problem solving',
                             'collaboration', 'creativity', 'analytical']
            if any(indicator in skill_lower for indicator in soft_indicators):
                market_analysis['soft'].append(skill)
            
            # Skills that have certifications available
            for cert in ALL_CERTIFICATIONS:
                if any(word in cert.lower() for word in skill_lower.split()) and skill not in market_analysis['certifiable']:
                    market_analysis['certifiable'].append(skill)
        
        # Identify top in-demand skills (appearing in >30% of jobs)
        high_demand_threshold = total_jobs * 0.3
        for skill, count in skill_counts.items():
            if count >= high_demand_threshold:
                demand_percentage = (count / total_jobs) * 100
                market_analysis['in_demand_skills'].append({
                    'skill': skill.title(),
                    'demand_percentage': round(demand_percentage, 1),
                    'job_count': count
                })
        
        # Sort by demand
        market_analysis['in_demand_skills'].sort(
            key=lambda x: x['demand_percentage'], 
            reverse=True
        )
        
        # Identify emerging/trending skills (moderate demand, technology-related)
        emerging_threshold = total_jobs * 0.15
        tech_keywords = ['ai', 'ml', 'cloud', 'automation', 'analytics', 'digital', 'api', 'mobile', 'web', 'data']
        
        for skill, count in skill_counts.items():
            if emerging_threshold <= count < high_demand_threshold:
                if any(keyword in skill.lower() for keyword in tech_keywords):
                    demand_percentage = (count / total_jobs) * 100
                    market_analysis['emerging_skills'].append({
                        'skill': skill.title(),
                        'demand_percentage': round(demand_percentage, 1),
                        'growth_potential': 'High'
                    })
        
        # Generate skill recommendations
        user_scores = list(market_analysis['skill_demand_scores'].values())
        if user_scores:
            avg_user_score = sum(user_scores) / len(user_scores)
            
            if avg_user_score < 20:
                market_analysis['recommendations'].append(
                    "Consider developing more in-demand skills to improve market competitiveness"
                )
            elif avg_user_score > 40:
                market_analysis['recommendations'].append(
                    "Your skills align well with current market demand"
                )
            
            # Recommend specific high-demand skills user doesn't have
            missing_skills = []
            for skill_info in market_analysis['in_demand_skills'][:5]:
                skill_name = skill_info['skill'].lower()
                if not any(skill_name in user_skill or user_skill in skill_name for user_skill in skills_lower):
                    missing_skills.append(skill_info['skill'])
            
            if missing_skills:
                market_analysis['recommendations'].append(
                    f"Consider learning these high-demand skills: {', '.join(missing_skills[:3])}"
                )
        
        # Create enhanced summary with market insights
        total_market_value_skills = len(market_analysis['market_value'])
        high_demand_count = len(market_analysis['high_demand'])
        
        market_analysis['summary'] = [
            f"Technical Skills: {len(market_analysis['technical'])} identified",
            f"Soft Skills: {len(market_analysis['soft'])} identified", 
            f"High-Demand Market Skills: {high_demand_count} identified",
            f"Skills with Market Value: {total_market_value_skills} found in job postings",
            f"Certifiable Skills: {len(market_analysis['certifiable'])} have available certifications",
            f"Total Skills: {len(user_skills)}"
        ]
        
        return market_analysis
    
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
    
    def _suggest_career_paths_from_dataset(
        self,
        user_skills: List[str],
        user_interests: Optional[List[str]],
        target_role: Optional[str],
        experience_level: str
    ) -> List[CareerPath]:
        """Suggest career paths based on real job market data."""
        suggested_paths = []
        skills_lower = [skill.lower() for skill in user_skills]
        interests_lower = [interest.lower() for interest in (user_interests or [])]
        
        # Score each career path from dataset
        path_scores = {}
        
        for path_key, path_data in self.career_paths.items():
            score = 0
            required_skills = path_data['required_skills']
            
            # Calculate skill match score based on exact and partial matches
            skill_matches = 0
            for required_skill in required_skills:
                # Exact match
                if required_skill in skills_lower:
                    skill_matches += 2
                # Partial match (e.g., "javascript" matches "advanced javascript")
                elif any(required_skill in user_skill for user_skill in skills_lower):
                    skill_matches += 1
                # Reverse partial match (e.g., "python" in user skills matches "python programming")
                elif any(user_skill in required_skill for user_skill in skills_lower if len(user_skill) > 2):
                    skill_matches += 1
            
            # Calculate percentage match
            if required_skills:
                skill_match_percentage = (skill_matches / len(required_skills)) * 100
                score += skill_match_percentage
            
            # Interest bonus
            title_lower = path_data['title'].lower()
            industry_lower = path_data.get('industry', '').lower()
            
            for interest in interests_lower:
                if interest in title_lower or interest in industry_lower:
                    score += 15
            
            # Target role bonus
            if target_role:
                target_lower = target_role.lower()
                if target_lower in title_lower or any(word in title_lower for word in target_lower.split()):
                    score += 25
            
            # Experience level appropriateness
            title_lower = path_data['title'].lower()
            if experience_level == 'entry' and any(word in title_lower for word in ['junior', 'entry', 'associate']):
                score += 10
            elif experience_level == 'senior' and any(word in title_lower for word in ['senior', 'lead', 'principal', 'architect']):
                score += 10
            elif experience_level == 'mid' and not any(word in title_lower for word in ['junior', 'senior', 'lead', 'principal']):
                score += 5
            
            path_scores[path_key] = score
        
        # Sort and select top paths
        sorted_paths = sorted(path_scores.items(), key=lambda x: x[1], reverse=True)
        
        for path_key, score in sorted_paths[:5]:
            if score > 10:  # Only include paths with reasonable relevance
                path_data = self.career_paths[path_key]
                career_path = CareerPath(
                    title=path_data['title'],
                    description=path_data['description'],
                    required_skills=path_data['required_skills'][:10],  # Limit for readability
                    growth_potential=path_data['growth_potential'],
                    average_salary=path_data['average_salary']
                )
                suggested_paths.append(career_path)
        
        # Fallback to high-growth technology paths if no good matches
        if not suggested_paths:
            fallback_paths = ['data_scientist', 'junior_python_developer', 'digital_marketing_specialist']
            for path_key in fallback_paths:
                if path_key in self.career_paths:
                    path_data = self.career_paths[path_key]
                    career_path = CareerPath(
                        title=path_data['title'],
                        description=path_data['description'],
                        required_skills=path_data['required_skills'][:10],
                        growth_potential=path_data['growth_potential'],
                        average_salary=path_data['average_salary']
                    )
                    suggested_paths.append(career_path)
        
        return suggested_paths[:3]  # Return top 3 suggestions
    
    def _identify_skill_gaps_from_dataset(
        self,
        user_skills: List[str],
        suggested_paths: List[CareerPath],
        target_role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Identify missing skills for suggested career paths using real job market data."""
        user_skills_lower = [skill.lower().strip() for skill in user_skills]
        skill_gap_analysis = []
        
        # Analyze gaps for suggested career paths
        for path in suggested_paths:
            path_gaps = []
            for required_skill in path.required_skills:
                # Check if user has this skill (exact or partial match)
                has_skill = False
                for user_skill in user_skills_lower:
                    if (required_skill.lower() in user_skill or 
                        user_skill in required_skill.lower()):
                        has_skill = True
                        break
                
                if not has_skill:
                    # Get market demand for this skill
                    skill_demand = 0
                    for job in self.job_dataset:
                        job_skills = [s.lower().strip() for s in job.get('skillKeywords', [])]
                        if required_skill.lower() in job_skills:
                            skill_demand += 1
                    
                    demand_percentage = (skill_demand / len(self.job_dataset)) * 100 if self.job_dataset else 0
                    
                    path_gaps.append({
                        'skill': required_skill.title(),
                        'demand_percentage': round(demand_percentage, 1),
                        'priority': 'High' if demand_percentage > 30 else 'Medium' if demand_percentage > 15 else 'Low',
                        'job_count': skill_demand
                    })
            
            if path_gaps:
                skill_gap_analysis.append({
                    'career_path': path.title,
                    'missing_skills': sorted(path_gaps, key=lambda x: x['demand_percentage'], reverse=True)
                })
        
        # Add general high-demand skills that user doesn't have
        general_gaps = []
        skill_counts = {}
        
        # Count all skills across dataset
        for job in self.job_dataset:
            for skill in job.get('skillKeywords', []):
                skill_lower = skill.lower().strip()
                skill_counts[skill_lower] = skill_counts.get(skill_lower, 0) + 1
        
        # Find top missing skills
        high_demand_threshold = len(self.job_dataset) * 0.25  # Skills in 25%+ of jobs
        
        for skill, count in skill_counts.items():
            if count >= high_demand_threshold:
                # Check if user has this skill
                has_skill = any(skill in user_skill or user_skill in skill 
                              for user_skill in user_skills_lower)
                
                if not has_skill:
                    demand_percentage = (count / len(self.job_dataset)) * 100
                    general_gaps.append({
                        'skill': skill.title(),
                        'demand_percentage': round(demand_percentage, 1),
                        'priority': 'High' if demand_percentage > 40 else 'Medium',
                        'job_count': count,
                        'reason': 'Market demand'
                    })
        
        # Sort general gaps by demand
        general_gaps.sort(key=lambda x: x['demand_percentage'], reverse=True)
        
        # Add general gaps to analysis
        if general_gaps:
            skill_gap_analysis.append({
                'career_path': 'General Market Demand',
                'missing_skills': general_gaps[:6]  # Top 6 general gaps
            })
        
        return skill_gap_analysis
    
    def _recommend_learning_resources_enhanced(
        self,
        skill_gap_analysis: List[Dict[str, Any]],
        suggested_paths: List[CareerPath]
    ) -> List[Dict[str, Any]]:
        """Recommend learning resources based on detailed skill gap analysis."""
        resource_recommendations = []
        
        # Enhanced skill-to-resource mapping based on real job market data
        skill_resources = {
            'python': {
                'courses': ['Python for Everybody (Coursera)', 'Complete Python Bootcamp (Udemy)'],
                'certifications': ['Python Institute PCAP', 'Microsoft Python Certification'],
                'practice': ['HackerRank Python', 'LeetCode Python Problems'],
                'time_estimate': '2-3 months'
            },
            'sql': {
                'courses': ['SQL Fundamentals (DataCamp)', 'The Complete SQL Bootcamp (Udemy)'],
                'certifications': ['Oracle SQL Certification', 'Microsoft SQL Server Certification'],
                'practice': ['SQLBolt', 'HackerRank SQL'],
                'time_estimate': '1-2 months'
            },
            'javascript': {
                'courses': ['JavaScript: The Complete Guide (Udemy)', 'JavaScript Algorithms (freeCodeCamp)'],
                'certifications': ['FreeCodeCamp JavaScript Certification'],
                'practice': ['Codewars JavaScript', 'JavaScript30 Challenge'],
                'time_estimate': '2-3 months'
            },
            'machine learning': {
                'courses': ['Machine Learning Course (Coursera)', 'Fast.ai Practical Deep Learning'],
                'certifications': ['Google ML Certification', 'AWS ML Specialty'],
                'practice': ['Kaggle Competitions', 'Jupyter Notebook Projects'],
                'time_estimate': '4-6 months'
            },
            'aws': {
                'courses': ['AWS Cloud Practitioner (AWS Training)', 'AWS Solutions Architect (A Cloud Guru)'],
                'certifications': ['AWS Cloud Practitioner', 'AWS Solutions Architect Associate'],
                'practice': ['AWS Free Tier Hands-on', 'CloudAcademy Labs'],
                'time_estimate': '2-4 months'
            },
            'communication': {
                'courses': ['Business Communication (Coursera)', 'Public Speaking (Toastmasters)'],
                'certifications': ['PMI Communication Certification'],
                'practice': ['Toastmasters Club', 'Presentation Practice'],
                'time_estimate': '1-3 months'
            },
            'react': {
                'courses': ['React Complete Guide (Udemy)', 'React Documentation (Official)'],
                'certifications': ['FreeCodeCamp React Certification'],
                'practice': ['Build React Projects', 'React Challenges'],
                'time_estimate': '2-3 months'
            },
            'docker': {
                'courses': ['Docker Mastery (Udemy)', 'Docker Deep Dive (Pluralsight)'],
                'certifications': ['Docker Certified Associate'],
                'practice': ['Docker Labs', 'Containerize Sample Apps'],
                'time_estimate': '1-2 months'
            }
        }
        
        # Process each career path's skill gaps
        for gap_info in skill_gap_analysis:
            career_path = gap_info['career_path']
            missing_skills = gap_info['missing_skills']
            
            path_resources = {
                'career_path': career_path,
                'priority_resources': []
            }
            
            # Sort skills by priority (high-demand first)
            high_priority_skills = [s for s in missing_skills if s.get('priority') == 'High']
            medium_priority_skills = [s for s in missing_skills if s.get('priority') == 'Medium']
            
            # Add resources for high-priority skills first
            for skill_info in high_priority_skills[:3]:  # Top 3 high-priority
                skill_name = skill_info['skill'].lower()
                
                # Find matching resource
                matching_resource = None
                for resource_skill, resources in skill_resources.items():
                    if resource_skill in skill_name or skill_name in resource_skill:
                        matching_resource = resources.copy()
                        matching_resource['skill'] = skill_info['skill']
                        matching_resource['market_demand'] = f"{skill_info['demand_percentage']}%"
                        matching_resource['priority'] = skill_info['priority']
                        break
                
                if matching_resource:
                    path_resources['priority_resources'].append(matching_resource)
                else:
                    # Generic resource for unmatched skills
                    path_resources['priority_resources'].append({
                        'skill': skill_info['skill'],
                        'courses': [f'Search "{skill_info["skill"]}" on Coursera/Udemy'],
                        'certifications': ['Industry-specific certifications'],
                        'practice': ['Professional projects and practice'],
                        'time_estimate': '2-4 months',
                        'market_demand': f"{skill_info['demand_percentage']}%",
                        'priority': skill_info['priority']
                    })
            
            # Add a few medium-priority skills if space allows
            for skill_info in medium_priority_skills[:2]:
                if len(path_resources['priority_resources']) < 5:
                    skill_name = skill_info['skill'].lower()
                    for resource_skill, resources in skill_resources.items():
                        if resource_skill in skill_name or skill_name in resource_skill:
                            matching_resource = resources.copy()
                            matching_resource['skill'] = skill_info['skill']
                            matching_resource['market_demand'] = f"{skill_info['demand_percentage']}%"
                            matching_resource['priority'] = skill_info['priority']
                            path_resources['priority_resources'].append(matching_resource)
                            break
            
            if path_resources['priority_resources']:
                resource_recommendations.append(path_resources)
        
        return resource_recommendations
    
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
    
    def _calculate_market_adjusted_score(
        self,
        user_skills: List[str],
        user_experience: List[str],
        skill_gap_analysis: List[Dict[str, Any]]
    ) -> float:
        """Calculate market-adjusted career readiness score using real job data."""
        score = 0.0
        
        # Base score from number of skills (max 35 points)
        skill_score = min(len(user_skills) * 3.5, 35)
        score += skill_score
        
        # Experience score (max 25 points)
        experience_score = min(len(user_experience) * 8, 25)
        score += experience_score
        
        # Market demand score based on user skills (max 25 points)
        market_demand_score = 0
        skill_counts = {}
        
        # Count skill frequency in job dataset
        for job in self.job_dataset:
            for skill in job.get('skillKeywords', []):
                skill_lower = skill.lower().strip()
                skill_counts[skill_lower] = skill_counts.get(skill_lower, 0) + 1
        
        total_jobs = len(self.job_dataset)
        user_skills_lower = [skill.lower().strip() for skill in user_skills]
        
        for user_skill in user_skills_lower:
            # Find market demand for this skill
            skill_demand = 0
            for market_skill, count in skill_counts.items():
                if user_skill in market_skill or market_skill in user_skill:
                    skill_demand = max(skill_demand, count)
            
            if total_jobs > 0:
                demand_percentage = (skill_demand / total_jobs) * 100
                # Award points based on demand (0-2.5 points per skill)
                skill_points = min(demand_percentage / 20, 2.5)  # 50%+ demand = max points
                market_demand_score += skill_points
        
        market_demand_score = min(market_demand_score, 25)
        score += market_demand_score
        
        # Skill gap penalty based on analysis (max 10 point penalty)
        gap_penalty = 0
        for gap_info in skill_gap_analysis:
            high_priority_gaps = [s for s in gap_info.get('missing_skills', []) 
                                if s.get('priority') == 'High']
            gap_penalty += len(high_priority_gaps) * 1.5  # 1.5 points per high-priority gap
        
        gap_penalty = min(gap_penalty, 10)
        score -= gap_penalty
        
        # Career path alignment bonus (max 15 points)
        alignment_bonus = 0
        if skill_gap_analysis:
            # If user has good alignment with suggested paths
            total_gaps = sum(len(gap_info.get('missing_skills', [])) 
                           for gap_info in skill_gap_analysis)
            if total_gaps <= 3:  # Very good alignment
                alignment_bonus = 15
            elif total_gaps <= 6:  # Good alignment
                alignment_bonus = 10
            elif total_gaps <= 10:  # Moderate alignment
                alignment_bonus = 5
        
        score += alignment_bonus
        
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
