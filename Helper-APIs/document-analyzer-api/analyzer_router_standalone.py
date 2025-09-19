"""
Standalone Document Analyzer API Router
Endpoints for document analysis and processing
"""

import logging
import os
import sys
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from app.services.document_analyzer import DocumentAnalyzerService
    from app.services.database_service import DatabaseService
    from app.services.gcs_service import GCSService
    from app.models.schemas.processed_document import ProcessedDocumentSchema
    from app.config import settings
    SERVICES_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Services not available: {e}")
    SERVICES_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(tags=["analyzer"])


# Request/Response Models
class AnalyzeDocumentRequest(BaseModel):
    """Request model for document analysis"""

    document_id: str = Field(..., description="Unique document identifier")
    document_type: Optional[str] = Field(None, description="Type of document (rental/loan/tos) - optional if stored in document metadata")
    user_id: str = Field(..., description="User who owns the document")

    @classmethod
    def model_json_schema(cls, **kwargs):
        schema = super().model_json_schema(**kwargs)
        schema["example"] = {
            "example": {
                "document_id": "doc_123456",
                "document_type": "rental",
                "user_id": "user_789"
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""

    success: bool = Field(True, description="Whether the request was successful")
    data: dict = Field(..., description="Analysis result data")
    meta: dict = Field(..., description="Metadata about the response")

    @classmethod
    def model_json_schema(cls, **kwargs):
        schema = super().model_json_schema(**kwargs)
        schema["example"] = {
            "example": {
                "success": True,
                "data": {
                    "document_id": "doc_123456",
                    "status": "processing",
                    "message": "Document analysis started successfully"
                },
                "meta": {
                    "timestamp": "2025-09-18T10:30:00Z",
                    "processing_time_seconds": 0.5
                }
            }
        }


class DocumentListResponse(BaseModel):
    """Response model for document list"""

    success: bool = Field(True, description="Whether the request was successful")
    data: dict = Field(..., description="Document list data")
    meta: dict = Field(..., description="Metadata about the response")


# Dependency injection functions
async def get_analyzer_service() -> DocumentAnalyzerService:
    """Get document analyzer service instance"""
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Analysis services not available")

    return DocumentAnalyzerService(
        gemini_api_key=settings.GEMINI_API_KEY,
        gemini_model=settings.GEMINI_MODEL
    )


async def get_database_service() -> DatabaseService:
    """Get database service instance"""
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Database services not available")

    db_service = DatabaseService(
        connection_string=settings.MONGO_URI,
        database_name=settings.MONGO_DB,
        collection_name=settings.MONGO_PROCESSED_DOCS_COLLECTION
    )
    await db_service.connect()
    return db_service


async def get_gcs_service() -> GCSService:
    """Get GCS service instance"""
    if not SERVICES_AVAILABLE:
        raise HTTPException(status_code=503, detail="Storage services not available")

    return GCSService(
        bucket_name=settings.USER_DOC_BUCKET,
        credentials_path=settings.GOOGLE_CREDENTIALS_PATH
    )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_document(
    request: AnalyzeDocumentRequest,
    background_tasks: BackgroundTasks,
    analyzer_service: DocumentAnalyzerService = Depends(get_analyzer_service),
    db_service: DatabaseService = Depends(get_database_service),
    gcs_service: GCSService = Depends(get_gcs_service)
):
    """
    Analyze a legal document

    This endpoint accepts a document ID and analyzes the corresponding document
    stored in Google Cloud Storage using LangExtract and Gemini Flash.
    """
    try:
        logger.info(f"Starting analysis for document: {request.document_id}")

        # Validate document type if provided
        valid_types = ["rental", "loan", "tos"]
        if request.document_type and request.document_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document type. Must be one of: {valid_types}"
            )

        # Query document from upload API database
        document_info = await db_service.get_document_info(request.document_id, request.user_id)

        if not document_info:
            raise HTTPException(
                status_code=404,
                detail="Document not found. Please ensure the document has been uploaded first."
            )

        # Use GCS path from document info
        gcs_path = document_info.get('gcs_object_path', f"user_documents/{request.user_id}/{request.document_id}")

        # Verify document exists in GCS
        if not await gcs_service.document_exists(gcs_path):
            raise HTTPException(
                status_code=404,
                detail="Document not found in storage"
            )

        # Download and extract text from document
        document_text = await gcs_service.get_document_text(gcs_path)

        # If document type not provided, try to get from document metadata
        if not request.document_type:
            request.document_type = document_info.get('document_metadata', {}).get('document_type', 'rental')

        if not document_text or len(document_text.strip()) < 100:
            raise HTTPException(
                status_code=400,
                detail="Document content is too short or empty for meaningful analysis"
            )

        # Check if analysis already exists
        existing_analysis = await db_service.get_analysis_result(request.document_id, request.user_id)

        if existing_analysis and existing_analysis.status == "completed":
            # Return existing analysis
            return AnalysisResponse(
                success=True,
                data={
                    "document_id": request.document_id,
                    "status": "completed",
                    "analysis_result": existing_analysis.analysis_result.dict(),
                    "message": "Analysis already exists"
                },
                meta={
                    "timestamp": "2025-09-18T10:30:00Z",
                    "cached": True
                }
            )

        # Update status to processing
        await db_service.update_analysis_status(request.document_id, "processing")

        # Schedule background analysis
        background_tasks.add_task(
            process_document_analysis,
            request.document_id,
            document_text,
            request.document_type,
            request.user_id,
            analyzer_service,
            db_service
        )

        return AnalysisResponse(
            success=True,
            data={
                "document_id": request.document_id,
                "status": "processing",
                "message": "Document analysis started successfully. Results will be available shortly."
            },
            meta={
                "timestamp": "2025-09-18T10:30:00Z",
                "background_processing": True
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis request failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis request failed: {str(e)}"
        )


@router.get("/results/{document_id}", response_model=AnalysisResponse)
async def get_analysis_results(
    document_id: str,
    user_id: str = Query(..., description="User ID for security"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Get analysis results for a document

    Returns the structured analysis results for a previously analyzed document.
    """
    try:
        logger.info(f"Retrieving analysis results for document: {document_id}")

        # Get analysis results
        analysis_result = await db_service.get_analysis_result(document_id, user_id)

        if not analysis_result:
            raise HTTPException(
                status_code=404,
                detail="Analysis results not found. Document may not have been analyzed yet."
            )

        return AnalysisResponse(
            success=True,
            data={
                "document_id": document_id,
                "status": analysis_result.status,
                "analysis_result": analysis_result.analysis_result.dict() if analysis_result.status == "completed" else None,
                "error_message": analysis_result.error_message if analysis_result.status == "failed" else None
            },
            meta={
                "timestamp": "2025-09-18T10:30:00Z",
                "processing_time_seconds": analysis_result.processing_duration_seconds
            }
        )

    except HTTPException:
        raise
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
        "status": "healthy" if SERVICES_AVAILABLE else "services_unavailable",
        "timestamp": "2025-09-18T10:30:00Z",
        "version": "1.0.0"
    }


# Background task function
async def process_document_analysis(
    document_id: str,
    document_text: str,
    document_type: str,
    user_id: str,
    analyzer_service: DocumentAnalyzerService,
    db_service: DatabaseService
):
    """
    Background task to process document analysis

    This function runs in the background and performs the actual document analysis.
    """
    try:
        logger.info(f"Starting background analysis for document: {document_id}")

        # Perform analysis
        analysis_result = await analyzer_service.analyze_document(
            document_id=document_id,
            document_text=document_text,
            document_type=document_type,
            user_id=user_id
        )

        # Store results
        await db_service.store_analysis_result(analysis_result)

        # Update status to completed
        await db_service.update_analysis_status(document_id, "completed")

        logger.info(f"Background analysis completed for document: {document_id}")

    except Exception as e:
        logger.error(f"Background analysis failed for document {document_id}: {e}")

        # Update status to failed
        await db_service.update_analysis_status(
            document_id,
            "failed",
            error_message=str(e)
        )

        # Store minimal error result
        try:
            error_result = type('ErrorResult', (), {
                'document_id': document_id,
                'document_type': document_type,
                'user_id': user_id,
                'processing_status': 'failed'
            })()
            await db_service.store_analysis_result(error_result)
        except Exception as store_error:
            logger.error(f"Failed to store error result: {store_error}")
