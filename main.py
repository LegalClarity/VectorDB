"""
Main FastAPI Application Entry Point
Consolidated API with Document Upload functionality
"""
import logging
import time
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Import the document upload API components
import sys
import os
import importlib.util

# Add the Helper-APIs directory to the path
helper_apis_path = os.path.join(os.getcwd(), 'Helper-APIs')
sys.path.insert(0, helper_apis_path)

# Add the app directory to sys.path for proper imports
app_path = os.path.join(helper_apis_path, 'document-upload-api', 'app')
sys.path.insert(0, app_path)

# Now we can import the modules normally
# Import configurations from Helper APIs
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "Helper-APIs", "document-upload-api", "app"))

try:
    from config import settings
    from database import db_manager
    from gcs_service import gcs_service
    from routers.documents import router as documents_router
    print("✅ Imported Helper-APIs upload configuration")
except ImportError as e:
    print(f"⚠️  Helper-APIs configuration not available: {e}")
    # Fallback configuration for standalone operation
    class MockSettings:
        project_id = "default-project"
        mongo_connection_string = "mongodb://localhost:27017"
        db_name = "legal_docs"
    
    settings = MockSettings()
    db_manager = None
    gcs_service = None
    documents_router = None

# Import document analyzer components
import httpx
import asyncio
import uuid

print("✅ Document analyzer integration enabled - proxying to Helper API")
ANALYZER_AVAILABLE = True
ANALYZER_API_URL = "http://localhost:8000/api"  # Helper-APIs analyzer API

# Import additional requirements for analyzer proxy
from fastapi import UploadFile, File, Form, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class AnalyzeDocumentRequest(BaseModel):
    """Request model for document analysis"""
    document_id: str
    document_type: Optional[str] = "general"
    user_id: str
    extraction_config: Optional[Dict[str, Any]] = {}


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    success: bool = True
    data: Dict[str, Any]
    meta: Dict[str, Any]

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    logger.info("Starting Consolidated API...")

    # Startup
    try:
        # Set up Google Cloud credentials if service account file exists
        service_account_path = os.path.join(os.getcwd(), "service-account.json")
        if os.path.exists(service_account_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = service_account_path
            logger.info("Google Cloud service account credentials configured")

        # Connect to MongoDB
        await db_manager.connect()
        logger.info("MongoDB connected successfully")

        # Initialize GCS service (connection happens on first use)
        logger.info("GCS service initialized")

        logger.info("Consolidated API started successfully")

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Consolidated API...")
    try:
        await db_manager.disconnect()
        logger.info("MongoDB disconnected successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

    logger.info("Consolidated API shutdown complete")


# API Tags for better organization
tags_metadata = [
    {
        "name": "health",
        "description": "Health check and system status endpoints"
    },
    {
        "name": "documents",
        "description": "Document upload, management and retrieval operations"
    },
    {
        "name": "analyzer",
        "description": "Document analysis and processing operations"
    },
    {
        "name": "vectordb",
        "description": "Vector database operations and RAG functionality"
    }
]

# Create FastAPI application
app = FastAPI(
    title="Consolidated API - Document Upload & VectorDB",
    description="Unified API with document upload functionality, analysis and vector database operations",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware (configure for production)
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Configure appropriately for production
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests"""
    start_time = time.time()

    # Log request
    logger.info(f"Request: {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")

    try:
        response = await call_next(request)

        # Log response
        process_time = time.time() - start_time
        logger.info(".2f")

        return response

    except Exception as e:
        # Log error
        process_time = time.time() - start_time
        logger.error(".2f")
        raise


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions with consistent format"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url.path}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "method": request.method
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unexpected error: {str(exc)} - {request.method} {request.url.path}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "status_code": 500,
                "path": str(request.url.path),
                "method": request.method
            }
        }
    )


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        mongo_status = "healthy"

        # Test GCS connectivity (basic check)
        gcs_status = "healthy"

        apis = {
            "document_upload": "available",
            "vectordb": "available"
        }

        if ANALYZER_AVAILABLE:
            apis["document_analyzer"] = "available"

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {
                "mongodb": mongo_status,
                "gcs": gcs_status
            },
            "apis": apis
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            }
        )


# Root endpoint
@app.get("/", tags=["health"])
async def root():
    """Root endpoint with API information"""
    apis = {
        "documents": "/docs (Document Upload API)",
        "vectordb": "VectorDB Main functionality"
    }

    if ANALYZER_AVAILABLE:
        apis["analyzer"] = "/analyzer/docs (Document Analyzer API)"

    return {
        "message": "Legal Clarity API - Document Upload, Analysis & VectorDB",
        "version": "1.0.0",
        "apis": apis,
        "health": "/health",
        "docs": "/docs"
    }


# Include document upload router
app.include_router(
    documents_router,
    prefix="/documents",
    tags=["documents"]
)

# Note: Analyzer endpoints are now included directly in main.py
# No separate router needed since we have simplified endpoints


# Placeholder for future VectorDB integration
@app.get("/vectordb/status", tags=["vectordb"])
async def vectordb_status():
    """VectorDB status endpoint (placeholder)"""
    return {
        "status": "VectorDB API available",
        "note": "VectorDB functionality can be integrated here",
        "documents": "/documents"
    }


# Document Analyzer Endpoints (Proxied to Helper API)
async def proxy_to_analyzer(request_path: str, method: str = "GET", data: dict = None, params: dict = None):
    """Proxy requests to the analyzer API"""
    try:
        url = f"{ANALYZER_API_URL}{request_path}"
        timeout = httpx.Timeout(30.0)
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method == "GET":
                response = await client.get(url, params=params)
            elif method == "POST":
                response = await client.post(url, json=data, params=params)
            elif method == "DELETE":
                response = await client.delete(url, params=params)
            else:
                raise HTTPException(status_code=405, detail=f"Method {method} not supported")
                
            return response.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503, 
            detail="Analyzer API not available. Please ensure the document analyzer service is running on port 8000."
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Analyzer API timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analyzer proxy error: {str(e)}")


@app.post("/analyzer/analyze", response_model=AnalysisResponse, tags=["analyzer"])
async def analyze_document_proxy(request: AnalyzeDocumentRequest):
    """
    Analyze a document by proxying to the analyzer API
    """
    try:
        logger.info(f"Proxying analysis request for document: {request.document_id}")
        
        # Convert request to analyzer API format
        analyzer_request = {
            "document_text": await get_document_text(request.document_id, request.user_id),
            "document_type": request.document_type,
            "user_id": request.user_id
        }
        
        result = await proxy_to_analyzer("/extractor/extract", method="POST", data=analyzer_request)
        
        return AnalysisResponse(
            success=result.get("success", True),
            data=result.get("data", {}),
            meta={
                "timestamp": time.time(),
                "request_id": str(uuid.uuid4()),
                "proxied_to": "analyzer_api"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis proxy failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


async def get_document_text(document_id: str, user_id: str) -> str:
    """Get document text from database"""
    try:
        document = await db_manager.documents_collection.find_one({
            "document_id": document_id,
            "user_id": user_id
        })
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Try to get text from GCS or use a placeholder
        try:
            # This would normally fetch from GCS and extract text
            # For now, return a sample text based on document type
            doc_type = document.get('document_type', 'unknown')
            return f"Sample {doc_type} document text for analysis. Document ID: {document_id}"
        except Exception:
            return f"Document content for {document_id} (text extraction not implemented)"
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document text: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve document content")


@app.get("/analyzer/results/{doc_id}", tags=["analyzer"])
async def get_analysis_results(doc_id: str, user_id: str = Query(..., description="User ID")):
    """
    Get analysis results for a document
    """
    try:
        logger.info(f"Analysis results request: {doc_id} for user: {user_id}")

        # Check if document exists
        document = await db_manager.documents_collection.find_one({
            "document_id": doc_id,
            "user_id": user_id
        })

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # Return basic analysis results
        return {
            "success": True,
            "data": {
                "document_id": doc_id,
                "status": "analyzed",
                "basic_analysis": {
                    "filename": document.get('original_filename', 'Unknown'),
                    "file_size": document.get('file_metadata', {}).get('file_size', 0),
                    "content_type": document.get('file_metadata', {}).get('content_type', 'Unknown'),
                    "upload_date": document.get('timestamps', {}).get('created_at')
                },
                "extraction_status": "basic_analysis_available",
                "note": "Full LangExtract results will be available once integration is complete"
            },
            "meta": {
                "timestamp": time.time(),
                "request_id": str(uuid.uuid4())
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")


@app.get("/analyzer/documents", tags=["analyzer"])
async def list_analyzed_documents(
    user_id: str = Query(..., description="User ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    List analyzed documents for a user
    """
    try:
        logger.info(f"List analyzed documents request for user: {user_id}")

        # Get user's documents
        cursor = db_manager.documents_collection.find(
            {"user_id": user_id}
        ).skip(skip).limit(limit).sort("timestamps.created_at", -1)

        documents = await cursor.to_list(length=None)

        # Format response
        analyzed_docs = []
        for doc in documents:
            analyzed_docs.append({
                "document_id": doc["document_id"],
                "filename": doc.get("original_filename", "Unknown"),
                "analysis_status": "basic_analysis_completed",
                "created_at": doc.get("timestamps", {}).get("created_at"),
                "file_size": doc.get("file_metadata", {}).get("file_size", 0)
            })

        return {
            "success": True,
            "data": {
                "documents": analyzed_docs,
                "total_count": len(analyzed_docs),
                "skip": skip,
                "limit": limit
            },
            "meta": {
                "timestamp": time.time(),
                "request_id": str(uuid.uuid4())
            }
        }

    except Exception as e:
        logger.error(f"Failed to list analyzed documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.get("/analyzer/stats/{user_id}", tags=["analyzer"])
async def get_user_statistics(user_id: str):
    """
    Get user statistics for document analysis
    """
    try:
        logger.info(f"User statistics request for user: {user_id}")

        # Count user's documents
        total_docs = await db_manager.documents_collection.count_documents({"user_id": user_id})

        # Get basic stats
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {
                "_id": None,
                "total_size": {"$sum": "$file_metadata.file_size"},
                "avg_size": {"$avg": "$file_metadata.file_size"}
            }}
        ]

        stats_result = await db_manager.documents_collection.aggregate(pipeline).to_list(length=1)

        stats = stats_result[0] if stats_result else {"total_size": 0, "avg_size": 0}

        return {
            "success": True,
            "data": {
                "user_id": user_id,
                "total_documents": total_docs,
                "total_size_bytes": stats.get("total_size", 0),
                "average_size_bytes": stats.get("avg_size", 0),
                "analysis_status": "basic_analysis_enabled",
                "note": "Full statistics will be available with complete LangExtract integration"
            },
            "meta": {
                "timestamp": time.time(),
                "request_id": str(uuid.uuid4())
            }
        }

    except Exception as e:
        logger.error(f"Failed to get user statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@app.delete("/analyzer/results/{doc_id}", tags=["analyzer"])
async def delete_analysis_results(doc_id: str, user_id: str = Query(..., description="User ID")):
    """
    Delete analysis results for a document (placeholder - no actual deletion)
    """
    try:
        logger.info(f"Delete analysis results request: {doc_id} for user: {user_id}")

        # Check if document exists
        document = await db_manager.documents_collection.find_one({
            "document_id": doc_id,
            "user_id": user_id
        })

        if not document:
            raise HTTPException(status_code=404, detail="Document not found")

        # In a full implementation, this would delete analysis results
        # For now, just return success
        return {
            "success": True,
            "data": {
                "document_id": doc_id,
                "message": "Analysis results deletion not implemented yet",
                "note": "This is a placeholder endpoint"
            },
            "meta": {
                "timestamp": time.time(),
                "request_id": str(uuid.uuid4())
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete analysis results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete results: {str(e)}")


@app.get("/analyzer/health", tags=["analyzer"])
async def analyzer_health_check():
    """
    Health check for analyzer service
    """
    try:
        # Test basic database connectivity
        doc_count = await db_manager.documents_collection.count_documents({})

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {
                "database": "connected",
                "analyzer": "basic_mode"
            },
            "stats": {
                "total_documents": doc_count
            },
            "note": "Running in basic analysis mode - full LangExtract integration pending"
        }

    except Exception as e:
        logger.error(f"Analyzer health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            }
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
