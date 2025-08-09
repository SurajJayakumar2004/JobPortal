"""
AI-powered job-candidate matching service.

This service implements intelligent matching algorithms to rank candidates
based on their resume content against job requirements using TF-IDF
vectorization and cosine similarity calculations.
"""

import logging
from typing import List, Dict, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from collections import Counter

from app.schemas import CandidateMatch, JobMatchResponse
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MatchingService:
    """Service for matching candidates to job requirements using AI/ML techniques."""
    
    def __init__(self):
        """Initialize the matching service."""
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.min_similarity_score = settings.min_similarity_score
        self.max_candidates = settings.max_candidates_return
    
    async def match_candidates_to_job(
        self,
        job_description: str,
        job_requirements: List[str],
        candidates: List[Dict]
    ) -> JobMatchResponse:
        """
        Match and rank candidates against a job posting.
        
        Args:
            job_description: The job description text
            job_requirements: List of required skills/qualifications
            candidates: List of candidate data with resume information
            
        Returns:
            JobMatchResponse: Ranked list of candidates with match scores
        """
        if not candidates:
            return JobMatchResponse(
                job_id="",
                job_title="",
                total_candidates=0,
                candidates=[],
                average_match_score=0.0
            )
        
        try:
            # Prepare job text for comparison
            job_text = self._prepare_job_text(job_description, job_requirements)
            
            # Prepare candidate texts
            candidate_texts = []
            candidate_info = []
            
            for candidate in candidates:
                # Extract resume text and skills
                resume_text = candidate.get('resume_text', '')
                skills = candidate.get('skills', [])
                experience = candidate.get('experience', [])
                
                # Combine all candidate text
                candidate_text = self._prepare_candidate_text(resume_text, skills, experience)
                candidate_texts.append(candidate_text)
                candidate_info.append(candidate)
            
            # Calculate similarity scores
            matches = self._calculate_similarity_scores(
                job_text, 
                candidate_texts, 
                candidate_info,
                job_requirements
            )
            
            # Filter and sort matches
            filtered_matches = [
                match for match in matches 
                if match.match_score >= self.min_similarity_score
            ]
            
            # Sort by match score (descending)
            filtered_matches.sort(key=lambda x: x.match_score, reverse=True)
            
            # Limit results
            top_matches = filtered_matches[:self.max_candidates]
            
            # Calculate average score
            avg_score = (
                sum(match.match_score for match in top_matches) / len(top_matches)
                if top_matches else 0.0
            )
            
            return JobMatchResponse(
                job_id=candidates[0].get('job_id', '') if candidates else '',
                job_title=job_description[:50] + '...' if len(job_description) > 50 else job_description,
                total_candidates=len(top_matches),
                candidates=top_matches,
                average_match_score=avg_score
            )
            
        except Exception as e:
            logger.error(f"Error matching candidates to job: {str(e)}")
            return JobMatchResponse(
                job_id="",
                job_title="",
                total_candidates=0,
                candidates=[],
                average_match_score=0.0
            )
    
    def _prepare_job_text(self, description: str, requirements: List[str]) -> str:
        """
        Prepare job text for matching by combining description and requirements.
        
        Args:
            description: Job description
            requirements: List of job requirements
            
        Returns:
            str: Combined and cleaned job text
        """
        # Combine description and requirements
        job_text = description + " " + " ".join(requirements)
        
        # Clean and normalize text
        job_text = self._clean_text(job_text)
        
        return job_text
    
    def _prepare_candidate_text(
        self, 
        resume_text: str, 
        skills: List[str], 
        experience: List[str]
    ) -> str:
        """
        Prepare candidate text for matching by combining all available information.
        
        Args:
            resume_text: Full resume text
            skills: List of candidate skills
            experience: List of experience entries
            
        Returns:
            str: Combined and cleaned candidate text
        """
        # Combine all candidate information
        candidate_text = resume_text
        
        if skills:
            # Weight skills more heavily by repeating them
            skills_text = " ".join(skills) * 2
            candidate_text += " " + skills_text
        
        if experience:
            experience_text = " ".join(experience)
            candidate_text += " " + experience_text
        
        # Clean and normalize text
        candidate_text = self._clean_text(candidate_text)
        
        return candidate_text
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for better matching.
        
        Args:
            text: Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep alphanumeric and spaces
        text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _calculate_similarity_scores(
        self,
        job_text: str,
        candidate_texts: List[str],
        candidate_info: List[Dict],
        job_requirements: List[str]
    ) -> List[CandidateMatch]:
        """
        Calculate similarity scores between job and candidates using TF-IDF and cosine similarity.
        
        Args:
            job_text: Prepared job text
            candidate_texts: List of prepared candidate texts
            candidate_info: List of candidate information
            job_requirements: List of job requirements for skill matching
            
        Returns:
            List[CandidateMatch]: List of candidate matches with scores
        """
        matches = []
        
        try:
            # Prepare all texts for vectorization
            all_texts = [job_text] + candidate_texts
            
            # Fit and transform texts using TF-IDF
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            # Calculate cosine similarity between job and each candidate
            job_vector = tfidf_matrix[0:1]  # First row is job text
            candidate_vectors = tfidf_matrix[1:]  # Rest are candidates
            
            similarity_scores = cosine_similarity(job_vector, candidate_vectors)[0]
            
            # Create matches with detailed analysis
            for i, (score, candidate_text, candidate) in enumerate(
                zip(similarity_scores, candidate_texts, candidate_info)
            ):
                # Analyze skill matches
                matching_skills, missing_skills = self._analyze_skill_match(
                    candidate.get('skills', []),
                    job_requirements
                )
                
                match = CandidateMatch(
                    user_id=candidate.get('user_id', ''),
                    user_name=candidate.get('user_name', 'Unknown'),
                    user_email=candidate.get('user_email', ''),
                    resume_id=candidate.get('resume_id', ''),
                    match_score=float(score),
                    matching_skills=matching_skills,
                    missing_skills=missing_skills,
                    experience_level=candidate.get('experience_level')
                )
                
                matches.append(match)
                
        except Exception as e:
            logger.error(f"Error calculating similarity scores: {str(e)}")
            # Return empty matches on error
            for candidate in candidate_info:
                match = CandidateMatch(
                    user_id=candidate.get('user_id', ''),
                    user_name=candidate.get('user_name', 'Unknown'),
                    user_email=candidate.get('user_email', ''),
                    resume_id=candidate.get('resume_id', ''),
                    match_score=0.0,
                    matching_skills=[],
                    missing_skills=job_requirements,
                    experience_level=candidate.get('experience_level')
                )
                matches.append(match)
        
        return matches
    
    def _analyze_skill_match(
        self, 
        candidate_skills: List[str], 
        job_requirements: List[str]
    ) -> Tuple[List[str], List[str]]:
        """
        Analyze skill overlap between candidate and job requirements.
        
        Args:
            candidate_skills: List of candidate skills
            job_requirements: List of job requirements
            
        Returns:
            Tuple[List[str], List[str]]: (matching_skills, missing_skills)
        """
        # Normalize skills for comparison
        candidate_skills_lower = [skill.lower().strip() for skill in candidate_skills]
        job_requirements_lower = [req.lower().strip() for req in job_requirements]
        
        matching_skills = []
        missing_skills = []
        
        for requirement in job_requirements:
            requirement_lower = requirement.lower().strip()
            
            # Check for exact match
            if requirement_lower in candidate_skills_lower:
                matching_skills.append(requirement)
            else:
                # Check for partial match (e.g., "machine learning" in "ml")
                found_partial = False
                for candidate_skill in candidate_skills_lower:
                    if (requirement_lower in candidate_skill or 
                        candidate_skill in requirement_lower):
                        matching_skills.append(requirement)
                        found_partial = True
                        break
                
                if not found_partial:
                    missing_skills.append(requirement)
        
        return matching_skills, missing_skills
    
    async def get_job_recommendations_for_candidate(
        self,
        candidate_text: str,
        candidate_skills: List[str],
        available_jobs: List[Dict]
    ) -> List[Dict]:
        """
        Get job recommendations for a candidate based on their profile.
        
        Args:
            candidate_text: Candidate's resume text
            candidate_skills: List of candidate skills
            available_jobs: List of available job postings
            
        Returns:
            List[Dict]: Recommended jobs with match scores
        """
        if not available_jobs:
            return []
        
        try:
            # Prepare candidate text
            prepared_candidate_text = self._prepare_candidate_text(
                candidate_text, candidate_skills, []
            )
            
            # Prepare job texts
            job_texts = []
            for job in available_jobs:
                job_text = self._prepare_job_text(
                    job.get('description', ''),
                    job.get('required_skills', [])
                )
                job_texts.append(job_text)
            
            # Calculate similarities
            all_texts = [prepared_candidate_text] + job_texts
            tfidf_matrix = self.vectorizer.fit_transform(all_texts)
            
            candidate_vector = tfidf_matrix[0:1]
            job_vectors = tfidf_matrix[1:]
            
            similarity_scores = cosine_similarity(candidate_vector, job_vectors)[0]
            
            # Create recommendations
            recommendations = []
            for i, (score, job) in enumerate(zip(similarity_scores, available_jobs)):
                if score >= self.min_similarity_score:
                    recommendation = {
                        'job': job,
                        'match_score': float(score),
                        'matching_skills': self._analyze_skill_match(
                            candidate_skills,
                            job.get('required_skills', [])
                        )[0]
                    }
                    recommendations.append(recommendation)
            
            # Sort by match score
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            
            return recommendations[:10]  # Return top 10 recommendations
            
        except Exception as e:
            logger.error(f"Error generating job recommendations: {str(e)}")
            return []
    
    def calculate_skill_gap_score(
        self, 
        candidate_skills: List[str], 
        job_requirements: List[str]
    ) -> Dict[str, float]:
        """
        Calculate detailed skill gap analysis with personalized insights.
        
        Args:
            candidate_skills: List of candidate skills
            job_requirements: List of job requirements
            
        Returns:
            Dict with comprehensive gap analysis metrics and personalized recommendations
        """
        matching_skills, missing_skills = self._analyze_skill_match(
            candidate_skills, job_requirements
        )
        
        total_requirements = len(job_requirements)
        if total_requirements == 0:
            return {
                'skill_coverage': 100.0,
                'gap_score': 0.0,
                'critical_gaps': 0,
                'matching_skills_count': 0,
                'missing_skills_count': 0,
                'personalized_insights': {
                    'professional_insights': ['No specific requirements to analyze'],
                    'career_recommendations': ['Continue developing general skills'],
                    'priority_skills': [],
                    'learning_timeline': 'N/A'
                }
            }
        
        skill_coverage = (len(matching_skills) / total_requirements) * 100
        gap_score = (len(missing_skills) / total_requirements) * 100
        
        # Identify critical gaps (high importance skills)
        critical_skills = ['python', 'java', 'sql', 'aws', 'react', 'machine learning', 'data science']
        critical_gaps = sum(
            1 for skill in missing_skills 
            if any(critical.lower() in skill.lower() for critical in critical_skills)
        )
        
        # Generate personalized insights
        personalized_insights = self._generate_personalized_career_insights(
            candidate_skills, job_requirements, matching_skills, missing_skills, skill_coverage
        )
        
        return {
            'skill_coverage': skill_coverage,
            'gap_score': gap_score,
            'critical_gaps': critical_gaps,
            'matching_skills_count': len(matching_skills),
            'missing_skills_count': len(missing_skills),
            'matching_skills': matching_skills,
            'missing_skills': missing_skills,
            'personalized_insights': personalized_insights
        }
    
    def _generate_personalized_career_insights(
        self,
        candidate_skills: List[str],
        job_requirements: List[str],
        matching_skills: List[str],
        missing_skills: List[str],
        skill_coverage: float
    ) -> Dict:
        """
        Generate comprehensive personalized career insights for students.
        
        Args:
            candidate_skills: Current candidate skills
            job_requirements: Required job skills
            matching_skills: Skills that match
            missing_skills: Skills that are missing
            skill_coverage: Percentage of skill coverage
            
        Returns:
            Dict with personalized insights and recommendations
        """
        
        # Professional Insights
        professional_insights = []
        if skill_coverage >= 80:
            professional_insights.extend([
                f"Excellent match! You possess {len(matching_skills)} of {len(job_requirements)} required skills ({skill_coverage:.1f}% coverage)",
                "You are well-positioned for this role and should confidently apply",
                "Focus on showcasing your matching skills through portfolio projects",
                "Consider this role as an immediate career opportunity"
            ])
        elif skill_coverage >= 60:
            professional_insights.extend([
                f"Strong foundation! You have {len(matching_skills)} of {len(job_requirements)} required skills ({skill_coverage:.1f}% coverage)",
                "You have good potential for this role with some skill development",
                "Focusing on the missing skills will significantly improve your competitiveness",
                "Consider applying while continuing to develop missing competencies"
            ])
        elif skill_coverage >= 40:
            professional_insights.extend([
                f"Developing foundation! You possess {len(matching_skills)} of {len(job_requirements)} required skills ({skill_coverage:.1f}% coverage)",
                "This role represents a growth opportunity that requires focused skill development",
                "Prioritize learning the missing skills before applying to maximize success",
                "Consider entry-level positions in related areas to build experience"
            ])
        else:
            professional_insights.extend([
                f"Early stage match! You have {len(matching_skills)} of {len(job_requirements)} required skills ({skill_coverage:.1f}% coverage)",
                "This role is a longer-term career goal requiring significant skill development",
                "Focus on building foundational skills in this domain",
                "Consider this as a 6-12 month development target"
            ])
        
        # Career Recommendations
        career_recommendations = []
        
        # General recommendations
        career_recommendations.extend([
            "Build a portfolio showcasing your existing skills through real projects",
            "Network with professionals in your target industry through LinkedIn and events",
            "Consider informational interviews to learn about day-to-day responsibilities"
        ])
        
        # Skill-specific recommendations
        if missing_skills:
            career_recommendations.append(f"Focus on developing these key skills: {', '.join(missing_skills[:3])}")
            
            # Programming skills
            programming_skills = [skill for skill in missing_skills if any(prog in skill.lower() 
                                 for prog in ['python', 'java', 'javascript', 'sql', 'programming'])]
            if programming_skills:
                career_recommendations.append("Consider online coding bootcamps or courses for programming skills")
                
            # Design skills
            design_skills = [skill for skill in missing_skills if any(design in skill.lower() 
                           for design in ['design', 'figma', 'adobe', 'ui', 'ux'])]
            if design_skills:
                career_recommendations.append("Practice design skills through daily UI challenges and design projects")
                
            # Cloud/DevOps skills
            cloud_skills = [skill for skill in missing_skills if any(cloud in skill.lower() 
                          for cloud in ['aws', 'azure', 'cloud', 'docker', 'kubernetes'])]
            if cloud_skills:
                career_recommendations.append("Start with cloud certification programs and hands-on labs")
        
        # Experience level recommendations
        if skill_coverage < 50:
            career_recommendations.extend([
                "Consider internships or entry-level positions to gain practical experience",
                "Look for mentorship opportunities with experienced professionals"
            ])
        
        # Priority Skills Development
        priority_skills = []
        for i, skill in enumerate(missing_skills[:5]):  # Top 5 missing skills
            priority_level = "High" if i < 2 else "Medium" if i < 4 else "Low"
            estimated_time = self._estimate_learning_time(skill)
            
            priority_skills.append({
                "skill": skill,
                "priority": priority_level,
                "estimated_learning_time": estimated_time,
                "learning_resources": self._suggest_skill_resources(skill),
                "importance_reason": self._explain_skill_importance(skill, job_requirements)
            })
        
        # Suggested Career Paths
        suggested_paths = self._generate_career_progression_paths(candidate_skills, job_requirements)
        
        # Learning Timeline
        learning_timeline = self._calculate_personalized_timeline(missing_skills, skill_coverage)
        
        return {
            "professional_insights": professional_insights,
            "career_recommendations": career_recommendations,
            "skill_breakdown": {
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "skill_match_percentage": round(skill_coverage, 1),
                "total_skills_assessed": len(job_requirements),
                "candidate_skills_count": len(candidate_skills)
            },
            "priority_skills_to_develop": priority_skills,
            "suggested_career_paths": suggested_paths,
            "learning_timeline": learning_timeline
        }
    
    def _estimate_learning_time(self, skill: str) -> str:
        """Estimate learning time for a specific skill."""
        skill_lower = skill.lower()
        
        time_estimates = {
            'python': '2-3 months',
            'javascript': '2-3 months', 
            'sql': '1-2 months',
            'react': '3-4 months',
            'machine learning': '4-6 months',
            'aws': '2-3 months',
            'azure': '2-3 months',
            'docker': '1-2 months',
            'kubernetes': '3-4 months',
            'git': '2-4 weeks',
            'figma': '3-4 weeks',
            'adobe': '2-3 months',
            'communication': 'Ongoing',
            'leadership': 'Ongoing'
        }
        
        for key, time in time_estimates.items():
            if key in skill_lower:
                return time
        
        return '2-3 months'  # Default
    
    def _suggest_skill_resources(self, skill: str) -> List[Dict]:
        """Suggest learning resources for a specific skill."""
        skill_lower = skill.lower()
        
        resources_map = {
            'python': [
                {"type": "Course", "name": "Python for Everybody (Coursera)", "cost": "Free"},
                {"type": "Practice", "name": "LeetCode Python Track", "cost": "Free/Premium"},
                {"type": "Book", "name": "Automate the Boring Stuff", "cost": "$30"}
            ],
            'javascript': [
                {"type": "Course", "name": "JavaScript30 by Wes Bos", "cost": "Free"},
                {"type": "Platform", "name": "freeCodeCamp", "cost": "Free"},
                {"type": "Book", "name": "You Don't Know JS", "cost": "Free online"}
            ],
            'sql': [
                {"type": "Course", "name": "SQL Basics (Khan Academy)", "cost": "Free"},
                {"type": "Practice", "name": "SQLBolt Interactive Lessons", "cost": "Free"},
                {"type": "Platform", "name": "HackerRank SQL", "cost": "Free"}
            ],
            'react': [
                {"type": "Course", "name": "React Official Tutorial", "cost": "Free"},
                {"type": "Course", "name": "React for Beginners (Wes Bos)", "cost": "$97"},
                {"type": "Practice", "name": "React Challenges", "cost": "Free"}
            ],
            'aws': [
                {"type": "Course", "name": "AWS Cloud Practitioner", "cost": "Free tier"},
                {"type": "Platform", "name": "A Cloud Guru", "cost": "$35/month"},
                {"type": "Practice", "name": "AWS Free Tier Labs", "cost": "Free"}
            ]
        }
        
        # Find matching resources
        for key, resources in resources_map.items():
            if key in skill_lower:
                return resources
        
        # Default resources
        return [
            {"type": "Search", "name": f"{skill} online courses", "cost": "Varies"},
            {"type": "Practice", "name": f"{skill} practice projects", "cost": "Free"},
            {"type": "Documentation", "name": f"Official {skill} docs", "cost": "Free"}
        ]
    
    def _explain_skill_importance(self, skill: str, job_requirements: List[str]) -> str:
        """Explain why a skill is important for the job."""
        skill_lower = skill.lower()
        
        importance_map = {
            'python': 'Essential programming language for backend development, data analysis, and automation',
            'javascript': 'Core language for web development and interactive user interfaces',
            'sql': 'Critical for database operations and data manipulation in most technical roles',
            'react': 'Popular frontend framework for building modern web applications',
            'machine learning': 'Key technology for AI-driven features and data insights',
            'aws': 'Leading cloud platform essential for modern application deployment',
            'git': 'Industry standard for version control and collaborative development',
            'communication': 'Essential soft skill for teamwork, presentations, and client interactions',
            'problem solving': 'Core competency for analyzing challenges and developing solutions'
        }
        
        for key, importance in importance_map.items():
            if key in skill_lower:
                return importance
        
        return f"Important skill that enhances job performance and career growth"
    
    def _generate_career_progression_paths(self, candidate_skills: List[str], job_requirements: List[str]) -> List[Dict]:
        """Generate potential career progression paths."""
        
        # Analyze skill categories
        tech_skills = [skill for skill in candidate_skills if any(tech in skill.lower() 
                      for tech in ['python', 'java', 'sql', 'programming', 'development'])]
        
        design_skills = [skill for skill in candidate_skills if any(design in skill.lower() 
                        for design in ['design', 'ui', 'ux', 'figma', 'adobe'])]
        
        data_skills = [skill for skill in candidate_skills if any(data in skill.lower() 
                      for data in ['data', 'analytics', 'sql', 'statistics', 'machine learning'])]
        
        paths = []
        
        # Technology path
        if tech_skills:
            paths.append({
                "path_name": "Software Development Track",
                "description": "Progress through development roles with increasing responsibility",
                "steps": [
                    {"role": "Junior Developer", "timeline": "0-2 years", "skills_needed": ["Basic programming", "Git", "Debugging"]},
                    {"role": "Software Developer", "timeline": "2-4 years", "skills_needed": ["Advanced programming", "System design", "Testing"]},
                    {"role": "Senior Developer", "timeline": "4-6 years", "skills_needed": ["Architecture", "Mentoring", "Technical leadership"]},
                    {"role": "Tech Lead/Architect", "timeline": "6+ years", "skills_needed": ["Strategic thinking", "Team management", "Innovation"]}
                ],
                "growth_potential": "High",
                "average_salary_range": "$60k - $180k+"
            })
        
        # Data path
        if data_skills:
            paths.append({
                "path_name": "Data Science Track",
                "description": "Specialize in data analysis and machine learning",
                "steps": [
                    {"role": "Data Analyst", "timeline": "0-2 years", "skills_needed": ["SQL", "Excel", "Basic statistics"]},
                    {"role": "Data Scientist", "timeline": "2-4 years", "skills_needed": ["Python/R", "Machine learning", "Visualization"]},
                    {"role": "Senior Data Scientist", "timeline": "4-6 years", "skills_needed": ["Deep learning", "Research", "Business strategy"]},
                    {"role": "Chief Data Officer", "timeline": "6+ years", "skills_needed": ["Leadership", "Strategy", "Innovation"]}
                ],
                "growth_potential": "Very High",
                "average_salary_range": "$70k - $200k+"
            })
        
        # Design path
        if design_skills:
            paths.append({
                "path_name": "UX/UI Design Track",
                "description": "Create user-centered design solutions",
                "steps": [
                    {"role": "Junior UX/UI Designer", "timeline": "0-2 years", "skills_needed": ["Design tools", "User research", "Wireframing"]},
                    {"role": "UX/UI Designer", "timeline": "2-4 years", "skills_needed": ["Advanced prototyping", "Design systems", "User testing"]},
                    {"role": "Senior Designer", "timeline": "4-6 years", "skills_needed": ["Design strategy", "Team collaboration", "Innovation"]},
                    {"role": "Design Director", "timeline": "6+ years", "skills_needed": ["Leadership", "Business acumen", "Vision"]}
                ],
                "growth_potential": "High",
                "average_salary_range": "$55k - $150k+"
            })
        
        # Default general path
        if not paths:
            paths.append({
                "path_name": "General Technology Track",
                "description": "Flexible career path adaptable to various technology roles",
                "steps": [
                    {"role": "Entry Level Position", "timeline": "0-1 years", "skills_needed": ["Basic technical skills", "Communication"]},
                    {"role": "Specialist Role", "timeline": "1-3 years", "skills_needed": ["Domain expertise", "Problem solving"]},
                    {"role": "Senior Specialist", "timeline": "3-5 years", "skills_needed": ["Advanced skills", "Mentoring"]},
                    {"role": "Team Lead", "timeline": "5+ years", "skills_needed": ["Leadership", "Strategic thinking"]}
                ],
                "growth_potential": "Medium to High",
                "average_salary_range": "$50k - $130k+"
            })
        
        return paths
    
    def _calculate_personalized_timeline(self, missing_skills: List[str], skill_coverage: float) -> Dict:
        """Calculate personalized learning timeline with milestones."""
        
        # Base timeline calculation
        base_weeks = len(missing_skills) * 6  # 6 weeks per skill average
        
        # Adjust based on current skill coverage
        if skill_coverage >= 70:
            base_weeks *= 0.7  # Faster learning with good foundation
        elif skill_coverage >= 50:
            base_weeks *= 0.85  # Moderate adjustment
        elif skill_coverage < 30:
            base_weeks *= 1.3  # Need more time for foundational learning
        
        timeline_months = max(1, int(base_weeks / 4))
        
        # Generate milestones
        milestones = []
        skills_per_milestone = max(1, len(missing_skills) // 4)
        
        for i in range(min(4, len(missing_skills))):
            milestone_month = int((i + 1) * (timeline_months / 4))
            skills_count = min(skills_per_milestone, len(missing_skills) - i * skills_per_milestone)
            
            milestones.append({
                "month": milestone_month,
                "goal": f"Master {skills_count} priority skill{'s' if skills_count > 1 else ''}",
                "deliverable": f"Complete {skills_count} portfolio project{'s' if skills_count > 1 else ''}",
                "skills_focus": missing_skills[i * skills_per_milestone:(i + 1) * skills_per_milestone]
            })
        
        # Final milestone
        milestones.append({
            "month": timeline_months,
            "goal": "Job application readiness",
            "deliverable": "Complete portfolio, updated resume, and interview preparation",
            "skills_focus": ["All target skills integrated"]
        })
        
        # Confidence assessment
        confidence_level = "High" if skill_coverage >= 70 else \
                          "Medium" if skill_coverage >= 50 else \
                          "Requires dedication"
        
        return {
            "estimated_months": timeline_months,
            "confidence_level": confidence_level,
            "weekly_time_commitment": "10-15 hours recommended",
            "total_learning_hours": base_weeks * 10,  # 10 hours per week
            "milestones": milestones,
            "success_factors": [
                "Consistent daily practice",
                "Building real projects",
                "Seeking feedback from experts",
                "Joining professional communities"
            ]
        }
