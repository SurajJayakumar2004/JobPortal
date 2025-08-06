"""
AI-powered resume parsing service.

This service handles the extraction and parsing of text from resume files,
performs natural language processing to identify key sections and skills,
and provides AI-driven feedback on resume quality and ATS compatibility.
"""

import os
import re
import uuid
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import fitz  # PyMuPDF
import docx2txt
import spacy
from collections import Counter
import logging

from app.schemas import ParsedResumeSection, AIFeedback
from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load spaCy model (download with: python -m spacy download en_core_web_sm)
try:
    nlp = spacy.load(settings.spacy_model)
except OSError:
    logger.warning(f"spaCy model '{settings.spacy_model}' not found. Please install it with: python -m spacy download {settings.spacy_model}")
    nlp = None

# Common skills database (in production, this would be a more comprehensive database)
TECH_SKILLS = {
    'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'scala'],
    'web': ['html', 'css', 'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask', 'fastapi'],
    'database': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sqlite'],
    'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'jenkins'],
    'data': ['pandas', 'numpy', 'sklearn', 'tensorflow', 'pytorch', 'matplotlib', 'tableau'],
    'tools': ['git', 'jira', 'confluence', 'slack', 'figma', 'photoshop', 'excel']
}

# Flatten skills for easier searching
ALL_SKILLS = []
for category in TECH_SKILLS.values():
    ALL_SKILLS.extend(category)

# Section headers to identify resume sections
SECTION_PATTERNS = {
    'summary': r'(summary|profile|objective|about|overview)',
    'experience': r'(experience|employment|work history|professional experience|career)',
    'education': r'(education|academic|qualifications|degrees)',
    'skills': r'(skills|technical skills|competencies|expertise|technologies)',
    'projects': r'(projects|portfolio|personal projects)',
    'certifications': r'(certifications|certificates|credentials|licenses)'
}


class ResumeParserService:
    """Service class for parsing and analyzing resumes."""
    
    def __init__(self):
        """Initialize the resume parser service."""
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
    
    async def parse_resume_file(self, file_path: str, filename: str) -> Dict:
        """
        Parse a resume file and extract structured information.
        
        Args:
            file_path: Path to the uploaded resume file
            filename: Original filename of the resume
            
        Returns:
            Dict containing parsed resume data and AI feedback
        """
        try:
            # Extract text from file
            text = self._extract_text_from_file(file_path)
            
            if not text.strip():
                raise ValueError("Could not extract text from resume file")
            
            # Parse sections
            parsed_sections = self._parse_resume_sections(text)
            
            # Generate AI feedback
            ai_feedback = self._generate_ai_feedback(text, parsed_sections)
            
            return {
                'parsed_text': text,
                'parsed_sections': parsed_sections,
                'ai_feedback': ai_feedback,
                'processing_status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Error parsing resume {filename}: {str(e)}")
            return {
                'parsed_text': None,
                'parsed_sections': None,
                'ai_feedback': None,
                'processing_status': 'failed',
                'error': str(e)
            }
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from PDF or DOCX file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            str: Extracted text content
        """
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return self._extract_text_from_docx(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file using PyMuPDF."""
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            
            doc.close()
            return text
            
        except Exception as e:
            raise ValueError(f"Error extracting text from PDF: {str(e)}")
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file using docx2txt."""
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            raise ValueError(f"Error extracting text from DOCX: {str(e)}")
    
    def _parse_resume_sections(self, text: str) -> ParsedResumeSection:
        """
        Parse resume text into structured sections.
        
        Args:
            text: Raw resume text
            
        Returns:
            ParsedResumeSection: Structured resume sections
        """
        # Split text into lines and clean
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Initialize sections
        sections = {
            'summary': [],
            'experience': [],
            'education': [],
            'skills': [],
            'projects': [],
            'certifications': []
        }
        
        current_section = None
        
        # Parse sections based on headers
        for line in lines:
            line_lower = line.lower()
            
            # Check if line is a section header
            section_found = False
            for section_name, pattern in SECTION_PATTERNS.items():
                if re.search(pattern, line_lower):
                    current_section = section_name
                    section_found = True
                    break
            
            # If not a header and we have a current section, add to that section
            if not section_found and current_section and len(line) > 10:
                sections[current_section].append(line)
        
        # Extract skills using NLP and pattern matching
        extracted_skills = self._extract_skills(text)
        if extracted_skills:
            sections['skills'].extend(extracted_skills)
        
        # Remove duplicates and clean sections
        for section_name in sections:
            sections[section_name] = list(set(sections[section_name]))
        
        return ParsedResumeSection(
            summary='\n'.join(sections['summary']) if sections['summary'] else None,
            experience=sections['experience'],
            education=sections['education'],
            skills=sections['skills'],
            projects=sections['projects'],
            certifications=sections['certifications']
        )
    
    def _extract_skills(self, text: str) -> List[str]:
        """
        Extract skills from resume text using NLP and pattern matching.
        
        Args:
            text: Resume text
            
        Returns:
            List[str]: Extracted skills
        """
        found_skills = []
        text_lower = text.lower()
        
        # Pattern-based skill extraction
        for skill in ALL_SKILLS:
            if skill.lower() in text_lower:
                found_skills.append(skill.title())
        
        # NLP-based skill extraction (if spaCy is available)
        if nlp:
            try:
                doc = nlp(text)
                
                # Extract entities that might be skills
                for ent in doc.ents:
                    if ent.label_ in ['ORG', 'PRODUCT']:  # Organizations and products are often technologies
                        potential_skill = ent.text.lower()
                        if len(potential_skill) > 2 and potential_skill in [s.lower() for s in ALL_SKILLS]:
                            found_skills.append(potential_skill.title())
                
                # Extract noun phrases that might be skills
                for chunk in doc.noun_chunks:
                    chunk_text = chunk.text.lower()
                    if len(chunk_text) < 20:  # Avoid long phrases
                        for skill in ALL_SKILLS:
                            if skill.lower() in chunk_text:
                                found_skills.append(skill.title())
                                
            except Exception as e:
                logger.warning(f"NLP skill extraction failed: {str(e)}")
        
        return list(set(found_skills))
    
    def _generate_ai_feedback(self, text: str, sections: ParsedResumeSection) -> AIFeedback:
        """
        Generate AI feedback for the resume.
        
        Args:
            text: Raw resume text
            sections: Parsed resume sections
            
        Returns:
            AIFeedback: AI-generated feedback and scores
        """
        # Calculate ATS compatibility score
        ats_score = self._calculate_ats_score(text, sections)
        
        # Calculate formatting score
        formatting_score = self._calculate_formatting_score(text)
        
        # Calculate completeness score
        completeness_score = self._calculate_completeness_score(sections)
        
        # Generate suggestions
        suggestions = self._generate_suggestions(sections, ats_score, formatting_score, completeness_score)
        
        # Identify strengths
        strengths = self._identify_strengths(sections)
        
        # Identify skill gaps (basic implementation)
        skill_gaps = self._identify_skill_gaps(sections.skills or [])
        
        return AIFeedback(
            ats_score=ats_score,
            formatting_score=formatting_score,
            completeness_score=completeness_score,
            suggestions=suggestions,
            strengths=strengths,
            skill_gaps=skill_gaps
        )
    
    def _calculate_ats_score(self, text: str, sections: ParsedResumeSection) -> float:
        """Calculate ATS (Applicant Tracking System) compatibility score."""
        score = 0.0
        
        # Check for contact information
        if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
            score += 20
        
        if re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text):
            score += 15
        
        # Check for section headers
        sections_found = 0
        for pattern in SECTION_PATTERNS.values():
            if re.search(pattern, text, re.IGNORECASE):
                sections_found += 1
        score += min(sections_found * 10, 40)
        
        # Check for skills section
        if sections.skills:
            score += 15
        
        # Check for experience section
        if sections.experience:
            score += 10
        
        return min(score, 100.0)
    
    def _calculate_formatting_score(self, text: str) -> float:
        """Calculate formatting quality score."""
        score = 0.0
        
        # Check text length
        if 200 <= len(text) <= 2000:
            score += 30
        elif len(text) > 2000:
            score += 20
        
        # Check for proper capitalization
        lines = text.split('\n')
        capitalized_lines = sum(1 for line in lines if line and line[0].isupper())
        if capitalized_lines / max(len(lines), 1) > 0.3:
            score += 25
        
        # Check for bullet points or structured formatting
        if '•' in text or '*' in text or '-' in text:
            score += 20
        
        # Check for numbers (dates, achievements)
        if re.search(r'\d{4}', text):  # Years
            score += 15
        
        # Check for action verbs (common in good resumes)
        action_verbs = ['managed', 'developed', 'created', 'implemented', 'led', 'designed', 'built', 'improved']
        found_verbs = sum(1 for verb in action_verbs if verb.lower() in text.lower())
        score += min(found_verbs * 2, 10)
        
        return min(score, 100.0)
    
    def _calculate_completeness_score(self, sections: ParsedResumeSection) -> float:
        """Calculate completeness score based on available sections."""
        score = 0.0
        
        if sections.experience:
            score += 30
        if sections.education:
            score += 25
        if sections.skills:
            score += 25
        if sections.summary:
            score += 10
        if sections.projects:
            score += 5
        if sections.certifications:
            score += 5
        
        return min(score, 100.0)
    
    def _generate_suggestions(self, sections: ParsedResumeSection, ats_score: float, 
                            formatting_score: float, completeness_score: float) -> List[str]:
        """Generate improvement suggestions based on analysis."""
        suggestions = []
        
        if ats_score < 70:
            suggestions.append("Improve ATS compatibility by adding clear section headers and contact information")
        
        if formatting_score < 70:
            suggestions.append("Enhance formatting with bullet points and consistent structure")
        
        if completeness_score < 70:
            suggestions.append("Add missing sections like experience, education, or skills")
        
        if not sections.skills or len(sections.skills) < 5:
            suggestions.append("Add more relevant technical and soft skills")
        
        if not sections.summary:
            suggestions.append("Include a professional summary at the top of your resume")
        
        if sections.experience and len(sections.experience) < 3:
            suggestions.append("Provide more detailed work experience with quantifiable achievements")
        
        return suggestions
    
    def _identify_strengths(self, sections: ParsedResumeSection) -> List[str]:
        """Identify resume strengths."""
        strengths = []
        
        if sections.skills and len(sections.skills) >= 8:
            strengths.append("Comprehensive skills section")
        
        if sections.experience and len(sections.experience) >= 3:
            strengths.append("Detailed work experience")
        
        if sections.education:
            strengths.append("Educational background included")
        
        if sections.projects:
            strengths.append("Project experience demonstrated")
        
        if sections.certifications:
            strengths.append("Professional certifications listed")
        
        return strengths
    
    def _identify_skill_gaps(self, current_skills: List[str]) -> List[str]:
        """Identify potential skill gaps based on current market trends."""
        current_skills_lower = [skill.lower() for skill in current_skills]
        
        # High-demand skills that are often missing
        high_demand_skills = [
            'cloud computing', 'machine learning', 'data analysis',
            'project management', 'agile methodology', 'api development'
        ]
        
        gaps = []
        for skill in high_demand_skills:
            if skill not in current_skills_lower:
                gaps.append(skill.title())
        
        return gaps[:5]  # Return top 5 gaps
    
    async def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to disk and return file path.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            str: Path to saved file
        """
        # Generate unique filename
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = self.upload_dir / unique_filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        return str(file_path)
