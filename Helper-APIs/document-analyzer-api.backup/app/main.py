"""
Document Analyzer API - Main FastAPI Application
Legal document analysis using LangExtract and Gemini Flash
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .routers.analyzer import router as analyzer_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    logger.info("Starting Document Analyzer API...")

    # Startup
    try:
        # Validate configuration
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required")
        if not settings.MONGO_URI:
            raise ValueError("MONGO_URI is required")
        if not settings.USER_DOC_BUCKET:
            raise ValueError("USER_DOC_BUCKET is required")

        # Validate Google Cloud credentials
        if settings.GOOGLE_CREDENTIALS_PATH and not os.path.exists(settings.GOOGLE_CREDENTIALS_PATH):
            logger.warning(f"Google credentials file not found: {settings.GOOGLE_CREDENTIALS_PATH}")
        elif not settings.GOOGLE_CREDENTIALS_PATH:
            logger.warning("GOOGLE_APPLICATION_CREDENTIALS not set - using default credentials")

        logger.info("Document Analyzer API started successfully")

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Document Analyzer API...")
    logger.info("Document Analyzer API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Legal Clarity - Document Analyzer API",
    description="AI-powered legal document analysis using LangExtract and Gemini Flash",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
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
if not settings.DEBUG:
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
            "success": False,
            "error": {
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "method": request.method
            },
            "meta": {
                "timestamp": time.time()
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
            "success": False,
            "error": {
                "message": "Internal server error",
                "status_code": 500,
                "path": str(request.url.path),
                "method": request.method
            },
            "meta": {
                "timestamp": time.time()
            }
        }
    )


# Include routers
app.include_router(
    analyzer_router,
    prefix="/api/analyzer",
    tags=["Document Analyzer API"]
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Legal Clarity - Document Analyzer API",
        "version": "1.0.0",
        "description": "AI-powered legal document analysis using LangExtract and Gemini Flash",
        "endpoints": {
            "analyze": "/api/analyzer/analyze (POST)",
            "results": "/api/analyzer/results/{document_id} (GET)",
            "documents": "/api/analyzer/documents (GET)",
            "stats": "/api/analyzer/stats/{user_id} (GET)",
            "health": "/api/analyzer/health (GET)"
        },
        "docs": "/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "service": "document_analyzer",
            "timestamp": time.time(),
            "version": "1.0.0",
            "configuration": {
                "gemini_model": settings.GEMINI_MODEL,
                "mongo_db": settings.MONGO_DB,
                "gcs_bucket": settings.USER_DOC_BUCKET
            }
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "document_analyzer",
                "timestamp": time.time(),
                "error": str(e)
            }
        )


# Service info endpoint
@app.get("/info")
async def service_info():
    """Service information endpoint"""
    return {
        "service": "Legal Clarity Document Analyzer",
        "version": "1.0.0",
        "description": "AI-powered legal document analysis service",
        "capabilities": [
            "Rental agreement analysis",
            "Loan agreement analysis",
            "Terms of Service analysis",
            "Risk assessment",
            "Compliance checking",
            "Financial analysis"
        ],
        "technologies": [
            "LangExtract",
            "Gemini Flash",
            "FastAPI",
            "MongoDB",
            "Google Cloud Storage"
        ],
        "supported_formats": ["PDF", "DOCX", "TXT"],
        "max_file_size": f"{settings.MAX_FILE_SIZE_MB}MB"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
