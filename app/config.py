from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Application Settings
    app_name: str = "Job Portal API"
    app_version: str = "1.0.0"
    debug: bool = True  # Set to True for development
    
    # Database Settings
    database_url: str = "sqlite:///./jobportal.db"  # Default to SQLite for development
    
    # Security Settings
    secret_key: str = "your-secret-key-change-this-in-production-make-it-really-long-and-random"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # File Upload Settings
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # AI/ML Settings (for future phases)
    model_path: str = "models"
    resume_similarity_threshold: float = 0.7
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env
        
    @property
    def allowed_file_extensions_list(self) -> List[str]:
        """Allowed file extensions for uploads"""
        return [".pdf", ".doc", ".docx"]
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Allowed origins for CORS"""
        return ["http://localhost:3000", "http://127.0.0.1:3000"]


# Global settings instance
settings = Settings()

# In-memory data storage (replace with actual database in production)
app_data = {
    "resumes": [],
    "jobs": [],
    "applications": [],
    "users": {}
}

# Ensure upload directory exists
def create_upload_directory():
    """Create upload directory if it doesn't exist"""
    if not os.path.exists(settings.upload_dir):
        os.makedirs(settings.upload_dir)
        
        # Create subdirectories for different file types
        subdirs = ["resumes", "company_logos", "temp"]
        for subdir in subdirs:
            subdir_path = os.path.join(settings.upload_dir, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)