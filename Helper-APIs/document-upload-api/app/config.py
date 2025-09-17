"""
Configuration settings for the Legal Document Upload API
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # MongoDB Configuration
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    mongo_db: str = os.getenv("MONGO_DB", "LegalClarity")
    mongo_users_collection: str = os.getenv("MONGO_USERS_COLLECTION", "users")
    mongo_docs_collection: str = os.getenv("MONGO_DOCS_COLLECTION", "documents")

    # Google Cloud Storage Configuration
    google_project_id: str = os.getenv("GOOGLE_PROJECT_ID", "")
    google_region: str = os.getenv("GOOGLE_REGION", "asia-south1")
    user_doc_bucket: str = os.getenv("USER_DOC_BUCKET", "")
    gcs_service_account_path: Optional[str] = os.getenv("GCS_SERVICE_ACCOUNT_PATH")

    # Gemini API (for potential future use)
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")

    # File Upload Configuration
    max_upload_size: int = int(os.getenv("MAX_UPLOAD_SIZE", "15728640"))  # 15MB default
    allowed_extensions: set = {'.pdf', '.docx', '.doc', '.txt'}
    allowed_mime_types: set = {
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain'
    }

    # Application Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Security Configuration
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # VectorDB Configuration (for future integration)
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    qdrant_host: str = os.getenv("QDRANT_HOST", "")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env file


# Global settings instance
settings = Settings()
