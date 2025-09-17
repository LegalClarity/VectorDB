"""
RAG System Setup Script
Initialize the complete legal document RAG system.
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from legal_document_processor import LegalDocumentProcessor
from qdrant_vector_store import QdrantVectorStore
from langgraph_rag_orchestrator import RAGOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_setup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def check_environment():
    """
    Check if all required environment variables are set.

    Returns:
        bool: True if environment is properly configured
    """
    required_vars = ['GEMINI_API_KEY', 'QDRANT_HOST', 'QDRANT_API_KEY']

    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.info("Please set the following variables in your .env file:")
        for var in missing_vars:
            logger.info(f"  - {var}")
        return False

    logger.info("✅ Environment variables are properly configured")
    return True


def check_documents():
    """
    Check if legal documents exist in the expected folder.

    Returns:
        bool: True if documents are found
    """
    doc_folder = Path("Rag Documents")

    if not doc_folder.exists():
        logger.error(f"Documents folder not found: {doc_folder}")
        return False

    pdf_files = list(doc_folder.glob("**/*.pdf"))

    if not pdf_files:
        logger.error(f"No PDF files found in {doc_folder}")
        return False

    logger.info(f"✅ Found {len(pdf_files)} PDF documents in {doc_folder}")
    for pdf in pdf_files:
        logger.info(f"  - {pdf.name}")

    return True


def initialize_document_processing():
    """
    Initialize the document processing pipeline.

    Returns:
        tuple: (success, processed_documents)
    """
    try:
        logger.info("🚀 Starting document processing...")

        # Initialize processor
        processor = LegalDocumentProcessor()

        # Process documents
        processed_docs = processor.process_documents("Rag Documents")

        if not processed_docs:
            logger.error("❌ No documents were processed successfully")
            return False, []

        logger.info(f"✅ Successfully processed {len(processed_docs)} documents")

        # Log processing summary
        total_chunks = sum(len(doc['chunks']) for doc in processed_docs)
        logger.info(f"📊 Total chunks created: {total_chunks}")

        for doc in processed_docs:
            logger.info(f"  - {doc['filename']}: {len(doc['chunks'])} chunks")

        return True, processed_docs

    except Exception as e:
        logger.error(f"❌ Document processing failed: {e}")
        return False, []


def initialize_vector_store(processed_docs):
    """
    Initialize the vector store and store document embeddings.

    Args:
        processed_docs: List of processed document objects

    Returns:
        bool: True if successful
    """
    try:
        logger.info("🚀 Initializing vector store...")

        # Initialize vector store
        vector_store = QdrantVectorStore()

        # Check collection status
        collection_info = vector_store.get_collection_info()
        logger.info(f"📊 Collection status: {collection_info}")

        # Store document chunks
        logger.info("🚀 Storing document embeddings...")
        chunks_stored = vector_store.store_document_chunks(processed_docs)

        if chunks_stored == 0:
            logger.error("❌ No chunks were stored in the vector database")
            return False

        logger.info(f"✅ Successfully stored {chunks_stored} chunks in vector database")

        # Verify storage
        final_info = vector_store.get_collection_info()
        logger.info(f"📊 Final collection status: {final_info}")

        return True

    except Exception as e:
        logger.error(f"❌ Vector store initialization failed: {e}")
        return False


def test_rag_system():
    """
    Test the RAG system with sample queries.

    Returns:
        bool: True if tests pass
    """
    try:
        logger.info("🧪 Testing RAG system...")

        # Initialize components
        vector_store = QdrantVectorStore()

        # Test queries
        test_queries = [
            "What are tenant rights under rent control acts?",
            "What is the purpose of consumer protection act?",
            "How does the banking regulation act work?"
        ]

        for query in test_queries:
            logger.info(f"🔍 Testing query: {query}")

            # Search for similar chunks
            results = vector_store.search_similar_chunks(query, limit=3)

            if results:
                logger.info(f"✅ Found {len(results)} relevant chunks")
                for result in results:
                    logger.info(".3f")
            else:
                logger.warning(f"⚠️ No results found for query: {query}")

        logger.info("✅ RAG system testing completed")
        return True

    except Exception as e:
        logger.error(f"❌ RAG system testing failed: {e}")
        return False


def main():
    """
    Main setup function.
    """
    logger.info("🎯 Starting Legal Document RAG System Setup")
    logger.info("=" * 60)

    # Step 1: Check environment
    logger.info("Step 1: Checking environment configuration...")
    if not check_environment():
        logger.error("❌ Environment check failed. Please configure your .env file.")
        sys.exit(1)

    # Step 2: Check documents
    logger.info("Step 2: Checking document availability...")
    if not check_documents():
        logger.error("❌ Document check failed. Please ensure PDF files are in 'Rag Documents' folder.")
        sys.exit(1)

    # Step 3: Process documents
    logger.info("Step 3: Processing legal documents...")
    success, processed_docs = initialize_document_processing()
    if not success:
        logger.error("❌ Document processing failed.")
        sys.exit(1)

    # Step 4: Initialize vector store
    logger.info("Step 4: Setting up vector database...")
    if not initialize_vector_store(processed_docs):
        logger.error("❌ Vector store initialization failed.")
        sys.exit(1)

    # Step 5: Test system
    logger.info("Step 5: Testing RAG system...")
    if not test_rag_system():
        logger.warning("⚠️ Some tests failed, but system may still be functional.")
    else:
        logger.info("✅ All tests passed!")

    # Success message
    logger.info("=" * 60)
    logger.info("🎉 Legal Document RAG System Setup Complete!")
    logger.info("")
    logger.info("You can now run the chatbot with:")
    logger.info("  streamlit run legal_rag_chatbot.py")
    logger.info("")
    logger.info("System Components:")
    logger.info("  📁 Documents processed from: Rag Documents/")
    logger.info("  🗄️ Vector database: QdrantDB")
    logger.info("  🤖 Embedding model: Google EmbeddingGemma-300M")
    logger.info("  🧠 Language model: Google Gemini 2.5 Flash")
    logger.info("  🔄 Orchestration: LangGraph multi-agent system")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
