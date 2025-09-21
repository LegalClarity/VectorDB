"""
Legal Extractor Service Layer
FastAPI-compatible wrapper for legal document extraction
"""

import asyncio
from typing import Dict, Any, Optional
from .improved_legal_extractor import ImprovedLegalDocumentExtractor
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
        # The extractor method is already async, so call it directly
        result = await self.extractor.extract_clauses_and_relationships(
            document_text,
            document_type
        )
        # Convert ExtractionResult to dict for JSON serialization
        if hasattr(result, 'dict'):
            return result.dict()
        elif hasattr(result, 'model_dump'):
            return result.model_dump()
        else:
            # Manual conversion for the ExtractionResult
            return {
                "document_id": result.document_id,
                "document_type": result.document_type.value if hasattr(result.document_type, 'value') else str(result.document_type),
                "extracted_clauses": [clause.dict() if hasattr(clause, 'dict') else clause.model_dump() for clause in result.extracted_clauses],
                "clause_relationships": [rel.dict() if hasattr(rel, 'dict') else rel.model_dump() for rel in result.clause_relationships],
                "confidence_score": result.confidence_score,
                "processing_time_seconds": result.processing_time_seconds,
                "extraction_metadata": result.extraction_metadata
            }

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
