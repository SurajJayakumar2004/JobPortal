# AI-Powered Job Portal Backend

A comprehensive FastAPI-based backend for an intelligent job portal that uses AI for resume parsing, candidate matching, and career counseling.

## Features

- **AI-Driven Resume Screening**: Intelligent parsing of PDF/DOCX resumes with skill extraction and ATS compatibility scoring
- **Smart Job Matching**: AI-powered candidate-job matching using TF-IDF and cosine similarity
- **Career Counseling**: Automated career path suggestions and skill gap analysis
- **Employer Portal**: Complete job posting and candidate management system
- **Secure Authentication**: JWT-based authentication with role-based access control

## Technology Stack

- **Backend**: Python 3.10+ with FastAPI
- **AI/ML**: spaCy, scikit-learn, PyMuPDF, NLTK
- **Database Models**: Pydantic (ready for MongoDB with Beanie ODM)
- **Authentication**: JWT tokens
- **File Processing**: PyMuPDF, python-docx
- **API Documentation**: Automatic OpenAPI/Swagger docs

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd JobPortal
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

### Running the Application

1. Start the development server:
```bash
uvicorn main:app --reload
```

2. Access the application:
- API Documentation: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Resumes
- `POST /resumes/upload` - Upload and parse resume
- `GET /resumes/{resume_id}/feedback` - Get AI feedback

### Jobs
- `POST /jobs` - Create job posting
- `GET /jobs` - List jobs
- `GET /jobs/{job_id}/candidates` - Get ranked candidates for a job

### Applications
- `POST /applications` - Apply to a job
- `GET /applications` - Get user applications

### Career Counseling
- `POST /counseling/generate` - Generate career advice

## Project Structure

```
JobPortal/
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── README.md                 # Project documentation
├── app/
│   ├── __init__.py
│   ├── schemas.py            # Pydantic models
│   ├── config.py             # Configuration settings
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication routes
│   │   ├── resumes.py        # Resume management routes
│   │   ├── jobs.py           # Job posting routes
│   │   ├── applications.py   # Application routes
│   │   └── counseling.py     # Career counseling routes
│   ├── services/
│   │   ├── __init__.py
│   │   ├── resume_parser.py  # AI resume parsing service
│   │   ├── matching_service.py # Job-candidate matching
│   │   ├── auth_service.py   # Authentication logic
│   │   └── counseling_service.py # Career counseling AI
│   └── utils/
│       ├── __init__.py
│       ├── dependencies.py   # FastAPI dependencies
│       └── security.py       # Security utilities
└── uploads/                  # Resume upload directory
```

## Development Notes

- The project uses Pydantic models extensively for data validation
- Database models are designed for MongoDB compatibility using Beanie ODM patterns
- AI services use spaCy for NLP and scikit-learn for matching algorithms
- All endpoints include proper error handling and validation
- The codebase follows modern Python best practices with type hints

## Next Steps

1. Set up MongoDB database and configure Beanie ODM
2. Implement proper file storage (cloud storage integration)
3. Add comprehensive test coverage
4. Set up CI/CD pipeline
5. Add rate limiting and API versioning
6. Implement advanced ML models for better matching accuracy
