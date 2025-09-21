"""
Enhanced Legal Document Processing Models and Schemas
Based on the comprehensive legal schemas and LangExtract best practices
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Enhanced Request Models
class DocumentType(str, Enum):
    RENTAL_AGREEMENT = "rental_agreement"
    LOAN_AGREEMENT = "loan_agreement"
    TERMS_OF_SERVICE = "terms_of_service"
    CONTRACT = "contract"
    LEGAL_DOCUMENT = "legal_document"

class ProcessingPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal" 
    HIGH = "high"
    URGENT = "urgent"

class DocumentAnalysisRequest(BaseModel):
    document_id: str = Field(
        ..., 
        description="Document ID from MongoDB",
        example="c0133bb6-f25a-4114-a4c3-1b1e8630e27f",
        min_length=1
    )
    user_id: Optional[str] = Field(
        None,
        description="User ID for security and access control",
        example="e0722091-aaeb-43f3-8cac-d6562c85ec79"
    )
    document_type: DocumentType = Field(
        DocumentType.LEGAL_DOCUMENT,
        description="Type of legal document for specialized processing"
    )
    analysis_options: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional analysis configuration options",
        example={
            "include_risk_assessment": True,
            "include_compliance_check": True,
            "extract_financial_terms": True,
            "identify_parties": True
        }
    )
    priority: ProcessingPriority = Field(
        ProcessingPriority.NORMAL,
        description="Processing priority level"
    )
    
    @validator('document_id')
    def validate_document_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Document ID cannot be empty')
        return v.strip()

class DocumentExtractionRequest(BaseModel):
    document_id: str = Field(
        ..., 
        description="Document ID from MongoDB",
        example="c0133bb6-f25a-4114-a4c3-1b1e8630e27f",
        min_length=1
    )
    user_id: Optional[str] = Field(
        None,
        description="User ID for security and access control",
        example="e0722091-aaeb-43f3-8cac-d6562c85ec79"
    )
    document_type: DocumentType = Field(
        DocumentType.RENTAL_AGREEMENT,
        description="Type of legal document for specialized clause extraction"
    )
    extraction_options: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "extract_parties": True,
            "extract_financial_terms": True,
            "extract_dates": True,
            "extract_obligations": True,
            "extract_conditions": True,
            "extract_relationships": True
        },
        description="Specific extraction configuration options"
    )
    include_source_grounding: bool = Field(
        True,
        description="Include source text locations for extractions"
    )
    priority: ProcessingPriority = Field(
        ProcessingPriority.NORMAL,
        description="Processing priority level"
    )
    
    @validator('document_id')
    def validate_document_id(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Document ID cannot be empty')
        return v.strip()

# Enhanced Response Models
class ExtractedEntity(BaseModel):
    entity_class: str = Field(..., description="Type of extracted entity")
    entity_text: str = Field(..., description="Exact text from document")
    confidence: float = Field(..., description="Extraction confidence score", ge=0.0, le=1.0)
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Entity attributes and metadata")
    source_location: Optional[Dict[str, Any]] = Field(None, description="Location in source document")

class LegalClause(BaseModel):
    clause_id: str = Field(..., description="Unique clause identifier")
    clause_type: str = Field(..., description="Type of legal clause")
    clause_text: str = Field(..., description="Full clause text")
    clause_summary: Optional[str] = Field(None, description="Brief clause summary")
    key_terms: List[str] = Field(default_factory=list, description="Key terms in clause")
    obligations: List[str] = Field(default_factory=list, description="Obligations defined")
    rights: List[str] = Field(default_factory=list, description="Rights defined")
    conditions: List[str] = Field(default_factory=list, description="Conditions specified")
    source_location: Optional[Dict[str, Any]] = Field(None, description="Source location")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)

class ClauseRelationship(BaseModel):
    relationship_id: str = Field(..., description="Unique relationship identifier")
    relationship_type: str = Field(..., description="Type of relationship")
    source_clause_id: str = Field(..., description="Source clause ID")
    target_clause_id: str = Field(..., description="Target clause ID")
    relationship_description: str = Field(..., description="Description of relationship")
    strength: Optional[float] = Field(None, description="Relationship strength", ge=0.0, le=1.0)

class RiskAssessment(BaseModel):
    overall_risk_level: str = Field(..., description="Overall risk level")
    risk_score: float = Field(..., description="Numerical risk score", ge=0.0, le=100.0)
    risk_factors: List[Dict[str, Any]] = Field(default_factory=list, description="Identified risk factors")
    recommendations: List[str] = Field(default_factory=list, description="Risk mitigation recommendations")
    high_risk_clauses: List[str] = Field(default_factory=list, description="High-risk clause IDs")

class ComplianceCheck(BaseModel):
    compliance_score: float = Field(..., description="Overall compliance score", ge=0.0, le=100.0)
    compliant_areas: List[str] = Field(default_factory=list, description="Areas of compliance")
    non_compliant_areas: List[str] = Field(default_factory=list, description="Areas of non-compliance")
    recommendations: List[str] = Field(default_factory=list, description="Compliance recommendations")
    legal_framework: Optional[str] = Field(None, description="Applicable legal framework")

class AnalysisResult(BaseModel):
    document_id: str = Field(..., description="Document ID")
    document_type: str = Field(..., description="Document type")
    processing_timestamp: datetime = Field(..., description="When analysis was completed")
    extracted_entities: List[ExtractedEntity] = Field(
        default_factory=list, 
        description="Entities extracted from document"
    )
    key_terms: List[str] = Field(
        default_factory=list,
        description="Important terms identified"
    )
    risk_assessment: RiskAssessment = Field(..., description="Risk analysis results")
    compliance_check: ComplianceCheck = Field(..., description="Compliance analysis results")
    summary: str = Field(..., description="Executive summary of analysis")
    actionable_insights: List[str] = Field(
        default_factory=list,
        description="Actionable insights from analysis"
    )
    processing_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Processing metadata and statistics"
    )

class ExtractionResult(BaseModel):
    document_id: str = Field(..., description="Document ID")
    document_type: str = Field(..., description="Document type")
    processing_timestamp: datetime = Field(..., description="When extraction was completed")
    extracted_clauses: List[LegalClause] = Field(
        default_factory=list,
        description="Legal clauses extracted from document"
    )
    clause_relationships: List[ClauseRelationship] = Field(
        default_factory=list,
        description="Relationships between clauses"
    )
    parties_identified: List[ExtractedEntity] = Field(
        default_factory=list,
        description="Parties involved in the document"
    )
    financial_terms: List[ExtractedEntity] = Field(
        default_factory=list,
        description="Financial terms and amounts"
    )
    important_dates: List[ExtractedEntity] = Field(
        default_factory=list,
        description="Important dates and deadlines"
    )
    obligations_and_rights: List[ExtractedEntity] = Field(
        default_factory=list,
        description="Obligations and rights identified"
    )
    source_grounding: Dict[str, Any] = Field(
        default_factory=dict,
        description="Source text grounding information"
    )
    extraction_confidence: float = Field(..., description="Overall extraction confidence", ge=0.0, le=1.0)
    processing_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Processing metadata and statistics"
    )

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ApiResponse(BaseModel):
    success: bool = Field(True, description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[Union[AnalysisResult, ExtractionResult, Dict[str, Any]]] = Field(
        None, 
        description="Response data"
    )
    error: Optional[str] = Field(None, description="Error message if any")
    meta: Optional[Dict[str, Any]] = Field(
        None, 
        description="Response metadata",
        example={
            "processing_time": 2.5,
            "document_size": 1024,
            "model_used": "gemini-2.5-flash",
            "extraction_method": "langextract"
        }
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

# Status Response Models
class ProcessingStatusResponse(BaseModel):
    document_id: str = Field(..., description="Document ID")
    status: ProcessingStatus = Field(..., description="Current processing status")
    progress_percentage: Optional[float] = Field(None, description="Processing progress", ge=0.0, le=100.0)
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    started_at: Optional[datetime] = Field(None, description="Processing start time")
    completed_at: Optional[datetime] = Field(None, description="Processing completion time")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")

# Error Models
class DocumentNotFoundError(BaseModel):
    error_type: str = Field("document_not_found", description="Error type")
    message: str = Field(..., description="Error message")
    document_id: str = Field(..., description="Document ID that was not found")

class ProcessingError(BaseModel):
    error_type: str = Field("processing_error", description="Error type") 
    message: str = Field(..., description="Error message")
    document_id: str = Field(..., description="Document ID being processed")
    stage: str = Field(..., description="Processing stage where error occurred")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")