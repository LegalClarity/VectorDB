"""
Pydantic schemas for API request/response validation
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class FileMetadataSchema(BaseModel):
    """File metadata API schema"""
    content_type: str
    file_size: int
    file_hash: str
    upload_method: str


class DocumentMetadataSchema(BaseModel):
    """Document metadata API schema"""
    document_type: str = ""
    category: str = ""
    tags: List[str] = []
    description: str = ""
    confidentiality: str = "private"


class TimestampsSchema(BaseModel):
    """Timestamp API schema"""
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None


class StatusSchema(BaseModel):
    """Status API schema"""
    upload_status: str = "pending"
    processing_status: str = "processing"
    validation_errors: List[str] = []


class DocumentResponse(BaseModel):
    """Document response schema"""
    user_id: str
    document_id: str
    original_filename: str
    stored_filename: str
    gcs_bucket_name: str
    gcs_object_path: str
    file_metadata: FileMetadataSchema
    document_metadata: DocumentMetadataSchema
    timestamps: TimestampsSchema
    status: StatusSchema

    model_config = {
        "from_attributes": True
    }


class UserResponse(BaseModel):
    """User response schema"""
    user_id: str
    email: str
    name: str
    organization: str = ""
    role: str = "client"
    created_at: datetime
    last_active: datetime

    model_config = {
        "from_attributes": True
    }


class UploadRequest(BaseModel):
    """Upload request schema (for metadata only)"""
    user_id: str
    document_type: Optional[str] = ""
    category: Optional[str] = ""
    tags: Optional[List[str]] = []
    description: Optional[str] = ""
    confidentiality: Optional[str] = "private"


class BatchUploadRequest(BaseModel):
    """Batch upload request schema"""
    user_id: str
    files_metadata: List[UploadRequest]


class DocumentListResponse(BaseModel):
    """Document list response schema"""
    documents: List[DocumentResponse]
    total_count: int
    page: int = 1
    page_size: int = 10


class DocumentFilter(BaseModel):
    """Document filtering options"""
    document_type: Optional[str] = None
    category: Optional[str] = None
    confidentiality: Optional[str] = None
    tags: Optional[List[str]] = None
    upload_status: Optional[str] = None


class SignedURLRequest(BaseModel):
    """Request for signed GCS URL"""
    user_id: str
    document_id: str
    expiration_minutes: int = 60


class SignedURLResponse(BaseModel):
    """Response with signed GCS URL"""
    document_id: str
    signed_url: str
    expires_at: datetime


class ValidationResult(BaseModel):
    """File validation result"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    services: dict
