"""
QdrantDB Vector Store Integration for Legal Documents
Handles embedding generation, vector storage, and retrieval operations.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """
    QdrantDB integration for storing and retrieving legal document embeddings.
    """

    def __init__(self,
                 collection_name: str = "legal_documents",
                 embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the vector store.

        Args:
            collection_name: Name of the Qdrant collection
            embedding_model_name: Name of the embedding model to use
        """
        # Initialize QdrantDB client
        self.client = QdrantClient(
            url=os.getenv("QDRANT_HOST", "https://15929434-00ee-41f7-ab85-35d8ffa3c7a6.europe-west3-0.gcp.cloud.qdrant.io"),
            api_key=os.getenv("QDRANT_API_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.YQW-y2048hAJUFX0oN5Zvyp9R2FZj37102HWArV-nTA")
        )

        self.collection_name = collection_name
        self.embedding_model_name = embedding_model_name

        # Initialize embedding model
        logger.info(f"Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)

        # Create collection if it doesn't exist
        self._ensure_collection_exists()

        # Global counter for chunk IDs
        self.chunk_id_counter = 0

    def _get_next_chunk_id(self) -> int:
        """
        Get the next available chunk ID.

        Returns:
            Integer chunk ID
        """
        self.chunk_id_counter += 1
        return self.chunk_id_counter

    def _ensure_collection_exists(self):
        """
        Ensure the Qdrant collection exists with proper configuration.
        """
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")

                # Create collection with proper vector configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # all-MiniLM-L6-v2 produces 384-dimensional vectors
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection {self.collection_name} created successfully")
            else:
                logger.info(f"Collection {self.collection_name} already exists")

        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            raise

    def generate_embeddings(self,
                          texts: List[str],
                          prompt_name: str = "retrieval_document") -> np.ndarray:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings
            prompt_name: Prompt type for the embedding model

        Returns:
            Numpy array of embeddings
        """
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts using {prompt_name} prompt")

            # Use the specified prompt for task-specific embeddings
            embeddings = self.embedding_model.encode(
                texts,
                prompt_name=prompt_name,
                convert_to_numpy=True,
                normalize_embeddings=True  # Normalize for cosine similarity
            )

            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise

    def store_document_chunks(self,
                            processed_documents: List[Dict[str, Any]]) -> int:
        """
        Store document chunks in QdrantDB with metadata.

        Args:
            processed_documents: List of processed document objects

        Returns:
            Number of chunks stored
        """
        points = []
        chunk_count = 0

        for doc in processed_documents:
            logger.info(f"Processing document: {doc['filename']}")

            # Collect all chunk texts
            chunk_texts = [chunk['content'] for chunk in doc['chunks']]

            if not chunk_texts:
                logger.warning(f"No chunks found for document: {doc['filename']}")
                continue

            # Generate embeddings for all chunks at once
            try:
                embeddings = self.generate_embeddings(chunk_texts, prompt_name="document")
            except Exception as e:
                logger.error(f"Failed to generate embeddings for {doc['filename']}: {e}")
                continue

            # Create points for each chunk
            for i, (chunk, embedding) in enumerate(zip(doc['chunks'], embeddings)):
                # Use integer ID based on global counter
                chunk_id = self._get_next_chunk_id()

                # Prepare metadata
                payload = {
                    "document_filename": doc['filename'],
                    "document_path": doc['filepath'],
                    "document_type": doc['doc_type'],
                    "chunk_id": i,
                    "chunk_type": chunk['chunk_type'],
                    "content": chunk['content'],
                    "word_count": chunk['word_count'],
                    "entities": chunk['entities'],
                    "summary": doc['summary']
                }

                # Create point
                point = PointStruct(
                    id=chunk_id,
                    vector=embedding.tolist(),
                    payload=payload
                )

                points.append(point)
                chunk_count += 1

                # Batch insert every 50 points to avoid memory issues and timeouts
                if len(points) >= 50:
                    self._batch_insert_points(points)
                    points = []

        # Insert remaining points
        if points:
            self._batch_insert_points(points)

        logger.info(f"Successfully stored {chunk_count} chunks in QdrantDB")
        return chunk_count

    def _batch_insert_points(self, points: List[PointStruct], max_retries: int = 3):
        """
        Batch insert points into QdrantDB with retry logic.

        Args:
            points: List of PointStruct objects
            max_retries: Maximum number of retry attempts
        """
        for attempt in range(max_retries):
            try:
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=points,
                    wait=True  # Wait for operation to complete
                )
                logger.info(f"Inserted batch of {len(points)} points (attempt {attempt + 1})")
                return
            except Exception as e:
                logger.warning(f"Error inserting batch (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"Failed to insert batch after {max_retries} attempts: {e}")
                    raise

    def search_similar_chunks(self,
                            query: str,
                            limit: int = 5,
                            score_threshold: float = 0.7,
                            filter_doc_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for similar document chunks.

        Args:
            query: Search query
            limit: Maximum number of results
            score_threshold: Minimum similarity score
            filter_doc_type: Filter by document type

        Returns:
            List of similar chunks with metadata
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embeddings(
                [query],
                prompt_name="query"
            )[0]

            # Prepare search filters
            search_filter = None
            if filter_doc_type:
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                search_filter = Filter(
                    must=[
                        FieldCondition(
                            key="document_type",
                            match=MatchValue(value=filter_doc_type)
                        )
                    ]
                )

            # Perform search
            search_params = {
                "collection_name": self.collection_name,
                "query_vector": query_embedding.tolist(),
                "limit": limit,
                "score_threshold": score_threshold,
                "with_payload": True
            }

            if search_filter:
                search_params["query_filter"] = search_filter

            search_results = self.client.search(**search_params)

            # Format results
            results = []
            for result in search_results:
                result_dict = {
                    "chunk_id": result.id,
                    "score": result.score,
                    "content": result.payload.get("content", ""),
                    "document_filename": result.payload.get("document_filename", ""),
                    "document_type": result.payload.get("document_type", ""),
                    "chunk_type": result.payload.get("chunk_type", ""),
                    "entities": result.payload.get("entities", {}),
                    "word_count": result.payload.get("word_count", 0)
                }
                results.append(result_dict)

            logger.info(f"Found {len(results)} similar chunks for query: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Error searching similar chunks: {e}")
            return []

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection.

        Returns:
            Collection information
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": collection_info.vectors_count if hasattr(collection_info, 'vectors_count') else 0,
                "points_count": collection_info.points_count if hasattr(collection_info, 'points_count') else 0,
                "status": "ready"
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"status": "error", "error": str(e)}

    def delete_collection(self):
        """
        Delete the collection (for testing/cleanup).
        """
        try:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")

    def hybrid_search(self,
                     query: str,
                     limit: int = 5,
                     keyword_weight: float = 0.3,
                     semantic_weight: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining keyword and semantic similarity.

        Args:
            query: Search query
            limit: Maximum number of results
            keyword_weight: Weight for keyword matching
            semantic_weight: Weight for semantic similarity

        Returns:
            List of search results
        """
        # For now, implement basic semantic search
        # TODO: Implement proper hybrid search with sparse vectors
        return self.search_similar_chunks(query, limit)


# Usage example
if __name__ == "__main__":
    # Initialize vector store
    vector_store = QdrantVectorStore()

    # Get collection info
    info = vector_store.get_collection_info()
    print(f"Collection Info: {info}")

    # Example search
    query = "What are the rights of tenants under rent control acts?"
    results = vector_store.search_similar_chunks(query, limit=3)

    for result in results:
        print(f"\nScore: {result['score']:.3f}")
        print(f"Document: {result['document_filename']}")
        print(f"Content: {result['content'][:200]}...")
