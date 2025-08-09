"""
Main FastAPI application entry point for the AI-Powered Job Portal.

This file initializes the FastAPI application, configures middleware,
includes all routers, and sets up the basic application structure.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

from app.routers import auth, jobs, applications, employers, counseling, job_generator  # resumes temporarily disabled
# from app.routers.ai_analysis import router as ai_analysis_router  # Temporarily disabled
from app.config import settings

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle application startup and shutdown events.
    """
    # Startup
    print("🚀 Starting AI-Powered Job Portal...")
    print("📊 Initializing AI models...")
    
    # Here you would typically initialize:
    # - Database connections
    # - ML models
    # - Cache connections
    # - External service clients
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Job Portal...")

# Initialize FastAPI application
app = FastAPI(
    title="AI-Powered Job Portal API",
    description="A comprehensive backend API for an intelligent job portal with AI-driven resume screening, job matching, and career counseling.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Include routers with proper prefixes
# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
# app.include_router(resumes.router, prefix="/api/resumes", tags=["Resumes"])  # Temporarily disabled
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(employers.router, prefix="/api/employers", tags=["Employers"])
app.include_router(counseling.router, prefix="/api/counseling", tags=["Career Counseling"])
app.include_router(job_generator.router, prefix="/api/job-generator", tags=["Job Generator"])
# app.include_router(ai_analysis_router, prefix="/api/ai", tags=["AI Analysis"])  # Temporarily disabled

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "message": "Welcome to AI-Powered Job Portal API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    """
    return {
        "status": "healthy",
        "service": "ai-job-portal-api",
        "version": "1.0.0"
    }

# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Global HTTP exception handler.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

# Global exception handler for unhandled exceptions
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ Error: uvicorn not found!")
        print("Please run the application using one of these methods:")
        print("1. ./venv/bin/uvicorn main:app --reload")
        print("2. source venv/bin/activate && uvicorn main:app --reload")
        print("3. ./venv/bin/python -m uvicorn main:app --reload")
