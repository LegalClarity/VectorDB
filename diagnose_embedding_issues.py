"""
Diagnose Embedding Issues in QdrantDB Collection
Script to identify and analyze embedding dimension inconsistencies.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from qdrant_vector_store import QdrantVectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diagnose_embeddings.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def diagnose_collection_issues():
    """
    Diagnose issues with the QdrantDB collection and embeddings.
    """
    logger.info("🔍 Starting embedding diagnostics")
    logger.info("=" * 60)

    try:
        # Initialize vector store
        vector_store = QdrantVectorStore()

        # Step 1: Get collection info
        logger.info("Step 1: Analyzing collection configuration...")
        collection_info = vector_store.get_collection_info()
        logger.info(f"✅ Collection info: {collection_info}")

        # Step 2: Sample some vectors to check dimensions
        logger.info("Step 2: Sampling vectors for dimension analysis...")

        # Get some points to inspect
        try:
            # Use Qdrant client directly to inspect vectors
            points_response = vector_store.client.retrieve(
                collection_name="legal_documents",
                ids=[1, 2, 3, 100, 200, 500],  # Sample some IDs
                with_payload=False,
                with_vectors=True
            )

            logger.info(f"✅ Retrieved {len(points_response)} sample points")

            for i, point in enumerate(points_response[:3]):  # Show first 3
                vector_dim = len(point.vector) if point.vector else 0
                logger.info(f"  Point ID {point.id}: Vector dimension = {vector_dim}")

            # Count dimensions
            dim_counts = {}
            for point in points_response:
                if point.vector:
                    dim = len(point.vector)
                    dim_counts[dim] = dim_counts.get(dim, 0) + 1

            logger.info(f"📊 Dimension distribution in sample: {dim_counts}")

        except Exception as e:
            logger.warning(f"Could not retrieve sample points: {e}")

        # Step 3: Test basic search
        logger.info("Step 3: Testing basic search functionality...")

        test_queries = [
            "tenant rights",
            "contract agreement",
            "banking regulations"
        ]

        for query in test_queries:
            logger.info(f"🔍 Testing query: '{query}'")
            try:
                results = vector_store.search_similar_chunks(
                    query=query,
                    limit=3,
                    score_threshold=0.0  # Very low threshold to get any results
                )

                if results:
                    logger.info(f"✅ Found {len(results)} results")
                    for result in results[:2]:
                        logger.info(".3f")
                else:
                    logger.warning("⚠️ No results found (even with low threshold)")

            except Exception as e:
                logger.error(f"❌ Search failed for '{query}': {e}")

        # Step 4: Analyze potential issues
        logger.info("Step 4: Analyzing potential issues...")

        issues_found = []

        # Check for dimension mismatch
        if collection_info.get('vectors_count') is None:
            logger.warning("⚠️ Collection vectors_count is None - may indicate issues")

        # Check if we have points but no search results
        points_count = collection_info.get('points_count', 0)
        if points_count > 0:
            logger.info(f"✅ Collection has {points_count} points")

            # Try a very simple search
            try:
                simple_results = vector_store.client.search(
                    collection_name="legal_documents",
                    query_vector=[0.1] * 768,  # Simple query vector
                    limit=1,
                    score_threshold=0.0
                )
                if not simple_results:
                    issues_found.append("Search returns no results even with simple query")
                    logger.warning("⚠️ Even simple vector search returns no results")
            except Exception as e:
                issues_found.append(f"Simple search failed: {e}")
                logger.error(f"❌ Simple search failed: {e}")

        # Step 5: Provide recommendations
        logger.info("Step 5: Generating recommendations...")
        logger.info("=" * 60)

        if issues_found:
            logger.info("🚨 ISSUES IDENTIFIED:")
            for issue in issues_found:
                logger.info(f"  - {issue}")
        else:
            logger.info("✅ No major issues detected")

        logger.info("\n📋 RECOMMENDATIONS:")
        logger.info("1. 🔄 Consider recreating collection with consistent embedding dimensions")
        logger.info("2. 📊 Verify all vectors have the same dimension (768 for EmbeddingGemma)")
        logger.info("3. 🔍 Test with lower similarity thresholds")
        logger.info("4. 🏗️ If issues persist, recreate collection from scratch")
        logger.info("5. 📈 Monitor embedding quality and search performance")

        return True

    except Exception as e:
        logger.error(f"❌ Diagnostics failed: {e}")
        return False


def test_embedding_dimensions():
    """
    Test if embedding dimensions are consistent.
    """
    logger.info("🧪 Testing embedding dimension consistency...")

    try:
        vector_store = QdrantVectorStore()

        # Test embedding generation
        test_texts = ["This is a test document.", "Another test text."]

        # Generate with document prompt
        doc_embeddings = vector_store.generate_embeddings(test_texts, prompt_name="document")
        logger.info(f"📊 Document embeddings shape: {doc_embeddings.shape}")

        # Generate with query prompt
        query_embedding = vector_store.generate_embeddings(["test query"], prompt_name="query")
        logger.info(f"📊 Query embeddings shape: {query_embedding.shape}")

        # Check if dimensions match
        if doc_embeddings.shape[1] == query_embedding.shape[1] == 768:
            logger.info("✅ All embeddings have consistent 768 dimensions")
            return True
        else:
            logger.error(f"❌ Dimension mismatch: docs={doc_embeddings.shape[1]}, query={query_embedding.shape[1]}")
            return False

    except Exception as e:
        logger.error(f"❌ Embedding dimension test failed: {e}")
        return False


if __name__ == "__main__":
    logger.info("🩺 Starting QdrantDB Embedding Diagnostics")
    logger.info("=" * 60)

    # Run diagnostics
    success = diagnose_collection_issues()

    if success:
        logger.info("\n🧪 Testing embedding dimensions...")
        dim_test = test_embedding_dimensions()

        logger.info("=" * 60)
        if dim_test:
            logger.info("✅ Embedding diagnostics completed successfully")
        else:
            logger.info("⚠️ Embedding diagnostics completed with warnings")
    else:
        logger.info("❌ Embedding diagnostics failed")

    logger.info("=" * 60)
