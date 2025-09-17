"""
Google Cloud Storage service for file uploads and management
"""
import os
import hashlib
import logging
from typing import Optional, BinaryIO
from datetime import datetime, timedelta
from google.cloud import storage
from google.oauth2 import service_account
from google.api_core.exceptions import GoogleAPIError, NotFound

from config import settings

logger = logging.getLogger(__name__)


class GCSService:
    """Google Cloud Storage service for document management"""

    def __init__(self):
        self.client: Optional[storage.Client] = None
        self.bucket = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize GCS client with service account authentication"""
        try:
            if settings.gcs_service_account_path and os.path.exists(settings.gcs_service_account_path):
                # Use service account key file
                credentials = service_account.Credentials.from_service_account_file(
                    settings.gcs_service_account_path
                )
                self.client = storage.Client(
                    credentials=credentials,
                    project=settings.google_project_id
                )
            else:
                # Use Application Default Credentials (ADC)
                self.client = storage.Client(project=settings.google_project_id)

            # Get bucket reference
            self.bucket = self.client.bucket(settings.user_doc_bucket)
            logger.info(f"GCS client initialized for bucket: {settings.user_doc_bucket}")

        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise

    def _calculate_file_hash(self, file_obj: BinaryIO) -> str:
        """Calculate SHA-256 hash of file content"""
        file_obj.seek(0)  # Reset file pointer to beginning
        hash_sha256 = hashlib.sha256()

        # Read file in chunks to handle large files
        for chunk in iter(lambda: file_obj.read(4096), b""):
            hash_sha256.update(chunk)

        file_obj.seek(0)  # Reset file pointer again
        return hash_sha256.hexdigest()

    async def upload_file(
        self,
        file_obj: BinaryIO,
        user_id: str,
        document_id: str,
        original_filename: str,
        content_type: str
    ) -> dict:
        """
        Upload file to GCS with proper organization

        Args:
            file_obj: File object to upload
            user_id: User identifier
            document_id: Unique document identifier
            original_filename: Original filename
            content_type: MIME content type

        Returns:
            dict: Upload result with metadata
        """
        try:
            # Calculate file hash for integrity verification
            file_hash = self._calculate_file_hash(file_obj)

            # Create object path: users/{user_id}/{document_id}
            object_path = f"users/{user_id}/{document_id}"

            # Create blob
            blob = self.bucket.blob(object_path)

            # Set metadata
            blob.metadata = {
                'original_filename': original_filename,
                'user_id': user_id,
                'document_id': document_id,
                'uploaded_at': datetime.utcnow().isoformat(),
                'file_hash': file_hash
            }

            # Upload file with content type
            blob.upload_from_file(
                file_obj,
                content_type=content_type,
                predefined_acl='private'  # Private access by default
            )

            # Get file size
            file_size = blob.size

            logger.info(f"File uploaded successfully: {object_path}")

            return {
                'success': True,
                'object_path': object_path,
                'file_hash': file_hash,
                'file_size': file_size,
                'gcs_url': f"gs://{settings.user_doc_bucket}/{object_path}",
                'public_url': blob.public_url if blob.public_url else None
            }

        except GoogleAPIError as e:
            logger.error(f"GCS upload failed: {e}")
            raise Exception(f"Failed to upload file to GCS: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during GCS upload: {e}")
            raise Exception(f"Unexpected error during file upload: {str(e)}")

    async def generate_signed_url(
        self,
        object_path: str,
        expiration_minutes: int = 60
    ) -> str:
        """
        Generate signed URL for secure file access

        Args:
            object_path: GCS object path
            expiration_minutes: URL expiration time in minutes

        Returns:
            str: Signed URL for file access
        """
        try:
            blob = self.bucket.blob(object_path)

            # Check if blob exists
            if not blob.exists():
                raise NotFound(f"File not found: {object_path}")

            # Generate signed URL
            expiration = datetime.utcnow() + timedelta(minutes=expiration_minutes)
            signed_url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET"
            )

            logger.info(f"Signed URL generated for: {object_path}")
            return signed_url

        except NotFound:
            raise Exception(f"File not found: {object_path}")
        except GoogleAPIError as e:
            logger.error(f"Failed to generate signed URL: {e}")
            raise Exception(f"Failed to generate signed URL: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error generating signed URL: {e}")
            raise Exception(f"Unexpected error: {str(e)}")

    async def delete_file(self, object_path: str) -> bool:
        """
        Delete file from GCS

        Args:
            object_path: GCS object path to delete

        Returns:
            bool: True if deletion successful
        """
        try:
            blob = self.bucket.blob(object_path)

            # Check if blob exists
            if not blob.exists():
                logger.warning(f"File not found for deletion: {object_path}")
                return False

            # Delete the blob
            blob.delete()

            logger.info(f"File deleted successfully: {object_path}")
            return True

        except GoogleAPIError as e:
            logger.error(f"GCS delete failed: {e}")
            raise Exception(f"Failed to delete file from GCS: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during GCS delete: {e}")
            raise Exception(f"Unexpected error during file deletion: {str(e)}")

    async def get_file_metadata(self, object_path: str) -> Optional[dict]:
        """
        Get file metadata from GCS

        Args:
            object_path: GCS object path

        Returns:
            dict: File metadata or None if not found
        """
        try:
            blob = self.bucket.blob(object_path)

            # Check if blob exists
            if not blob.exists():
                return None

            # Reload to get metadata
            blob.reload()

            metadata = {
                'name': blob.name,
                'size': blob.size,
                'content_type': blob.content_type,
                'created': blob.time_created,
                'updated': blob.updated,
                'metadata': blob.metadata or {},
                'public_url': blob.public_url if hasattr(blob, 'public_url') else None
            }

            return metadata

        except GoogleAPIError as e:
            logger.error(f"Failed to get file metadata: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting file metadata: {e}")
            return None

    async def list_user_files(self, user_id: str, max_results: int = 100) -> list:
        """
        List all files for a specific user

        Args:
            user_id: User identifier
            max_results: Maximum number of results to return

        Returns:
            list: List of file objects
        """
        try:
            prefix = f"users/{user_id}/"
            blobs = list(self.bucket.list_blobs(prefix=prefix, max_results=max_results))

            files = []
            for blob in blobs:
                files.append({
                    'name': blob.name,
                    'size': blob.size,
                    'content_type': blob.content_type,
                    'created': blob.time_created,
                    'updated': blob.updated,
                    'metadata': blob.metadata or {}
                })

            return files

        except GoogleAPIError as e:
            logger.error(f"Failed to list user files: {e}")
            raise Exception(f"Failed to list files: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error listing files: {e}")
            raise Exception(f"Unexpected error: {str(e)}")


# Global GCS service instance
gcs_service = GCSService()
