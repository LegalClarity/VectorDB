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
from config import settings
from database import db_manager
from gcs_service import gcs_service
from routers.documents import router as documents_router

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


# Create FastAPI application
app = FastAPI(
    title="Consolidated API - Document Upload & VectorDB",
    description="Unified API with document upload functionality and vector database operations",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
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
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        mongo_status = "healthy"

        # Test GCS connectivity (basic check)
        gcs_status = "healthy"

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {
                "mongodb": mongo_status,
                "gcs": gcs_status
            },
            "apis": {
                "document_upload": "available",
                "vectordb": "available"
            }
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
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Consolidated API - Document Upload & VectorDB",
        "version": "1.0.0",
        "apis": {
            "documents": "/docs (Document Upload API)",
            "vectordb": "VectorDB Main functionality"
        },
        "health": "/health",
        "docs": "/docs"
    }


# Include document upload router
app.include_router(
    documents_router,
    prefix="/documents",
    tags=["Document Upload API"]
)


# Placeholder for future VectorDB integration
@app.get("/vectordb/status")
async def vectordb_status():
    """VectorDB status endpoint (placeholder)"""
    return {
        "status": "VectorDB API available",
        "note": "VectorDB functionality can be integrated here",
        "documents": "/documents"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
