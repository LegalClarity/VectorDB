"""
MongoDB document models for the Legal Document Upload System
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic models"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class FileMetadata(BaseModel):
    """File metadata schema"""
    content_type: str
    file_size: int
    file_hash: str
    upload_method: str


class DocumentMetadata(BaseModel):
    """Document metadata schema"""
    document_type: str = ""
    category: str = ""
    tags: List[str] = []
    description: str = ""
    confidentiality: str = "private"


class Timestamps(BaseModel):
    """Timestamp tracking"""
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None


class Status(BaseModel):
    """Document processing status"""
    upload_status: str = "pending"
    processing_status: str = "processing"
    validation_errors: List[str] = []


class Document(BaseModel):
    """Main document model for MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    document_id: str
    original_filename: str
    stored_filename: str
    gcs_bucket_name: str
    gcs_object_path: str
    file_metadata: FileMetadata
    document_metadata: DocumentMetadata
    timestamps: Timestamps
    status: Status

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class User(BaseModel):
    """User model for MongoDB"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    email: str
    name: str
    organization: str = ""
    role: str = "client"
    created_at: datetime
    last_active: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DocumentCreateRequest(BaseModel):
    """Request model for creating a document"""
    user_id: str
    document_type: Optional[str] = ""
    category: Optional[str] = ""
    tags: Optional[List[str]] = []
    description: Optional[str] = ""
    confidentiality: Optional[str] = "private"


class DocumentUpdateRequest(BaseModel):
    """Request model for updating document metadata"""
    document_type: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    confidentiality: Optional[str] = None


class UploadResponse(BaseModel):
    """Response model for successful upload"""
    document_id: str
    gcs_url: str
    message: str = "Document uploaded successfully"


class BatchUploadResponse(BaseModel):
    """Response model for batch upload"""
    total_files: int
    successful_uploads: int
    failed_uploads: int
    results: List[dict]


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: dict
