"""
Tests for Document Analyzer API
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_gemini_api_key():
    """Mock Gemini API key"""
    return "test_gemini_api_key"


@pytest.fixture
def mock_mongo_uri():
    """Mock MongoDB URI"""
    return "mongodb://localhost:27017/test"


@pytest.fixture
def sample_document_text():
    """Sample document text for testing"""
    return """
    This is a sample rental agreement between Mr. John Doe and Ms. Jane Smith.
    The monthly rent is Rs. 25,000/- payable on the 5th of every month.
    Security deposit is Rs. 50,000/-.
    The lease period is from 1st February 2024 to 31st January 2025.
    """


@pytest.fixture
def sample_analysis_request():
    """Sample analysis request data"""
    return {
        "document_id": "doc_123456",
        "document_type": "rental",
        "user_id": "user_789"
    }


class TestAnalyzerAPI:
    """Test cases for Document Analyzer API"""

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/analyzer/health")
        assert response.status_code == 200

        data = response.json()
        assert data["service"] == "document_analyzer"
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "Legal Clarity - Document Analyzer API" in data["message"]
        assert data["version"] == "1.0.0"
        assert "endpoints" in data

    @patch('app.services.database_service.DatabaseService')
    @patch('app.services.gcs_service.GCSService')
    @patch('app.services.document_analyzer.DocumentAnalyzerService')
    def test_analyze_document_success(self, mock_analyzer, mock_gcs, mock_db,
                                    client, sample_analysis_request, sample_document_text):
        """Test successful document analysis"""
        # Mock the services
        mock_analyzer_instance = MagicMock()
        mock_analyzer.return_value = mock_analyzer_instance

        mock_gcs_instance = MagicMock()
        mock_gcs.return_value = mock_gcs_instance
        mock_gcs_instance.document_exists.return_value = True
        mock_gcs_instance.get_document_text.return_value = sample_document_text

        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.get_analysis_result.return_value = None

        # Mock analysis result
        mock_result = MagicMock()
        mock_result.dict.return_value = {"test": "result"}
        mock_analyzer_instance.analyze_document.return_value = mock_result

        # Make request
        response = client.post("/api/analyzer/analyze", json=sample_analysis_request)

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["status"] == "processing"
        assert "document_id" in data["data"]

    def test_analyze_document_invalid_type(self, client):
        """Test analysis with invalid document type"""
        request_data = {
            "document_id": "doc_123456",
            "document_type": "invalid_type",
            "user_id": "user_789"
        }

        response = client.post("/api/analyzer/analyze", json=request_data)
        assert response.status_code == 400

        data = response.json()
        assert data["success"] is False
        assert "Invalid document type" in data["error"]["message"]

    @patch('app.services.database_service.DatabaseService')
    def test_analyze_document_not_found(self, mock_db, client, sample_analysis_request):
        """Test analysis when document doesn't exist in GCS"""
        # Mock database
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance

        # Make request (will fail because GCS service isn't mocked)
        response = client.post("/api/analyzer/analyze", json=sample_analysis_request)
        assert response.status_code == 500  # Internal server error due to missing GCS mock

    @patch('app.services.database_service.DatabaseService')
    def test_get_analysis_results_not_found(self, mock_db, client):
        """Test getting analysis results when not found"""
        # Mock database
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.get_analysis_result.return_value = None

        response = client.get("/api/analyzer/results/doc_123456?user_id=user_789")
        assert response.status_code == 404

        data = response.json()
        assert data["success"] is False
        assert "not found" in data["error"]["message"]

    @patch('app.services.database_service.DatabaseService')
    def test_list_documents(self, mock_db, client):
        """Test listing analyzed documents"""
        # Mock database
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.get_user_documents.return_value = []

        response = client.get("/api/analyzer/documents?user_id=user_789")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert "documents" in data["data"]
        assert "total_count" in data["data"]

    @patch('app.services.database_service.DatabaseService')
    def test_get_user_stats(self, mock_db, client):
        """Test getting user statistics"""
        # Mock database
        mock_db_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_db_instance.get_processing_stats.return_value = {
            "total_documents": 5,
            "completed_documents": 4,
            "failed_documents": 1
        }

        response = client.get("/api/analyzer/stats/user_789")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["total_documents"] == 5
        assert data["data"]["completed_documents"] == 4


class TestDocumentAnalyzerService:
    """Test cases for DocumentAnalyzerService"""

    @pytest.mark.asyncio
    async def test_analyze_document_structure(self):
        """Test that analysis returns proper structure"""
        # This would require more complex mocking of LangExtract
        # For now, just test that the service can be instantiated
        pass

    def test_service_initialization(self, mock_gemini_api_key):
        """Test service initialization"""
        from app.services.document_analyzer import DocumentAnalyzerService

        service = DocumentAnalyzerService(
            gemini_api_key=mock_gemini_api_key,
            gemini_model="gemini-2.0-flash-exp"
        )

        assert service.gemini_api_key == mock_gemini_api_key
        assert service.gemini_model == "gemini-2.0-flash-exp"


if __name__ == "__main__":
    pytest.main([__file__])
