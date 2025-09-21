# Document Analyzer Routers Package
"""
FastAPI routers for document analysis endpoints.
"""

from .analyzer import router as analyzer_router
from .extractor import router as extractor_router

__all__ = ["analyzer_router", "extractor_router"]
