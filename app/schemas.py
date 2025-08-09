"""
Pydantic models for data validation and serialization.

This module contains all the data models used throughout the application,
including request/response models and database schema definitions.
The models are designed to be compatible with MongoDB using Beanie ODM.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class UserRole(str, Enum):
    STUDENT = "student"
    EMPLOYER = "employer"


class ApplicationStatus(str, Enum):
    APPLIED = "applied"
    REVIEWED = "reviewed"
    SHORTLISTED = "shortlisted"
    INTERVIEWED = "interviewed"
    REJECTED = "rejected"
    HIRED = "hired"


class JobStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    DRAFT = "draft"


# Base Models
class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at timestamps."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# User Models
class UserProfile(BaseModel):
    """User profile information."""
    name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')
    photo_url: Optional[str] = None
    education: Optional[List[str]] = []
    skills: Optional[List[str]] = []
    interests: Optional[List[str]] = []
    location: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=1000)
    # Employer-specific fields
    organization_name: Optional[str] = Field(None, min_length=2, max_length=200)
    organization_email: Optional[EmailStr] = None


class EmployerRegistration(BaseModel):
    """Model for employer registration with specific fields."""
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of the employer")
    organization_name: str = Field(..., min_length=2, max_length=200, description="Name of the organization")
    organization_email: EmailStr = Field(..., description="Organization's email address")
    phone_number: str = Field(..., pattern=r'^\+?[\d\s\-\(\)]+$', description="Phone number")
    password: str = Field(..., min_length=8, max_length=100, description="Password")

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class StudentRegistration(BaseModel):
    """Model for student registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str = Field(..., min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[\d\s\-\(\)]+$')

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserCreate(BaseModel):
    """Model for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole
    profile: UserProfile

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserLogin(BaseModel):
    """Model for user login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Model for updating user information."""
    profile: Optional[UserProfile] = None


class UserOut(BaseModel):
    """Model for user response (without sensitive data)."""
    id: str = Field(alias="_id")
    email: EmailStr
    role: UserRole
    profile: UserProfile
    created_at: datetime
    updated_at: datetime

    class Config:
        allow_population_by_field_name = True


class User(BaseModel):
    """Complete user model for database storage."""
    id: str = Field(alias="_id")
    email: EmailStr
    hashed_password: str
    role: UserRole
    profile: UserProfile
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True


# Resume Models
class ParsedResumeSection(BaseModel):
    """Parsed sections from a resume."""
    summary: Optional[str] = None
    experience: Optional[List[str]] = []
    education: Optional[List[str]] = []
    skills: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
    projects: Optional[List[str]] = []


class AIFeedback(BaseModel):
    """AI-generated feedback for resume."""
    ats_score: float = Field(..., ge=0, le=100)
    skill_gaps: List[str] = []
    suggestions: List[str] = []
    strengths: List[str] = []
    formatting_score: float = Field(..., ge=0, le=100)
    completeness_score: float = Field(..., ge=0, le=100)


class ResumeCreate(BaseModel):
    """Model for resume upload."""
    filename: str
    content_type: str


class ResumeOut(BaseModel):
    """Model for resume response."""
    id: str = Field(alias="_id")
    user_id: str
    filename: str
    upload_date: datetime
    file_url: str
    parsed_sections: Optional[ParsedResumeSection] = None
    ai_feedback: Optional[AIFeedback] = None
    processing_status: str = "pending"  # pending, processing, completed, failed

    class Config:
        allow_population_by_field_name = True


class Resume(BaseModel):
    """Complete resume model for database storage."""
    id: str = Field(alias="_id")
    user_id: str
    filename: str
    original_file_url: str
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    parsed_text: Optional[str] = None
    parsed_sections: Optional[ParsedResumeSection] = None
    ai_feedback: Optional[AIFeedback] = None
    processing_status: str = "pending"
    counseling_report_id: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


# Job Models
class JobCreate(BaseModel):
    """Model for creating a job posting."""
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=50, max_length=5000)
    required_skills: List[str] = Field(..., min_items=1)
    location: str = Field(..., min_length=2, max_length=100)
    experience_level: Optional[str] = Field(None, pattern=r'^(entry|mid|senior|lead|executive)$')
    employment_type: Optional[str] = Field(None, pattern=r'^(full-time|part-time|contract|internship)$')
    salary_range: Optional[str] = None
    company_name: str = Field(..., min_length=2, max_length=100)


class JobUpdate(BaseModel):
    """Model for updating a job posting."""
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=50, max_length=5000)
    required_skills: Optional[List[str]] = None
    location: Optional[str] = Field(None, min_length=2, max_length=100)
    status: Optional[JobStatus] = None
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    salary_range: Optional[str] = None


class JobOut(BaseModel):
    """Model for job response."""
    _id: str  # Use _id directly to match frontend expectations
    employer_id: str
    title: str
    description: str
    required_skills: List[str]
    location: str
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    salary_range: Optional[str] = None
    company_name: str
    status: JobStatus
    posted_at: datetime
    updated_at: datetime
    applications_count: int = 0

    class Config:
        allow_population_by_field_name = True


class Job(BaseModel):
    """Complete job model for database storage."""
    id: str = Field(alias="_id")
    employer_id: str
    title: str
    description: str
    required_skills: List[str]
    location: str
    experience_level: Optional[str] = None
    employment_type: Optional[str] = None
    salary_range: Optional[str] = None
    company_name: str
    status: JobStatus = JobStatus.OPEN
    posted_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True


# Application Models
class ApplicationCreate(BaseModel):
    """Model for creating a job application."""
    job_id: str
    resume_id: str
    cover_letter: Optional[str] = Field(None, max_length=2000)


class ApplicationUpdate(BaseModel):
    """Model for updating application status."""
    status: ApplicationStatus
    notes: Optional[str] = Field(None, max_length=1000)


class ApplicationOut(BaseModel):
    """Model for application response."""
    id: str = Field(alias="_id")
    job_id: str
    user_id: str
    resume_id: str
    status: ApplicationStatus
    cover_letter: Optional[str] = None
    applied_at: datetime
    updated_at: datetime
    match_score: Optional[float] = None
    notes: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class Application(BaseModel):
    """Complete application model for database storage."""
    id: str = Field(alias="_id")
    job_id: str
    user_id: str
    resume_id: str
    status: ApplicationStatus = ApplicationStatus.APPLIED
    cover_letter: Optional[str] = None
    applied_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    match_score: Optional[float] = None
    notes: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


# Company Models
class CompanyCreate(BaseModel):
    """Model for creating a company profile."""
    name: str = Field(..., min_length=2, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = Field(None, pattern=r'^(1-10|11-50|51-200|201-500|501-1000|1000\+)$')


class CompanyOut(BaseModel):
    """Model for company response."""
    id: str = Field(alias="_id")
    employer_id: str
    name: str
    description: str
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    created_at: datetime

    class Config:
        allow_population_by_field_name = True


class Company(BaseModel):
    """Complete company model for database storage."""
    id: str = Field(alias="_id")
    employer_id: str
    name: str
    description: str
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True


# Career Counseling Models
class CounselingReportCreate(BaseModel):
    """Model for generating career counseling report."""
    user_id: str
    target_role: Optional[str] = None
    interests: Optional[List[str]] = []


class CareerPath(BaseModel):
    """Model for career path suggestions."""
    title: str
    description: str
    required_skills: List[str]
    growth_potential: str
    average_salary: Optional[str] = None


class CounselingReportOut(BaseModel):
    """Model for counseling report response."""
    id: str = Field(alias="_id")
    user_id: str
    generated_on: datetime
    skills_summary: List[str]
    suggested_paths: List[CareerPath]
    missing_skills: List[str]
    recommended_resources: List[str]
    overall_score: float = Field(..., ge=0, le=100)

    class Config:
        allow_population_by_field_name = True


class CounselingReport(BaseModel):
    """Complete counseling report model for database storage."""
    id: str = Field(alias="_id")
    user_id: str
    generated_on: datetime = Field(default_factory=datetime.utcnow)
    skills_summary: List[str]
    suggested_paths: List[CareerPath]
    missing_skills: List[str]
    recommended_resources: List[str]
    overall_score: float = Field(..., ge=0, le=100)

    class Config:
        allow_population_by_field_name = True


# AI Matching Models
class CandidateMatch(BaseModel):
    """Model for candidate matching results."""
    user_id: str
    user_name: str
    user_email: EmailStr
    resume_id: str
    match_score: float = Field(..., ge=0, le=1)
    matching_skills: List[str]
    missing_skills: List[str]
    experience_level: Optional[str] = None


class JobMatchResponse(BaseModel):
    """Response model for job candidate matching."""
    job_id: str
    job_title: str
    total_candidates: int
    candidates: List[CandidateMatch]
    average_match_score: float


# Token Models
class Token(BaseModel):
    """Model for authentication token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Model for token data."""
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[UserRole] = None


# Response Models
class SuccessResponse(BaseModel):
    """Generic success response model."""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Generic error response model."""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# Job Generator Models
class JobPosting(BaseModel):
    """Model for job posting data used in job generation."""
    title: str
    company: str
    location: str
    department: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    salary_range: Optional[str] = None
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    description: Optional[str] = None
    responsibilities: List[str] = []
    qualifications: List[str] = []
    benefits: List[str] = []


class PersonalizedInsightsRequest(BaseModel):
    """Request model for personalized career insights."""
    candidate_id: str
    job_id: str
    resume_text: Optional[str] = None


class PersonalizedInsightsResponse(BaseModel):
    """Response model for personalized career insights."""
    candidate_id: str
    job_id: str
    professional_insights: str
    career_recommendations: List[str]
    skill_breakdown: Dict[str, Any]
    suggested_career_paths: List[Dict[str, Any]]
    priority_skills: List[Dict[str, Any]]
    learning_timeline: Dict[str, Any]


# AI Analysis Models
class SkillGapAnalysisRequest(BaseModel):
    """Request model for skill gap analysis."""
    candidate_id: str
    job_id: str


class SkillGapAnalysisResponse(BaseModel):
    """Response model for skill gap analysis."""
    candidate_id: str
    job_id: str
    skill_coverage: float = Field(..., ge=0, le=100)
    missing_skills: List[str]
    matching_skills: List[str]
    critical_gaps: int
    recommendations: List[str]
    improvement_areas: List[str]


class CandidateRecommendationRequest(BaseModel):
    """Request model for candidate recommendations."""
    job_id: str
    max_candidates: int = Field(default=10, ge=1, le=50)
    min_match_score: float = Field(default=0.5, ge=0, le=1)


class MarketTrendData(BaseModel):
    """Model for market trend information."""
    skill_demand: Dict[str, Any]
    job_categories: Dict[str, Any]
    salary_trends: Dict[str, Any]
    remote_work: Dict[str, Any]
    hiring_timeline: Dict[str, Any]


class JobOptimizationSuggestion(BaseModel):
    """Model for job posting optimization suggestions."""
    job_id: str
    current_performance: Dict[str, Any]
    title_optimization: Dict[str, Any]
    description_optimization: Dict[str, Any]
    requirements_optimization: Dict[str, Any]
    compensation_optimization: Dict[str, Any]
    ats_optimization: Dict[str, Any]


class CandidateInsights(BaseModel):
    """Model for candidate insights and recommendations."""
    candidate_id: str
    profile_strength: Dict[str, Any]
    market_fit: Dict[str, Any]
    career_recommendations: List[str]
    job_match_potential: Dict[str, Any]
