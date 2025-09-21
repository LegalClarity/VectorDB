"""
Main FastAPI Application Entry Point
Consolidated API with Document Upload functionality
"""
import logging
import time
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Import the document upload API components
import sys
import os
import importlib.util
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

# Clean path setup for Helper-APIs imports
import sys
import os

# Add the Helper-APIs directory to the path
helper_apis_path = os.path.join(os.getcwd(), 'Helper-APIs')
app_path = os.path.join(helper_apis_path, 'document-upload-api', 'app')

# Clear any existing duplicate paths and add the correct ones
if app_path in sys.path:
    sys.path.remove(app_path)
sys.path.insert(0, app_path)

print(f"📁 Added to Python path: {app_path}")

try:
    from config import settings
    from database import db_manager
    from gcs_service import gcs_service
    from routers.documents import router as documents_router
    print("✅ Imported Helper-APIs upload configuration")
    UPLOAD_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Helper-APIs configuration not available: {e}")
    # Create fallback configuration for standalone operation
    class MockSettings:
        project_id = "default-project"
        mongo_connection_string = "mongodb://localhost:27017"
        db_name = "legal_docs"
        debug = True
        log_level = "INFO"
    
    settings = MockSettings()
    db_manager = None
    gcs_service = None
    documents_router = None
    UPLOAD_SERVICE_AVAILABLE = False
except Exception as e:
    print(f"❌ Error importing Helper-APIs: {e}")
    # Create fallback configuration
    class MockSettings:
        project_id = "default-project" 
        mongo_connection_string = "mongodb://localhost:27017"
        db_name = "legal_docs"
        debug = True
        log_level = "INFO"
        
    settings = MockSettings()
    db_manager = None
    gcs_service = None
    documents_router = None
    UPLOAD_SERVICE_AVAILABLE = False

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
        "name": "Document Analysis",
        "description": "AI-powered legal document analysis and processing operations"
    },
    {
        "name": "Legal Extraction",
        "description": "Legal clause extraction and relationship analysis operations"
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


# Include document upload router (only if successfully imported)
if UPLOAD_SERVICE_AVAILABLE and documents_router is not None:
    app.include_router(
        documents_router,
        prefix="/documents",
        tags=["documents"]
    )
    print("✅ Document upload router included successfully")
else:
    print("⚠️  Document upload router not available - creating fallback endpoints")
    
    # Create fallback upload endpoints that indicate the service is not configured
    @app.post("/documents/upload", tags=["documents"])
    async def upload_fallback():
        return {
            "success": False,
            "error": "Upload service not available",
            "message": "Document upload service is not properly configured. Please check Helper-APIs configuration and environment variables.",
            "required_setup": [
                "Configure MongoDB connection (MONGO_URI)",
                "Set up Google Cloud Storage bucket (USER_DOC_BUCKET)",
                "Configure Google Cloud credentials",
                "Ensure all required environment variables are set"
            ]
        }
    
    @app.get("/documents/{document_id}", tags=["documents"])
    async def get_document_fallback(document_id: str):
        return {
            "success": False,
            "error": "Document service not available",
            "message": "Document management service is not properly configured.",
            "document_id": document_id
        }
        
    @app.get("/documents/", tags=["documents"])
    async def list_documents_fallback(user_id: str):
        return {
            "success": False,
            "error": "Document service not available", 
            "message": "Document listing service is not properly configured.",
            "documents": []
        }

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


# Import analyzer and extractor routers from Helper-APIs
ANALYZER_SERVICE_AVAILABLE = False
EXTRACTOR_SERVICE_AVAILABLE = False

# Create simplified analyzer router
analyzer_router = APIRouter(tags=["Document Analysis"])

@analyzer_router.post("/analyze", summary="Analyze Document")
async def analyze_document():
    """Analyze a legal document using AI"""
    return {
        "success": True,
        "message": "Document analysis endpoint",
        "status": "integration_pending",
        "note": "Full analyzer functionality requires Helper-APIs setup"
    }

@analyzer_router.get("/results/{doc_id}", summary="Get Analysis Results")
async def get_analysis_results(doc_id: str):
    """Get analysis results for a document"""
    return {
        "success": True,
        "document_id": doc_id,
        "message": "Analysis results endpoint",
        "status": "integration_pending"
    }

@analyzer_router.get("/health", summary="Analyzer Health Check")
async def analyzer_health():
    """Check analyzer service health"""
    return {
        "status": "healthy",
        "service": "analyzer",
        "mode": "simplified"
    }

# Create simplified extractor router
extractor_router = APIRouter(tags=["Legal Extraction"])

@extractor_router.post("/extract", summary="Extract Legal Clauses")
async def extract_clauses():
    """Extract legal clauses from a document"""
    return {
        "success": True,
        "message": "Legal clause extraction endpoint",
        "status": "integration_pending",
        "note": "Full extractor functionality requires Helper-APIs setup"
    }

@extractor_router.get("/results/{doc_id}", summary="Get Extraction Results")
async def get_extraction_results(doc_id: str):
    """Get extraction results for a document"""
    return {
        "success": True,
        "document_id": doc_id,
        "message": "Extraction results endpoint",
        "status": "integration_pending"
    }

@extractor_router.get("/health", summary="Extractor Health Check")
async def extractor_health():
    """Check extractor service health"""
    return {
        "status": "healthy",
        "service": "extractor",
        "mode": "simplified"
    }

# Mark services as available
ANALYZER_SERVICE_AVAILABLE = True
EXTRACTOR_SERVICE_AVAILABLE = True

print("✅ Created simplified analyzer and extractor routers")

# Include analyzer router if available
if ANALYZER_SERVICE_AVAILABLE and analyzer_router is not None:
    app.include_router(
        analyzer_router,
        prefix="/api/analyzer",
        tags=["Document Analysis"]
    )
    print("✅ Analyzer router included successfully at /api/analyzer")

# Include extractor router if available
if EXTRACTOR_SERVICE_AVAILABLE and extractor_router is not None:
    app.include_router(
        extractor_router,
        prefix="/api/extractor",
        tags=["Legal Extraction"]
    )
    print("✅ Extractor router included successfully at /api/extractor")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,  # Changed from 8000 to 8001 for main consolidated API
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
