"""
MongoDB Service for Document Analyzer API
Handles all MongoDB operations using async Motor
"""

import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError
from bson import ObjectId

logger = logging.getLogger(__name__)


class MongoDBService:
    """Service for MongoDB operations with async Motor"""

    def __init__(self, mongo_uri: str, database_name: str):
        """
        Initialize MongoDB service
        
        Args:
            mongo_uri: MongoDB connection URI
            database_name: Name of the database to use
        """
        self.mongo_uri = mongo_uri
        self.database_name = database_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._connected = False

    async def connect(self) -> bool:
        """
        Connect to MongoDB
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
            
            # Test the connection
            await self.client.admin.command('ping')
            
            self.database = self.client[self.database_name]
            self._connected = True
            
            logger.info(f"Successfully connected to MongoDB database: {self.database_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._connected = False
            return False

    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")

    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        return self._connected

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform MongoDB health check
        
        Returns:
            Health status information
        """
        try:
            if not self._connected:
                return {"status": "disconnected", "error": "Not connected to MongoDB"}

            # Ping the database
            start_time = time.time()
            await self.client.admin.command('ping')
            ping_time = time.time() - start_time

            # Get server info
            server_info = await self.client.server_info()
            
            return {
                "status": "healthy",
                "database": self.database_name,
                "ping_time_ms": round(ping_time * 1000, 2),
                "server_version": server_info.get("version", "unknown")
            }

        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }

    def get_collection(self, collection_name: str) -> AsyncIOMotorCollection:
        """
        Get a collection reference
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection reference
        """
        if not self.database:
            raise RuntimeError("Not connected to MongoDB")
        
        return self.database[collection_name]

    async def insert_processed_document(self, 
                                       document_id: str,
                                       user_id: str,
                                       extraction_result: Dict[str, Any],
                                       original_filename: str,
                                       document_type: str) -> bool:
        """
        Insert a processed document into the processed_documents collection
        
        Args:
            document_id: Unique document identifier
            user_id: User who owns the document
            extraction_result: LangExtract extraction results
            original_filename: Original filename of the document
            document_type: Type of document (rental, loan, tos)
            
        Returns:
            True if insertion successful, False otherwise
        """
        try:
            collection = self.get_collection("processed_documents")
            
            processed_document = {
                "document_id": document_id,
                "user_id": user_id,
                "original_filename": original_filename,
                "document_type": document_type,
                "extraction_result": extraction_result,
                "processing_status": "completed",
                "timestamps": {
                    "processed_at": datetime.utcnow(),
                    "created_at": datetime.utcnow()
                },
                "metadata": {
                    "extraction_engine": "LangExtract",
                    "confidence_score": extraction_result.get("confidence_score", 0.0),
                    "processing_time_seconds": extraction_result.get("processing_time_seconds", 0.0),
                    "total_clauses": len(extraction_result.get("extracted_clauses", [])),
                    "total_relationships": len(extraction_result.get("clause_relationships", []))
                }
            }

            result = await collection.insert_one(processed_document)
            
            if result.inserted_id:
                logger.info(f"Successfully inserted processed document: {document_id}")
                return True
            else:
                logger.error(f"Failed to insert processed document: {document_id}")
                return False

        except Exception as e:
            logger.error(f"Error inserting processed document {document_id}: {e}")
            return False

    async def get_processed_document(self, document_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a processed document by document_id and user_id
        
        Args:
            document_id: Document identifier
            user_id: User identifier
            
        Returns:
            Processed document data or None if not found
        """
        try:
            collection = self.get_collection("processed_documents")
            
            document = await collection.find_one({
                "document_id": document_id,
                "user_id": user_id
            })

            if document:
                # Convert ObjectId to string for JSON serialization
                if "_id" in document:
                    document["_id"] = str(document["_id"])
                
                logger.debug(f"Retrieved processed document: {document_id}")
                return document
            else:
                logger.warning(f"Processed document not found: {document_id} for user: {user_id}")
                return None

        except Exception as e:
            logger.error(f"Error retrieving processed document {document_id}: {e}")
            return None

    async def list_processed_documents(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List processed documents for a user
        
        Args:
            user_id: User identifier
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of processed documents
        """
        try:
            collection = self.get_collection("processed_documents")
            
            cursor = collection.find(
                {"user_id": user_id}
            ).sort("timestamps.processed_at", -1).skip(skip).limit(limit)

            documents = []
            async for doc in cursor:
                # Convert ObjectId to string for JSON serialization
                if "_id" in doc:
                    doc["_id"] = str(doc["_id"])
                documents.append(doc)

            logger.debug(f"Retrieved {len(documents)} processed documents for user: {user_id}")
            return documents

        except Exception as e:
            logger.error(f"Error listing processed documents for user {user_id}: {e}")
            return []

    async def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get processing statistics for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            User statistics
        """
        try:
            collection = self.get_collection("processed_documents")
            
            # Count total documents
            total_docs = await collection.count_documents({"user_id": user_id})
            
            # Count by document type
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": "$document_type",
                    "count": {"$sum": 1}
                }}
            ]
            
            type_counts = {}
            async for result in collection.aggregate(pipeline):
                type_counts[result["_id"]] = result["count"]

            # Average confidence score
            confidence_pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": None,
                    "avg_confidence": {"$avg": "$metadata.confidence_score"}
                }}
            ]
            
            avg_confidence = 0.0
            async for result in collection.aggregate(confidence_pipeline):
                avg_confidence = result.get("avg_confidence", 0.0)

            return {
                "total_documents": total_docs,
                "documents_by_type": type_counts,
                "average_confidence_score": round(avg_confidence, 3) if avg_confidence else 0.0,
                "user_id": user_id
            }

        except Exception as e:
            logger.error(f"Error getting user statistics for {user_id}: {e}")
            return {
                "total_documents": 0,
                "documents_by_type": {},
                "average_confidence_score": 0.0,
                "user_id": user_id,
                "error": str(e)
            }

    async def delete_processed_document(self, document_id: str, user_id: str) -> bool:
        """
        Delete a processed document
        
        Args:
            document_id: Document identifier
            user_id: User identifier
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            collection = self.get_collection("processed_documents")
            
            result = await collection.delete_one({
                "document_id": document_id,
                "user_id": user_id
            })

            if result.deleted_count > 0:
                logger.info(f"Successfully deleted processed document: {document_id}")
                return True
            else:
                logger.warning(f"No document found to delete: {document_id} for user: {user_id}")
                return False

        except Exception as e:
            logger.error(f"Error deleting processed document {document_id}: {e}")
            return False

    async def update_document_processing_status(self, document_id: str, user_id: str, status: str) -> bool:
        """
        Update the processing status of a document
        
        Args:
            document_id: Document identifier
            user_id: User identifier
            status: New processing status
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            collection = self.get_collection("processed_documents")
            
            result = await collection.update_one(
                {
                    "document_id": document_id,
                    "user_id": user_id
                },
                {
                    "$set": {
                        "processing_status": status,
                        "timestamps.last_updated": datetime.utcnow()
                    }
                }
            )

            if result.modified_count > 0:
                logger.info(f"Updated processing status for document {document_id} to: {status}")
                return True
            else:
                logger.warning(f"No document found to update: {document_id} for user: {user_id}")
                return False

        except Exception as e:
            logger.error(f"Error updating document status {document_id}: {e}")
            return False


# Global instance (will be initialized in main.py lifespan)
mongodb_service: Optional[MongoDBService] = None


def get_mongodb_service() -> MongoDBService:
    """Dependency injection for MongoDB service"""
    if mongodb_service is None:
        raise RuntimeError("MongoDB service not initialized")
    return mongodb_service


async def initialize_mongodb_service(mongo_uri: str, database_name: str) -> MongoDBService:
    """
    Initialize the global MongoDB service
    
    Args:
        mongo_uri: MongoDB connection URI
        database_name: Database name
        
    Returns:
        Initialized MongoDB service
    """
    global mongodb_service
    
    mongodb_service = MongoDBService(mongo_uri, database_name)
    
    # Connect to MongoDB
    connected = await mongodb_service.connect()
    if not connected:
        raise RuntimeError("Failed to connect to MongoDB")
    
    logger.info("MongoDB service initialized successfully")
    return mongodb_service


async def cleanup_mongodb_service():
    """Cleanup the global MongoDB service"""
    global mongodb_service
    
    if mongodb_service:
        await mongodb_service.disconnect()
        mongodb_service = None
        logger.info("MongoDB service cleaned up")