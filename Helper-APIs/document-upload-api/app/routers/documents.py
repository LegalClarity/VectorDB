"""
Document upload and management endpoints
"""
import uuid
import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse

from config import settings
from models import Document, UploadResponse, BatchUploadResponse
from schemas import DocumentResponse, DocumentListResponse, DocumentFilter, SignedURLResponse
from database import document_repo, user_repo
from gcs_service import gcs_service
from validation import document_validator, ValidationResult

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    """
    Upload a single document

    - Validates file type and size
    - Stores file in Google Cloud Storage
    - Saves metadata in MongoDB
    - Returns upload confirmation
    """
    try:
        logger.info(f"Document upload request from user: {user_id}, file: {file.filename}")

        # Validate user_id
        if not document_validator.validate_user_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")

        # Validate file
        validation_result = await document_validator.validate_file(file)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "File validation failed",
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings
                }
            )

        # Generate unique document ID
        document_id = str(uuid.uuid4())

        # Upload file to GCS
        upload_result = await gcs_service.upload_file(
            file_obj=file.file,
            user_id=user_id,
            document_id=document_id,
            original_filename=file.filename,
            content_type=file.content_type
        )

        # Prepare document metadata for MongoDB
        document_data = {
            "user_id": user_id,
            "document_id": document_id,
            "original_filename": file.filename,
            "stored_filename": f"{user_id}_{document_id}",
            "gcs_bucket_name": settings.user_doc_bucket,
            "gcs_object_path": upload_result['object_path'],
            "file_metadata": {
                "content_type": file.content_type,
                "file_size": upload_result['file_size'],
                "file_hash": upload_result['file_hash'],
                "upload_method": "single"
            },
            "document_metadata": {
                "document_type": "",
                "category": "",
                "tags": [],
                "description": "",
                "confidentiality": "private"
            },
            "timestamps": {
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "expires_at": None
            },
            "status": {
                "upload_status": "completed",
                "processing_status": "processed",
                "validation_errors": []
            }
        }

        # Save to MongoDB
        await document_repo.create_document(document_data)

        # Update user activity
        background_tasks.add_task(user_repo.update_user_activity, user_id)

        logger.info(f"Document uploaded successfully: {document_id}")

        return UploadResponse(
            document_id=document_id,
            gcs_url=upload_result['gcs_url'],
            message="Document uploaded successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload-multiple", response_model=BatchUploadResponse)
async def upload_multiple_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    user_id: str = Form(...)
):
    """
    Upload multiple documents in batch

    - Processes multiple files simultaneously
    - Returns batch results with individual status
    """
    try:
        logger.info(f"Batch upload request from user: {user_id}, files: {len(files)}")

        # Validate user_id
        if not document_validator.validate_user_id(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID")

        if not files:
            raise HTTPException(status_code=400, detail="No files provided")

        if len(files) > 10:  # Limit batch size
            raise HTTPException(status_code=400, detail="Maximum 10 files per batch upload")

        successful_uploads = 0
        failed_uploads = 0
        results = []

        for file in files:
            try:
                # Validate file
                validation_result = await document_validator.validate_file(file)
                if not validation_result.is_valid:
                    failed_uploads += 1
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "errors": validation_result.errors
                    })
                    continue

                # Generate unique document ID
                document_id = str(uuid.uuid4())

                # Upload file to GCS
                upload_result = await gcs_service.upload_file(
                    file_obj=file.file,
                    user_id=user_id,
                    document_id=document_id,
                    original_filename=file.filename,
                    content_type=file.content_type
                )

                # Prepare document metadata
                document_data = {
                    "user_id": user_id,
                    "document_id": document_id,
                    "original_filename": file.filename,
                    "stored_filename": f"{user_id}_{document_id}",
                    "gcs_bucket_name": settings.user_doc_bucket,
                    "gcs_object_path": upload_result['object_path'],
                    "file_metadata": {
                        "content_type": file.content_type,
                        "file_size": upload_result['file_size'],
                        "file_hash": upload_result['file_hash'],
                        "upload_method": "batch"
                    },
                    "document_metadata": {
                        "document_type": "",
                        "category": "",
                        "tags": [],
                        "description": "",
                        "confidentiality": "private"
                    },
                    "timestamps": {
                        "created_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow(),
                        "expires_at": None
                    },
                    "status": {
                        "upload_status": "completed",
                        "processing_status": "processed",
                        "validation_errors": []
                    }
                }

                # Save to MongoDB
                await document_repo.create_document(document_data)

                successful_uploads += 1
                results.append({
                    "filename": file.filename,
                    "success": True,
                    "document_id": document_id,
                    "gcs_url": upload_result['gcs_url']
                })

            except Exception as e:
                failed_uploads += 1
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "errors": [str(e)]
                })
                logger.error(f"Failed to upload file {file.filename}: {e}")

        # Update user activity
        background_tasks.add_task(user_repo.update_user_activity, user_id)

        logger.info(f"Batch upload completed: {successful_uploads} successful, {failed_uploads} failed")

        return BatchUploadResponse(
            total_files=len(files),
            successful_uploads=successful_uploads,
            failed_uploads=failed_uploads,
            results=results
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """
    Get document metadata by document ID

    - Requires user_id for authorization
    - Returns document metadata and signed GCS URL
    """
    try:
        logger.info(f"Document retrieval request: {document_id} for user: {user_id}")

        # Get document from database
        document = await document_repo.get_document_by_id_and_user(document_id, user_id)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found or access denied")

        # Generate signed URL for secure access
        try:
            signed_url = await gcs_service.generate_signed_url(
                document['gcs_object_path'],
                expiration_minutes=60
            )
            document['signed_url'] = signed_url
        except Exception as e:
            logger.warning(f"Could not generate signed URL for {document_id}: {e}")
            document['signed_url'] = None

        # Convert to response format
        response = DocumentResponse(**document)

        logger.info(f"Document retrieved successfully: {document_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    user_id: str = Query(..., description="User ID"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    document_type: Optional[str] = Query(None, description="Filter by document type"),
    category: Optional[str] = Query(None, description="Filter by category"),
    confidentiality: Optional[str] = Query(None, description="Filter by confidentiality"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags")
):
    """
    List user's documents with optional filtering and pagination

    - Returns paginated list of user's documents
    - Supports filtering by various criteria
    """
    try:
        logger.info(f"Document list request for user: {user_id}, page: {page}")

        # Prepare filters
        filters = {}
        if document_type:
            filters['document_type'] = document_type
        if category:
            filters['category'] = category
        if confidentiality:
            filters['confidentiality'] = confidentiality
        if tags:
            filters['tags'] = tags

        # Calculate skip for pagination
        skip = (page - 1) * page_size

        # Get documents
        documents = await document_repo.get_user_documents(
            user_id=user_id,
            skip=skip,
            limit=page_size,
            filters=filters
        )

        # Get total count for pagination
        total_count = await document_repo.get_user_documents_count(user_id, filters)

        # Generate signed URLs for all documents
        for document in documents:
            try:
                signed_url = await gcs_service.generate_signed_url(
                    document['gcs_object_path'],
                    expiration_minutes=60
                )
                document['signed_url'] = signed_url
            except Exception as e:
                logger.warning(f"Could not generate signed URL for {document.get('document_id')}: {e}")
                document['signed_url'] = None

        response = DocumentListResponse(
            documents=[DocumentResponse(**doc) for doc in documents],
            total_count=total_count,
            page=page,
            page_size=page_size
        )

        logger.info(f"Document list retrieved: {len(documents)} documents for user {user_id}")
        return response

    except Exception as e:
        logger.error(f"Document list retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"List retrieval failed: {str(e)}")


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """
    Delete document by document ID

    - Requires user_id for authorization
    - Deletes from both GCS and MongoDB
    """
    try:
        logger.info(f"Document deletion request: {document_id} for user: {user_id}")

        # Get document to verify ownership and get GCS path
        document = await document_repo.get_document_by_id_and_user(document_id, user_id)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found or access denied")

        # Delete from GCS
        gcs_deleted = await gcs_service.delete_file(document['gcs_object_path'])

        # Delete from MongoDB
        db_deleted = await document_repo.delete_document(document_id, user_id)

        if gcs_deleted and db_deleted:
            logger.info(f"Document deleted successfully: {document_id}")
            return {"message": "Document deleted successfully"}
        else:
            logger.warning(f"Partial deletion for document {document_id}: GCS={gcs_deleted}, DB={db_deleted}")
            raise HTTPException(
                status_code=500,
                detail="Document partially deleted. Please contact support."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@router.get("/{document_id}/signed-url", response_model=SignedURLResponse)
async def get_signed_url(
    document_id: str,
    user_id: str = Query(..., description="User ID for authorization"),
    expiration_minutes: int = Query(60, ge=1, le=1440, description="URL expiration in minutes")
):
    """
    Generate signed URL for secure document access

    - Requires user_id for authorization
    - Returns time-limited signed URL
    """
    try:
        logger.info(f"Signed URL request: {document_id} for user: {user_id}")

        # Get document to verify ownership and get GCS path
        document = await document_repo.get_document_by_id_and_user(document_id, user_id)

        if not document:
            raise HTTPException(status_code=404, detail="Document not found or access denied")

        # Generate signed URL
        signed_url = await gcs_service.generate_signed_url(
            document['gcs_object_path'],
            expiration_minutes=expiration_minutes
        )

        response = SignedURLResponse(
            document_id=document_id,
            signed_url=signed_url,
            expires_at=datetime.utcnow().replace(second=0, microsecond=0)  # Remove seconds for cleaner output
        )

        logger.info(f"Signed URL generated for document: {document_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signed URL generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Signed URL generation failed: {str(e)}")
