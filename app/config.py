"""
Configuration settings for the AI-Powered Job Portal application.

This module handles all environment variables and application settings
using Pydantic's BaseSettings for type validation and environment loading.
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    """
    
    # Application settings
    app_name: str = "AI-Powered Job Portal"
    debug: bool = False
    
    # Security settings
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database settings (MongoDB)
    database_url: str = "mongodb://localhost:27017"
    database_name: str = "job_portal"
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = [".pdf", ".docx", ".doc"]
    upload_dir: str = "uploads"
    
    # AI/ML settings
    spacy_model: str = "en_core_web_sm"
    min_similarity_score: float = 0.1
    max_candidates_return: int = 50
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }

    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins from environment or default."""
        return [
            "http://localhost:3000",
            "http://localhost:8080", 
            "http://127.0.0.1:3000"
        ]

# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)
