"""
Document Analyzer API Router
Endpoints for document analysis and processing
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..services.document_analyzer import DocumentAnalyzerService
from ..services.database_service import DatabaseService
from ..services.gcs_service import GCSService
from ..models.schemas.processed_document import ProcessedDocumentSchema

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class AnalyzeDocumentRequest(BaseModel):
    """Request model for document analysis"""

    document_id: str = Field(..., description="Unique document identifier")
    document_type: str = Field(..., description="Type of document (rental/loan/tos)")
    user_id: str = Field(..., description="User who owns the document")

    class Config:
        schema_extra = {
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

    class Config:
        schema_extra = {
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
    # This would typically come from a dependency injection container
    # For now, we'll create it here (in production, use proper DI)
    from ..config import settings
    return DocumentAnalyzerService(
        gemini_api_key=settings.GEMINI_API_KEY,
        gemini_model=settings.GEMINI_MODEL
    )


async def get_database_service() -> DatabaseService:
    """Get database service instance"""
    from ..config import settings
    db_service = DatabaseService(
        connection_string=settings.MONGO_URI,
        database_name=settings.MONGO_DB,
        collection_name=settings.MONGO_PROCESSED_DOCS_COLLECTION
    )
    await db_service.connect()
    return db_service


async def get_gcs_service() -> GCSService:
    """Get GCS service instance"""
    from ..config import settings
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

        # Validate document type
        valid_types = ["rental", "loan", "tos"]
        if request.document_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid document type. Must be one of: {valid_types}"
            )

        # Check if document exists in database (assuming documents collection exists)
        # This would typically query the documents collection to get GCS path
        # For now, we'll construct the expected GCS path
        gcs_path = f"user_documents/{request.user_id}/{request.document_id}"

        # Verify document exists in GCS
        if not await gcs_service.document_exists(gcs_path):
            raise HTTPException(
                status_code=404,
                detail="Document not found in storage"
            )

        # Download and extract text from document
        document_text = await gcs_service.get_document_text(gcs_path)

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


@router.get("/documents", response_model=DocumentListResponse)
async def list_analyzed_documents(
    user_id: str = Query(..., description="User ID"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    status: Optional[str] = Query(None, description="Filter by processing status"),
    skip: int = Query(0, ge=0, description="Number of documents to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of documents to return"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    List analyzed documents for a user

    Returns a paginated list of documents that have been analyzed.
    """
    try:
        logger.info(f"Listing analyzed documents for user: {user_id}")

        # Get documents
        documents = await db_service.get_user_documents(
            user_id=user_id,
            document_type=document_type,
            status=status,
            skip=skip,
            limit=limit
        )

        # Convert to dict format
        document_list = []
        for doc in documents:
            document_list.append({
                "document_id": doc.document_id,
                "document_type": doc.document_type,
                "status": doc.status,
                "created_at": doc.created_at.isoformat(),
                "processing_duration_seconds": doc.processing_duration_seconds,
                "file_name": doc.file_name,
                "error_message": doc.error_message if doc.status == "failed" else None
            })

        return DocumentListResponse(
            success=True,
            data={
                "documents": document_list,
                "total_count": len(document_list),
                "has_more": len(document_list) == limit
            },
            meta={
                "timestamp": "2025-09-18T10:30:00Z",
                "pagination": {
                    "skip": skip,
                    "limit": limit
                }
            }
        )

    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.get("/stats/{user_id}")
async def get_user_stats(
    user_id: str,
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Get analysis statistics for a user

    Returns statistics about document processing and analysis.
    """
    try:
        logger.info(f"Getting stats for user: {user_id}")

        stats = await db_service.get_processing_stats(user_id)

        return JSONResponse(
            content={
                "success": True,
                "data": stats,
                "meta": {
                    "timestamp": "2025-09-18T10:30:00Z"
                }
            }
        )

    except Exception as e:
        logger.error(f"Failed to get user stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user stats: {str(e)}"
        )


@router.delete("/results/{document_id}")
async def delete_analysis_results(
    document_id: str,
    user_id: str = Query(..., description="User ID for security"),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Delete analysis results for a document

    Removes the analysis results from the database.
    """
    try:
        logger.info(f"Deleting analysis results for document: {document_id}")

        deleted = await db_service.delete_analysis_result(document_id, user_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail="Analysis results not found"
            )

        return JSONResponse(
            content={
                "success": True,
                "data": {
                    "document_id": document_id,
                    "message": "Analysis results deleted successfully"
                },
                "meta": {
                    "timestamp": "2025-09-18T10:30:00Z"
                }
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete analysis results: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete analysis results: {str(e)}"
        )


@router.get("/health")
async def analyzer_health():
    """Health check endpoint for the analyzer service"""
    return {
        "service": "document_analyzer",
        "status": "healthy",
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
        error_result = analysis_result = type('ErrorResult', (), {
            'document_id': document_id,
            'document_type': document_type,
            'user_id': user_id,
            'processing_status': 'failed',
            'processing_errors': [str(e)]
        })()

        try:
            await db_service.store_analysis_result(error_result)
        except Exception as store_error:
            logger.error(f"Failed to store error result: {store_error}")
