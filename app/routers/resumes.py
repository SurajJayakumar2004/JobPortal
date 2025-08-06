"""
Resume management endpoints for file upload, parsing, and analysis.
Includes AI-powered resume parsing and skill extraction.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.security import HTTPBearer
from app.schemas import ResumeCreate, ResumeResponse, UserResponse, APIResponse, UserRole
from app.utils.dependencies import get_current_user
from app.services.resume_parser import resume_parser
from app.config import app_data
import os
import uuid
from pathlib import Path
import logging

router = APIRouter(prefix="/resumes", tags=["resumes"])
security = HTTPBearer()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Global counter for resume IDs (in production, use database auto-increment)
resume_id_counter = 1

def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Supported formats: {', '.join(ALLOWED_EXTENSIONS)}"
        )

@router.post("/upload", response_model=APIResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload and parse a resume file with AI-powered analysis."""
    global resume_id_counter
    
    try:
        # Validate user role
        if current_user.get("role") != UserRole.JOB_SEEKER:
            raise HTTPException(
                status_code=403, 
                detail="Only job seekers can upload resumes"
            )
        
        # Validate file
        validate_file(file)
        file_extension = Path(file.filename).suffix.lower()
        
        # Check file size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Reset file position for saving
        await file.seek(0)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Parse resume using AI
        parsing_result = resume_parser.parse_resume(str(file_path))
        
        # Create resume record
        resume_data = {
            "id": resume_id_counter,
            "user_id": current_user["id"],
            "original_filename": file.filename,
            "stored_filename": unique_filename,
            "file_path": str(file_path),
            "file_size": len(content),
            "content_type": file.content_type,
            "parsing_result": parsing_result,
            "upload_timestamp": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
        }
        
        resume_id_counter += 1
        
        # Store in app data
        app_data["resumes"].append(resume_data)
        
        return APIResponse(
            success=True,
            message="Resume uploaded and parsed successfully",
            data={
                "resume_id": resume_data["id"],
                "parsing_success": parsing_result.get("success", False),
                "skills_found": parsing_result.get("total_skills", 0),
                "skill_score": parsing_result.get("skill_score", 0),
                "contact_info": parsing_result.get("contact_info", {}),
                "experience_years": parsing_result.get("experience_years"),
                "education_count": len(parsing_result.get("education", [])),
                "file_info": {
                    "original_name": file.filename,
                    "size_mb": round(len(content) / (1024*1024), 2),
                    "format": file_extension.upper()
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}")
        # Clean up file if it was created
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail="Failed to process resume")

@router.get("/", response_model=APIResponse)
async def get_user_resumes(current_user: dict = Depends(get_current_user)):
    """Get all resumes for the current user."""
    user_resumes = [
        resume for resume in app_data["resumes"] 
        if resume["user_id"] == current_user["id"]
    ]
    
    # Format response data
    formatted_resumes = []
    for resume in user_resumes:
        parsing_result = resume.get("parsing_result", {})
        formatted_resumes.append({
            "id": resume["id"],
            "original_filename": resume["original_filename"],
            "upload_timestamp": resume["upload_timestamp"],
            "file_size_mb": round(resume["file_size"] / (1024*1024), 2),
            "parsing_success": parsing_result.get("success", False),
            "skill_score": parsing_result.get("skill_score", 0),
            "total_skills": parsing_result.get("total_skills", 0),
            "experience_years": parsing_result.get("experience_years"),
            "contact_info": parsing_result.get("contact_info", {}),
            "education_count": len(parsing_result.get("education", []))
        })
    
    return APIResponse(
        success=True,
        message=f"Found {len(formatted_resumes)} resumes",
        data=formatted_resumes
    )

@router.get("/{resume_id}/analysis", response_model=APIResponse)
async def get_resume_analysis(
    resume_id: int, 
    current_user: dict = Depends(get_current_user)
):
    """Get detailed analysis of a specific resume."""
    resume = next(
        (r for r in app_data["resumes"] if r["id"] == resume_id), 
        None
    )
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Check ownership
    if resume["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    parsing_result = resume.get("parsing_result", {})
    
    return APIResponse(
        success=True,
        message="Resume analysis retrieved successfully",
        data={
            "resume_info": {
                "id": resume["id"],
                "filename": resume["original_filename"],
                "upload_date": resume["upload_timestamp"]
            },
            "parsing_result": parsing_result,
            "analysis_summary": {
                "overall_score": parsing_result.get("skill_score", 0),
                "strengths": _analyze_strengths(parsing_result),
                "improvement_areas": _analyze_improvements(parsing_result),
                "keyword_density": _calculate_keyword_density(parsing_result)
            }
        }
    )

@router.delete("/{resume_id}", response_model=APIResponse)
async def delete_resume(
    resume_id: int, 
    current_user: dict = Depends(get_current_user)
):
    """Delete a resume file and its data."""
    resume = next(
        (r for r in app_data["resumes"] if r["id"] == resume_id), 
        None
    )
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Check ownership
    if resume["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Delete file from filesystem
        file_path = Path(resume["file_path"])
        if file_path.exists():
            file_path.unlink()
        
        # Remove from app data
        app_data["resumes"] = [
            r for r in app_data["resumes"] if r["id"] != resume_id
        ]
        
        return APIResponse(
            success=True,
            message="Resume deleted successfully",
            data={"deleted_resume_id": resume_id}
        )
        
    except Exception as e:
        logger.error(f"Error deleting resume {resume_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete resume")

def _analyze_strengths(parsing_result: dict) -> list:
    """Analyze resume strengths based on parsing results."""
    strengths = []
    
    if parsing_result.get("skill_score", 0) > 70:
        strengths.append("Strong technical skill set")
    
    if parsing_result.get("experience_years", 0) > 3:
        strengths.append("Good professional experience")
    
    if len(parsing_result.get("education", [])) > 0:
        strengths.append("Solid educational background")
    
    contact_info = parsing_result.get("contact_info", {})
    if contact_info.get("linkedin") or contact_info.get("github"):
        strengths.append("Professional online presence")
    
    sentiment = parsing_result.get("sentiment", {})
    if sentiment.get("polarity", 0) > 0.1:
        strengths.append("Positive language and tone")
    
    return strengths if strengths else ["Areas for improvement identified"]

def _analyze_improvements(parsing_result: dict) -> list:
    """Analyze areas for resume improvement."""
    improvements = []
    
    if parsing_result.get("skill_score", 0) < 50:
        improvements.append("Add more relevant technical skills")
    
    contact_info = parsing_result.get("contact_info", {})
    if not contact_info.get("email"):
        improvements.append("Include professional email address")
    
    if not contact_info.get("linkedin"):
        improvements.append("Add LinkedIn profile")
    
    if len(parsing_result.get("education", [])) == 0:
        improvements.append("Include educational background")
    
    if parsing_result.get("experience_years") is None:
        improvements.append("Clearly state years of experience")
    
    return improvements if improvements else ["Resume looks comprehensive"]

def _calculate_keyword_density(parsing_result: dict) -> dict:
    """Calculate keyword density for different skill categories."""
    skills = parsing_result.get("skills", {})
    total_skills = sum(len(skill_list) for skill_list in skills.values())
    
    if total_skills == 0:
        return {}
    
    density = {}
    for category, skill_list in skills.items():
        density[category] = {
            "count": len(skill_list),
            "percentage": round((len(skill_list) / total_skills) * 100, 1)
        }
    
    return density