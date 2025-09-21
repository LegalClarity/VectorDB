#!/usr/bin/env python3
"""
Minimal API server for testing consolidation
Runs without Helper-APIs dependencies to validate API structure
"""
import os
import sys
import time
from typing import Dict, Any

# Add current directory to path
sys.path.insert(0, os.getcwd())

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Minimal FastAPI app for testing
app = FastAPI(
    title="Legal Clarity - Consolidated API (Test Mode)",
    description="Unified API for legal document analysis - running in test mode",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", tags=["root"])
async def read_root():
    """
    Welcome to the Legal Clarity API - Consolidated Version
    """
    return {
        "message": "Welcome to Legal Clarity - Consolidated API",
        "version": "2.0.0",
        "status": "running_test_mode",
        "apis": {
            "documents": "/api/documents - Document upload and management",
            "analyzer": "/api/analyzer - AI-powered document analysis", 
            "extractor": "/api/extractor - Legal clause extraction",
            "vectordb": "/vectordb - Vector database operations",
            "health": "/health - System health checks",
            "docs": "/docs - Interactive API documentation"
        },
        "consolidation_status": "✅ All duplicate endpoints removed",
        "port": 8001,
        "note": "Running in test mode - Helper-APIs integration disabled"
    }

# Health endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0",
        "consolidation": "completed",
        "services": {
            "api_server": "running",
            "documents": "test_mode",
            "analyzer": "fallback_available",
            "extractor": "fallback_available"
        },
        "endpoints": {
            "document_upload": "/api/documents/upload",
            "document_analysis": "/api/analyzer/analyze",
            "legal_extraction": "/api/extractor/extract",
            "api_docs": "/docs"
        }
    }

# VectorDB status
@app.get("/vectordb/status", tags=["vectordb"])
async def vectordb_status():
    """VectorDB status endpoint"""
    return {
        "status": "VectorDB API available",
        "note": "VectorDB functionality can be integrated here",
        "documents": "/api/documents"
    }

# Document endpoints (fallback)
@app.post("/api/documents/upload", tags=["Documents"])
async def upload_document_fallback():
    """Document upload fallback endpoint"""
    return {
        "success": True,
        "message": "Document upload endpoint consolidated successfully",
        "status": "fallback_mode",
        "note": "Full upload functionality available when Helper-APIs are properly integrated"
    }

@app.get("/api/documents/{document_id}", tags=["Documents"])
async def get_document_fallback(document_id: str):
    """Document retrieval fallback endpoint"""
    return {
        "success": True,
        "document_id": document_id,
        "message": "Document retrieval endpoint consolidated successfully",
        "status": "fallback_mode"
    }

# Analyzer endpoints (fallback)
@app.post("/api/analyzer/analyze", tags=["Document Analysis"])
async def analyze_document_fallback():
    """Document analysis fallback endpoint"""
    return {
        "success": True,
        "message": "Document analyzer endpoint consolidated successfully",
        "status": "fallback_mode",
        "note": "Analyzer router will be properly integrated when Helper-APIs dependencies are resolved"
    }

@app.get("/api/analyzer/results/{doc_id}", tags=["Document Analysis"])
async def get_analysis_results_fallback(doc_id: str):
    """Analysis results fallback endpoint"""
    return {
        "success": True,
        "document_id": doc_id,
        "message": "Analysis results endpoint consolidated successfully",
        "status": "fallback_mode"
    }

# Extractor endpoints (fallback)
@app.post("/api/extractor/extract", tags=["Legal Extraction"])
async def extract_clauses_fallback():
    """Legal extraction fallback endpoint"""
    return {
        "success": True,
        "message": "Legal extractor endpoint consolidated successfully", 
        "status": "fallback_mode",
        "note": "Extractor router will be properly integrated when Helper-APIs dependencies are resolved"
    }

@app.get("/api/extractor/results/{doc_id}", tags=["Legal Extraction"])
async def get_extraction_results_fallback(doc_id: str):
    """Extraction results fallback endpoint"""
    return {
        "success": True,
        "document_id": doc_id,
        "message": "Extraction results endpoint consolidated successfully",
        "status": "fallback_mode"
    }

if __name__ == "__main__":
    print("🚀 Starting Legal Clarity - Consolidated API (Test Mode)")
    print("=" * 60)
    print("✅ All proxy endpoints removed")
    print("✅ Unified API structure implemented")
    print("✅ Running on single port: 8001")
    print("✅ Fallback endpoints available")
    print("📚 API Docs: http://localhost:8001/docs")
    print("🔍 Health Check: http://localhost:8001/health")
    print("=" * 60)
    
    uvicorn.run(
        "minimal_test_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )