"""
Simple Document Analyzer API Router
Minimal implementation for testing
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analyzer"])

class AnalyzeDocumentRequest(BaseModel):
    document_id: str
    document_type: Optional[str] = None
    user_id: str

class AnalysisResponse(BaseModel):
    success: bool
    data: dict
    meta: dict

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(request: AnalyzeDocumentRequest):
    """Analyze a legal document"""
    try:
        logger.info(f"Starting analysis for document: {request.document_id}")

        # Mock response for testing
        return AnalysisResponse(
            success=True,
            data={
                "document_id": request.document_id,
                "status": "processing",
                "message": "Document analysis started successfully. Results will be stored in MongoDB collection: processed_documents",
                "user_id": request.user_id,
                "document_type": request.document_type or "detected_from_metadata"
            },
            meta={
                "timestamp": "2025-09-18T20:30:00Z",
                "background_processing": True,
                "collection": "processed_documents"
            }
        )

    except Exception as e:
        logger.error(f"Analysis request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis request failed: {str(e)}"
        )

@router.get("/results/{document_id}", response_model=AnalysisResponse)
async def get_analysis_results(document_id: str, user_id: str):
    """Get analysis results for a document"""
    try:
        logger.info(f"Retrieving analysis results for document: {document_id}")

        # Mock response for testing
        return AnalysisResponse(
            success=True,
            data={
                "document_id": document_id,
                "status": "completed",
                "analysis_result": {
                    "document_type": "rental",
                    "extracted_clauses": [
                        {
                            "clause_id": "clause_1",
                            "clause_type": "PARTY_IDENTIFICATION",
                            "clause_text": "Landlord: ABC Properties",
                            "confidence_score": 0.95
                        },
                        {
                            "clause_id": "clause_2",
                            "clause_type": "FINANCIAL_TERMS",
                            "clause_text": "Monthly rent: Rs. 25,000",
                            "confidence_score": 0.92
                        }
                    ],
                    "confidence_score": 0.85,
                    "processing_time_seconds": 2.5
                },
                "message": "Analysis completed successfully"
            },
            meta={
                "timestamp": "2025-09-18T20:32:00Z",
                "stored_in_collection": "processed_documents"
            }
        )

    except Exception as e:
        logger.error(f"Failed to retrieve analysis results: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analysis results: {str(e)}"
        )

@router.get("/health")
async def analyzer_health():
    """Health check endpoint for the analyzer service"""
    return {
        "service": "document_analyzer",
        "status": "healthy",
        "timestamp": "2025-09-18T20:30:00Z",
        "version": "1.0.0",
        "mongodb_collection": "processed_documents"
    }
