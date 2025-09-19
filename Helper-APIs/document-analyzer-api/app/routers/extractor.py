"""
Legal Document Extractor API Router
REST endpoints for legal document clause and relationship extraction
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..services.legal_extractor_service import LegalExtractorService
from ..models.schemas.legal_schemas import DocumentType

router = APIRouter(tags=["legal-extraction"])


class ExtractionRequest(BaseModel):
    """Request model for document extraction"""
    document_text: str
    document_type: DocumentType
    user_id: Optional[str] = None


class ExtractionResponse(BaseModel):
    """Response model for extraction results"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


class StructuredDocumentRequest(BaseModel):
    """Request model for structured document creation"""
    extraction_result: Dict[str, Any]
    original_text: str
    document_type: DocumentType


@router.post("/extract", response_model=ExtractionResponse)
async def extract_document_clauses(
    request: ExtractionRequest,
    background_tasks: BackgroundTasks,
    service: LegalExtractorService = Depends()
):
    """Extract clauses and relationships from legal document"""
    try:
        import time
        start_time = time.time()

        result = await service.extract_clauses_and_relationships(
            request.document_text,
            request.document_type.value
        )

        processing_time = time.time() - start_time

        return ExtractionResponse(
            success=True,
            data=result.dict() if hasattr(result, 'dict') else result,
            processing_time=processing_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/structured", response_model=ExtractionResponse)
async def create_structured_document(
    request: StructuredDocumentRequest,
    service: LegalExtractorService = Depends()
):
    """Create structured legal document from extraction results"""
    try:
        structured_doc = await service.create_structured_document(
            request.extraction_result,
            request.original_text
        )

        return ExtractionResponse(success=True, data=structured_doc)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Structuring failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for legal extractor service"""
    return {"status": "healthy", "service": "legal-extractor"}
