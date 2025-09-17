"""
File validation logic for legal documents
"""
import os
import logging
from typing import List, Optional, BinaryIO
from fastapi import UploadFile, HTTPException
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result of file validation"""

    def __init__(self):
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.metadata: dict = {}

    def add_error(self, error: str):
        """Add validation error"""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """Add validation warning"""
        self.warnings.append(warning)

    def set_metadata(self, key: str, value: any):
        """Set metadata"""
        self.metadata[key] = value


class DocumentValidator:
    """Validator for legal document uploads"""

    def __init__(self):
        self.allowed_extensions = settings.allowed_extensions
        self.allowed_mime_types = settings.allowed_mime_types
        self.max_file_size = settings.max_upload_size

    async def validate_file(self, file: UploadFile) -> ValidationResult:
        """
        Comprehensive file validation

        Args:
            file: FastAPI UploadFile object

        Returns:
            ValidationResult: Validation results with errors/warnings
        """
        result = ValidationResult()

        try:
            # Validate file extension
            await self._validate_file_extension(file.filename, result)

            # Validate MIME type
            await self._validate_mime_type(file.content_type, result)

            # Validate file size
            await self._validate_file_size(file, result)

            # Basic content validation
            await self._validate_file_content(file, result)

            # Extract metadata
            await self._extract_metadata(file, result)

        except Exception as e:
            logger.error(f"Error during file validation: {e}")
            result.add_error(f"Validation failed: {str(e)}")

        return result

    async def _validate_file_extension(self, filename: str, result: ValidationResult):
        """Validate file extension"""
        if not filename:
            result.add_error("Filename is required")
            return

        file_extension = Path(filename).suffix.lower()

        if not file_extension:
            result.add_error("File must have an extension")
            return

        if file_extension not in self.allowed_extensions:
            result.add_error(
                f"Unsupported file type: {file_extension}. "
                f"Allowed types: {', '.join(self.allowed_extensions)}"
            )

    async def _validate_mime_type(self, content_type: str, result: ValidationResult):
        """Validate MIME content type"""
        if not content_type:
            result.add_error("Content type is required")
            return

        if content_type not in self.allowed_mime_types:
            result.add_error(
                f"Unsupported content type: {content_type}. "
                f"Allowed types: {', '.join(self.allowed_mime_types)}"
            )

    async def _validate_file_size(self, file: UploadFile, result: ValidationResult):
        """Validate file size"""
        try:
            # Get file size
            file_size = await self._get_file_size(file)

            if file_size > self.max_file_size:
                result.add_error(
                    f"File size ({file_size} bytes) exceeds maximum limit "
                    f"({self.max_file_size} bytes)"
                )
            elif file_size == 0:
                result.add_error("File is empty")
            else:
                result.set_metadata('file_size', file_size)

        except Exception as e:
            result.add_error(f"Could not determine file size: {str(e)}")

    async def _validate_file_content(self, file: UploadFile, result: ValidationResult):
        """Basic content validation"""
        try:
            # Read first few bytes to check if file is readable
            content = await file.read(1024)
            await file.seek(0)  # Reset file pointer

            if not content:
                result.add_error("File appears to be empty")
                return

            # Basic checks for different file types
            content_type = file.content_type

            if content_type == 'application/pdf':
                if not content.startswith(b'%PDF'):
                    result.add_error("Invalid PDF file format")
            elif content_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                # For Word documents, check for basic structure
                if len(content) < 10:
                    result.add_error("Word document appears to be corrupted")
            elif content_type == 'text/plain':
                # For text files, check if it's actually text
                try:
                    content.decode('utf-8')
                except UnicodeDecodeError:
                    result.add_warning("File may contain non-text content")

        except Exception as e:
            result.add_error(f"Content validation failed: {str(e)}")

    async def _extract_metadata(self, file: UploadFile, result: ValidationResult):
        """Extract file metadata"""
        try:
            result.set_metadata('filename', file.filename)
            result.set_metadata('content_type', file.content_type)

            # Get file size if not already set
            if 'file_size' not in result.metadata:
                file_size = await self._get_file_size(file)
                result.set_metadata('file_size', file_size)

        except Exception as e:
            logger.warning(f"Could not extract metadata: {str(e)}")

    async def _get_file_size(self, file: UploadFile) -> int:
        """Get file size efficiently"""
        # Try to get size from file object first
        if hasattr(file, 'size') and file.size is not None:
            return file.size

        # Fallback: read file to determine size
        original_position = await file.tell()
        await file.seek(0, 2)  # Seek to end
        file_size = await file.tell()
        await file.seek(original_position)  # Reset position

        return file_size

    def validate_user_id(self, user_id: str) -> bool:
        """Validate user ID format"""
        if not user_id or not isinstance(user_id, str):
            return False

        # Basic validation - user_id should not be empty and should not contain special characters
        if len(user_id.strip()) == 0:
            return False

        # Check for potentially dangerous characters
        dangerous_chars = ['/', '\\', '<', '>', ':', '*', '?', '"', '|']
        if any(char in user_id for char in dangerous_chars):
            return False

        return True

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage"""
        if not filename:
            return "unnamed_file"

        # Remove path separators and dangerous characters
        dangerous_chars = ['/', '\\', '<', '>', ':', '*', '?', '"', '|', '\0']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')

        # Limit filename length
        name_part, ext_part = os.path.splitext(filename)
        if len(name_part) > 100:
            name_part = name_part[:100]

        return name_part + ext_part


# Global validator instance
document_validator = DocumentValidator()


def validate_upload_request(user_id: str, file: UploadFile) -> ValidationResult:
    """
    Convenience function to validate upload request

    Args:
        user_id: User identifier
        file: Uploaded file

    Returns:
        ValidationResult: Validation results

    Raises:
        HTTPException: If validation fails
    """
    # Validate user_id
    if not document_validator.validate_user_id(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    # Validate file
    # Note: This is synchronous but calls async validation
    # In practice, this should be called from an async context
    import asyncio
    result = asyncio.run(document_validator.validate_file(file))

    if not result.is_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "File validation failed",
                "errors": result.errors,
                "warnings": result.warnings
            }
        )

    return result
