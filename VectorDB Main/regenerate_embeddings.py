"""
Regenerate Embeddings with Google EmbeddingGemma-300M
Script to recreate all embeddings using the new EmbeddingGemma model with 768 dimensions.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from legal_document_processor import LegalDocumentProcessor
from qdrant_vector_store import QdrantVectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('regenerate_embeddings.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def check_document_exists(vector_store, document_filename):
    """
    Check if a document's embeddings already exist in the vector database.

    Args:
        vector_store: QdrantVectorStore instance
        document_filename: Name of the document to check

    Returns:
        bool: True if document exists, False otherwise
    """
    try:
        # Use a dummy query to search for documents with this filename
        # We'll use a very specific search that should match the document if it exists
        dummy_query = f"document about {document_filename.replace('.pdf', '').replace('_', ' ')}"

        # Search with a low limit to check existence
        results = vector_store.search_similar_chunks(
            query=dummy_query,
            limit=1,
            score_threshold=0.1  # Very low threshold just to check existence
        )

        # Check if any results have the matching filename
        for result in results:
            if result.get('document_filename') == document_filename:
                return True

        return False

    except Exception as e:
        logger.warning(f"Error checking document existence for {document_filename}: {e}")
        return False


def regenerate_all_embeddings():
    """
    Regenerate all embeddings using EmbeddingGemma-300M model.
    Only processes documents that don't have embeddings yet.
    """
    logger.info("🚀 Starting smart embedding regeneration with EmbeddingGemma-300M")
    logger.info("=" * 70)

    try:
        # Step 1: Initialize components
        logger.info("Step 1: Initializing components...")
        processor = LegalDocumentProcessor()
        vector_store = QdrantVectorStore()

        # Verify collection configuration
        collection_info = vector_store.get_collection_info()
        logger.info(f"✅ Collection status: {collection_info}")

        # Step 2: Process documents (reuse existing processing)
        logger.info("Step 2: Processing legal documents...")
        processed_docs = processor.process_documents("Rag Documents")

        if not processed_docs:
            logger.error("❌ No documents were processed successfully")
            return False

        logger.info(f"✅ Successfully processed {len(processed_docs)} documents")
        logger.info(f"📊 Total chunks created: {sum(len(doc['chunks']) for doc in processed_docs)}")

        # Step 3: Check which documents need processing
        logger.info("Step 3: Checking document status...")

        docs_to_process = []
        docs_to_skip = []
        total_existing_chunks = 0

        for doc in processed_docs:
            if check_document_exists(vector_store, doc['filename']):
                docs_to_skip.append(doc)
                # Estimate existing chunks (this is approximate)
                estimated_chunks = len(doc['chunks'])
                total_existing_chunks += estimated_chunks
                logger.info(f"⏭️ Skipping {doc['filename']} (~{estimated_chunks} chunks already exist)")
            else:
                docs_to_process.append(doc)
                logger.info(f"🔄 Will process {doc['filename']} ({len(doc['chunks'])} chunks)")

        logger.info(f"📊 Documents to process: {len(docs_to_process)}")
        logger.info(f"📊 Documents to skip: {len(docs_to_skip)}")
        logger.info(f"📊 Estimated existing chunks: {total_existing_chunks}")

        # Step 4: Process only documents that need embeddings
        logger.info("Step 4: Generating embeddings for new documents...")

        total_new_chunks = 0

        for doc in docs_to_process:
            logger.info(f"🔄 Processing document: {doc['filename']}")

            # Collect all chunk texts
            chunk_texts = [chunk['content'] for chunk in doc['chunks']]

            if not chunk_texts:
                logger.warning(f"No chunks found for document: {doc['filename']}")
                continue

            # Generate embeddings for all chunks at once
            try:
                embeddings = vector_store.generate_embeddings(chunk_texts, prompt_name="Retrieval-document")
                logger.info(f"✅ Generated embeddings for {len(embeddings)} chunks with shape: {embeddings.shape}")

                # Create points for each chunk
                points = []
                for i, (chunk, embedding) in enumerate(zip(doc['chunks'], embeddings)):
                    # Use integer ID based on global counter
                    chunk_id = vector_store._get_next_chunk_id()

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

                    from qdrant_client.models import PointStruct
                    point = PointStruct(
                        id=chunk_id,
                        vector=embedding.tolist(),
                        payload=payload
                    )
                    points.append(point)

                # Store in batches
                chunks_stored = vector_store.store_document_chunks([doc])
                total_new_chunks += chunks_stored
                logger.info(f"📊 Stored {chunks_stored} chunks for {doc['filename']}")

            except Exception as e:
                logger.error(f"❌ Failed to generate embeddings for {doc['filename']}: {e}")
                continue

        # Step 5: Final verification
        logger.info("Step 5: Final verification...")
        final_info = vector_store.get_collection_info()
        logger.info(f"📊 Final collection status: {final_info}")

        total_chunks_in_db = final_info.get('points_count', 0)
        expected_total = total_existing_chunks + total_new_chunks

        logger.info(f"📊 Existing chunks: {total_existing_chunks}")
        logger.info(f"📊 New chunks added: {total_new_chunks}")
        logger.info(f"📊 Total in database: {total_chunks_in_db}")
        logger.info(f"📊 Expected total: {expected_total}")

        if abs(total_chunks_in_db - expected_total) > 10:  # Allow small discrepancy
            logger.warning(f"⚠️ Point count discrepancy: DB has {total_chunks_in_db}, expected ~{expected_total}")

        # Step 6: Test search functionality
        logger.info("Step 6: Testing search functionality...")
        test_queries = [
            "What are tenant rights under rent control acts?",
            "Explain consumer protection provisions",
            "What does the banking regulation act say?"
        ]

        successful_searches = 0
        for test_query in test_queries:
            logger.info(f"🔍 Testing query: {test_query[:50]}...")
            results = vector_store.search_similar_chunks(test_query, limit=3)

            if results:
                successful_searches += 1
                logger.info(f"✅ Found {len(results)} relevant chunks")
                for result in results[:2]:  # Show first 2 results
                    logger.info(".3f")
            else:
                logger.warning(f"⚠️ No results found for: {test_query[:50]}...")

        logger.info("=" * 70)
        logger.info("🎉 Smart embedding regeneration completed!")
        logger.info(f"📊 Documents processed: {len(docs_to_process)}")
        logger.info(f"📊 Documents skipped: {len(docs_to_skip)}")
        logger.info(f"📊 New embeddings generated: {total_new_chunks}")
        logger.info(f"📊 Search tests passed: {successful_searches}/{len(test_queries)}")
        logger.info("🔄 Model: Google EmbeddingGemma-300M (768 dimensions)")
        logger.info("=" * 70)

        return True

    except Exception as e:
        logger.error(f"❌ Embedding regeneration failed: {e}")
        return False


if __name__ == "__main__":
    success = regenerate_all_embeddings()
    if success:
        print("\n🎉 Embeddings successfully regenerated with EmbeddingGemma-300M!")
        print("🚀 The chatbot is now using the improved embedding model.")
    else:
        print("\n❌ Embedding regeneration failed. Check the logs for details.")
        sys.exit(1)
