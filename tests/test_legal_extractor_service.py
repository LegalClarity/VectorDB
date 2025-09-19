"""
Unit tests for Legal Extractor Service Layer
Tests the LegalExtractorService wrapper class
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import sys
import os

# Add the API path to sys.path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Helper-APIs', 'document-analyzer-api'))

from app.services.legal_extractor_service import LegalExtractorService


class TestLegalExtractorService:
    """Test cases for legal extractor service"""

    @pytest.fixture
    def service(self):
        """Create service instance for testing"""
        return LegalExtractorService()

    def test_service_initialization(self, service):
        """Test service initialization"""
        assert service.extractor is not None
        assert hasattr(service.extractor, 'extract_clauses_and_relationships')

    @pytest.mark.asyncio
    async def test_extract_clauses_and_relationships(self, service):
        """Test clause extraction functionality"""
        # Mock the underlying extractor
        service.extractor = MagicMock()
        service.extractor.extract_clauses_and_relationships = MagicMock(return_value={
            "document_type": "rental",
            "extracted_clauses": [],
            "relationships": []
        })

        result = await service.extract_clauses_and_relationships(
            "test document text",
            "rental"
        )

        assert result is not None
        assert "document_type" in result
        service.extractor.extract_clauses_and_relationships.assert_called_once_with(
            "test document text",
            "rental"
        )

    @pytest.mark.asyncio
    async def test_create_structured_document(self, service):
        """Test structured document creation"""
        # Mock the underlying extractor
        service.extractor = MagicMock()
        service.extractor.create_structured_document = MagicMock(return_value={
            "structured_document": "mocked result",
            "validation_status": "success"
        })

        mock_extraction_result = {"test": "data"}
        mock_original_text = "Original document text"

        result = await service.create_structured_document(
            mock_extraction_result,
            mock_original_text
        )

        assert result is not None
        assert "structured_document" in result
        service.extractor.create_structured_document.assert_called_once_with(
            mock_extraction_result,
            mock_original_text
        )

    @pytest.mark.asyncio
    async def test_extract_with_progress(self, service):
        """Test extraction with progress callback"""
        # Mock the underlying extractor
        service.extractor = MagicMock()
        service.extractor.extract_clauses_and_relationships = MagicMock(return_value={
            "status": "completed",
            "progress": 100
        })

        def mock_callback(progress):
            pass

        result = await service.extract_with_progress(
            "test text",
            "rental",
            mock_callback
        )

        assert result is not None
        assert result["status"] == "completed"

    def test_service_with_custom_api_key(self):
        """Test service initialization with custom API key"""
        custom_key = "test-api-key-123"
        service = LegalExtractorService(gemini_api_key=custom_key)

        # The service should pass the API key to the extractor
        assert service.extractor is not None

    @pytest.mark.asyncio
    async def test_async_wrapper_error_handling(self, service):
        """Test error handling in async wrapper"""
        # Mock extractor to raise an exception
        service.extractor = MagicMock()
        service.extractor.extract_clauses_and_relationships = MagicMock(
            side_effect=Exception("Mock extraction error")
        )

        with pytest.raises(Exception):
            await service.extract_clauses_and_relationships("test", "rental")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
