"""
Configuration settings for Document Analyzer API
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    # Google Cloud Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL_FLASH")
    GOOGLE_PROJECT_ID: str = os.getenv("GOOGLE_PROJECT_ID")
    GOOGLE_REGION: str = os.getenv("GOOGLE_REGION")
    USER_DOC_BUCKET: str = os.getenv("USER_DOC_BUCKET")
    GOOGLE_CREDENTIALS_PATH: Optional[str] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Qdrant Configuration
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    QDRANT_HOST: str = os.getenv("QDRANT_HOST")

    # MongoDB Configuration
    MONGO_URI: str = os.getenv("MONGO_URI")
    MONGO_DB: str = os.getenv("MONGO_DB")
    MONGO_USERS_COLLECTION: str = os.getenv("MONGO_USERS_COLLECTION")
    MONGO_DOCS_COLLECTION: str = os.getenv("MONGO_DOCS_COLLECTION")
    MONGO_PROCESSED_DOCS_COLLECTION: str = os.getenv("MONGO_PROCESSED_DOCS_COLLECTION")

    # Application Configuration
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_WORKERS: int = int(os.getenv("API_WORKERS", "1"))

    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # File Processing Configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    ALLOWED_FILE_TYPES: list = [".pdf", ".txt", ".docx"]

    # Analysis Configuration
    MAX_EXTRACTION_PASSES: int = int(os.getenv("MAX_EXTRACTION_PASSES", "2"))
    EXTRACTION_TIMEOUT_SECONDS: int = int(os.getenv("EXTRACTION_TIMEOUT_SECONDS", "300"))

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
