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
        Calculate detailed skill gap analysis.
        
        Args:
            candidate_skills: List of candidate skills
            job_requirements: List of job requirements
            
        Returns:
            Dict with gap analysis metrics
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
                'missing_skills_count': 0
            }
        
        skill_coverage = (len(matching_skills) / total_requirements) * 100
        gap_score = (len(missing_skills) / total_requirements) * 100
        
        # Identify critical gaps (high importance skills)
        critical_skills = ['python', 'java', 'sql', 'aws', 'react', 'machine learning']
        critical_gaps = sum(
            1 for skill in missing_skills 
            if any(critical.lower() in skill.lower() for critical in critical_skills)
        )
        
        return {
            'skill_coverage': skill_coverage,
            'gap_score': gap_score,
            'critical_gaps': critical_gaps,
            'matching_skills_count': len(matching_skills),
            'missing_skills_count': len(missing_skills),
            'matching_skills': matching_skills,
            'missing_skills': missing_skills
        }
