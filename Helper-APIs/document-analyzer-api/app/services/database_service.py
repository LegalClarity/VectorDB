"""
MongoDB Database Service for processed documents
Handles storage and retrieval of document analysis results
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, OperationFailure
from bson import ObjectId

import sys
import os
# Add the models directory to sys.path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
models_dir = os.path.join(parent_dir, 'models')
if models_dir not in sys.path:
    sys.path.insert(0, models_dir)

from schemas.processed_document import ProcessedDocumentSchema, DocumentAnalysisResult

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for MongoDB operations on processed documents"""

    def __init__(self, connection_string: str, database_name: str, collection_name: str = "processed_documents"):
        """
        Initialize database service

        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database
            collection_name: Name of the collection for processed documents
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.collection_name = collection_name

        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.collection: Optional[AsyncIOMotorCollection] = None

    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.connection_string)
            self.database = self.client[self.database_name]
            self.collection = self.database[self.collection_name]

            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Connected to MongoDB database: {self.database_name}")

            # Create indexes
            await self._create_indexes()

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise Exception(f"MongoDB connection failed: {str(e)}")

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def _create_indexes(self):
        """Create necessary indexes for optimal performance"""
        try:
            # Index for document lookup
            await self.collection.create_index("document_id", unique=True)

            # Index for user queries
            await self.collection.create_index("user_id")

            # Index for document type queries
            await self.collection.create_index("document_type")

            # Index for status queries
            await self.collection.create_index("status")

            # Index for processing queries
            await self.collection.create_index("processing_id")

            # Compound index for user + document type queries
            await self.collection.create_index(["user_id", "document_type"])

            # Compound index for status + date queries
            await self.collection.create_index(["status", "created_at"])

            # Index for text search on summary and key terms
            await self.collection.create_index("analysis_result.summary")
            await self.collection.create_index("analysis_result.key_terms")

            logger.info("Database indexes created successfully")

        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")

    async def store_analysis_result(self, analysis_result: DocumentAnalysisResult) -> str:
        """
        Store document analysis result

        Args:
            analysis_result: The analysis result to store

        Returns:
            The MongoDB document ID
        """
        try:
            # Create document data
            document_data = {
                "document_id": analysis_result.document_id,
                "document_type": analysis_result.document_type,
                "user_id": analysis_result.user_id,
                "analysis_result": analysis_result.dict(),
                "status": "completed",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "version": "1.0",
                "document_type_user_id": f"{analysis_result.document_type}_{analysis_result.user_id}",
                "processing_status_date": f"completed_{datetime.utcnow().date()}"
            }

            # Insert document
            result = await self.collection.insert_one(document_data)
            document_id = str(result.inserted_id)

            logger.info(f"Stored analysis result for document: {analysis_result.document_id}")
            return document_id

        except OperationFailure as e:
            logger.error(f"MongoDB operation failed: {e}")
            raise Exception(f"Database operation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to store analysis result: {e}")
            raise Exception(f"Storage failed: {str(e)}")

    async def get_analysis_result(self, document_id: str, user_id: str) -> Optional[ProcessedDocumentSchema]:
        """
        Retrieve analysis result by document ID

        Args:
            document_id: The document ID
            user_id: The user ID (for security)

        Returns:
            ProcessedDocumentSchema if found, None otherwise
        """
        try:
            # Query document
            query = {"document_id": document_id, "user_id": user_id}
            document = await self.collection.find_one(query)

            if document:
                # Convert ObjectId to string
                document["_id"] = str(document["_id"])
                return ProcessedDocumentSchema(**document)

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve analysis result: {e}")
            raise Exception(f"Retrieval failed: {str(e)}")

    async def update_analysis_status(self, document_id: str, status: str, error_message: Optional[str] = None):
        """
        Update analysis status

        Args:
            document_id: The document ID
            status: New status (pending/processing/completed/failed)
            error_message: Error message if status is failed
        """
        try:
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }

            if error_message:
                update_data["error_message"] = error_message

            # Update compound index field if status changed
            if status in ["completed", "failed"]:
                update_data["processing_status_date"] = f"{status}_{datetime.utcnow().date()}"

            await self.collection.update_one(
                {"document_id": document_id},
                {"$set": update_data}
            )

            logger.info(f"Updated status for document {document_id}: {status}")

        except Exception as e:
            logger.error(f"Failed to update analysis status: {e}")
            raise Exception(f"Status update failed: {str(e)}")

    async def get_user_documents(self, user_id: str, document_type: Optional[str] = None,
                               status: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[ProcessedDocumentSchema]:
        """
        Get user's processed documents with filtering

        Args:
            user_id: User ID
            document_type: Filter by document type (optional)
            status: Filter by processing status (optional)
            skip: Number of documents to skip
            limit: Maximum number of documents to return

        Returns:
            List of processed documents
        """
        try:
            # Build query
            query = {"user_id": user_id}

            if document_type:
                query["document_type"] = document_type

            if status:
                query["status"] = status

            # Query documents
            cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)

            documents = []
            async for document in cursor:
                document["_id"] = str(document["_id"])
                documents.append(ProcessedDocumentSchema(**document))

            return documents

        except Exception as e:
            logger.error(f"Failed to get user documents: {e}")
            raise Exception(f"Document retrieval failed: {str(e)}")

    async def search_documents(self, user_id: str, search_query: str,
                             document_type: Optional[str] = None, limit: int = 20) -> List[ProcessedDocumentSchema]:
        """
        Search documents by text content

        Args:
            user_id: User ID
            search_query: Search query string
            document_type: Filter by document type (optional)
            limit: Maximum number of results

        Returns:
            List of matching documents
        """
        try:
            # Build query
            query = {"user_id": user_id}

            if document_type:
                query["document_type"] = document_type

            # Text search on summary and key terms
            text_query = {
                "$text": {"$search": search_query}
            }

            combined_query = {"$and": [query, text_query]}

            # Query documents
            cursor = self.collection.find(combined_query).sort("created_at", -1).limit(limit)

            documents = []
            async for document in cursor:
                document["_id"] = str(document["_id"])
                documents.append(ProcessedDocumentSchema(**document))

            return documents

        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            raise Exception(f"Document search failed: {str(e)}")

    async def get_processing_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get processing statistics for user

        Args:
            user_id: User ID

        Returns:
            Dictionary with processing statistics
        """
        try:
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": None,
                    "total_documents": {"$sum": 1},
                    "completed_documents": {
                        "$sum": {"$cond": [{"$eq": ["$status", "completed"]}, 1, 0]}
                    },
                    "failed_documents": {
                        "$sum": {"$cond": [{"$eq": ["$status", "failed"]}, 1, 0]}
                    },
                    "by_document_type": {
                        "$push": "$document_type"
                    }
                }}
            ]

            result = await self.collection.aggregate(pipeline).to_list(length=1)

            if result:
                stats = result[0]
                # Count document types
                type_counts = {}
                for doc_type in stats["by_document_type"]:
                    type_counts[doc_type] = type_counts.get(doc_type, 0) + 1

                stats["document_type_breakdown"] = type_counts
                del stats["_id"]
                del stats["by_document_type"]

                return stats

            return {
                "total_documents": 0,
                "completed_documents": 0,
                "failed_documents": 0,
                "document_type_breakdown": {}
            }

        except Exception as e:
            logger.error(f"Failed to get processing stats: {e}")
            return {
                "total_documents": 0,
                "completed_documents": 0,
                "failed_documents": 0,
                "document_type_breakdown": {},
                "error": str(e)
            }

    async def delete_analysis_result(self, document_id: str, user_id: str) -> bool:
        """
        Delete analysis result

        Args:
            document_id: The document ID
            user_id: The user ID (for security)

        Returns:
            True if deleted, False if not found
        """
        try:
            result = await self.collection.delete_one({
                "document_id": document_id,
                "user_id": user_id
            })

            if result.deleted_count > 0:
                logger.info(f"Deleted analysis result for document: {document_id}")
                return True

            return False

        except Exception as e:
            logger.error(f"Failed to delete analysis result: {e}")
            raise Exception(f"Deletion failed: {str(e)}")

    async def get_recent_analyses(self, user_id: str, limit: int = 10) -> List[ProcessedDocumentSchema]:
        """
        Get recently processed documents

        Args:
            user_id: User ID
            limit: Maximum number of documents to return

        Returns:
            List of recently processed documents
        """
        try:
            cursor = self.collection.find(
                {"user_id": user_id, "status": "completed"}
            ).sort("created_at", -1).limit(limit)

            documents = []
            async for document in cursor:
                document["_id"] = str(document["_id"])
                documents.append(ProcessedDocumentSchema(**document))

            return documents

        except Exception as e:
            logger.error(f"Failed to get recent analyses: {e}")
            raise Exception(f"Recent analyses retrieval failed: {str(e)}")
