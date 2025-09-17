"""
Comprehensive tests for the Legal Document Upload API
"""
import pytest
import io
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import UploadFile

from app.main import app
from app.config import settings
from app.validation import document_validator, ValidationResult


# Test client
client = TestClient(app)


class TestDocumentValidator:
    """Test document validation functionality"""

    def test_validate_user_id_valid(self):
        """Test valid user ID validation"""
        assert document_validator.validate_user_id("user123") == True
        assert document_validator.validate_user_id("test_user") == True

    def test_validate_user_id_invalid(self):
        """Test invalid user ID validation"""
        assert document_validator.validate_user_id("") == False
        assert document_validator.validate_user_id("   ") == False
        assert document_validator.validate_user_id("user/with/slashes") == False
        assert document_validator.validate_user_id("user<with>brackets") == False

    @pytest.mark.asyncio
    async def test_validate_file_valid_pdf(self):
        """Test valid PDF file validation"""
        # Create mock PDF content
        pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n"
        file = UploadFile(
            filename="test.pdf",
            file=io.BytesIO(pdf_content),
            content_type="application/pdf"
        )

        result = await document_validator.validate_file(file)
        assert result.is_valid == True
        assert result.metadata['filename'] == "test.pdf"
        assert result.metadata['content_type'] == "application/pdf"

    @pytest.mark.asyncio
    async def test_validate_file_invalid_extension(self):
        """Test file with invalid extension"""
        file = UploadFile(
            filename="test.exe",
            file=io.BytesIO(b"test content"),
            content_type="application/octet-stream"
        )

        result = await document_validator.validate_file(file)
        assert result.is_valid == False
        assert len(result.errors) > 0
        assert "Unsupported file type" in result.errors[0]

    @pytest.mark.asyncio
    async def test_validate_file_oversized(self):
        """Test oversized file validation"""
        # Create a file larger than the limit
        large_content = b"x" * (settings.max_upload_size + 1)
        file = UploadFile(
            filename="large.pdf",
            file=io.BytesIO(large_content),
            content_type="application/pdf"
        )

        result = await document_validator.validate_file(file)
        assert result.is_valid == False
        assert any("exceeds maximum limit" in error for error in result.errors)

    @pytest.mark.asyncio
    async def test_validate_file_empty(self):
        """Test empty file validation"""
        file = UploadFile(
            filename="empty.pdf",
            file=io.BytesIO(b""),
            content_type="application/pdf"
        )

        result = await document_validator.validate_file(file)
        assert result.is_valid == False
        assert any("empty" in error.lower() for error in result.errors)


class TestDocumentEndpoints:
    """Test document upload endpoints"""

    @patch('app.database.document_repo.create_document')
    @patch('app.database.user_repo.update_user_activity')
    @patch('app.gcs_service.gcs_service.upload_file')
    @pytest.mark.asyncio
    async def test_upload_document_success(self, mock_gcs_upload, mock_user_activity, mock_create_doc):
        """Test successful document upload"""
        # Mock GCS upload response
        mock_gcs_upload.return_value = {
            'success': True,
            'object_path': 'users/test_user/123e4567-e89b-12d3-a456-426614174000',
            'file_hash': 'test_hash',
            'file_size': 1024,
            'gcs_url': 'gs://test-bucket/users/test_user/123e4567-e89b-12d3-a456-426614174000'
        }

        # Mock database operations
        mock_create_doc.return_value = "mock_id"

        # Create test file
        file_content = b"%PDF-1.4\ntest pdf content"
        files = {'file': ('test.pdf', io.BytesIO(file_content), 'application/pdf')}
        data = {'user_id': 'test_user'}

        response = client.post("/documents/upload", files=files, data=data)

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['document_id'] is not None
        assert response_data['gcs_url'] is not None
        assert response_data['message'] == "Document uploaded successfully"

        # Verify mocks were called
        mock_gcs_upload.assert_called_once()
        mock_create_doc.assert_called_once()
        mock_user_activity.assert_called_once()

    def test_upload_document_invalid_user_id(self):
        """Test upload with invalid user ID"""
        file_content = b"test content"
        files = {'file': ('test.pdf', io.BytesIO(file_content), 'application/pdf')}
        data = {'user_id': ''}

        response = client.post("/documents/upload", files=files, data=data)

        assert response.status_code == 400
        assert "Invalid user ID" in response.json()['detail']

    def test_upload_document_no_file(self):
        """Test upload without file"""
        data = {'user_id': 'test_user'}

        response = client.post("/documents/upload", data=data)

        assert response.status_code == 422  # Validation error

    @patch('app.gcs_service.gcs_service.upload_file')
    def test_upload_document_gcs_failure(self, mock_gcs_upload):
        """Test upload when GCS fails"""
        # Mock GCS failure
        mock_gcs_upload.side_effect = Exception("GCS upload failed")

        file_content = b"%PDF-1.4\ntest content"
        files = {'file': ('test.pdf', io.BytesIO(file_content), 'application/pdf')}
        data = {'user_id': 'test_user'}

        response = client.post("/documents/upload", files=files, data=data)

        assert response.status_code == 500
        assert "Upload failed" in response.json()['detail']

    @patch('app.database.document_repo.get_document_by_id_and_user')
    @patch('app.gcs_service.gcs_service.generate_signed_url')
    def test_get_document_success(self, mock_signed_url, mock_get_doc):
        """Test successful document retrieval"""
        # Mock document data
        mock_document = {
            'user_id': 'test_user',
            'document_id': '123e4567-e89b-12d3-a456-426614174000',
            'original_filename': 'test.pdf',
            'stored_filename': 'test_user_123e4567-e89b-12d3-a456-426614174000',
            'gcs_bucket_name': 'test-bucket',
            'gcs_object_path': 'users/test_user/123e4567-e89b-12d3-a456-426614174000',
            'file_metadata': {
                'content_type': 'application/pdf',
                'file_size': 1024,
                'file_hash': 'test_hash',
                'upload_method': 'single'
            },
            'document_metadata': {
                'document_type': '',
                'category': '',
                'tags': [],
                'description': '',
                'confidentiality': 'private'
            },
            'timestamps': {
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-01T00:00:00Z',
                'expires_at': None
            },
            'status': {
                'upload_status': 'completed',
                'processing_status': 'processed',
                'validation_errors': []
            }
        }

        mock_get_doc.return_value = mock_document
        mock_signed_url.return_value = "https://signed-url.example.com"

        response = client.get("/documents/123e4567-e89b-12d3-a456-426614174000?user_id=test_user")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['document_id'] == '123e4567-e89b-12d3-a456-426614174000'
        assert response_data['user_id'] == 'test_user'
        assert 'signed_url' in response_data

    def test_get_document_not_found(self):
        """Test document retrieval when not found"""
        with patch('app.database.document_repo.get_document_by_id_and_user', return_value=None):
            response = client.get("/documents/nonexistent-id?user_id=test_user")

            assert response.status_code == 404
            assert "not found" in response.json()['detail'].lower()

    @patch('app.database.document_repo.get_user_documents')
    @patch('app.database.document_repo.get_user_documents_count')
    @patch('app.gcs_service.gcs_service.generate_signed_url')
    def test_list_documents_success(self, mock_signed_url, mock_count, mock_get_docs):
        """Test successful document listing"""
        # Mock documents
        mock_docs = [
            {
                'user_id': 'test_user',
                'document_id': '123e4567-e89b-12d3-a456-426614174000',
                'original_filename': 'test1.pdf',
                'gcs_object_path': 'users/test_user/123e4567-e89b-12d3-a456-426614174000',
                'document_metadata': {'document_type': 'contract'},
                'timestamps': {'created_at': '2023-01-01T00:00:00Z'},
                'status': {'upload_status': 'completed'}
            }
        ]

        mock_get_docs.return_value = mock_docs
        mock_count.return_value = 1
        mock_signed_url.return_value = "https://signed-url.example.com"

        response = client.get("/documents?user_id=test_user")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['total_count'] == 1
        assert len(response_data['documents']) == 1
        assert response_data['documents'][0]['document_id'] == '123e4567-e89b-12d3-a456-426614174000'

    @patch('app.database.document_repo.delete_document')
    @patch('app.gcs_service.gcs_service.delete_file')
    @patch('app.database.document_repo.get_document_by_id_and_user')
    def test_delete_document_success(self, mock_get_doc, mock_gcs_delete, mock_db_delete):
        """Test successful document deletion"""
        # Mock document data
        mock_document = {
            'user_id': 'test_user',
            'document_id': '123e4567-e89b-12d3-a456-426614174000',
            'gcs_object_path': 'users/test_user/123e4567-e89b-12d3-a456-426614174000'
        }

        mock_get_doc.return_value = mock_document
        mock_gcs_delete.return_value = True
        mock_db_delete.return_value = True

        response = client.delete("/documents/123e4567-e89b-12d3-a456-426614174000?user_id=test_user")

        assert response.status_code == 200
        assert "deleted successfully" in response.json()['message']

    def test_delete_document_not_found(self):
        """Test document deletion when not found"""
        with patch('app.database.document_repo.get_document_by_id_and_user', return_value=None):
            response = client.delete("/documents/nonexistent-id?user_id=test_user")

            assert response.status_code == 404
            assert "not found" in response.json()['detail'].lower()


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check_success(self):
        """Test successful health check"""
        response = client.get("/health")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['status'] == 'healthy'
        assert 'services' in response_data
        assert 'mongodb' in response_data['services']
        assert 'gcs' in response_data['services']


class TestRootEndpoint:
    """Test root endpoint"""

    def test_root_endpoint(self):
        """Test root endpoint returns correct information"""
        response = client.get("/")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data['message'] == 'Legal Document Upload API'
        assert 'docs' in response_data
        assert 'health' in response_data


if __name__ == "__main__":
    pytest.main([__file__])
