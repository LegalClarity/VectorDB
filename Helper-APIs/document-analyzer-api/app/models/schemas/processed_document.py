"""
Processed Document Schema for MongoDB Storage
Schema for storing analyzed legal documents with extracted clauses and metadata
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from decimal import Decimal


class ExtractedEntity(BaseModel):
    """Individual extracted entity from document analysis"""

    class_name: str = Field(..., description="Entity classification (e.g., lessor_name, monthly_rent)")
    text: str = Field(..., description="Extracted text from document")
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Additional attributes for the entity")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence score")
    source_location: Dict[str, Any] = Field(..., description="Location in source document")


class SourceGrounding(BaseModel):
    """Source grounding information for legal verification"""

    original_text: str = Field(..., description="Original text from document")
    extracted_value: str = Field(..., description="Extracted value")
    verification_needed: bool = Field(True, description="Whether manual verification is needed")


class ExtractionMetadata(BaseModel):
    """Metadata about the extraction process"""

    total_extractions: int = Field(..., ge=0, description="Total number of entities extracted")
    processing_timestamp: datetime = Field(default_factory=datetime.utcnow, description="When extraction was performed")
    extraction_confidence: float = Field(..., ge=0.0, le=1.0, description="Overall extraction confidence")
    processing_time_seconds: float = Field(..., ge=0.0, description="Time taken for extraction")


class DocumentClauses(BaseModel):
    """Structured clauses extracted from the document"""

    financial_clauses: List[Dict[str, Any]] = Field(default_factory=list, description="Financial terms and conditions")
    legal_clauses: List[Dict[str, Any]] = Field(default_factory=list, description="Legal obligations and rights")
    operational_clauses: List[Dict[str, Any]] = Field(default_factory=list, description="Operational terms")
    compliance_clauses: List[Dict[str, Any]] = Field(default_factory=list, description="Compliance requirements")
    termination_clauses: List[Dict[str, Any]] = Field(default_factory=list, description="Termination conditions")
    dispute_resolution_clauses: List[Dict[str, Any]] = Field(default_factory=list, description="Dispute resolution mechanisms")


class RiskAssessment(BaseModel):
    """Risk assessment results"""

    overall_risk_level: str = Field(..., description="Low/Medium/High/Critical")
    risk_factors: List[Dict[str, Any]] = Field(default_factory=list, description="Identified risk factors")
    risk_score: float = Field(..., ge=0.0, le=10.0, description="Quantitative risk score")
    recommendations: List[str] = Field(default_factory=list, description="Risk mitigation recommendations")


class ComplianceCheck(BaseModel):
    """Compliance check results"""

    indian_law_compliance: Dict[str, Any] = Field(..., description="Compliance with Indian laws")
    regulatory_requirements: List[Dict[str, Any]] = Field(default_factory=list, description="Regulatory compliance status")
    mandatory_disclosures: List[str] = Field(default_factory=list, description="Required disclosures present")
    compliance_score: float = Field(..., ge=0.0, le=100.0, description="Compliance percentage score")


class FinancialAnalysis(BaseModel):
    """Financial implications and analysis"""

    monetary_values: List[Dict[str, Any]] = Field(default_factory=list, description="All monetary values extracted")
    payment_obligations: List[Dict[str, Any]] = Field(default_factory=list, description="Payment obligations")
    financial_risks: List[str] = Field(default_factory=list, description="Financial risk factors")
    cost_benefit_analysis: Optional[Dict[str, Any]] = Field(None, description="Basic cost-benefit analysis")


class DocumentAnalysisResult(BaseModel):
    """Complete analysis result for a processed document"""

    document_id: str = Field(..., description="Original document ID")
    document_type: str = Field(..., description="Type of document (rental/loan/tos)")
    user_id: str = Field(..., description="User who owns the document")

    # Extraction Results
    extracted_entities: List[ExtractedEntity] = Field(default_factory=list, description="All extracted entities")
    source_grounding: Dict[str, SourceGrounding] = Field(default_factory=dict, description="Source verification data")
    extraction_metadata: ExtractionMetadata = Field(..., description="Extraction process metadata")

    # Structured Analysis
    document_clauses: DocumentClauses = Field(..., description="Structured clauses by category")
    risk_assessment: RiskAssessment = Field(..., description="Risk assessment results")
    compliance_check: ComplianceCheck = Field(..., description="Compliance verification results")
    financial_analysis: FinancialAnalysis = Field(..., description="Financial analysis results")

    # Document Summary
    summary: str = Field(..., description="Human-readable summary of the document")
    key_terms: List[str] = Field(default_factory=list, description="Key terms and conditions")
    actionable_insights: List[str] = Field(default_factory=list, description="Actionable insights for user")

    # Processing Metadata
    processing_status: str = Field(..., description="Processing status (completed/failed/pending)")
    processing_version: str = Field("1.0", description="Processing pipeline version")
    processing_errors: List[str] = Field(default_factory=list, description="Any processing errors encountered")

    # Audit Trail
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When analysis was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="When analysis was last updated")
    processed_by: str = Field(..., description="Processing service identifier")

    class Config:
        """Pydantic configuration"""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }


class ProcessedDocumentSchema(BaseModel):
    """
    MongoDB schema for storing processed legal documents
    This collection stores the complete analysis results and extracted data
    """

    # MongoDB Document ID (auto-generated)
    id: Optional[str] = Field(None, alias="_id", description="MongoDB document ID")

    # Core Document Information
    document_id: str = Field(..., description="Original document ID from documents collection")
    document_type: str = Field(..., description="Type of document (rental/loan/tos)")
    user_id: str = Field(..., description="User who owns the document")

    # File Information
    file_name: str = Field(..., description="Original file name")
    file_size: int = Field(..., ge=0, description="File size in bytes")
    gcs_path: str = Field(..., description="Google Cloud Storage path")

    # Processing Information
    processing_id: str = Field(..., description="Unique processing job ID")
    processing_started_at: datetime = Field(default_factory=datetime.utcnow, description="When processing started")
    processing_completed_at: Optional[datetime] = Field(None, description="When processing completed")
    processing_duration_seconds: Optional[float] = Field(None, ge=0.0, description="Processing duration")

    # Analysis Results
    analysis_result: DocumentAnalysisResult = Field(..., description="Complete analysis results")

    # Processing Status
    status: str = Field(..., description="Processing status (pending/processing/completed/failed)")
    error_message: Optional[str] = Field(None, description="Error message if processing failed")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Document creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    version: str = Field("1.0", description="Schema version")

    # Indexing fields for efficient queries
    document_type_user_id: Optional[str] = Field(None, description="Compound index field")
    processing_status_date: Optional[str] = Field(None, description="Compound index for status queries")

    class Config:
        """Pydantic configuration"""
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "document_id": "doc_123456",
                "document_type": "rental",
                "user_id": "user_789",
                "file_name": "rental_agreement.pdf",
                "file_size": 245760,
                "gcs_path": "user_documents/user_789/rental_agreement.pdf",
                "processing_id": "proc_abcdef123456",
                "processing_started_at": "2025-09-18T10:00:00Z",
                "processing_completed_at": "2025-09-18T10:02:15Z",
                "processing_duration_seconds": 135.5,
                "analysis_result": {
                    "document_id": "doc_123456",
                    "document_type": "rental",
                    "user_id": "user_789",
                    "extraction_metadata": {
                        "total_extractions": 25,
                        "processing_timestamp": "2025-09-18T10:02:15Z",
                        "extraction_confidence": 0.89,
                        "processing_time_seconds": 135.5
                    },
                    "document_clauses": {
                        "financial_clauses": [
                            {
                                "type": "rent_amount",
                                "amount": 25000.0,
                                "frequency": "monthly",
                                "description": "Monthly rent payment"
                            }
                        ],
                        "legal_clauses": [
                            {
                                "type": "termination",
                                "notice_period_days": 30,
                                "description": "Termination conditions"
                            }
                        ]
                    },
                    "risk_assessment": {
                        "overall_risk_level": "medium",
                        "risk_score": 6.5,
                        "recommendations": [
                            "Verify lessor identity",
                            "Check property registration",
                            "Review termination clauses"
                        ]
                    },
                    "compliance_check": {
                        "indian_law_compliance": {
                            "stamp_duty_paid": True,
                            "registration_required": True,
                            "witnesses_present": True
                        },
                        "compliance_score": 85.0
                    },
                    "summary": "This is a residential rental agreement for a 2BHK apartment in Mumbai with monthly rent of ₹25,000. The agreement includes standard clauses for maintenance, utilities, and termination.",
                    "key_terms": [
                        "Monthly rent: ₹25,000",
                        "Security deposit: ₹50,000",
                        "Lease period: 1 year",
                        "Notice period: 30 days"
                    ],
                    "actionable_insights": [
                        "Verify property ownership documents",
                        "Check society NOC if applicable",
                        "Ensure rent agreement is registered if lease >11 months"
                    ]
                },
                "status": "completed",
                "created_at": "2025-09-18T10:00:00Z",
                "updated_at": "2025-09-18T10:02:15Z",
                "version": "1.0"
            }
        }
