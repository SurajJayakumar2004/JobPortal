"""
AI-powered Job Matching Service using ML algorithms for candidate-job compatibility scoring.
This service implements similarity matching, skill scoring, and recommendation algorithms.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Optional, Tuple
import logging
import re
from collections import defaultdict
import math

logger = logging.getLogger(__name__)

class JobMatchingService:
    """Service for AI-powered job matching and candidate recommendation."""
    
    def __init__(self):
        """Initialize the matching service with ML components."""
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.scaler = StandardScaler()
        
        # Skill importance weights for different job levels
        self.skill_weights = {
            "entry_level": {
                "programming_languages": 0.3,
                "frameworks_libraries": 0.2,
                "databases": 0.15,
                "cloud_devops": 0.1,
                "soft_skills": 0.2,
                "tools_technologies": 0.05
            },
            "mid_level": {
                "programming_languages": 0.25,
                "frameworks_libraries": 0.25,
                "databases": 0.2,
                "cloud_devops": 0.15,
                "soft_skills": 0.1,
                "tools_technologies": 0.05
            },
            "senior_level": {
                "programming_languages": 0.2,
                "frameworks_libraries": 0.2,
                "databases": 0.15,
                "cloud_devops": 0.2,
                "soft_skills": 0.15,
                "tools_technologies": 0.1
            }
        }
    
    def extract_job_requirements(self, job_description: str) -> Dict[str, List[str]]:
        """Extract required skills from job description using pattern matching."""
        job_description_lower = job_description.lower()
        
        # Common skill patterns in job descriptions
        skill_patterns = {
            "programming_languages": [
                "python", "java", "javascript", "typescript", "c++", "c#", "php", "ruby",
                "go", "rust", "swift", "kotlin", "scala", "r", "sql"
            ],
            "frameworks_libraries": [
                "react", "angular", "vue", "django", "flask", "fastapi", "express",
                "spring", "rails", "node.js", "tensorflow", "pytorch", "pandas"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "redis", "oracle", "sql server",
                "elasticsearch", "cassandra", "dynamodb"
            ],
            "cloud_devops": [
                "aws", "azure", "google cloud", "docker", "kubernetes", "jenkins",
                "terraform", "ansible", "ci/cd", "microservices"
            ],
            "soft_skills": [
                "leadership", "communication", "teamwork", "problem solving",
                "analytical", "project management", "agile", "scrum"
            ],
            "tools_technologies": [
                "git", "jira", "api", "rest", "graphql", "agile", "scrum",
                "test driven development", "unit testing"
            ]
        }
        
        required_skills = defaultdict(list)
        
        for category, skills in skill_patterns.items():
            for skill in skills:
                if skill in job_description_lower:
                    required_skills[category].append(skill.title())
        
        return dict(required_skills)
    
    def determine_job_level(self, job_description: str, job_title: str) -> str:
        """Determine job level based on title and description."""
        text = f"{job_title} {job_description}".lower()
        
        senior_keywords = ["senior", "lead", "principal", "architect", "manager", "director"]
        entry_keywords = ["junior", "entry", "graduate", "intern", "trainee", "associate"]
        
        if any(keyword in text for keyword in senior_keywords):
            return "senior_level"
        elif any(keyword in text for keyword in entry_keywords):
            return "entry_level"
        else:
            return "mid_level"
    
    def calculate_skill_match_score(self, candidate_skills: Dict[str, List[str]], 
                                  job_requirements: Dict[str, List[str]], 
                                  job_level: str) -> Tuple[float, Dict[str, float]]:
        """Calculate skill match score between candidate and job requirements."""
        weights = self.skill_weights.get(job_level, self.skill_weights["mid_level"])
        
        category_scores = {}
        weighted_total = 0.0
        
        for category, weight in weights.items():
            candidate_category_skills = set(skill.lower() for skill in candidate_skills.get(category, []))
            required_category_skills = set(skill.lower() for skill in job_requirements.get(category, []))
            
            if not required_category_skills:
                # If no requirements in this category, give partial credit
                category_scores[category] = 0.5
            else:
                # Calculate Jaccard similarity
                intersection = len(candidate_category_skills.intersection(required_category_skills))
                union = len(candidate_category_skills.union(required_category_skills))
                
                if union == 0:
                    category_scores[category] = 0.0
                else:
                    jaccard_score = intersection / union
                    # Boost score if candidate has all required skills
                    if intersection == len(required_category_skills):
                        jaccard_score = min(1.0, jaccard_score * 1.2)
                    category_scores[category] = jaccard_score
            
            weighted_total += category_scores[category] * weight
        
        return weighted_total, category_scores
    
    def calculate_experience_match(self, candidate_experience: Optional[int], 
                                 job_requirements: str) -> float:
        """Calculate experience match score."""
        if candidate_experience is None:
            return 0.3  # Default score for unknown experience
        
        # Extract required experience from job description
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*experience',
            r'(\d+)\+?\s*years?\s*of\s*experience',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?'
        ]
        
        required_experience = None
        for pattern in experience_patterns:
            matches = re.findall(pattern, job_requirements.lower())
            if matches:
                required_experience = int(matches[0])
                break
        
        if required_experience is None:
            return 0.7  # Default score when requirements are unclear
        
        # Calculate experience match score
        if candidate_experience >= required_experience:
            # Bonus for exceeding requirements (up to 2x)
            excess_ratio = min(candidate_experience / required_experience, 2.0)
            return min(1.0, 0.8 + (excess_ratio - 1.0) * 0.2)
        else:
            # Penalty for insufficient experience
            return max(0.0, candidate_experience / required_experience)
    
    def calculate_text_similarity(self, candidate_text: str, job_description: str) -> float:
        """Calculate text similarity using TF-IDF and cosine similarity."""
        try:
            # Combine texts for TF-IDF fitting
            texts = [candidate_text, job_description]
            
            # Handle empty texts
            if not candidate_text.strip() or not job_description.strip():
                return 0.0
            
            # Create TF-IDF vectors
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
            
            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            
            return float(similarity_matrix[0][0])
        
        except Exception as e:
            logger.error(f"Error calculating text similarity: {str(e)}")
            return 0.0
    
    def calculate_education_match(self, candidate_education: List[Dict], 
                                job_requirements: str) -> float:
        """Calculate education match score."""
        if not candidate_education:
            return 0.3  # Default score for unknown education
        
        job_req_lower = job_requirements.lower()
        
        # Education level scoring
        education_scores = {
            "bachelor": 0.6,
            "master": 0.8,
            "phd": 1.0,
            "doctorate": 1.0,
            "diploma": 0.4,
            "certificate": 0.3
        }
        
        # Check for education requirements
        requires_masters = "master" in job_req_lower or "m.s." in job_req_lower or "m.a." in job_req_lower
        requires_phd = "phd" in job_req_lower or "doctorate" in job_req_lower
        requires_bachelor = "bachelor" in job_req_lower or "b.s." in job_req_lower or "b.a." in job_req_lower
        
        # Get candidate's highest education level
        candidate_max_score = 0.0
        for edu in candidate_education:
            degree = edu.get("degree", "").lower()
            for edu_type, score in education_scores.items():
                if edu_type in degree:
                    candidate_max_score = max(candidate_max_score, score)
        
        # If no specific requirements, give credit for any education
        if not (requires_masters or requires_phd or requires_bachelor):
            return min(1.0, candidate_max_score + 0.3)
        
        # Calculate match based on requirements
        if requires_phd and candidate_max_score >= education_scores["phd"]:
            return 1.0
        elif requires_masters and candidate_max_score >= education_scores["master"]:
            return 1.0
        elif requires_bachelor and candidate_max_score >= education_scores["bachelor"]:
            return 1.0
        else:
            return candidate_max_score * 0.7  # Partial credit
    
    def calculate_overall_match_score(self, candidate_data: Dict, job_data: Dict) -> Dict:
        """Calculate comprehensive match score between candidate and job."""
        try:
            # Extract job requirements
            job_requirements = self.extract_job_requirements(job_data.get("description", ""))
            job_level = self.determine_job_level(
                job_data.get("description", ""), 
                job_data.get("title", "")
            )
            
            # Calculate individual scores
            skill_score, skill_breakdown = self.calculate_skill_match_score(
                candidate_data.get("skills", {}),
                job_requirements,
                job_level
            )
            
            experience_score = self.calculate_experience_match(
                candidate_data.get("experience_years"),
                job_data.get("description", "")
            )
            
            text_similarity_score = self.calculate_text_similarity(
                candidate_data.get("text", ""),
                job_data.get("description", "")
            )
            
            education_score = self.calculate_education_match(
                candidate_data.get("education", []),
                job_data.get("description", "")
            )
            
            # Weight the different components
            weights = {
                "skills": 0.4,
                "experience": 0.25,
                "text_similarity": 0.2,
                "education": 0.15
            }
            
            # Calculate overall score
            overall_score = (
                skill_score * weights["skills"] +
                experience_score * weights["experience"] +
                text_similarity_score * weights["text_similarity"] +
                education_score * weights["education"]
            )
            
            # Convert to percentage and round
            overall_percentage = round(overall_score * 100, 1)
            
            return {
                "overall_score": overall_percentage,
                "skill_match": round(skill_score * 100, 1),
                "experience_match": round(experience_score * 100, 1),
                "text_similarity": round(text_similarity_score * 100, 1),
                "education_match": round(education_score * 100, 1),
                "skill_breakdown": {k: round(v * 100, 1) for k, v in skill_breakdown.items()},
                "job_level": job_level,
                "required_skills": job_requirements,
                "matching_skills": self._find_matching_skills(
                    candidate_data.get("skills", {}), 
                    job_requirements
                ),
                "missing_skills": self._find_missing_skills(
                    candidate_data.get("skills", {}), 
                    job_requirements
                )
            }
            
        except Exception as e:
            logger.error(f"Error calculating match score: {str(e)}")
            return {
                "overall_score": 0.0,
                "skill_match": 0.0,
                "experience_match": 0.0,
                "text_similarity": 0.0,
                "education_match": 0.0,
                "skill_breakdown": {},
                "job_level": "unknown",
                "required_skills": {},
                "matching_skills": {},
                "missing_skills": {},
                "error": str(e)
            }
    
    def _find_matching_skills(self, candidate_skills: Dict[str, List[str]], 
                            job_requirements: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Find skills that match between candidate and job requirements."""
        matching_skills = {}
        
        for category in job_requirements:
            candidate_category_skills = set(skill.lower() for skill in candidate_skills.get(category, []))
            required_category_skills = set(skill.lower() for skill in job_requirements[category])
            
            matches = candidate_category_skills.intersection(required_category_skills)
            if matches:
                matching_skills[category] = [skill.title() for skill in matches]
        
        return matching_skills
    
    def _find_missing_skills(self, candidate_skills: Dict[str, List[str]], 
                           job_requirements: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Find skills that are required but missing from candidate."""
        missing_skills = {}
        
        for category, required_skills in job_requirements.items():
            candidate_category_skills = set(skill.lower() for skill in candidate_skills.get(category, []))
            required_category_skills = set(skill.lower() for skill in required_skills)
            
            missing = required_category_skills - candidate_category_skills
            if missing:
                missing_skills[category] = [skill.title() for skill in missing]
        
        return missing_skills
    
    def rank_candidates_for_job(self, candidates: List[Dict], job_data: Dict) -> List[Dict]:
        """Rank candidates for a specific job based on match scores."""
        ranked_candidates = []
        
        for candidate in candidates:
            match_result = self.calculate_overall_match_score(candidate, job_data)
            
            ranked_candidates.append({
                "candidate_id": candidate.get("id"),
                "candidate_data": candidate,
                "match_score": match_result["overall_score"],
                "match_details": match_result
            })
        
        # Sort by match score (descending)
        ranked_candidates.sort(key=lambda x: x["match_score"], reverse=True)
        
        return ranked_candidates
    
    def recommend_jobs_for_candidate(self, candidate_data: Dict, jobs: List[Dict], 
                                   top_n: int = 10) -> List[Dict]:
        """Recommend top matching jobs for a candidate."""
        job_matches = []
        
        for job in jobs:
            match_result = self.calculate_overall_match_score(candidate_data, job)
            
            job_matches.append({
                "job_id": job.get("id"),
                "job_data": job,
                "match_score": match_result["overall_score"],
                "match_details": match_result
            })
        
        # Sort by match score (descending) and return top N
        job_matches.sort(key=lambda x: x["match_score"], reverse=True)
        
        return job_matches[:top_n]

# Global instance
job_matching_service = JobMatchingService()
