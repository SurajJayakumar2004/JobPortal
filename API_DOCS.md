# API Documentation - AI-Powered Job Portal

## Overview

The AI-Powered Job Portal provides a comprehensive RESTful API for managing job applications, resume parsing, and AI-driven career counseling. This API serves both students (job seekers) and employers with intelligent matching and recommendation features.

## Base URL

```
http://localhost:8000
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

## API Endpoints

### Authentication Endpoints

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "role": "student",
  "profile": {
    "name": "John Doe",
    "phone": "+1234567890",
    "skills": ["Python", "JavaScript", "React"],
    "interests": ["Software Development", "AI"],
    "location": "San Francisco, CA",
    "bio": "Passionate software developer"
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": "user_id",
      "email": "user@example.com",
      "role": "student",
      "profile": {...},
      "created_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

#### POST /auth/login
Authenticate and receive access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": {
      "id": "user_id",
      "email": "user@example.com",
      "role": "student"
    }
  }
}
```

### Resume Management Endpoints

#### POST /resumes/upload
Upload and parse a resume file.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Authentication: Required (Student role)

**Form Data:**
- `file`: Resume file (PDF or DOCX, max 10MB)

**Response:**
```json
{
  "success": true,
  "message": "Resume uploaded and processed successfully",
  "data": {
    "resume": {
      "id": "resume_id",
      "filename": "john_doe_resume.pdf",
      "upload_date": "2024-01-01T00:00:00Z",
      "processing_status": "completed",
      "ai_feedback": {
        "ats_score": 85.5,
        "formatting_score": 90.0,
        "completeness_score": 88.0,
        "suggestions": ["Add more quantifiable achievements"],
        "strengths": ["Strong technical skills section"],
        "skill_gaps": ["Cloud Computing", "Machine Learning"]
      }
    }
  }
}
```

#### GET /resumes/{resume_id}/feedback
Get AI feedback for a specific resume.

**Response:**
```json
{
  "success": true,
  "message": "Resume feedback retrieved successfully",
  "data": {
    "resume_id": "resume_id",
    "feedback": {
      "ats_score": 85.5,
      "suggestions": [...],
      "strengths": [...],
      "skill_gaps": [...]
    },
    "recommendations": [
      "Improve ATS compatibility",
      "Add more keywords"
    ]
  }
}
```

### Job Management Endpoints

#### POST /jobs
Create a new job posting (Employer only).

**Request Body:**
```json
{
  "title": "Senior Software Engineer",
  "description": "We are looking for an experienced software engineer...",
  "required_skills": ["Python", "Django", "PostgreSQL", "AWS"],
  "location": "San Francisco, CA",
  "experience_level": "senior",
  "employment_type": "full-time",
  "salary_range": "$120,000 - $160,000",
  "company_name": "Tech Corp Inc."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Job posting created successfully",
  "data": {
    "job": {
      "id": "job_id",
      "title": "Senior Software Engineer",
      "description": "...",
      "required_skills": [...],
      "status": "open",
      "posted_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

#### GET /jobs
List available job postings with filtering.

**Query Parameters:**
- `skip`: Number of jobs to skip (pagination)
- `limit`: Number of jobs to return (max 100)
- `location`: Filter by location
- `experience_level`: Filter by experience level
- `skills`: Filter by skills (comma-separated)

**Response:**
```json
{
  "success": true,
  "message": "Found 25 jobs",
  "data": {
    "jobs": [...],
    "pagination": {
      "total": 25,
      "skip": 0,
      "limit": 20,
      "has_more": true
    }
  }
}
```

#### GET /jobs/{job_id}/candidates
Get AI-ranked candidates for a job (Employer only).

**Response:**
```json
{
  "success": true,
  "message": "Found 15 candidates for this job",
  "data": {
    "job_id": "job_id",
    "job_title": "Senior Software Engineer",
    "total_candidates": 15,
    "candidates": [
      {
        "user_id": "candidate_id",
        "user_name": "Jane Smith",
        "user_email": "jane@example.com",
        "match_score": 0.92,
        "matching_skills": ["Python", "Django", "AWS"],
        "missing_skills": ["PostgreSQL"],
        "experience_level": "senior"
      }
    ],
    "average_match_score": 0.78
  }
}
```

### Application Endpoints

#### POST /applications
Apply to a job posting (Student only).

**Request Body:**
```json
{
  "job_id": "job_id",
  "resume_id": "resume_id",
  "cover_letter": "I am very interested in this position..."
}
```

**Response:**
```json
{
  "success": true,
  "message": "Application submitted successfully",
  "data": {
    "application": {
      "id": "application_id",
      "job_id": "job_id",
      "status": "applied",
      "applied_at": "2024-01-01T00:00:00Z"
    },
    "job_info": {
      "title": "Senior Software Engineer",
      "company": "Tech Corp Inc."
    }
  }
}
```

#### GET /applications
Get applications for current user.

**Response (Student):**
```json
{
  "success": true,
  "message": "Found 5 applications",
  "data": {
    "applications": [
      {
        "id": "application_id",
        "status": "reviewed",
        "applied_at": "2024-01-01T00:00:00Z",
        "job_info": {
          "title": "Senior Software Engineer",
          "company": "Tech Corp Inc."
        }
      }
    ],
    "total": 5
  }
}
```

### Career Counseling Endpoints

#### POST /counseling/generate
Generate AI-powered career counseling report.

**Query Parameters:**
- `target_role`: Target role for guidance (optional)
- `interests`: User interests, comma-separated (optional)

**Response:**
```json
{
  "success": true,
  "message": "Career counseling report generated successfully",
  "data": {
    "report": {
      "id": "report_id",
      "generated_on": "2024-01-01T00:00:00Z",
      "overall_score": 78.5,
      "skills_summary": [...],
      "suggested_paths": [
        {
          "title": "Data Scientist",
          "description": "Analyze complex data...",
          "required_skills": ["Python", "Statistics", "ML"],
          "growth_potential": "Very High",
          "average_salary": "$90,000 - $150,000"
        }
      ],
      "missing_skills": ["Machine Learning", "Statistics"],
      "recommended_resources": [
        "Coursera - Data Science Specialization",
        "Kaggle Learn - Free Data Science Courses"
      ]
    }
  }
}
```

#### GET /counseling/skill-recommendations
Get skill recommendations for target role.

**Query Parameters:**
- `target_role`: Target role (required)

**Response:**
```json
{
  "success": true,
  "message": "Skill recommendations generated for Data Scientist",
  "data": {
    "target_role": "Data Scientist",
    "current_skills": ["Python", "SQL"],
    "recommendations": {
      "required_skills": ["Python", "Statistics", "Machine Learning"],
      "recommended_skills": ["Deep Learning", "TensorFlow"],
      "missing_skills": ["Statistics", "Machine Learning"]
    },
    "skill_gap_analysis": {
      "skill_coverage": 33.3
    }
  }
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": true,
  "message": "Error description",
  "status_code": 400
}
```

### Common HTTP Status Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Rate Limiting

API endpoints are rate-limited to prevent abuse:
- Authentication endpoints: 5 requests per minute
- Upload endpoints: 10 requests per hour
- Other endpoints: 100 requests per minute

## Data Models

### User Roles
- `student`: Job seekers who can upload resumes and apply to jobs
- `employer`: Companies who can post jobs and manage applications

### Application Status
- `applied`: Initial application submitted
- `reviewed`: Application has been reviewed
- `shortlisted`: Candidate has been shortlisted
- `interviewed`: Candidate has been interviewed
- `rejected`: Application rejected
- `hired`: Candidate hired

### File Types
Supported resume file formats:
- PDF (.pdf)
- Microsoft Word (.docx, .doc)

Maximum file size: 10MB

## Testing

Use the provided test endpoints to verify functionality:

### Health Check
```
GET /health
```

### API Documentation
- Interactive docs: `GET /docs`
- Alternative docs: `GET /redoc`

## Example Usage

### Complete Workflow Example

1. **Register a student account:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123",
    "role": "student",
    "profile": {
      "name": "John Student",
      "skills": ["Python", "JavaScript"]
    }
  }'
```

2. **Login and get token:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123"
  }'
```

3. **Upload resume:**
```bash
curl -X POST "http://localhost:8000/resumes/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@resume.pdf"
```

4. **Search for jobs:**
```bash
curl -X GET "http://localhost:8000/jobs?skills=Python" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

5. **Apply to a job:**
```bash
curl -X POST "http://localhost:8000/applications" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "JOB_ID",
    "resume_id": "RESUME_ID",
    "cover_letter": "I am interested in this position..."
  }'
```

This API provides a complete backend solution for an intelligent job portal with AI-driven features for resume analysis, candidate matching, and career guidance.
