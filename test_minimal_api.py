"""
Minimal API test to verify the core functionality works
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time

app = FastAPI(
    title="Test API",
    description="Minimal API for testing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "message": "API is running successfully"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Test API is running",
        "version": "1.0.0",
        "health": "/health"
    }

@app.post("/test-analyze")
async def test_analyze(data: dict):
    """Test analysis endpoint"""
    return {
        "success": True,
        "data": {
            "document_id": data.get("document_id", "test_id"),
            "status": "processing",
            "message": f"Document {data.get('document_id')} analysis started. Results will be stored in MongoDB collection: processed_documents",
            "user_id": data.get("user_id", "test_user"),
            "document_type": data.get("document_type", "rental")
        },
        "meta": {
            "timestamp": time.time(),
            "collection": "processed_documents"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "test_minimal_api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
