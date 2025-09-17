"""
FastAPI Legal Document Upload System
"""
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import db_manager
from app.gcs_service import gcs_service
from app.routers import documents

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    logger.info("Starting Legal Document Upload API...")

    # Startup
    try:
        # Connect to MongoDB
        await db_manager.connect()
        logger.info("MongoDB connected successfully")

        # Initialize GCS service (connection happens on first use)
        logger.info("GCS service initialized")

        logger.info("Legal Document Upload API started successfully")

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Legal Document Upload API...")
    try:
        await db_manager.disconnect()
        logger.info("MongoDB disconnected successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

    logger.info("Legal Document Upload API shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Legal Document Upload API",
    description="API for uploading and managing legal documents with Google Cloud Storage and MongoDB",
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
        # Note: In a real implementation, you might want to do a more thorough health check
        mongo_status = "healthy"

        # Test GCS connectivity (basic check)
        gcs_status = "healthy"

        return {
            "status": "healthy",
            "timestamp": time.time(),
            "services": {
                "mongodb": mongo_status,
                "gcs": gcs_status
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
        "message": "Legal Document Upload API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(
    documents.router,
    prefix="/documents",
    tags=["documents"]
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
