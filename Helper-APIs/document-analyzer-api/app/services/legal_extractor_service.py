"""
Legal Extractor Service Layer
FastAPI-compatible wrapper for legal document extraction
"""

import asyncio
from typing import Dict, Any, Optional
from .legal_extractor import ImprovedLegalDocumentExtractor
from ..models.schemas.legal_schemas import DocumentType


class LegalExtractorService:
    """Service layer for legal document extraction"""

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.extractor = ImprovedLegalDocumentExtractor(gemini_api_key)

    async def extract_clauses_and_relationships(
        self,
        document_text: str,
        document_type: str
    ) -> Dict[str, Any]:
        """Async wrapper for clause and relationship extraction"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.extractor.extract_clauses_and_relationships,
            document_text,
            document_type
        )

    async def create_structured_document(
        self,
        extraction_result: Dict[str, Any],
        original_text: str
    ) -> Dict[str, Any]:
        """Create structured legal document from extraction results"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.extractor.create_structured_document,
            extraction_result,
            original_text
        )

    async def extract_with_progress(
        self,
        document_text: str,
        document_type: str,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Extract with progress tracking"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.extractor.extract_clauses_and_relationships(
                document_text,
                document_type,
                progress_callback=progress_callback
            )
        )
