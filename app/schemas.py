from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    JOB_SEEKER = "job_seeker"
    EMPLOYER = "employer"
    COUNSELOR = "counselor"


class ApplicationStatus(str, Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    SHORTLISTED = "shortlisted"
    REJECTED = "rejected"
    HIRED = "hired"


class JobType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    id: int
    phone: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Job Schemas
class JobBase(BaseModel):
    title: str
    description: str
    company_name: str
    location: str
    job_type: JobType
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    requirements: List[str] = []
    benefits: List[str] = []


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[JobType] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    requirements: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    is_active: Optional[bool] = None


class JobResponse(JobBase):
    id: int
    employer_id: int
    is_active: bool
    created_at: datetime
    applications_count: Optional[int] = 0

    class Config:
        from_attributes = True


# Application Schemas
class ApplicationBase(BaseModel):
    cover_letter: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    job_id: int
    resume_file: Optional[str] = None


class ApplicationUpdate(BaseModel):
    status: Optional[ApplicationStatus] = None
    employer_notes: Optional[str] = None


class ApplicationResponse(ApplicationBase):
    id: int
    job_id: int
    user_id: int
    status: ApplicationStatus
    resume_file: Optional[str] = None
    employer_notes: Optional[str] = None
    ai_score: Optional[float] = None
    applied_at: datetime

    class Config:
        from_attributes = True


class ApplicationWithDetails(ApplicationResponse):
    job: JobResponse
    user: UserResponse


# Resume Schemas
class ResumeBase(BaseModel):
    filename: str
    file_path: str
    file_size: int


class ResumeCreate(ResumeBase):
    pass


class ResumeResponse(ResumeBase):
    id: int
    user_id: int
    uploaded_at: datetime
    parsed_content: Optional[dict] = None
    skills_extracted: Optional[List[str]] = None

    class Config:
        from_attributes = True


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# API Response Schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


# Counseling Schemas (for future phases)
class CounselingSessionBase(BaseModel):
    session_type: str
    notes: Optional[str] = None


class CounselingSessionCreate(CounselingSessionBase):
    user_id: int


class CounselingSessionResponse(CounselingSessionBase):
    id: int
    user_id: int
    counselor_id: int
    scheduled_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True