"""
AI-powered Career Counseling Service providing personalized career guidance,
skill gap analysis, and career path recommendations using ML algorithms.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from typing import List, Dict, Optional, Tuple
import logging
from collections import defaultdict, Counter
import re

logger = logging.getLogger(__name__)

class CareerCounselingService:
    """AI-powered service for career counseling and guidance."""
    
    def __init__(self):
        """Initialize the career counseling service."""
        
        # Career progression paths for different domains
        self.career_paths = {
            "software_development": {
                "entry_level": ["Junior Developer", "Software Engineer I", "Trainee Developer"],
                "mid_level": ["Software Engineer", "Full Stack Developer", "Backend Developer", "Frontend Developer"],
                "senior_level": ["Senior Software Engineer", "Lead Developer", "Principal Engineer"],
                "management": ["Engineering Manager", "Technical Lead", "VP Engineering"],
                "specialist": ["Software Architect", "System Architect", "Technical Consultant"]
            },
            "data_science": {
                "entry_level": ["Data Analyst", "Junior Data Scientist", "Business Analyst"],
                "mid_level": ["Data Scientist", "ML Engineer", "Analytics Engineer"],
                "senior_level": ["Senior Data Scientist", "Lead Data Scientist", "Principal Data Scientist"],
                "management": ["Data Science Manager", "Analytics Manager", "Chief Data Officer"],
                "specialist": ["ML Architect", "Data Science Consultant", "Research Scientist"]
            },
            "devops_cloud": {
                "entry_level": ["DevOps Engineer", "Cloud Support Engineer", "System Administrator"],
                "mid_level": ["Cloud Engineer", "Site Reliability Engineer", "Infrastructure Engineer"],
                "senior_level": ["Senior DevOps Engineer", "Lead SRE", "Principal Cloud Architect"],
                "management": ["DevOps Manager", "Infrastructure Manager", "Platform Engineering Manager"],
                "specialist": ["Cloud Architect", "Security Architect", "DevOps Consultant"]
            },
            "product_management": {
                "entry_level": ["Associate Product Manager", "Product Analyst", "Business Analyst"],
                "mid_level": ["Product Manager", "Technical Product Manager", "Senior Business Analyst"],
                "senior_level": ["Senior Product Manager", "Principal Product Manager", "Group Product Manager"],
                "management": ["Director of Product", "VP Product", "Chief Product Officer"],
                "specialist": ["Product Strategy Consultant", "Product Design Lead", "Growth Product Manager"]
            },
            "cybersecurity": {
                "entry_level": ["Security Analyst", "Junior Security Engineer", "SOC Analyst"],
                "mid_level": ["Security Engineer", "Cybersecurity Specialist", "Penetration Tester"],
                "senior_level": ["Senior Security Engineer", "Lead Security Architect", "Principal Security Engineer"],
                "management": ["Security Manager", "CISO", "Security Director"],
                "specialist": ["Security Consultant", "Ethical Hacker", "Incident Response Specialist"]
            }
        }
        
        # Skill requirements for different career levels
        self.level_skill_requirements = {
            "entry_level": {
                "min_skills": 5,
                "key_areas": ["programming_languages", "soft_skills"],
                "experience_years": 0
            },
            "mid_level": {
                "min_skills": 10,
                "key_areas": ["programming_languages", "frameworks_libraries", "databases"],
                "experience_years": 2
            },
            "senior_level": {
                "min_skills": 15,
                "key_areas": ["programming_languages", "frameworks_libraries", "databases", "cloud_devops"],
                "experience_years": 5
            },
            "management": {
                "min_skills": 12,
                "key_areas": ["soft_skills", "tools_technologies"],
                "experience_years": 7
            },
            "specialist": {
                "min_skills": 20,
                "key_areas": ["programming_languages", "frameworks_libraries", "cloud_devops", "tools_technologies"],
                "experience_years": 8
            }
        }
        
        # Industry growth trends and salary information (simplified)
        self.industry_trends = {
            "software_development": {
                "growth_rate": "high",
                "avg_salary_range": "$70k-$180k",
                "hot_skills": ["React", "Python", "Kubernetes", "Microservices", "AI/ML"],
                "market_demand": "very_high"
            },
            "data_science": {
                "growth_rate": "very_high",
                "avg_salary_range": "$85k-$200k",
                "hot_skills": ["Python", "TensorFlow", "PyTorch", "SQL", "Cloud Platforms"],
                "market_demand": "high"
            },
            "devops_cloud": {
                "growth_rate": "high",
                "avg_salary_range": "$80k-$170k",
                "hot_skills": ["AWS", "Docker", "Kubernetes", "Terraform", "Jenkins"],
                "market_demand": "high"
            },
            "cybersecurity": {
                "growth_rate": "very_high",
                "avg_salary_range": "$75k-$190k",
                "hot_skills": ["Ethical Hacking", "Cloud Security", "Zero Trust", "SIEM"],
                "market_demand": "very_high"
            }
        }
    
    def identify_career_domain(self, candidate_skills: Dict[str, List[str]], 
                              experience_years: Optional[int] = None) -> str:
        """Identify the most likely career domain based on candidate skills."""
        
        domain_scores = {}
        
        # Scoring based on skill patterns
        skill_patterns = {
            "software_development": {
                "programming_languages": 0.4,
                "frameworks_libraries": 0.3,
                "databases": 0.2,
                "tools_technologies": 0.1
            },
            "data_science": {
                "programming_languages": 0.3,  # Python, R
                "frameworks_libraries": 0.4,   # ML libraries
                "databases": 0.2,
                "tools_technologies": 0.1
            },
            "devops_cloud": {
                "cloud_devops": 0.5,
                "programming_languages": 0.2,
                "tools_technologies": 0.2,
                "databases": 0.1
            },
            "cybersecurity": {
                "cloud_devops": 0.3,
                "tools_technologies": 0.4,
                "programming_languages": 0.2,
                "soft_skills": 0.1
            },
            "product_management": {
                "soft_skills": 0.5,
                "tools_technologies": 0.3,
                "frameworks_libraries": 0.1,
                "programming_languages": 0.1
            }
        }
        
        for domain, weights in skill_patterns.items():
            score = 0.0
            for skill_category, weight in weights.items():
                skill_count = len(candidate_skills.get(skill_category, []))
                score += skill_count * weight
            
            domain_scores[domain] = score
        
        # Return domain with highest score
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        else:
            return "software_development"  # Default
    
    def assess_current_level(self, candidate_skills: Dict[str, List[str]], 
                           experience_years: Optional[int] = None,
                           education: List[Dict] = None) -> str:
        """Assess candidate's current career level."""
        
        total_skills = sum(len(skills) for skills in candidate_skills.values())
        experience = experience_years or 0
        
        # Education bonus
        education_bonus = 0
        if education:
            for edu in education:
                degree = edu.get("degree", "").lower()
                if "master" in degree or "phd" in degree:
                    education_bonus = 2
                elif "bachelor" in degree:
                    education_bonus = 1
        
        # Determine level based on skills and experience
        adjusted_experience = experience + education_bonus
        
        if total_skills >= 20 and adjusted_experience >= 8:
            return "specialist"
        elif total_skills >= 12 and adjusted_experience >= 7:
            return "management"
        elif total_skills >= 15 and adjusted_experience >= 5:
            return "senior_level"
        elif total_skills >= 10 and adjusted_experience >= 2:
            return "mid_level"
        else:
            return "entry_level"
    
    def analyze_skill_gaps(self, candidate_skills: Dict[str, List[str]], 
                          target_domain: str, target_level: str) -> Dict:
        """Analyze skill gaps for target career path."""
        
        requirements = self.level_skill_requirements.get(target_level, {})
        min_skills = requirements.get("min_skills", 0)
        key_areas = requirements.get("key_areas", [])
        
        current_total_skills = sum(len(skills) for skills in candidate_skills.values())
        
        # Calculate gaps in key areas
        skill_gaps = {}
        for area in key_areas:
            current_count = len(candidate_skills.get(area, []))
            recommended_count = max(3, min_skills // len(key_areas)) if key_areas else 3
            
            if current_count < recommended_count:
                skill_gaps[area] = {
                    "current": current_count,
                    "recommended": recommended_count,
                    "gap": recommended_count - current_count
                }
        
        # Recommend specific skills based on domain and industry trends
        recommended_skills = self._get_recommended_skills(target_domain, target_level)
        
        return {
            "total_skill_gap": max(0, min_skills - current_total_skills),
            "area_gaps": skill_gaps,
            "recommended_skills": recommended_skills,
            "priority_areas": key_areas,
            "readiness_score": min(100, (current_total_skills / min_skills) * 100) if min_skills > 0 else 100
        }
    
    def _get_recommended_skills(self, domain: str, level: str) -> Dict[str, List[str]]:
        """Get recommended skills for specific domain and level."""
        
        skill_recommendations = {
            "software_development": {
                "entry_level": {
                    "programming_languages": ["Python", "JavaScript", "SQL"],
                    "frameworks_libraries": ["React", "Node.js", "Express"],
                    "tools_technologies": ["Git", "API", "Agile"]
                },
                "mid_level": {
                    "programming_languages": ["TypeScript", "Java", "Python"],
                    "frameworks_libraries": ["React", "Spring Boot", "Django"],
                    "databases": ["PostgreSQL", "MongoDB", "Redis"],
                    "cloud_devops": ["Docker", "AWS", "CI/CD"]
                },
                "senior_level": {
                    "programming_languages": ["Python", "Java", "Go"],
                    "frameworks_libraries": ["Microservices", "Spring Boot", "React"],
                    "cloud_devops": ["Kubernetes", "AWS", "Terraform"],
                    "tools_technologies": ["System Design", "Architecture", "Code Review"]
                }
            },
            "data_science": {
                "entry_level": {
                    "programming_languages": ["Python", "SQL", "R"],
                    "frameworks_libraries": ["Pandas", "NumPy", "Matplotlib"],
                    "tools_technologies": ["Jupyter", "Excel", "Statistics"]
                },
                "mid_level": {
                    "programming_languages": ["Python", "SQL", "Scala"],
                    "frameworks_libraries": ["Scikit-learn", "TensorFlow", "Keras"],
                    "cloud_devops": ["AWS", "Docker", "Airflow"],
                    "tools_technologies": ["MLOps", "A/B Testing", "Feature Engineering"]
                }
            }
        }
        
        return skill_recommendations.get(domain, {}).get(level, {})
    
    def generate_learning_path(self, skill_gaps: Dict, timeframe_months: int = 6) -> List[Dict]:
        """Generate a personalized learning path to address skill gaps."""
        
        learning_path = []
        total_gap = skill_gaps.get("total_skill_gap", 0)
        area_gaps = skill_gaps.get("area_gaps", {})
        recommended_skills = skill_gaps.get("recommended_skills", {})
        
        # Prioritize areas with largest gaps
        sorted_areas = sorted(area_gaps.items(), key=lambda x: x[1]["gap"], reverse=True)
        
        months_per_area = max(1, timeframe_months // max(1, len(sorted_areas)))
        
        for i, (area, gap_info) in enumerate(sorted_areas):
            skills_to_learn = recommended_skills.get(area, [])[:gap_info["gap"]]
            
            if skills_to_learn:
                learning_path.append({
                    "phase": i + 1,
                    "timeframe": f"Months {i * months_per_area + 1}-{(i + 1) * months_per_area}",
                    "focus_area": area.replace("_", " ").title(),
                    "skills_to_learn": skills_to_learn,
                    "estimated_hours": gap_info["gap"] * 40,  # 40 hours per skill
                    "learning_resources": self._get_learning_resources(area, skills_to_learn),
                    "milestones": self._generate_milestones(skills_to_learn)
                })
        
        return learning_path
    
    def _get_learning_resources(self, area: str, skills: List[str]) -> List[Dict]:
        """Get learning resources for specific skills."""
        
        resource_templates = {
            "programming_languages": [
                {"type": "online_course", "platform": "Coursera", "focus": "fundamentals"},
                {"type": "practice", "platform": "LeetCode", "focus": "coding_problems"},
                {"type": "documentation", "platform": "Official Docs", "focus": "syntax_reference"}
            ],
            "frameworks_libraries": [
                {"type": "tutorial", "platform": "YouTube", "focus": "hands_on_projects"},
                {"type": "online_course", "platform": "Udemy", "focus": "practical_applications"},
                {"type": "practice", "platform": "GitHub", "focus": "open_source_projects"}
            ],
            "cloud_devops": [
                {"type": "certification", "platform": "AWS/Azure", "focus": "cloud_fundamentals"},
                {"type": "hands_on", "platform": "Cloud Labs", "focus": "practical_experience"},
                {"type": "book", "platform": "Technical Books", "focus": "best_practices"}
            ]
        }
        
        return resource_templates.get(area, [
            {"type": "online_search", "platform": "Google", "focus": "skill_specific_resources"}
        ])
    
    def _generate_milestones(self, skills: List[str]) -> List[str]:
        """Generate learning milestones for skills."""
        milestones = []
        
        for i, skill in enumerate(skills):
            milestones.extend([
                f"Complete basic {skill} tutorial",
                f"Build a simple project using {skill}",
                f"Pass a {skill} assessment test"
            ])
        
        return milestones[:6]  # Limit to 6 milestones per phase
    
    def get_career_recommendations(self, candidate_data: Dict) -> Dict:
        """Generate comprehensive career recommendations."""
        
        skills = candidate_data.get("skills", {})
        experience_years = candidate_data.get("experience_years")
        education = candidate_data.get("education", [])
        
        # Identify current state
        current_domain = self.identify_career_domain(skills, experience_years)
        current_level = self.assess_current_level(skills, experience_years, education)
        
        # Get possible next steps
        career_paths = self.career_paths.get(current_domain, {})
        current_roles = career_paths.get(current_level, [])
        
        # Determine next level
        level_progression = ["entry_level", "mid_level", "senior_level", "management", "specialist"]
        current_index = level_progression.index(current_level) if current_level in level_progression else 0
        
        next_level = level_progression[min(current_index + 1, len(level_progression) - 1)]
        next_roles = career_paths.get(next_level, [])
        
        # Analyze skill gaps for next level
        skill_gaps = self.analyze_skill_gaps(skills, current_domain, next_level)
        
        # Generate learning path
        learning_path = self.generate_learning_path(skill_gaps)
        
        # Get industry insights
        industry_info = self.industry_trends.get(current_domain, {})
        
        return {
            "current_assessment": {
                "domain": current_domain.replace("_", " ").title(),
                "level": current_level.replace("_", " ").title(),
                "suitable_roles": current_roles
            },
            "next_step": {
                "target_level": next_level.replace("_", " ").title(),
                "target_roles": next_roles,
                "readiness_score": skill_gaps.get("readiness_score", 0)
            },
            "skill_analysis": skill_gaps,
            "learning_path": learning_path,
            "industry_insights": {
                "growth_outlook": industry_info.get("growth_rate", "moderate"),
                "salary_range": industry_info.get("avg_salary_range", "varies"),
                "in_demand_skills": industry_info.get("hot_skills", []),
                "market_demand": industry_info.get("market_demand", "moderate")
            },
            "recommendations": self._generate_action_items(skill_gaps, learning_path)
        }
    
    def _generate_action_items(self, skill_gaps: Dict, learning_path: List[Dict]) -> List[str]:
        """Generate actionable recommendations."""
        
        recommendations = []
        
        # Immediate actions
        if skill_gaps.get("total_skill_gap", 0) > 0:
            recommendations.append(f"Focus on developing {skill_gaps['total_skill_gap']} additional skills")
        
        # Priority areas
        priority_areas = skill_gaps.get("priority_areas", [])
        if priority_areas:
            recommendations.append(f"Prioritize learning in: {', '.join(priority_areas)}")
        
        # Learning path actions
        if learning_path:
            first_phase = learning_path[0]
            recommendations.append(f"Start with {first_phase['focus_area']} - learn {', '.join(first_phase['skills_to_learn'][:3])}")
        
        # Readiness assessment
        readiness = skill_gaps.get("readiness_score", 0)
        if readiness < 70:
            recommendations.append("Consider building more foundational skills before advancing")
        elif readiness > 85:
            recommendations.append("You're ready to apply for advanced positions!")
        
        return recommendations

# Global instance
career_counseling_service = CareerCounselingService()
