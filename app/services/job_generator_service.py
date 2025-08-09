"""
Job Generator Service - Creates detailed job descriptions from structured data.

This service processes JSON job data and generates comprehensive job descriptions
with personalized recommendations for students based on their resumes and profiles.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
import uuid

from app.schemas import JobPosting
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobGeneratorService:
    """Service for generating detailed job descriptions and personalized recommendations."""
    
    def __init__(self):
        """Initialize the job generator service."""
        self.job_templates = {}
        self.career_paths = {
            "Technology": {
                "entry_level": ["Junior Python Developer", "UX/UI Designer"],
                "mid_level": ["Product Manager", "Data Engineer", "Cybersecurity Analyst"],
                "senior_level": ["Senior DevOps Engineer", "Data Scientist", "Cloud Architect"]
            },
            "Marketing": {
                "entry_level": ["Digital Marketing Specialist"],
                "mid_level": ["Marketing Manager", "Content Marketing Manager"],
                "senior_level": ["Marketing Director", "Chief Marketing Officer"]
            },
            "Healthcare": {
                "entry_level": ["Registered Nurse"],
                "mid_level": ["Nurse Practitioner", "Physician Assistant"],
                "senior_level": ["Chief Nursing Officer", "Medical Director"]
            }
        }
    
    def generate_job_description(self, job_data: Dict) -> Dict:
        """
        Generate a comprehensive job description from structured job data.
        
        Args:
            job_data: Dictionary containing job title, industry, skills, and certifications
            
        Returns:
            Dict: Complete job posting with description and requirements
        """
        job_title = job_data.get("jobTitle", "")
        industry = job_data.get("industry", "")
        skill_keywords = job_data.get("skillKeywords", [])
        required_certifications = job_data.get("requiredCertifications", [])
        
        # Generate job summary
        job_summary = self._generate_job_summary(job_title, industry, skill_keywords)
        
        # Generate key responsibilities
        key_responsibilities = self._generate_key_responsibilities(job_title, skill_keywords)
        
        # Generate full job description
        job_description = self._compile_job_description(
            job_title, industry, job_summary, key_responsibilities, 
            skill_keywords, required_certifications
        )
        
        # Determine experience level and salary range
        experience_level = self._determine_experience_level(job_title)
        salary_range = self._estimate_salary_range(job_title, experience_level)
        
        return {
            "id": str(uuid.uuid4()),
            "title": job_title,
            "company": "TechCorp Solutions",  # Default company name
            "location": "Remote / San Francisco, CA",
            "employment_type": "Full-time",
            "industry": industry,
            "description": job_description,
            "requirements": skill_keywords,
            "required_certifications": required_certifications,
            "experience_level": experience_level,
            "salary_min": salary_range["min"],
            "salary_max": salary_range["max"],
            "benefits": self._generate_benefits(experience_level),
            "posted_date": datetime.now().isoformat(),
            "application_deadline": self._get_application_deadline(),
            "is_remote": True,
            "skills_breakdown": self._categorize_skills(skill_keywords),
            "career_growth_path": self._generate_career_path(job_title, industry)
        }
    
    def _generate_job_summary(self, job_title: str, industry: str, skills: List[str]) -> str:
        """Generate a compelling job summary based on role and skills."""
        
        summaries = {
            "Junior Python Developer": f"We are seeking a motivated Junior Python Developer to join our dynamic {industry.lower()} team. The ideal candidate will have foundational programming skills and a passion for learning cutting-edge technologies. This role offers excellent opportunities for professional growth and mentorship from senior developers.",
            
            "UX/UI Designer": f"Join our creative team as a UX/UI Designer where you'll craft intuitive and visually stunning user experiences. We're looking for a designer who combines user research insights with aesthetic excellence to create products that users love. This role is perfect for someone passionate about human-centered design.",
            
            "Product Manager": f"We're seeking a strategic Product Manager to drive product development and innovation in our {industry.lower()} division. The ideal candidate will bridge the gap between technical teams and business stakeholders, using data-driven insights to build products that solve real user problems.",
            
            "Senior DevOps Engineer": f"Lead our infrastructure and deployment strategies as a Senior DevOps Engineer. We need an experienced professional who can architect scalable solutions, implement robust CI/CD pipelines, and foster a culture of automation and reliability across our engineering teams.",
            
            "Digital Marketing Specialist": f"Drive our digital presence as a Marketing Specialist focused on growth and engagement. We're looking for a data-driven marketer who can create compelling campaigns across multiple channels and optimize performance through continuous testing and analysis.",
            
            "Data Scientist": f"Unlock insights from complex datasets as our Data Scientist. We need someone who can transform raw data into actionable business intelligence using advanced analytics, machine learning, and statistical modeling to drive strategic decision-making.",
            
            "Registered Nurse": f"Provide compassionate, evidence-based patient care as a Registered Nurse in our healthcare facility. We're seeking a dedicated professional committed to patient safety, clinical excellence, and collaborative care delivery in a supportive environment.",
            
            "Data Engineer": f"Build and maintain the data infrastructure that powers our analytics and machine learning initiatives. We're looking for a Data Engineer who can design robust data pipelines, optimize performance, and ensure data quality across our organization.",
            
            "Cybersecurity Analyst": f"Protect our digital assets as a Cybersecurity Analyst focused on threat detection and incident response. We need a security professional who can identify vulnerabilities, monitor threats, and implement security measures to safeguard our systems and data.",
            
            "Cloud Architect": f"Design and implement scalable cloud solutions as our Cloud Architect. We're seeking an experienced professional who can architect secure, cost-effective cloud infrastructure that supports our business growth and innovation objectives."
        }
        
        return summaries.get(job_title, f"Join our {industry.lower()} team as a {job_title} and contribute to innovative projects using {', '.join(skills[:3])} and other cutting-edge technologies.")
    
    def _generate_key_responsibilities(self, job_title: str, skills: List[str]) -> List[str]:
        """Generate key responsibilities based on job title and required skills."""
        
        responsibility_templates = {
            "Junior Python Developer": [
                "Develop and maintain Python applications using best practices and coding standards",
                "Write comprehensive unit tests to ensure code quality and reliability",
                "Collaborate with senior developers on debugging and troubleshooting issues",
                "Implement REST APIs and integrate with third-party services",
                "Participate in code reviews and contribute to documentation",
                "Work with version control systems (Git) for collaborative development",
                "Support database operations and basic SQL query optimization"
            ],
            
            "UX/UI Designer": [
                "Conduct user research and usability testing to inform design decisions",
                "Create wireframes, prototypes, and high-fidelity mockups using Figma and Adobe XD",
                "Design intuitive user interfaces that align with brand guidelines and accessibility standards",
                "Collaborate with product managers and developers to implement design solutions",
                "Develop and maintain design systems and component libraries",
                "Analyze user feedback and iterate on designs to improve user experience",
                "Present design concepts and rationale to stakeholders"
            ],
            
            "Product Manager": [
                "Define product roadmaps and prioritize features based on user needs and business goals",
                "Write detailed user stories and acceptance criteria for development teams",
                "Conduct market research and competitive analysis to identify opportunities",
                "Manage stakeholder relationships and facilitate cross-functional collaboration",
                "Analyze product metrics and user data to drive data-driven decision making",
                "Lead agile ceremonies including sprint planning and retrospectives",
                "Coordinate product launches and go-to-market strategies"
            ],
            
            "Senior DevOps Engineer": [
                "Design and implement CI/CD pipelines for automated testing and deployment",
                "Manage cloud infrastructure using Infrastructure as Code (Terraform, Ansible)",
                "Orchestrate containerized applications using Kubernetes and Docker",
                "Monitor system performance and implement logging solutions for troubleshooting",
                "Implement security best practices and compliance standards",
                "Automate routine tasks through scripting (Python, Bash)",
                "Mentor junior team members and establish DevOps best practices"
            ],
            
            "Digital Marketing Specialist": [
                "Develop and execute SEO strategies to improve organic search rankings",
                "Create and manage paid advertising campaigns across Google Ads and social platforms",
                "Analyze campaign performance using Google Analytics and other marketing tools",
                "Produce engaging content for email marketing campaigns and social media",
                "Conduct A/B testing to optimize conversion rates and campaign effectiveness",
                "Collaborate with design and content teams to create marketing materials",
                "Track ROI and report on marketing KPIs to stakeholders"
            ],
            
            "Data Scientist": [
                "Develop machine learning models to solve complex business problems",
                "Perform statistical analysis and data visualization to communicate insights",
                "Clean and preprocess large datasets using Python, R, and SQL",
                "Build predictive models using scikit-learn, TensorFlow, and other ML frameworks",
                "Create interactive dashboards and reports using Tableau and other BI tools",
                "Collaborate with engineering teams to deploy models into production",
                "Present findings and recommendations to business stakeholders"
            ],
            
            "Registered Nurse": [
                "Provide direct patient care including assessment, medication administration, and monitoring",
                "Document patient information accurately in electronic health records (EHR)",
                "Collaborate with physicians and healthcare team members to develop care plans",
                "Educate patients and families about health conditions and treatment options",
                "Perform wound care, IV therapy, and other clinical procedures",
                "Respond to medical emergencies and provide critical care as needed",
                "Maintain compliance with healthcare regulations and safety protocols"
            ],
            
            "Data Engineer": [
                "Design and build scalable data pipelines for ETL/ELT processes",
                "Develop and maintain data warehouse solutions on cloud platforms",
                "Optimize database performance and ensure data quality and integrity",
                "Implement big data solutions using Hadoop, Spark, and other technologies",
                "Automate data processing workflows and monitoring systems",
                "Collaborate with data scientists to support analytics and ML initiatives",
                "Establish data governance and security best practices"
            ],
            
            "Cybersecurity Analyst": [
                "Monitor security systems and analyze threats using SIEM tools",
                "Conduct risk assessments and vulnerability analyses",
                "Respond to security incidents and perform forensic investigations",
                "Implement and maintain security controls including firewalls and encryption",
                "Develop security policies and procedures to ensure compliance",
                "Perform penetration testing and security audits",
                "Provide security awareness training to staff and stakeholders"
            ],
            
            "Cloud Architect": [
                "Design scalable and secure cloud infrastructure solutions",
                "Optimize cloud costs through resource planning and monitoring",
                "Implement DevOps practices and automation for cloud deployments",
                "Ensure compliance with security and governance requirements",
                "Evaluate and recommend cloud services and technologies",
                "Provide technical leadership and guidance to development teams",
                "Create architecture documentation and best practice guidelines"
            ]
        }
        
        return responsibility_templates.get(job_title, [
            f"Utilize {skills[0]} to accomplish key objectives",
            f"Apply {skills[1] if len(skills) > 1 else 'relevant skills'} in daily operations",
            "Collaborate with cross-functional teams to deliver results",
            "Contribute to continuous improvement initiatives"
        ])
    
    def _compile_job_description(self, title: str, industry: str, summary: str, 
                               responsibilities: List[str], skills: List[str], 
                               certifications: List[str]) -> str:
        """Compile all components into a formatted job description."""
        
        description = f"""
**Job Title:** {title}
**Industry:** {industry}

**Job Summary:**
{summary}

**Key Responsibilities:**
{chr(10).join([f"• {resp}" for resp in responsibilities])}

**Required Skills and Qualifications:**
{chr(10).join([f"• {skill}" for skill in skills])}

**Required Certifications:**
{chr(10).join([f"• {cert}" for cert in certifications])}

**What We Offer:**
• Competitive salary and comprehensive benefits package
• Professional development and certification support
• Flexible work arrangements and remote work options
• Collaborative and inclusive work environment
• Opportunities for career advancement and skill development
        """.strip()
        
        return description
    
    def _determine_experience_level(self, job_title: str) -> str:
        """Determine experience level based on job title."""
        title_lower = job_title.lower()
        
        if any(keyword in title_lower for keyword in ["junior", "entry", "associate", "trainee"]):
            return "Entry Level"
        elif any(keyword in title_lower for keyword in ["senior", "lead", "principal", "architect"]):
            return "Senior Level"
        else:
            return "Mid Level"
    
    def _estimate_salary_range(self, job_title: str, experience_level: str) -> Dict[str, int]:
        """Estimate salary range based on job title and experience level."""
        
        base_salaries = {
            "Junior Python Developer": {"Entry Level": (60000, 80000)},
            "UX/UI Designer": {"Entry Level": (65000, 85000), "Mid Level": (85000, 120000)},
            "Product Manager": {"Mid Level": (100000, 140000), "Senior Level": (140000, 180000)},
            "Senior DevOps Engineer": {"Senior Level": (120000, 160000)},
            "Digital Marketing Specialist": {"Entry Level": (45000, 65000), "Mid Level": (65000, 90000)},
            "Data Scientist": {"Mid Level": (90000, 130000), "Senior Level": (130000, 180000)},
            "Registered Nurse": {"Entry Level": (60000, 75000), "Mid Level": (75000, 90000)},
            "Data Engineer": {"Mid Level": (95000, 130000), "Senior Level": (130000, 170000)},
            "Cybersecurity Analyst": {"Mid Level": (80000, 110000), "Senior Level": (110000, 150000)},
            "Cloud Architect": {"Senior Level": (130000, 180000)}
        }
        
        salary_range = base_salaries.get(job_title, {}).get(experience_level, (50000, 80000))
        return {"min": salary_range[0], "max": salary_range[1]}
    
    def _generate_benefits(self, experience_level: str) -> List[str]:
        """Generate benefits package based on experience level."""
        
        base_benefits = [
            "Health, dental, and vision insurance",
            "401(k) with company matching",
            "Paid time off and holidays",
            "Professional development budget"
        ]
        
        if experience_level in ["Mid Level", "Senior Level"]:
            base_benefits.extend([
                "Stock options or equity participation",
                "Flexible work arrangements",
                "Conference attendance support"
            ])
        
        if experience_level == "Senior Level":
            base_benefits.extend([
                "Leadership development programs",
                "Sabbatical opportunities",
                "Executive coaching"
            ])
        
        return base_benefits
    
    def _get_application_deadline(self) -> str:
        """Generate application deadline (30 days from now)."""
        from datetime import datetime, timedelta
        deadline = datetime.now() + timedelta(days=30)
        return deadline.isoformat()
    
    def _categorize_skills(self, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into technical and soft skills."""
        
        technical_keywords = [
            "python", "java", "sql", "javascript", "react", "aws", "azure", "docker", 
            "kubernetes", "git", "machine learning", "data", "api", "database", "cloud",
            "figma", "adobe", "analytics", "testing", "security", "networking"
        ]
        
        technical_skills = []
        soft_skills = []
        
        for skill in skills:
            skill_lower = skill.lower()
            if any(tech in skill_lower for tech in technical_keywords):
                technical_skills.append(skill)
            else:
                soft_skills.append(skill)
        
        return {
            "technical": technical_skills,
            "soft": soft_skills
        }
    
    def _generate_career_path(self, job_title: str, industry: str) -> List[str]:
        """Generate potential career progression paths."""
        
        career_progressions = {
            "Junior Python Developer": [
                "Python Developer",
                "Senior Python Developer", 
                "Lead Developer",
                "Software Architect"
            ],
            "UX/UI Designer": [
                "Senior UX/UI Designer",
                "Lead Designer",
                "Design Manager",
                "Head of Design"
            ],
            "Product Manager": [
                "Senior Product Manager",
                "Principal Product Manager",
                "Director of Product",
                "VP of Product"
            ],
            "Digital Marketing Specialist": [
                "Senior Marketing Specialist",
                "Marketing Manager",
                "Marketing Director",
                "CMO"
            ]
        }
        
        return career_progressions.get(job_title, [
            f"Senior {job_title}",
            f"Lead {job_title}",
            f"{job_title} Manager"
        ])
    
    def generate_personalized_insights(self, student_resume: Dict, job_data: Dict) -> Dict:
        """
        Generate personalized career insights for a student based on their resume and target job.
        
        Args:
            student_resume: Student's resume data and skills
            job_data: Target job information
            
        Returns:
            Dict: Personalized insights and recommendations
        """
        student_skills = student_resume.get("skills", [])
        student_experience = student_resume.get("experience_level", "Entry Level")
        required_skills = job_data.get("skillKeywords", [])
        job_title = job_data.get("jobTitle", "")
        
        # Analyze skill gaps
        matching_skills = [skill for skill in student_skills if skill in required_skills]
        missing_skills = [skill for skill in required_skills if skill not in student_skills]
        
        # Generate personalized recommendations
        insights = {
            "professional_insights": self._generate_professional_insights(
                student_skills, matching_skills, missing_skills, job_title
            ),
            "career_recommendations": self._generate_career_recommendations(
                student_experience, job_title, matching_skills
            ),
            "skill_breakdown": {
                "matching_skills": matching_skills,
                "missing_skills": missing_skills,
                "skill_match_percentage": (len(matching_skills) / len(required_skills)) * 100 if required_skills else 0
            },
            "suggested_career_paths": self._generate_personalized_career_paths(
                student_skills, student_experience, job_data.get("industry")
            ),
            "priority_skills_to_develop": self._prioritize_skill_development(
                missing_skills, job_title
            ),
            "learning_resources": self._suggest_learning_resources(missing_skills),
            "timeline_to_readiness": self._estimate_readiness_timeline(
                len(missing_skills), student_experience
            )
        }
        
        return insights
    
    def _generate_professional_insights(self, student_skills: List[str], matching_skills: List[str], 
                                      missing_skills: List[str], job_title: str) -> List[str]:
        """Generate professional insights based on skill analysis."""
        
        insights = []
        match_percentage = (len(matching_skills) / (len(matching_skills) + len(missing_skills))) * 100 if (matching_skills or missing_skills) else 0
        
        if match_percentage >= 70:
            insights.append(f"Excellent match! You already possess {len(matching_skills)} of the key skills required for {job_title}.")
            insights.append("Focus on gaining practical experience and showcasing your existing skills through projects.")
        elif match_percentage >= 50:
            insights.append(f"Good foundation! You have {len(matching_skills)} relevant skills for {job_title}.")
            insights.append(f"Developing the {len(missing_skills)} missing skills will significantly improve your competitiveness.")
        else:
            insights.append(f"Growth opportunity! While you have {len(matching_skills)} relevant skills, focusing on skill development will be key.")
            insights.append("Consider this role as a medium-term goal while building foundational skills.")
        
        # Add specific skill insights
        if "Python" in matching_skills and job_title == "Junior Python Developer":
            insights.append("Your Python skills are a strong foundation. Focus on building practical projects to demonstrate your abilities.")
        
        if "Communication" in matching_skills:
            insights.append("Your communication skills are valuable across all roles and will help you stand out to employers.")
        
        return insights
    
    def _generate_career_recommendations(self, experience_level: str, job_title: str, 
                                       matching_skills: List[str]) -> List[str]:
        """Generate personalized career recommendations."""
        
        recommendations = []
        
        if experience_level == "Entry Level" and "Senior" in job_title:
            recommendations.append("Consider starting with a junior or entry-level position in this field to build experience.")
            recommendations.append("Look for internships or apprenticeships that can provide hands-on experience.")
        elif experience_level == "Entry Level":
            recommendations.append("This role aligns well with your current experience level.")
            recommendations.append("Focus on building a strong portfolio to demonstrate your skills to employers.")
        
        # Skill-based recommendations
        if len(matching_skills) >= 5:
            recommendations.append("You have a strong skill set for this role. Consider applying to positions that match your current level.")
        else:
            recommendations.append("Focus on developing 2-3 key missing skills before applying to maximize your chances.")
        
        recommendations.append("Network with professionals in this field through LinkedIn and industry events.")
        recommendations.append("Consider informational interviews to learn more about day-to-day responsibilities.")
        
        return recommendations
    
    def _generate_personalized_career_paths(self, student_skills: List[str], 
                                          experience_level: str, industry: str) -> List[Dict]:
        """Generate personalized career paths based on student profile."""
        
        paths = []
        
        # Analyze student's strongest skill areas
        tech_skills = [skill for skill in student_skills if any(tech in skill.lower() 
                      for tech in ["python", "java", "sql", "data", "cloud", "security"])]
        
        design_skills = [skill for skill in student_skills if any(design in skill.lower() 
                        for design in ["design", "ui", "ux", "figma", "adobe"])]
        
        # Generate paths based on strongest areas
        if tech_skills:
            if "python" in " ".join(tech_skills).lower():
                paths.append({
                    "path_name": "Software Development Track",
                    "steps": ["Junior Python Developer", "Python Developer", "Senior Developer", "Tech Lead"],
                    "timeline": "2-5 years",
                    "key_skills_needed": ["Advanced Python", "System Design", "Leadership"]
                })
            
            if any(data_skill in " ".join(tech_skills).lower() for data_skill in ["data", "sql", "analytics"]):
                paths.append({
                    "path_name": "Data Science Track",
                    "steps": ["Data Analyst", "Data Scientist", "Senior Data Scientist", "Data Science Manager"],
                    "timeline": "3-6 years",
                    "key_skills_needed": ["Machine Learning", "Statistics", "Business Acumen"]
                })
        
        if design_skills:
            paths.append({
                "path_name": "UX/UI Design Track",
                "steps": ["Junior Designer", "UX/UI Designer", "Senior Designer", "Design Lead"],
                "timeline": "3-5 years",
                "key_skills_needed": ["Advanced Prototyping", "User Research", "Design Systems"]
            })
        
        # Default path if no specific skills identified
        if not paths:
            paths.append({
                "path_name": "General Technology Track",
                "steps": ["Entry Level Role", "Specialist", "Senior Specialist", "Team Lead"],
                "timeline": "3-6 years",
                "key_skills_needed": ["Technical Skills", "Communication", "Leadership"]
            })
        
        return paths
    
    def _prioritize_skill_development(self, missing_skills: List[str], job_title: str) -> List[Dict]:
        """Prioritize skills to develop based on importance and learning difficulty."""
        
        skill_priorities = {
            "Python": {"priority": "High", "difficulty": "Medium", "timeline": "2-3 months"},
            "SQL": {"priority": "High", "difficulty": "Low", "timeline": "1-2 months"},
            "Git": {"priority": "High", "difficulty": "Low", "timeline": "2-4 weeks"},
            "Machine Learning": {"priority": "Medium", "difficulty": "High", "timeline": "4-6 months"},
            "AWS": {"priority": "Medium", "difficulty": "Medium", "timeline": "2-3 months"},
            "Figma": {"priority": "High", "difficulty": "Low", "timeline": "3-4 weeks"},
            "Communication": {"priority": "High", "difficulty": "Medium", "timeline": "Ongoing"},
            "Problem Solving": {"priority": "High", "difficulty": "Medium", "timeline": "Ongoing"}
        }
        
        prioritized_skills = []
        for skill in missing_skills[:5]:  # Top 5 missing skills
            skill_info = skill_priorities.get(skill, {
                "priority": "Medium", 
                "difficulty": "Medium", 
                "timeline": "2-3 months"
            })
            
            prioritized_skills.append({
                "skill": skill,
                "priority": skill_info["priority"],
                "difficulty": skill_info["difficulty"],
                "estimated_learning_time": skill_info["timeline"],
                "importance_reason": self._get_skill_importance_reason(skill, job_title)
            })
        
        # Sort by priority (High > Medium > Low)
        priority_order = {"High": 3, "Medium": 2, "Low": 1}
        prioritized_skills.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
        
        return prioritized_skills
    
    def _get_skill_importance_reason(self, skill: str, job_title: str) -> str:
        """Explain why a skill is important for the specific job."""
        
        reasons = {
            "Python": f"Essential programming language for {job_title}, used for core development tasks",
            "SQL": "Critical for database operations and data manipulation in most tech roles",
            "Git": "Industry standard for version control and collaborative development",
            "Machine Learning": "Key differentiator for data science and AI-related positions",
            "AWS": "Leading cloud platform, essential for modern infrastructure and deployment",
            "Figma": "Industry-standard design tool for creating professional UI/UX designs",
            "Communication": "Essential soft skill for collaboration and presenting ideas effectively"
        }
        
        return reasons.get(skill, f"Important skill that enhances performance in {job_title}")
    
    def _suggest_learning_resources(self, missing_skills: List[str]) -> Dict[str, List[Dict]]:
        """Suggest learning resources for missing skills."""
        
        resources = {}
        
        for skill in missing_skills[:5]:  # Top 5 skills
            skill_resources = self._get_skill_resources(skill)
            resources[skill] = skill_resources
        
        return resources
    
    def _get_skill_resources(self, skill: str) -> List[Dict]:
        """Get specific learning resources for a skill."""
        
        resource_map = {
            "Python": [
                {"type": "Course", "name": "Python for Everybody (Coursera)", "cost": "Free"},
                {"type": "Practice", "name": "LeetCode Python Problems", "cost": "Free/Premium"},
                {"type": "Book", "name": "Automate the Boring Stuff with Python", "cost": "$30"}
            ],
            "SQL": [
                {"type": "Course", "name": "SQL Basics (Khan Academy)", "cost": "Free"},
                {"type": "Practice", "name": "SQLBolt Interactive Lessons", "cost": "Free"},
                {"type": "Certification", "name": "Oracle SQL Certification", "cost": "$245"}
            ],
            "Git": [
                {"type": "Tutorial", "name": "Git Tutorial (Atlassian)", "cost": "Free"},
                {"type": "Practice", "name": "Learn Git Branching", "cost": "Free"},
                {"type": "Course", "name": "Git & GitHub Crash Course", "cost": "Free"}
            ],
            "Figma": [
                {"type": "Tutorial", "name": "Figma Academy", "cost": "Free"},
                {"type": "Course", "name": "UI/UX Design with Figma", "cost": "$50"},
                {"type": "Practice", "name": "Daily UI Design Challenges", "cost": "Free"}
            ]
        }
        
        return resource_map.get(skill, [
            {"type": "Course", "name": f"{skill} Fundamentals", "cost": "Varies"},
            {"type": "Practice", "name": f"{skill} Projects", "cost": "Free"},
            {"type": "Documentation", "name": f"Official {skill} Documentation", "cost": "Free"}
        ])
    
    def _estimate_readiness_timeline(self, missing_skills_count: int, experience_level: str) -> Dict:
        """Estimate timeline to job readiness."""
        
        base_timeline_weeks = missing_skills_count * 8  # 8 weeks per skill average
        
        # Adjust based on experience level
        if experience_level == "Entry Level":
            base_timeline_weeks *= 1.2  # 20% longer for beginners
        elif experience_level == "Senior Level":
            base_timeline_weeks *= 0.8  # 20% faster for experienced
        
        timeline_months = max(1, int(base_timeline_weeks / 4))
        
        return {
            "estimated_months": timeline_months,
            "confidence_level": "High" if missing_skills_count <= 3 else "Medium",
            "milestones": self._generate_learning_milestones(timeline_months, missing_skills_count)
        }
    
    def _generate_learning_milestones(self, timeline_months: int, skills_count: int) -> List[Dict]:
        """Generate learning milestones for the development timeline."""
        
        milestones = []
        months_per_skill = max(1, timeline_months // max(1, skills_count))
        
        for i in range(min(skills_count, 4)):  # Max 4 milestones
            milestone_month = (i + 1) * months_per_skill
            milestones.append({
                "month": milestone_month,
                "goal": f"Complete learning path for skill {i + 1}",
                "deliverable": "Portfolio project demonstrating new skill"
            })
        
        # Final milestone
        milestones.append({
            "month": timeline_months,
            "goal": "Job application readiness",
            "deliverable": "Updated resume and portfolio showcasing all skills"
        })
        
        return milestones
