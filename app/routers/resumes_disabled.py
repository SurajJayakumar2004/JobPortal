"""
Resume management router for file upload and processing.

This module handles all resume-related endpoints including file upload,
parsing, AI feedback generation, and resume management functionality.
"""

from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import Dict, Any, List
import uuid
import os
from datetime import datetime
import logging

from app.schemas import (
    ResumeOut, ResumeCreate, Resume, SuccessResponse,
    AIFeedback, ParsedResumeSection, UserRole
)
# Temporarily commented out to fix import issue
# from app.services.resume_parser import ResumeParserService
from app.utils.dependencies import get_current_active_user, require_student, TokenData
from app.config import settings

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# In-memory storage for resumes (replace with database in production)
resumes_db: Dict[str, Resume] = {}
user_resumes: Dict[str, List[str]] = {}  # user_id -> [resume_ids]

# Initialize resume parser service
# resume_parser = ResumeParserService()  # Temporarily commented out


@router.post("/upload", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(require_student())
):
    """
    Upload and parse a resume file.
    
    This endpoint allows students to upload their resume files (PDF or DOCX),
    automatically parses the content using AI, and provides detailed feedback
    on resume quality, ATS compatibility, and skill analysis.
    
    Args:
        file: The resume file to upload (PDF or DOCX)
        current_user: Current authenticated student user
        
    Returns:
        Dict containing upload status and parsing results
        
    Raises:
        HTTPException: If file validation fails or processing errors occur
    """
    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.allowed_file_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(settings.allowed_file_types)}"
        )
    
    # Validate file size
    content = await file.read()
    if len(content) > settings.max_file_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size of {settings.max_file_size / (1024*1024):.1f}MB"
        )
    
    # Reset file pointer for processing
    await file.seek(0)
    
    try:
        # Save uploaded file
        file_path = await resume_parser.save_uploaded_file(content, file.filename)
        
        # Generate unique resume ID
        resume_id = str(uuid.uuid4())
        
        # Create initial resume record
        resume = Resume(
            _id=resume_id,
            user_id=current_user.user_id,
            filename=file.filename,
            original_file_url=file_path,
            upload_date=datetime.utcnow(),
            processing_status="processing"
        )
        
        # Store in database
        resumes_db[resume_id] = resume
        
        # Update user's resume list
        if current_user.user_id not in user_resumes:
            user_resumes[current_user.user_id] = []
        user_resumes[current_user.user_id].append(resume_id)
        
        # Process resume asynchronously (in production, use background tasks)
        try:
            parsing_result = await resume_parser.parse_resume_file(file_path, file.filename)
            
            # Update resume with parsing results
            resume.parsed_text = parsing_result.get('parsed_text')
            resume.parsed_sections = parsing_result.get('parsed_sections')
            resume.ai_feedback = parsing_result.get('ai_feedback')
            resume.processing_status = parsing_result.get('processing_status', 'completed')
            
            # Update in database
            resumes_db[resume_id] = resume
            
            logger.info(f"Successfully processed resume {resume_id} for user {current_user.user_id}")
            
        except Exception as e:
            logger.error(f"Error processing resume {resume_id}: {str(e)}")
            resume.processing_status = "failed"
            resumes_db[resume_id] = resume
        
        # Create response
        resume_out = ResumeOut(
            _id=resume_id,
            user_id=current_user.user_id,
            filename=file.filename,
            upload_date=resume.upload_date,
            file_url=file_path,
            parsed_sections=resume.parsed_sections,
            ai_feedback=resume.ai_feedback,
            processing_status=resume.processing_status
        )
        
        return {
            "success": True,
            "message": "Resume uploaded and processed successfully",
            "data": {
                "resume": resume_out.dict(),
                "processing_time": "< 1 minute",
                "next_steps": [
                    "Review AI feedback and suggestions",
                    "Update your profile with extracted skills",
                    "Apply to relevant job postings"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error uploading resume for user {current_user.user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing resume: {str(e)}"
        )


@router.get("/{resume_id}/feedback", response_model=Dict[str, Any])
async def get_resume_feedback(
    resume_id: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Get AI feedback for a specific resume.
    
    This endpoint returns detailed AI analysis and feedback for a resume,
    including ATS compatibility score, formatting suggestions, and skill analysis.
    
    Args:
        resume_id: The ID of the resume to get feedback for
        current_user: Current authenticated user
        
    Returns:
        Dict containing detailed AI feedback and analysis
        
    Raises:
        HTTPException: If resume not found or access denied
    """
    # Check if resume exists
    if resume_id not in resumes_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    resume = resumes_db[resume_id]
    
    # Check ownership (students can only access their own resumes, employers can access applied resumes)
    if (current_user.role == UserRole.STUDENT and resume.user_id != current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resume"
        )
    
    # Check if processing is complete
    if resume.processing_status == "processing":
        return {
            "success": True,
            "message": "Resume is still being processed",
            "data": {
                "status": "processing",
                "estimated_completion": "< 1 minute"
            }
        }
    
    if resume.processing_status == "failed":
        return {
            "success": False,
            "message": "Resume processing failed",
            "data": {
                "status": "failed",
                "error": "Unable to process resume file"
            }
        }
    
    if not resume.ai_feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback available for this resume"
        )
    
    return {
        "success": True,
        "message": "Resume feedback retrieved successfully",
        "data": {
            "resume_id": resume_id,
            "feedback": resume.ai_feedback.dict(),
            "parsed_sections": resume.parsed_sections.dict() if resume.parsed_sections else None,
            "processing_date": resume.upload_date.isoformat(),
            "recommendations": _generate_action_items(resume.ai_feedback)
        }
    }


@router.get("/{resume_id}/parsed", response_model=Dict[str, Any])
async def get_parsed_resume(
    resume_id: str,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Get parsed resume sections and extracted information.
    
    Args:
        resume_id: The ID of the resume to get parsed data for
        current_user: Current authenticated user
        
    Returns:
        Dict containing parsed resume sections and metadata
        
    Raises:
        HTTPException: If resume not found or access denied
    """
    # Check if resume exists
    if resume_id not in resumes_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    resume = resumes_db[resume_id]
    
    # Check ownership
    if (current_user.role == UserRole.STUDENT and resume.user_id != current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resume"
        )
    
    return {
        "success": True,
        "message": "Parsed resume data retrieved successfully",
        "data": {
            "resume_id": resume_id,
            "filename": resume.filename,
            "upload_date": resume.upload_date.isoformat(),
            "parsed_sections": resume.parsed_sections.dict() if resume.parsed_sections else None,
            "processing_status": resume.processing_status,
            "text_length": len(resume.parsed_text) if resume.parsed_text else 0
        }
    }


@router.get("/", response_model=Dict[str, Any])
async def get_user_resumes(
    current_user: TokenData = Depends(require_student())
):
    """
    Get all resumes for the current user.
    
    Args:
        current_user: Current authenticated student user
        
    Returns:
        Dict containing list of user's resumes
    """
    user_resume_ids = user_resumes.get(current_user.user_id, [])
    
    if not user_resume_ids:
        return {
            "success": True,
            "message": "No resumes found",
            "data": {
                "resumes": [],
                "total": 0
            }
        }
    
    # Get resume details
    user_resume_list = []
    for resume_id in user_resume_ids:
        if resume_id in resumes_db:
            resume = resumes_db[resume_id]
            resume_out = ResumeOut(
                _id=resume_id,
                user_id=resume.user_id,
                filename=resume.filename,
                upload_date=resume.upload_date,
                file_url=resume.original_file_url,
                parsed_sections=resume.parsed_sections,
                ai_feedback=resume.ai_feedback,
                processing_status=resume.processing_status
            )
            user_resume_list.append(resume_out.dict())
    
    return {
        "success": True,
        "message": f"Found {len(user_resume_list)} resumes",
        "data": {
            "resumes": user_resume_list,
            "total": len(user_resume_list)
        }
    }


@router.delete("/{resume_id}", response_model=SuccessResponse)
async def delete_resume(
    resume_id: str,
    current_user: TokenData = Depends(require_student())
):
    """
    Delete a resume.
    
    Args:
        resume_id: The ID of the resume to delete
        current_user: Current authenticated student user
        
    Returns:
        Success response confirming deletion
        
    Raises:
        HTTPException: If resume not found or access denied
    """
    # Check if resume exists
    if resume_id not in resumes_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )
    
    resume = resumes_db[resume_id]
    
    # Check ownership
    if resume.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this resume"
        )
    
    try:
        # Delete file from storage
        if os.path.exists(resume.original_file_url):
            os.remove(resume.original_file_url)
        
        # Remove from database
        del resumes_db[resume_id]
        
        # Remove from user's resume list
        if current_user.user_id in user_resumes:
            user_resumes[current_user.user_id] = [
                rid for rid in user_resumes[current_user.user_id] 
                if rid != resume_id
            ]
        
        logger.info(f"Successfully deleted resume {resume_id} for user {current_user.user_id}")
        
        return SuccessResponse(
            message="Resume deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error deleting resume {resume_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting resume"
        )


def _generate_action_items(feedback: AIFeedback) -> List[str]:
    """Generate actionable recommendations based on AI feedback."""
    action_items = []
    
    if feedback.ats_score < 70:
        action_items.append("Improve ATS compatibility by using standard section headers")
    
    if feedback.formatting_score < 70:
        action_items.append("Enhance formatting with consistent bullet points and structure")
    
    if feedback.completeness_score < 80:
        action_items.append("Add missing sections to make your resume more comprehensive")
    
    if len(feedback.skill_gaps) > 3:
        action_items.append("Consider learning high-demand skills to improve job prospects")
    
    action_items.extend(feedback.suggestions[:3])  # Add top 3 suggestions
    
    return action_items[:5]  # Return top 5 action items
