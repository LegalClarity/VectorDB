"""
MongoDB database connection and operations using Motor async driver
"""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, OperationFailure

from config import settings
from models import Document, User, DocumentCreateRequest, DocumentUpdateRequest

logger = logging.getLogger(__name__)


class DatabaseManager:
    """MongoDB connection manager"""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self.documents_collection: Optional[AsyncIOMotorCollection] = None
        self.users_collection: Optional[AsyncIOMotorCollection] = None

    async def connect(self) -> None:
        """Establish connection to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.mongo_uri)
            self.database = self.client[settings.mongo_db]
            self.documents_collection = self.database[settings.mongo_docs_collection]
            self.users_collection = self.database[settings.mongo_users_collection]

            # Test connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")

            # Create indexes for better performance
            await self._create_indexes()

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise

    async def disconnect(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")

    async def _create_indexes(self) -> None:
        """Create database indexes for optimal performance"""
        try:
            # Document collection indexes
            await self.documents_collection.create_index([("user_id", 1)])
            await self.documents_collection.create_index([("document_id", 1)])
            await self.documents_collection.create_index([("user_id", 1), ("document_id", 1)], unique=True)
            await self.documents_collection.create_index([("timestamps.created_at", -1)])
            await self.documents_collection.create_index([("document_metadata.document_type", 1)])
            await self.documents_collection.create_index([("document_metadata.tags", 1)])
            await self.documents_collection.create_index([("status.upload_status", 1)])

            # User collection indexes
            await self.users_collection.create_index([("user_id", 1)], unique=True)
            await self.users_collection.create_index([("email", 1)], unique=True)
            await self.users_collection.create_index([("last_active", -1)])

            logger.info("Database indexes created successfully")

        except OperationFailure as e:
            logger.warning(f"Index creation failed (may already exist): {e}")


class DocumentRepository:
    """Repository for document operations"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def create_document(self, document_data: Dict[str, Any]) -> str:
        """Create a new document record"""
        try:
            result = await self.db_manager.documents_collection.insert_one(document_data)
            logger.info(f"Document created with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            raise

    async def get_document_by_id_and_user(self, document_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get document by document_id and user_id"""
        try:
            document = await self.db_manager.documents_collection.find_one({
                "document_id": document_id,
                "user_id": user_id
            })
            return document
        except Exception as e:
            logger.error(f"Failed to get document {document_id} for user {user_id}: {e}")
            raise

    async def get_user_documents(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Get documents for a user with optional filtering and pagination"""
        try:
            query = {"user_id": user_id}

            if filters:
                if filters.get("document_type"):
                    query["document_metadata.document_type"] = filters["document_type"]
                if filters.get("category"):
                    query["document_metadata.category"] = filters["category"]
                if filters.get("confidentiality"):
                    query["document_metadata.confidentiality"] = filters["confidentiality"]
                if filters.get("tags"):
                    query["document_metadata.tags"] = {"$in": filters["tags"]}
                if filters.get("upload_status"):
                    query["status.upload_status"] = filters["upload_status"]

            cursor = self.db_manager.documents_collection.find(query)
            cursor = cursor.skip(skip).limit(limit)
            cursor = cursor.sort("timestamps.created_at", -1)

            documents = await cursor.to_list(length=None)
            return documents

        except Exception as e:
            logger.error(f"Failed to get documents for user {user_id}: {e}")
            raise

    async def get_user_documents_count(self, user_id: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Get total count of user's documents"""
        try:
            query = {"user_id": user_id}

            if filters:
                if filters.get("document_type"):
                    query["document_metadata.document_type"] = filters["document_type"]
                if filters.get("category"):
                    query["document_metadata.category"] = filters["category"]
                if filters.get("confidentiality"):
                    query["document_metadata.confidentiality"] = filters["confidentiality"]
                if filters.get("tags"):
                    query["document_metadata.tags"] = {"$in": filters["tags"]}
                if filters.get("upload_status"):
                    query["status.upload_status"] = filters["upload_status"]

            count = await self.db_manager.documents_collection.count_documents(query)
            return count

        except Exception as e:
            logger.error(f"Failed to count documents for user {user_id}: {e}")
            raise

    async def update_document_status(self, document_id: str, user_id: str, status: Dict[str, Any]) -> bool:
        """Update document status"""
        try:
            result = await self.db_manager.documents_collection.update_one(
                {"document_id": document_id, "user_id": user_id},
                {
                    "$set": {
                        "status": status,
                        "timestamps.updated_at": datetime.utcnow()
                    }
                }
            )
            success = result.modified_count > 0
            if success:
                logger.info(f"Document {document_id} status updated")
            else:
                logger.warning(f"No document found to update: {document_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to update document {document_id} status: {e}")
            raise

    async def update_document_metadata(
        self,
        document_id: str,
        user_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Update document metadata"""
        try:
            update_data = {
                "timestamps.updated_at": datetime.utcnow()
            }

            # Only update fields that are provided
            if "document_metadata" in metadata:
                for key, value in metadata["document_metadata"].items():
                    if value is not None:
                        update_data[f"document_metadata.{key}"] = value

            result = await self.db_manager.documents_collection.update_one(
                {"document_id": document_id, "user_id": user_id},
                {"$set": update_data}
            )

            success = result.modified_count > 0
            if success:
                logger.info(f"Document {document_id} metadata updated")
            return success

        except Exception as e:
            logger.error(f"Failed to update document {document_id} metadata: {e}")
            raise

    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete document by document_id and user_id"""
        try:
            result = await self.db_manager.documents_collection.delete_one({
                "document_id": document_id,
                "user_id": user_id
            })
            success = result.deleted_count > 0
            if success:
                logger.info(f"Document {document_id} deleted from database")
            else:
                logger.warning(f"No document found to delete: {document_id}")
            return success
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            raise


class UserRepository:
    """Repository for user operations"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        try:
            result = await self.db_manager.users_collection.insert_one(user_data)
            logger.info(f"User created with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by user_id"""
        try:
            user = await self.db_manager.users_collection.find_one({"user_id": user_id})
            return user
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            user = await self.db_manager.users_collection.find_one({"email": email})
            return user
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            raise

    async def update_user_activity(self, user_id: str) -> bool:
        """Update user's last active timestamp"""
        try:
            result = await self.db_manager.users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"last_active": datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update user activity for {user_id}: {e}")
            raise


# Global instances
db_manager = DatabaseManager()
document_repo = DocumentRepository(db_manager)
user_repo = UserRepository(db_manager)
