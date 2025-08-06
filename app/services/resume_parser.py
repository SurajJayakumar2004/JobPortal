"""
Resume Parser Service with AI-powered text extraction and skill analysis.
This service handles PDF/DOC text extraction and uses NLP for skill identification.
"""

import re
import spacy
import pdfplumber
from docx import Document
from textblob import TextBlob
from typing import List, Dict, Optional, Tuple
import logging
from pathlib import Path

# Initialize spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
except IOError:
    print("spaCy English model not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None

logger = logging.getLogger(__name__)

class ResumeParserService:
    """Service for parsing resumes and extracting structured information using AI/NLP."""
    
    def __init__(self):
        """Initialize the resume parser with predefined skill categories."""
        self.skill_keywords = {
            "programming_languages": [
                "python", "java", "javascript", "typescript", "c++", "c#", "php", "ruby", 
                "go", "rust", "swift", "kotlin", "scala", "r", "matlab", "sql", "html", 
                "css", "sass", "less", "shell", "bash", "powershell", "perl", "lua"
            ],
            "frameworks_libraries": [
                "react", "angular", "vue", "django", "flask", "fastapi", "express", 
                "spring", "spring boot", "hibernate", "laravel", "rails", "jquery", 
                "bootstrap", "tailwind", "node.js", "next.js", "nuxt.js", "gatsby",
                "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy"
            ],
            "databases": [
                "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra", 
                "oracle", "sql server", "sqlite", "dynamodb", "neo4j", "couchdb"
            ],
            "cloud_devops": [
                "aws", "azure", "google cloud", "gcp", "docker", "kubernetes", "jenkins", 
                "gitlab", "github actions", "terraform", "ansible", "vagrant", "nginx", 
                "apache", "linux", "ubuntu", "centos", "debian"
            ],
            "soft_skills": [
                "leadership", "communication", "teamwork", "problem solving", "analytical", 
                "creative", "adaptable", "detail oriented", "time management", "project management",
                "collaboration", "mentoring", "presentation", "negotiation", "strategic thinking"
            ],
            "tools_technologies": [
                "git", "jira", "confluence", "slack", "trello", "asana", "notion", 
                "figma", "adobe", "photoshop", "illustrator", "sketch", "invision",
                "postman", "swagger", "api", "rest", "graphql", "soap", "microservices"
            ]
        }
        
        # Compile regex patterns for contact information
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.phone_pattern = re.compile(r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})')
        self.linkedin_pattern = re.compile(r'linkedin\.com/in/[\w-]+', re.IGNORECASE)
        self.github_pattern = re.compile(r'github\.com/[\w-]+', re.IGNORECASE)
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using pdfplumber."""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            return ""
    
    def extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file using python-docx."""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {str(e)}")
            return ""
    
    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from supported file formats."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return self.extract_text_from_pdf(str(file_path))
        elif extension in ['.docx', '.doc']:
            return self.extract_text_from_docx(str(file_path))
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract contact information from resume text."""
        contact_info = {
            "email": None,
            "phone": None,
            "linkedin": None,
            "github": None
        }
        
        # Extract email
        email_match = self.email_pattern.search(text)
        if email_match:
            contact_info["email"] = email_match.group()
        
        # Extract phone
        phone_match = self.phone_pattern.search(text)
        if phone_match:
            contact_info["phone"] = phone_match.group()
        
        # Extract LinkedIn
        linkedin_match = self.linkedin_pattern.search(text)
        if linkedin_match:
            contact_info["linkedin"] = "https://" + linkedin_match.group()
        
        # Extract GitHub
        github_match = self.github_pattern.search(text)
        if github_match:
            contact_info["github"] = "https://" + github_match.group()
        
        return contact_info
    
    def extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills from resume text using keyword matching and NLP."""
        text_lower = text.lower()
        extracted_skills = {category: [] for category in self.skill_keywords.keys()}
        
        # Keyword-based extraction
        for category, keywords in self.skill_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    extracted_skills[category].append(keyword.title())
        
        # Remove duplicates and sort
        for category in extracted_skills:
            extracted_skills[category] = sorted(list(set(extracted_skills[category])))
        
        return extracted_skills
    
    def extract_experience_years(self, text: str) -> Optional[int]:
        """Extract years of experience from resume text."""
        experience_patterns = [
            r'(\d+)\+?\s*years?\s*(of\s*)?experience',
            r'(\d+)\+?\s*years?\s*in',
            r'(\d+)\+?\s*yrs?\s*(of\s*)?experience',
            r'experience.*?(\d+)\+?\s*years?'
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text.lower())
            if matches:
                # Get the highest number found
                years = max([int(match[0] if isinstance(match, tuple) else match) for match in matches])
                return years
        
        return None
    
    def extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from resume text."""
        education_keywords = [
            "bachelor", "master", "phd", "doctorate", "diploma", "certificate",
            "b.s.", "b.a.", "m.s.", "m.a.", "m.b.a.", "b.tech", "m.tech",
            "university", "college", "institute", "school"
        ]
        
        degree_patterns = [
            r'(bachelor|master|phd|doctorate|diploma|certificate|b\.s\.|b\.a\.|m\.s\.|m\.a\.|m\.b\.a\.|b\.tech|m\.tech).*?(in|of)\s*([^\n,;]+)',
            r'(bachelor|master|phd|doctorate|diploma|certificate|b\.s\.|b\.a\.|m\.s\.|m\.a\.|m\.b\.a\.|b\.tech|m\.tech)\s*([^\n,;]+)'
        ]
        
        education = []
        text_lower = text.lower()
        
        for pattern in degree_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, tuple) and len(match) >= 2:
                    degree = match[0].strip()
                    field = (match[2] if len(match) > 2 else match[1]).strip()
                    education.append({
                        "degree": degree.title(),
                        "field": field.title()
                    })
        
        return education[:3]  # Return max 3 education entries
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of resume text using TextBlob."""
        try:
            blob = TextBlob(text)
            return {
                "polarity": round(blob.sentiment.polarity, 3),  # -1 to 1
                "subjectivity": round(blob.sentiment.subjectivity, 3)  # 0 to 1
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {"polarity": 0.0, "subjectivity": 0.0}
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy NLP."""
        if not nlp:
            return {"organizations": [], "locations": [], "persons": []}
        
        try:
            doc = nlp(text)
            entities = {
                "organizations": [],
                "locations": [],
                "persons": []
            }
            
            for ent in doc.ents:
                if ent.label_ == "ORG":
                    entities["organizations"].append(ent.text)
                elif ent.label_ in ["GPE", "LOC"]:
                    entities["locations"].append(ent.text)
                elif ent.label_ == "PERSON":
                    entities["persons"].append(ent.text)
            
            # Remove duplicates and limit results
            for key in entities:
                entities[key] = list(set(entities[key]))[:5]
            
            return entities
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {"organizations": [], "locations": [], "persons": []}
    
    def calculate_skill_score(self, skills: Dict[str, List[str]]) -> int:
        """Calculate a skill score based on the number and diversity of skills."""
        total_skills = sum(len(skill_list) for skill_list in skills.values())
        categories_with_skills = sum(1 for skill_list in skills.values() if skill_list)
        
        # Base score from total skills (max 70 points)
        skill_score = min(total_skills * 2, 70)
        
        # Bonus for skill diversity (max 30 points)
        diversity_bonus = categories_with_skills * 5
        
        return min(skill_score + diversity_bonus, 100)
    
    def parse_resume(self, file_path: str) -> Dict:
        """
        Main method to parse a resume file and extract all information.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            Dictionary containing all extracted information
        """
        try:
            # Extract text from file
            text = self.extract_text_from_file(file_path)
            
            if not text.strip():
                raise ValueError("No text could be extracted from the resume")
            
            # Extract all information
            contact_info = self.extract_contact_info(text)
            skills = self.extract_skills(text)
            experience_years = self.extract_experience_years(text)
            education = self.extract_education(text)
            sentiment = self.analyze_sentiment(text)
            entities = self.extract_entities(text)
            skill_score = self.calculate_skill_score(skills)
            
            return {
                "success": True,
                "text": text[:1000] + "..." if len(text) > 1000 else text,  # Truncate for storage
                "contact_info": contact_info,
                "skills": skills,
                "experience_years": experience_years,
                "education": education,
                "sentiment": sentiment,
                "entities": entities,
                "skill_score": skill_score,
                "total_skills": sum(len(skill_list) for skill_list in skills.values()),
                "text_length": len(text),
                "processing_metadata": {
                    "file_format": Path(file_path).suffix.lower(),
                    "nlp_enabled": nlp is not None
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing resume {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "contact_info": {},
                "skills": {},
                "experience_years": None,
                "education": [],
                "sentiment": {"polarity": 0.0, "subjectivity": 0.0},
                "entities": {"organizations": [], "locations": [], "persons": []},
                "skill_score": 0,
                "total_skills": 0,
                "text_length": 0
            }

# Global instance
resume_parser = ResumeParserService()
