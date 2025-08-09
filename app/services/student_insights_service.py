"""
Personalized AI-powered student career insights service.

This service provides individualized career recommendations, skill gap analysis,
and career path suggestions based on each student's specific resume content,
skills, experience, and job preferences.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from collections import defaultdict, Counter
import re

from app.schemas import ParsedResumeSection
from app.services.counseling_service import CounselingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StudentInsightsService:
    """Service for generating personalized career insights for students."""
    
    def __init__(self):
        """Initialize the student insights service."""
        self.counseling_service = CounselingService()
        
        # Industry-specific career paths and skills
        self.industry_paths = {
            'technology': {
                'entry_level': ['Junior Software Developer', 'Frontend Developer', 'QA Tester', 'IT Support Specialist'],
                'mid_level': ['Software Engineer', 'Full Stack Developer', 'DevOps Engineer', 'Data Analyst'],
                'senior_level': ['Senior Software Engineer', 'Technical Lead', 'Software Architect', 'Data Scientist'],
                'key_skills': ['programming', 'problem-solving', 'version control', 'testing', 'databases']
            },
            'healthcare': {
                'entry_level': ['Medical Assistant', 'Pharmacy Technician', 'Healthcare Data Analyst'],
                'mid_level': ['Registered Nurse', 'Healthcare Administrator', 'Medical Technologist'],
                'senior_level': ['Nurse Practitioner', 'Healthcare Manager', 'Clinical Director'],
                'key_skills': ['patient care', 'medical knowledge', 'communication', 'attention to detail']
            },
            'business': {
                'entry_level': ['Business Analyst', 'Marketing Coordinator', 'Sales Associate'],
                'mid_level': ['Project Manager', 'Marketing Manager', 'Operations Manager'],
                'senior_level': ['Director', 'VP of Operations', 'Chief Executive Officer'],
                'key_skills': ['leadership', 'strategic thinking', 'communication', 'data analysis']
            },
            'education': {
                'entry_level': ['Teaching Assistant', 'Tutor', 'Education Coordinator'],
                'mid_level': ['Teacher', 'Curriculum Developer', 'Academic Advisor'],
                'senior_level': ['Principal', 'Education Director', 'Superintendent'],
                'key_skills': ['teaching', 'curriculum development', 'classroom management', 'assessment']
            },
            'finance': {
                'entry_level': ['Financial Analyst', 'Junior Accountant', 'Banking Associate'],
                'mid_level': ['Senior Financial Analyst', 'Portfolio Manager', 'Risk Analyst'],
                'senior_level': ['Finance Director', 'Chief Financial Officer', 'Investment Manager'],
                'key_skills': ['financial analysis', 'accounting', 'risk management', 'excel', 'financial modeling']
            }
        }
        
        # Skill development priorities based on market demand
        self.skill_priorities = {
            'high_demand': {
                'technical': ['python', 'javascript', 'sql', 'cloud computing', 'machine learning', 'data analysis'],
                'soft': ['communication', 'leadership', 'problem solving', 'teamwork', 'adaptability'],
                'certifications': ['AWS Cloud Practitioner', 'Google Analytics', 'PMP', 'Scrum Master']
            },
            'emerging': {
                'technical': ['ai/ml', 'blockchain', 'cybersecurity', 'devops', 'mobile development'],
                'soft': ['emotional intelligence', 'digital literacy', 'remote collaboration'],
                'certifications': ['Azure Fundamentals', 'Certified Ethical Hacker', 'Kubernetes']
            }
        }
        
    async def generate_personalized_insights(
        self,
        student_id: str,
        parsed_resume: ParsedResumeSection,
        preferred_industries: List[str] = None,
        career_goals: str = None,
        target_salary_range: str = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive personalized career insights for a student.
        
        Args:
            student_id: The student's unique identifier
            parsed_resume: Parsed resume data including skills, experience, education
            preferred_industries: List of industries the student is interested in
            career_goals: Student's career goals or target role
            target_salary_range: Desired salary range
            
        Returns:
            Dict containing personalized insights and recommendations
        """
        try:
            # Extract key information from resume
            student_profile = self._build_student_profile(parsed_resume)
            
            # Generate personalized professional insights
            professional_insights = await self._generate_professional_insights(
                student_profile, preferred_industries, career_goals
            )
            
            # Generate personalized career recommendations
            career_recommendations = await self._generate_career_recommendations(
                student_profile, preferred_industries, career_goals, target_salary_range
            )
            
            # Generate personalized skill breakdown
            skill_breakdown = self._generate_skill_breakdown(
                student_profile, preferred_industries
            )
            
            # Generate suggested career paths
            career_paths = self._generate_suggested_career_paths(
                student_profile, preferred_industries, career_goals
            )
            
            # Generate priority skills to develop
            priority_skills = self._generate_priority_skills(
                student_profile, preferred_industries, career_goals
            )
            
            return {
                'student_id': student_id,
                'generated_on': datetime.utcnow().isoformat(),
                'student_profile': student_profile,
                'professional_insights': professional_insights,
                'career_recommendations': career_recommendations,
                'skill_breakdown': skill_breakdown,
                'suggested_career_paths': career_paths,
                'priority_skills_to_develop': priority_skills,
                'personalization_score': self._calculate_personalization_score(student_profile)
            }
            
        except Exception as e:
            logger.error(f"Error generating personalized insights for student {student_id}: {str(e)}")
            raise ValueError(f"Error generating personalized insights: {str(e)}")
    
    def _build_student_profile(self, parsed_resume: ParsedResumeSection) -> Dict[str, Any]:
        """Build a comprehensive student profile from resume data."""
        profile = {
            'skills': {
                'technical': [],
                'soft': [],
                'languages': [],
                'tools': []
            },
            'experience': {
                'work_experience': [],
                'internships': [],
                'projects': [],
                'total_years': 0
            },
            'education': {
                'degrees': [],
                'certifications': [],
                'gpa': None,
                'relevant_coursework': []
            },
            'achievements': [],
            'interests': [],
            'experience_level': 'entry'  # entry, junior, mid, senior
        }
        
        # Process skills
        if parsed_resume.skills:
            technical_keywords = ['python', 'java', 'javascript', 'sql', 'html', 'css', 'react', 'node', 'git', 'aws', 'docker']
            soft_keywords = ['communication', 'leadership', 'teamwork', 'problem solving', 'time management']
            tool_keywords = ['excel', 'tableau', 'figma', 'photoshop', 'jira', 'slack', 'office']
            
            for skill in parsed_resume.skills:
                skill_lower = skill.lower()
                if any(tech in skill_lower for tech in technical_keywords):
                    profile['skills']['technical'].append(skill)
                elif any(soft in skill_lower for soft in soft_keywords):
                    profile['skills']['soft'].append(skill)
                elif any(tool in skill_lower for tool in tool_keywords):
                    profile['skills']['tools'].append(skill)
                else:
                    # Check if it's a language
                    languages = ['english', 'spanish', 'french', 'german', 'chinese', 'japanese']
                    if any(lang in skill_lower for lang in languages):
                        profile['skills']['languages'].append(skill)
                    else:
                        profile['skills']['technical'].append(skill)  # Default to technical
        
        # Process experience
        if parsed_resume.experience:
            for exp in parsed_resume.experience:
                exp_lower = exp.lower()
                if 'intern' in exp_lower:
                    profile['experience']['internships'].append(exp)
                elif any(keyword in exp_lower for keyword in ['project', 'developed', 'built', 'created']):
                    profile['experience']['projects'].append(exp)
                else:
                    profile['experience']['work_experience'].append(exp)
                
                # Estimate years from experience text
                years_match = re.search(r'(\d+)\s*(?:year|yr)', exp_lower)
                if years_match:
                    profile['experience']['total_years'] += int(years_match.group(1))
        
        # Process education
        if parsed_resume.education:
            for edu in parsed_resume.education:
                edu_lower = edu.lower()
                if any(degree in edu_lower for degree in ['bachelor', 'master', 'phd', 'associate']):
                    profile['education']['degrees'].append(edu)
                elif 'gpa' in edu_lower:
                    gpa_match = re.search(r'(\d+\.?\d*)', edu_lower)
                    if gpa_match:
                        profile['education']['gpa'] = float(gpa_match.group(1))
                else:
                    profile['education']['relevant_coursework'].append(edu)
        
        # Process certifications
        if parsed_resume.certifications:
            profile['education']['certifications'] = parsed_resume.certifications
        
        # Process projects as achievements if they exist
        if parsed_resume.projects:
            profile['achievements'].extend(parsed_resume.projects)
        
        # Determine experience level
        total_exp = profile['experience']['total_years']
        if total_exp == 0 and not profile['experience']['internships']:
            profile['experience_level'] = 'entry'
        elif total_exp <= 2 or profile['experience']['internships']:
            profile['experience_level'] = 'junior'
        elif total_exp <= 5:
            profile['experience_level'] = 'mid'
        else:
            profile['experience_level'] = 'senior'
        
        return profile
    
    async def _generate_professional_insights(
        self,
        student_profile: Dict[str, Any],
        preferred_industries: List[str],
        career_goals: str
    ) -> Dict[str, Any]:
        """Generate personalized professional insights based on student's profile."""
        insights = {
            'strengths': [],
            'areas_for_improvement': [],
            'market_position': '',
            'competitive_advantages': [],
            'industry_readiness': {},
            'recommendations': []
        }
        
        # Analyze strengths based on skills and experience
        technical_skills_count = len(student_profile['skills']['technical'])
        soft_skills_count = len(student_profile['skills']['soft'])
        experience_level = student_profile['experience_level']
        
        # Identify strengths
        if technical_skills_count >= 5:
            insights['strengths'].append(f"Strong technical foundation with {technical_skills_count} technical skills")
        
        if soft_skills_count >= 3:
            insights['strengths'].append(f"Well-developed soft skills including {', '.join(student_profile['skills']['soft'][:3])}")
        
        if student_profile['experience']['internships']:
            insights['strengths'].append(f"Practical experience through {len(student_profile['experience']['internships'])} internship(s)")
        
        if student_profile['education']['certifications']:
            insights['strengths'].append(f"Professional certifications: {', '.join(student_profile['education']['certifications'][:2])}")
        
        if student_profile['education']['gpa'] and student_profile['education']['gpa'] >= 3.5:
            insights['strengths'].append(f"Strong academic performance (GPA: {student_profile['education']['gpa']})")
        
        # Identify areas for improvement
        if technical_skills_count < 3:
            insights['areas_for_improvement'].append("Expand technical skill set with in-demand technologies")
        
        if soft_skills_count < 2:
            insights['areas_for_improvement'].append("Develop essential soft skills like communication and teamwork")
        
        if not student_profile['experience']['work_experience'] and not student_profile['experience']['internships']:
            insights['areas_for_improvement'].append("Gain practical experience through internships or projects")
        
        if not student_profile['education']['certifications']:
            insights['areas_for_improvement'].append("Consider obtaining industry-relevant certifications")
        
        # Assess market position
        if experience_level == 'entry':
            if technical_skills_count >= 5 and student_profile['experience']['internships']:
                insights['market_position'] = "Strong entry-level candidate with good preparation for the job market"
            elif technical_skills_count >= 3:
                insights['market_position'] = "Competitive entry-level candidate with room for skill development"
            else:
                insights['market_position'] = "Early-stage candidate who would benefit from skill development"
        
        # Identify competitive advantages
        unique_skills = []
        high_demand_skills = ['python', 'javascript', 'sql', 'cloud', 'machine learning', 'data analysis']
        
        for skill in student_profile['skills']['technical']:
            if any(demand_skill in skill.lower() for demand_skill in high_demand_skills):
                unique_skills.append(skill)
        
        if unique_skills:
            insights['competitive_advantages'].append(f"High-demand skills: {', '.join(unique_skills[:3])}")
        
        if len(student_profile['skills']['languages']) > 1:
            insights['competitive_advantages'].append(f"Multilingual abilities: {', '.join(student_profile['skills']['languages'])}")
        
        # Assess industry readiness
        if preferred_industries:
            for industry in preferred_industries:
                if industry.lower() in self.industry_paths:
                    industry_data = self.industry_paths[industry.lower()]
                    required_skills = industry_data['key_skills']
                    
                    student_skills_lower = [s.lower() for s in student_profile['skills']['technical'] + student_profile['skills']['soft']]
                    matching_skills = [skill for skill in required_skills if any(skill in s for s in student_skills_lower)]
                    
                    readiness_score = (len(matching_skills) / len(required_skills)) * 100
                    insights['industry_readiness'][industry] = {
                        'readiness_score': round(readiness_score, 1),
                        'matching_skills': matching_skills,
                        'missing_skills': [skill for skill in required_skills if skill not in matching_skills]
                    }
        
        # Generate personalized recommendations
        if technical_skills_count < 5:
            insights['recommendations'].append("Focus on developing 2-3 additional technical skills relevant to your target industry")
        
        if not student_profile['experience']['projects']:
            insights['recommendations'].append("Build a portfolio with 2-3 personal projects to demonstrate your skills")
        
        if preferred_industries and len(preferred_industries) == 1:
            industry = preferred_industries[0].lower()
            if industry in self.industry_paths:
                insights['recommendations'].append(f"Consider developing {industry}-specific skills to strengthen your profile")
        
        return insights
    
    async def _generate_career_recommendations(
        self,
        student_profile: Dict[str, Any],
        preferred_industries: List[str],
        career_goals: str,
        target_salary_range: str
    ) -> Dict[str, Any]:
        """Generate personalized career recommendations."""
        recommendations = {
            'immediate_opportunities': [],
            'short_term_goals': [],
            'long_term_vision': [],
            'recommended_next_steps': [],
            'salary_expectations': {},
            'growth_trajectory': []
        }
        
        experience_level = student_profile['experience_level']
        technical_skills = student_profile['skills']['technical']
        
        # Generate immediate opportunities based on current profile
        if preferred_industries:
            for industry in preferred_industries:
                if industry.lower() in self.industry_paths:
                    industry_data = self.industry_paths[industry.lower()]
                    
                    # Match experience level to appropriate roles
                    if experience_level in ['entry', 'junior']:
                        suitable_roles = industry_data['entry_level']
                    elif experience_level == 'mid':
                        suitable_roles = industry_data['mid_level']
                    else:
                        suitable_roles = industry_data['senior_level']
                    
                    for role in suitable_roles[:3]:  # Top 3 roles
                        recommendations['immediate_opportunities'].append({
                            'role': role,
                            'industry': industry,
                            'match_reason': f"Aligns with your {experience_level}-level profile and {industry} interest",
                            'required_preparation': self._get_role_preparation(role, student_profile)
                        })
        
        # Generate short-term goals (6-18 months)
        if experience_level == 'entry':
            recommendations['short_term_goals'] = [
                "Secure an entry-level position or internship in your target industry",
                "Build a portfolio of 2-3 relevant projects",
                "Obtain 1-2 industry-relevant certifications",
                "Develop proficiency in high-demand technical skills"
            ]
        elif experience_level == 'junior':
            recommendations['short_term_goals'] = [
                "Transition to a full-time role with increased responsibilities",
                "Specialize in a particular technology stack or domain",
                "Build leadership experience through project management",
                "Expand professional network through industry events"
            ]
        
        # Generate long-term vision (2-5 years)
        if career_goals:
            recommendations['long_term_vision'].append(f"Work towards your stated goal: {career_goals}")
        
        # Add generic long-term goals based on industry
        if preferred_industries:
            for industry in preferred_industries:
                if industry.lower() in self.industry_paths:
                    industry_data = self.industry_paths[industry.lower()]
                    target_roles = industry_data['mid_level'] if experience_level == 'entry' else industry_data['senior_level']
                    recommendations['long_term_vision'].append(f"Progress to {target_roles[0]} or similar role in {industry}")
        
        # Generate recommended next steps
        missing_skills = []
        if len(technical_skills) < 5:
            missing_skills.append("Develop additional technical skills")
        
        if not student_profile['experience']['projects']:
            recommendations['recommended_next_steps'].append("Build a portfolio with personal projects")
        
        if not student_profile['education']['certifications']:
            recommendations['recommended_next_steps'].append("Obtain relevant industry certifications")
        
        if not student_profile['experience']['internships'] and experience_level == 'entry':
            recommendations['recommended_next_steps'].append("Apply for internships to gain practical experience")
        
        # Salary expectations based on industry and experience
        if preferred_industries and target_salary_range:
            recommendations['salary_expectations'] = self._generate_salary_guidance(
                preferred_industries, experience_level, target_salary_range
            )
        
        # Growth trajectory
        if preferred_industries:
            for industry in preferred_industries:
                if industry.lower() in self.industry_paths:
                    industry_data = self.industry_paths[industry.lower()]
                    trajectory = {
                        'industry': industry,
                        'entry_level': industry_data['entry_level'][0],
                        'mid_level': industry_data['mid_level'][0],
                        'senior_level': industry_data['senior_level'][0],
                        'timeline': "Typically 2-3 years between levels with consistent skill development"
                    }
                    recommendations['growth_trajectory'].append(trajectory)
        
        return recommendations
    
    def _generate_skill_breakdown(
        self,
        student_profile: Dict[str, Any],
        preferred_industries: List[str]
    ) -> Dict[str, Any]:
        """Generate personalized skill breakdown and analysis."""
        breakdown = {
            'current_skills_analysis': {},
            'skill_strength_areas': [],
            'skill_development_areas': [],
            'industry_skill_gaps': {},
            'skill_recommendations': [],
            'learning_path_suggestions': []
        }
        
        # Analyze current skills
        technical_skills = student_profile['skills']['technical']
        soft_skills = student_profile['skills']['soft']
        
        breakdown['current_skills_analysis'] = {
            'technical_skills_count': len(technical_skills),
            'soft_skills_count': len(soft_skills),
            'strongest_technical_areas': technical_skills[:3] if technical_skills else [],
            'strongest_soft_skills': soft_skills[:3] if soft_skills else [],
            'total_skills': len(technical_skills) + len(soft_skills)
        }
        
        # Identify skill strength areas
        high_demand_skills = self.skill_priorities['high_demand']['technical']
        matching_high_demand = [skill for skill in technical_skills 
                               if any(hd_skill in skill.lower() for hd_skill in high_demand_skills)]
        
        if matching_high_demand:
            breakdown['skill_strength_areas'].append(f"High-demand technical skills: {', '.join(matching_high_demand)}")
        
        if len(soft_skills) >= 3:
            breakdown['skill_strength_areas'].append(f"Strong soft skill foundation with {len(soft_skills)} identified skills")
        
        # Identify development areas
        if len(technical_skills) < 5:
            breakdown['skill_development_areas'].append("Technical skill portfolio needs expansion")
        
        if len(soft_skills) < 3:
            breakdown['skill_development_areas'].append("Soft skills development recommended")
        
        missing_high_demand = [skill for skill in high_demand_skills 
                              if not any(skill in ts.lower() for ts in technical_skills)]
        
        if missing_high_demand:
            breakdown['skill_development_areas'].append(f"Missing high-demand skills: {', '.join(missing_high_demand[:3])}")
        
        # Industry-specific skill gap analysis
        if preferred_industries:
            for industry in preferred_industries:
                if industry.lower() in self.industry_paths:
                    industry_data = self.industry_paths[industry.lower()]
                    required_skills = industry_data['key_skills']
                    
                    student_skills_lower = [s.lower() for s in technical_skills + soft_skills]
                    missing_industry_skills = [skill for skill in required_skills 
                                             if not any(skill in s for s in student_skills_lower)]
                    
                    if missing_industry_skills:
                        breakdown['industry_skill_gaps'][industry] = missing_industry_skills
        
        # Generate skill recommendations
        if len(technical_skills) < 5:
            breakdown['skill_recommendations'].append("Develop 2-3 additional programming languages or frameworks")
        
        if not any('data' in skill.lower() for skill in technical_skills):
            breakdown['skill_recommendations'].append("Consider learning data analysis or database management skills")
        
        if not any('cloud' in skill.lower() for skill in technical_skills):
            breakdown['skill_recommendations'].append("Explore cloud computing platforms (AWS, Azure, or GCP)")
        
        # Learning path suggestions
        if preferred_industries:
            for industry in preferred_industries:
                if industry.lower() == 'technology':
                    breakdown['learning_path_suggestions'].append({
                        'path': 'Full-Stack Development',
                        'skills': ['HTML/CSS', 'JavaScript', 'React', 'Node.js', 'Databases'],
                        'timeline': '3-6 months',
                        'resources': ['freeCodeCamp', 'The Odin Project', 'Codecademy']
                    })
                elif industry.lower() == 'business':
                    breakdown['learning_path_suggestions'].append({
                        'path': 'Business Analytics',
                        'skills': ['Excel', 'SQL', 'Tableau', 'Business Intelligence'],
                        'timeline': '2-4 months',
                        'resources': ['Coursera Business Analytics', 'LinkedIn Learning', 'Tableau Public']
                    })
        
        return breakdown
    
    def _generate_suggested_career_paths(
        self,
        student_profile: Dict[str, Any],
        preferred_industries: List[str],
        career_goals: str
    ) -> List[Dict[str, Any]]:
        """Generate personalized career path suggestions."""
        career_paths = []
        
        experience_level = student_profile['experience_level']
        technical_skills = student_profile['skills']['technical']
        
        # Technology career paths
        if not preferred_industries or 'Technology' in preferred_industries:
            if any(skill in ['python', 'javascript', 'java'] for skill in [s.lower() for s in technical_skills]):
                career_paths.append({
                    'title': 'Software Development Career Path',
                    'description': 'Progress from junior developer to senior engineer or architect',
                    'stages': [
                        {
                            'level': 'Entry (0-2 years)',
                            'roles': ['Junior Developer', 'Software Developer I'],
                            'skills_needed': ['Programming fundamentals', 'Version control', 'Testing'],
                            'salary_range': '$50,000 - $75,000'
                        },
                        {
                            'level': 'Mid (2-5 years)',
                            'roles': ['Software Engineer', 'Full Stack Developer'],
                            'skills_needed': ['Advanced programming', 'System design', 'Database management'],
                            'salary_range': '$75,000 - $120,000'
                        },
                        {
                            'level': 'Senior (5+ years)',
                            'roles': ['Senior Engineer', 'Tech Lead', 'Software Architect'],
                            'skills_needed': ['Leadership', 'Architecture design', 'Mentoring'],
                            'salary_range': '$120,000 - $200,000+'
                        }
                    ],
                    'personalization_note': f"Your {', '.join(technical_skills[:2])} skills provide a strong foundation for this path"
                })
        
        # Data Science career path
        if any(skill in ['python', 'sql', 'data', 'statistics'] for skill in [s.lower() for s in technical_skills]):
            career_paths.append({
                'title': 'Data Science Career Path',
                'description': 'Advance from data analyst to senior data scientist or chief data officer',
                'stages': [
                    {
                        'level': 'Entry (0-2 years)',
                        'roles': ['Data Analyst', 'Junior Data Scientist'],
                        'skills_needed': ['SQL', 'Excel', 'Basic statistics', 'Data visualization'],
                        'salary_range': '$55,000 - $80,000'
                    },
                    {
                        'level': 'Mid (2-5 years)',
                        'roles': ['Data Scientist', 'Senior Data Analyst'],
                        'skills_needed': ['Machine learning', 'Python/R', 'Advanced statistics'],
                        'salary_range': '$80,000 - $140,000'
                    },
                    {
                        'level': 'Senior (5+ years)',
                        'roles': ['Senior Data Scientist', 'Data Science Manager', 'Chief Data Officer'],
                        'skills_needed': ['Deep learning', 'Business strategy', 'Team leadership'],
                        'salary_range': '$140,000 - $250,000+'
                    }
                ],
                'personalization_note': "Your analytical skills and technical background align well with data science"
            })
        
        # Business/Management career path
        if not preferred_industries or any(industry in ['Business', 'Finance', 'Marketing'] for industry in preferred_industries):
            if student_profile['skills']['soft'] or student_profile['experience']['internships']:
                career_paths.append({
                    'title': 'Business Management Career Path',
                    'description': 'Progress from analyst to manager to executive leadership',
                    'stages': [
                        {
                            'level': 'Entry (0-2 years)',
                            'roles': ['Business Analyst', 'Management Trainee', 'Coordinator'],
                            'skills_needed': ['Communication', 'Data analysis', 'Problem solving'],
                            'salary_range': '$45,000 - $65,000'
                        },
                        {
                            'level': 'Mid (2-5 years)',
                            'roles': ['Project Manager', 'Team Lead', 'Senior Analyst'],
                            'skills_needed': ['Leadership', 'Strategic thinking', 'Project management'],
                            'salary_range': '$65,000 - $100,000'
                        },
                        {
                            'level': 'Senior (5+ years)',
                            'roles': ['Director', 'Vice President', 'General Manager'],
                            'skills_needed': ['Executive leadership', 'Business strategy', 'P&L management'],
                            'salary_range': '$100,000 - $300,000+'
                        }
                    ],
                    'personalization_note': f"Your {', '.join(student_profile['skills']['soft'][:2])} skills support management potential"
                })
        
        # If no specific paths match, provide a general technology path
        if not career_paths:
            career_paths.append({
                'title': 'Technology Generalist Career Path',
                'description': 'Flexible path that can adapt to various technology roles',
                'stages': [
                    {
                        'level': 'Foundation (0-1 years)',
                        'roles': ['IT Support', 'Junior Analyst', 'Technical Assistant'],
                        'skills_needed': ['Computer literacy', 'Problem solving', 'Communication'],
                        'salary_range': '$35,000 - $50,000'
                    },
                    {
                        'level': 'Specialization (1-3 years)',
                        'roles': ['Specialist', 'Coordinator', 'Analyst'],
                        'skills_needed': ['Specialized technical skills', 'Industry knowledge'],
                        'salary_range': '$50,000 - $80,000'
                    },
                    {
                        'level': 'Leadership (3+ years)',
                        'roles': ['Senior Specialist', 'Manager', 'Consultant'],
                        'skills_needed': ['Advanced expertise', 'Leadership', 'Strategic thinking'],
                        'salary_range': '$80,000 - $150,000+'
                    }
                ],
                'personalization_note': "This flexible path allows you to develop and specialize based on your interests"
            })
        
        return career_paths[:3]  # Return top 3 most relevant paths
    
    def _generate_priority_skills(
        self,
        student_profile: Dict[str, Any],
        preferred_industries: List[str],
        career_goals: str
    ) -> Dict[str, Any]:
        """Generate personalized priority skills for development."""
        priority_skills = {
            'immediate_priority': [],  # Skills to develop in next 3 months
            'short_term_priority': [],  # Skills for next 6-12 months
            'long_term_priority': [],   # Skills for career advancement
            'skill_learning_plan': [],
            'recommended_certifications': []
        }
        
        current_technical = [s.lower() for s in student_profile['skills']['technical']]
        current_soft = [s.lower() for s in student_profile['skills']['soft']]
        
        # Immediate priority (next 3 months) - Foundation skills
        if 'programming' not in ' '.join(current_technical):
            priority_skills['immediate_priority'].append({
                'skill': 'Programming Fundamentals',
                'reason': 'Essential foundation for technology careers',
                'learning_time': '2-3 months',
                'resources': ['Codecademy', 'freeCodeCamp', 'Python.org tutorial']
            })
        
        if not any(skill in ['communication', 'teamwork'] for skill in current_soft):
            priority_skills['immediate_priority'].append({
                'skill': 'Communication Skills',
                'reason': 'Critical for all professional roles',
                'learning_time': '1-2 months',
                'resources': ['Toastmasters', 'Coursera Communication courses', 'LinkedIn Learning']
            })
        
        # Short-term priority (6-12 months) - Industry-specific skills
        if preferred_industries:
            for industry in preferred_industries:
                if industry.lower() in self.industry_paths:
                    required_skills = self.industry_paths[industry.lower()]['key_skills']
                    missing_skills = [skill for skill in required_skills 
                                    if not any(skill in curr for curr in current_technical + current_soft)]
                    
                    for skill in missing_skills[:2]:  # Top 2 missing skills
                        priority_skills['short_term_priority'].append({
                            'skill': skill.title(),
                            'reason': f'Key requirement for {industry} industry',
                            'learning_time': '3-6 months',
                            'industry_relevance': industry
                        })
        
        # Add high-demand technical skills
        high_demand_missing = []
        for skill in self.skill_priorities['high_demand']['technical']:
            if not any(skill in curr for curr in current_technical):
                high_demand_missing.append(skill)
        
        for skill in high_demand_missing[:2]:
            priority_skills['short_term_priority'].append({
                'skill': skill.title(),
                'reason': 'High market demand across industries',
                'learning_time': '3-6 months',
                'market_demand': 'High'
            })
        
        # Long-term priority (career advancement)
        emerging_skills = self.skill_priorities['emerging']['technical']
        for skill in emerging_skills[:2]:
            if not any(skill in curr for curr in current_technical):
                priority_skills['long_term_priority'].append({
                    'skill': skill.title(),
                    'reason': 'Emerging technology with future growth potential',
                    'learning_time': '6-12 months',
                    'future_potential': 'High'
                })
        
        # Advanced soft skills for leadership
        leadership_skills = ['leadership', 'strategic thinking', 'emotional intelligence']
        for skill in leadership_skills:
            if not any(skill in curr for curr in current_soft):
                priority_skills['long_term_priority'].append({
                    'skill': skill.title(),
                    'reason': 'Essential for career advancement and leadership roles',
                    'learning_time': '6-12 months',
                    'career_impact': 'High'
                })
        
        # Create learning plan
        all_priority_skills = (priority_skills['immediate_priority'] + 
                              priority_skills['short_term_priority'][:2] + 
                              priority_skills['long_term_priority'][:1])
        
        for i, skill_info in enumerate(all_priority_skills[:4]):  # Top 4 skills
            priority_skills['skill_learning_plan'].append({
                'order': i + 1,
                'skill': skill_info['skill'],
                'timeline': skill_info['learning_time'],
                'priority_level': 'High' if i < 2 else 'Medium',
                'recommended_approach': self._get_learning_approach(skill_info['skill'])
            })
        
        # Recommended certifications
        cert_recommendations = []
        if any('python' in skill for skill in current_technical):
            cert_recommendations.append('Python Institute PCAP Certification')
        
        if preferred_industries and 'Technology' in preferred_industries:
            cert_recommendations.extend(['AWS Cloud Practitioner', 'Google IT Support Certificate'])
        
        if any('data' in skill for skill in current_technical):
            cert_recommendations.append('Google Data Analytics Certificate')
        
        priority_skills['recommended_certifications'] = cert_recommendations[:3]
        
        return priority_skills
    
    def _get_role_preparation(self, role: str, student_profile: Dict[str, Any]) -> List[str]:
        """Get specific preparation recommendations for a role."""
        preparation = []
        role_lower = role.lower()
        
        if 'developer' in role_lower or 'engineer' in role_lower:
            if len(student_profile['skills']['technical']) < 3:
                preparation.append("Learn 2-3 programming languages")
            preparation.append("Build a portfolio of coding projects")
            preparation.append("Practice coding interviews")
        
        elif 'analyst' in role_lower:
            preparation.append("Develop Excel and SQL skills")
            preparation.append("Learn data visualization tools")
            preparation.append("Practice presenting findings")
        
        elif 'manager' in role_lower:
            preparation.append("Develop leadership and communication skills")
            preparation.append("Gain project management experience")
            preparation.append("Learn business strategy fundamentals")
        
        return preparation[:3]  # Return top 3 recommendations
    
    def _generate_salary_guidance(
        self,
        preferred_industries: List[str],
        experience_level: str,
        target_salary_range: str
    ) -> Dict[str, Any]:
        """Generate personalized salary guidance."""
        guidance = {
            'market_analysis': {},
            'negotiation_tips': [],
            'realistic_expectations': '',
            'growth_potential': ''
        }
        
        # Basic salary ranges by industry and experience
        salary_data = {
            'technology': {
                'entry': (50000, 80000),
                'junior': (70000, 100000),
                'mid': (90000, 140000),
                'senior': (120000, 200000)
            },
            'business': {
                'entry': (40000, 60000),
                'junior': (55000, 80000),
                'mid': (75000, 120000),
                'senior': (100000, 180000)
            },
            'healthcare': {
                'entry': (35000, 55000),
                'junior': (50000, 75000),
                'mid': (70000, 110000),
                'senior': (90000, 150000)
            }
        }
        
        for industry in preferred_industries:
            industry_key = industry.lower()
            if industry_key in salary_data and experience_level in salary_data[industry_key]:
                min_sal, max_sal = salary_data[industry_key][experience_level]
                guidance['market_analysis'][industry] = {
                    'min_salary': min_sal,
                    'max_salary': max_sal,
                    'median_salary': (min_sal + max_sal) // 2
                }
        
        # Negotiation tips based on experience level
        if experience_level == 'entry':
            guidance['negotiation_tips'] = [
                "Focus on learning opportunities and growth potential",
                "Consider the full compensation package, not just salary",
                "Research typical entry-level salaries in your area"
            ]
        else:
            guidance['negotiation_tips'] = [
                "Highlight specific achievements and quantifiable results",
                "Research industry salary benchmarks for your role",
                "Consider negotiating for additional benefits or professional development"
            ]
        
        return guidance
    
    def _get_learning_approach(self, skill: str) -> str:
        """Get recommended learning approach for a skill."""
        skill_lower = skill.lower()
        
        if any(tech in skill_lower for tech in ['programming', 'python', 'javascript']):
            return "Hands-on coding with projects and practice problems"
        elif 'communication' in skill_lower:
            return "Practice through presentations, writing, and group activities"
        elif 'data' in skill_lower:
            return "Work with real datasets and build analysis projects"
        elif 'leadership' in skill_lower:
            return "Volunteer for leadership roles and seek mentoring opportunities"
        else:
            return "Combination of online courses and practical application"
    
    def _calculate_personalization_score(self, student_profile: Dict[str, Any]) -> float:
        """Calculate how well we can personalize insights for this student."""
        score = 0.0
        
        # Skills information
        if student_profile['skills']['technical']:
            score += 25
        if student_profile['skills']['soft']:
            score += 20
        
        # Experience information
        if student_profile['experience']['work_experience'] or student_profile['experience']['internships']:
            score += 25
        
        # Education information
        if student_profile['education']['degrees']:
            score += 15
        if student_profile['education']['certifications']:
            score += 10
        
        # Additional details
        if student_profile['experience']['projects']:
            score += 5
        
        return min(score, 100.0)
