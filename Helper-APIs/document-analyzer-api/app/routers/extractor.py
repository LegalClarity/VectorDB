"""
Legal Document Extractor API Router
REST endpoints for legal document clause and relationship extraction
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from pydantic import BaseModel
from typing import Optional, Dict, Any

from ..services.legal_extractor_service import LegalExtractorService
from ..services.mongodb_service import get_mongodb_service, MongoDBService
from ..config import settings
from ..models.schemas.legal_schemas import DocumentType

logger = logging.getLogger(__name__)


def get_legal_extractor_service() -> LegalExtractorService:
    """Dependency injection for LegalExtractorService"""
    return LegalExtractorService(gemini_api_key=settings.GEMINI_API_KEY)

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
    service: LegalExtractorService = Depends(get_legal_extractor_service),
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
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

        # Store the extraction result in MongoDB if user_id is provided
        if request.user_id:
            logger.info(f"🔄 Attempting to store extraction result for user: {request.user_id}")
            
            try:
                # Convert result to dict for storage if it's an ExtractionResult object
                result_dict = result
                if hasattr(result, 'dict'):
                    result_dict = result.dict()
                elif hasattr(result, 'model_dump'):
                    result_dict = result.model_dump()
                
                document_id = result_dict.get("document_id", f"extracted_{int(time.time())}")
                logger.info(f"🗂️ Storing document with ID: {document_id}")
                
                # Log the MongoDB service status
                if not mongodb_service.is_connected():
                    logger.error("❌ MongoDB service is not connected!")
                    return ExtractionResponse(
                        success=True,
                        data=result,
                        error="MongoDB connection failed - document not stored",
                        processing_time=processing_time
                    )
                else:
                    logger.info("✅ MongoDB service is connected")
                
                # Log the data being inserted
                logger.info(f"📊 Insertion parameters:")
                logger.info(f"   - document_id: {document_id}")
                logger.info(f"   - user_id: {request.user_id}")
                logger.info(f"   - document_type: {request.document_type.value}")
                logger.info(f"   - extraction_result keys: {list(result_dict.keys())}")
                
                success = await mongodb_service.insert_processed_document(
                    document_id=document_id,
                    user_id=request.user_id,
                    extraction_result=result_dict,
                    original_filename="text_input",
                    document_type=request.document_type.value
                )
                
                if success:
                    logger.info(f"✅ Successfully stored extraction result for document: {document_id}")
                    
                    # Verify by trying to retrieve immediately
                    verify_doc = await mongodb_service.get_processed_document(document_id, request.user_id)
                    if verify_doc:
                        logger.info(f"✅ Verified document storage - document retrieved successfully")
                    else:
                        logger.error(f"❌ Storage verification failed - document not found after insertion")
                else:
                    logger.error(f"❌ Failed to store extraction result for document: {document_id}")
                    
            except Exception as storage_error:
                logger.error(f"❌ Exception during MongoDB storage: {storage_error}")
                import traceback
                logger.error(f"Stack trace: {traceback.format_exc()}")
                # Don't fail the request, but log the error

        return ExtractionResponse(
            success=True,
            data=result_dict if request.user_id else (result.dict() if hasattr(result, 'dict') else result.model_dump()),
            processing_time=processing_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.post("/structured", response_model=ExtractionResponse)
async def create_structured_document(
    request: StructuredDocumentRequest,
    service: LegalExtractorService = Depends(get_legal_extractor_service)
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


@router.get("/results/{document_id}")
async def get_extraction_results(
    document_id: str,
    user_id: str = Query(..., description="User ID for security"),
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Get extraction results for a document"""
    try:
        logger.info(f"Retrieving extraction results for document: {document_id}")

        # Get processed document
        processed_doc = await mongodb_service.get_processed_document(document_id, user_id)

        if not processed_doc:
            raise HTTPException(
                status_code=404,
                detail="Document not found. It may not have been processed yet."
            )

        return ExtractionResponse(
            success=True,
            data=processed_doc["extraction_result"],
            error=None,
            processing_time=processed_doc.get("metadata", {}).get("processing_time_seconds", 0.0)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve extraction results: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve extraction results: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint for legal extractor service"""
    return {"status": "healthy", "service": "legal-extractor"}


@router.get("/results/{document_id}")
async def get_extraction_results(
    document_id: str,
    user_id: str,
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Get extraction results for a specific document"""
    try:
        result = await mongodb_service.get_processed_document(document_id, user_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Processed document not found")
        
        return ExtractionResponse(success=True, data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")


@router.get("/documents")
async def list_processed_documents(
    user_id: str,
    skip: int = 0,
    limit: int = 10,
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """List all processed documents for a user"""
    try:
        documents = await mongodb_service.list_processed_documents(user_id, skip, limit)
        
        return {
            "success": True,
            "data": {
                "documents": documents,
                "skip": skip,
                "limit": limit,
                "count": len(documents)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@router.get("/stats/{user_id}")
async def get_user_extraction_stats(
    user_id: str,
    mongodb_service: MongoDBService = Depends(get_mongodb_service)
):
    """Get extraction statistics for a user"""
    try:
        stats = await mongodb_service.get_user_statistics(user_id)
        
        return ExtractionResponse(success=True, data=stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
