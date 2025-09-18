"""
Google Cloud Storage Service for document retrieval
Handles downloading documents from GCS for analysis
"""

import logging
from typing import Optional
from google.cloud import storage
from google.oauth2 import service_account
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class GCSService:
    """Service for handling Google Cloud Storage operations"""

    def __init__(self, bucket_name: str, credentials_path: Optional[str] = None):
        """
        Initialize GCS service

        Args:
            bucket_name: Name of the GCS bucket
            credentials_path: Path to service account credentials (optional if using environment)
        """
        self.bucket_name = bucket_name
        self.credentials_path = credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if not self.credentials_path:
            raise ValueError("Google Cloud credentials not found. Set GOOGLE_APPLICATION_CREDENTIALS or provide credentials_path")

        # Initialize GCS client
        try:
            if os.path.exists(self.credentials_path):
                credentials = service_account.Credentials.from_service_account_file(self.credentials_path)
                self.client = storage.Client(credentials=credentials)
            else:
                # Use default credentials
                self.client = storage.Client()
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")
            raise

        self.bucket = self.client.bucket(bucket_name)
        logger.info(f"GCS service initialized for bucket: {bucket_name}")

    async def download_document(self, gcs_path: str) -> bytes:
        """
        Download document from GCS

        Args:
            gcs_path: Path to the document in GCS (without bucket name)

        Returns:
            Document content as bytes

        Raises:
            FileNotFoundError: If document doesn't exist
            Exception: For other GCS errors
        """
        try:
            logger.info(f"Downloading document from GCS: {gcs_path}")

            # Remove leading slash if present
            gcs_path = gcs_path.lstrip('/')

            # Get blob
            blob = self.bucket.blob(gcs_path)

            # Check if blob exists
            if not blob.exists():
                raise FileNotFoundError(f"Document not found in GCS: {gcs_path}")

            # Download content
            content = blob.download_as_bytes()

            logger.info(f"Successfully downloaded document: {gcs_path} ({len(content)} bytes)")
            return content

        except FileNotFoundError:
            logger.error(f"Document not found in GCS: {gcs_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to download document from GCS: {e}")
            raise Exception(f"GCS download failed: {str(e)}")

    async def get_document_metadata(self, gcs_path: str) -> dict:
        """
        Get document metadata from GCS

        Args:
            gcs_path: Path to the document in GCS

        Returns:
            Dictionary containing metadata
        """
        try:
            gcs_path = gcs_path.lstrip('/')
            blob = self.bucket.blob(gcs_path)

            if not blob.exists():
                raise FileNotFoundError(f"Document not found in GCS: {gcs_path}")

            # Reload blob to get metadata
            blob.reload()

            metadata = {
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created.isoformat() if blob.time_created else None,
                "updated": blob.updated.isoformat() if blob.updated else None,
                "md5_hash": blob.md5_hash,
                "crc32c": blob.crc32c,
                "generation": blob.generation
            }

            return metadata

        except Exception as e:
            logger.error(f"Failed to get document metadata: {e}")
            raise Exception(f"GCS metadata retrieval failed: {str(e)}")

    async def document_exists(self, gcs_path: str) -> bool:
        """
        Check if document exists in GCS

        Args:
            gcs_path: Path to the document in GCS

        Returns:
            True if document exists, False otherwise
        """
        try:
            gcs_path = gcs_path.lstrip('/')
            blob = self.bucket.blob(gcs_path)
            return blob.exists()

        except Exception as e:
            logger.error(f"Failed to check document existence: {e}")
            return False

    def get_signed_url(self, gcs_path: str, expiration_minutes: int = 60) -> str:
        """
        Generate signed URL for direct access to document

        Args:
            gcs_path: Path to the document in GCS
            expiration_minutes: URL expiration time in minutes

        Returns:
            Signed URL string
        """
        try:
            from datetime import timedelta

            gcs_path = gcs_path.lstrip('/')
            blob = self.bucket.blob(gcs_path)

            # Generate signed URL
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=expiration_minutes),
                method="GET"
            )

            return url

        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            raise Exception(f"Signed URL generation failed: {str(e)}")

    async def get_document_text(self, gcs_path: str, max_size_mb: int = 10) -> str:
        """
        Download and convert document to text

        Args:
            gcs_path: Path to the document in GCS
            max_size_mb: Maximum file size in MB

        Returns:
            Document content as text

        Raises:
            ValueError: If file is too large or unsupported format
        """
        try:
            # Download content
            content = await self.download_document(gcs_path)

            # Check file size
            max_size_bytes = max_size_mb * 1024 * 1024
            if len(content) > max_size_bytes:
                raise ValueError(f"Document too large: {len(content)} bytes (max: {max_size_bytes} bytes)")

            # Get file extension to determine processing method
            file_name = Path(gcs_path).name
            file_extension = Path(file_name).suffix.lower()

            # Convert to text based on file type
            if file_extension == '.txt':
                text = content.decode('utf-8', errors='ignore')
            elif file_extension == '.pdf':
                text = await self._extract_text_from_pdf(content)
            elif file_extension in ['.docx', '.doc']:
                text = await self._extract_text_from_docx(content)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

            return text

        except Exception as e:
            logger.error(f"Failed to extract text from document: {e}")
            raise Exception(f"Text extraction failed: {str(e)}")

    async def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            from pypdf import PdfReader
            from io import BytesIO

            pdf_file = BytesIO(content)
            pdf_reader = PdfReader(pdf_file)

            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            return text.strip()

        except ImportError:
            raise Exception("PyPDF2 not installed. Install with: pip install pypdf")
        except Exception as e:
            logger.warning(f"PDF text extraction failed: {e}")
            # Fallback to OCR if available
            try:
                return await self._perform_ocr(content)
            except:
                raise Exception("PDF processing failed and OCR not available")

    async def _extract_text_from_docx(self, content: bytes) -> str:
        """Extract text from DOCX content"""
        try:
            from docx import Document
            from io import BytesIO

            docx_file = BytesIO(content)
            doc = Document(docx_file)

            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            return text.strip()

        except ImportError:
            raise Exception("python-docx not installed. Install with: pip install python-docx")
        except Exception as e:
            raise Exception(f"DOCX processing failed: {str(e)}")

    async def _perform_ocr(self, content: bytes) -> str:
        """Perform OCR on image content"""
        try:
            import pytesseract
            from PIL import Image
            from io import BytesIO

            image = Image.open(BytesIO(content))
            text = pytesseract.image_to_string(image)

            return text.strip()

        except ImportError:
            raise Exception("OCR dependencies not installed. Install with: pip install pytesseract Pillow")
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")
