"""
Legal Document RAG Chatbot - Streamlit Interface
Complete chatbot application for legal document understanding.
"""

import streamlit as st
import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Import our custom modules
from langgraph_rag_orchestrator import QueryProcessor, RAGOrchestrator
from qdrant_vector_store import QdrantVectorStore

# Configure page
st.set_page_config(
    page_title="Legal Document Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processor" not in st.session_state:
    st.session_state.processor = QueryProcessor()
if "vector_store" not in st.session_state:
    st.session_state.vector_store = QdrantVectorStore()
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def add_message(role: str, content: str, metadata: Optional[Dict] = None):
    """
    Add a message to the chat history.

    Args:
        role: Message role ("user" or "assistant")
        content: Message content
        metadata: Additional metadata
    """
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "metadata": metadata or {}
    }
    st.session_state.messages.append(message)
    st.session_state.chat_history.append(message)


def display_message(message: Dict):
    """
    Display a message in the chat interface.

    Args:
        message: Message dictionary
    """
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])

            # Display metadata if available
            if message.get("metadata"):
                metadata = message["metadata"]
                if metadata.get("chunks_count", 0) > 0:
                    st.caption(f"📄 Based on {metadata['chunks_count']} relevant document sections")

                if metadata.get("processing_time"):
                    st.caption(f"⏱️ Response time: {metadata['processing_time']:.2f}s")


def process_user_query(query: str,
                      search_filters: Dict[str, Any],
                      use_streaming: bool = False) -> Dict[str, Any]:
    """
    Process a user query through the RAG pipeline.

    Args:
        query: User's legal question
        search_filters: Search configuration
        use_streaming: Whether to use streaming response

    Returns:
        Processing result
    """
    start_time = time.time()

    try:
        # Process the query
        result = st.session_state.processor.process_query(
            query=query,
            conversation_history=st.session_state.chat_history[-5:],  # Last 5 turns
            search_filters=search_filters
        )

        processing_time = time.time() - start_time

        # Add processing metadata
        result["processing_time"] = processing_time
        result["timestamp"] = datetime.now().isoformat()

        return result

    except Exception as e:
        processing_time = time.time() - start_time
        return {
            "query": query,
            "response": f"I apologize, but I encountered an error processing your query. Error: {str(e)}",
            "retrieved_chunks": [],
            "processing_status": "error",
            "error_message": str(e),
            "processing_time": processing_time,
            "timestamp": datetime.now().isoformat()
        }


def display_document_info():
    """
    Display information about indexed documents.
    """
    try:
        vector_store = st.session_state.vector_store
        collection_info = vector_store.get_collection_info()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Documents", "15")  # We know we have 15 PDF files

        with col2:
            st.metric("Indexed Chunks", collection_info.get("points_count", 0))

        with col3:
            status = "✅ Ready" if collection_info.get("status") == "ready" else "❌ Error"
            st.metric("System Status", status)

    except Exception as e:
        st.error(f"Error loading document information: {e}")


def display_retrieved_chunks(chunks: List[Dict[str, Any]]):
    """
    Display retrieved document chunks in an expandable section.

    Args:
        chunks: List of retrieved chunks
    """
    if not chunks:
        return

    with st.expander("📄 View Retrieved Document Sections", expanded=False):
        for i, chunk in enumerate(chunks, 1):
            st.markdown(f"**Document {i}:** {chunk.get('document_filename', 'Unknown')}")
            st.markdown(f"**Type:** {chunk.get('document_type', 'General Legal')}")
            st.markdown(".3f")
            st.markdown(f"**Content:** {chunk.get('content', '')[:300]}...")

            # Show entities if available
            entities = chunk.get('entities', {})
            if entities.get('parties') or entities.get('dates') or entities.get('monetary_amounts'):
                st.markdown("**Key Entities:**")
                if entities.get('parties'):
                    st.markdown(f"- Parties: {', '.join(entities['parties'][:3])}")
                if entities.get('dates'):
                    st.markdown(f"- Dates: {', '.join(entities['dates'][:3])}")
                if entities.get('monetary_amounts'):
                    st.markdown(f"- Amounts: {', '.join(entities['monetary_amounts'][:3])}")

            st.markdown("---")


def main():
    """
    Main Streamlit application.
    """
    # Title and description
    st.title("⚖️ Legal Document Assistant")
    st.markdown("*Understanding legal documents made simple*")

    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Configuration")

        # Document type filter
        document_types = [
            "All Documents",
            "rent_control_act",
            "contract_act",
            "banking_regulation",
            "consumer_protection",
            "housing_finance",
            "information_technology",
            "model_tenancy"
        ]

        selected_doc_type = st.selectbox(
            "Filter by Document Type:",
            document_types,
            index=0
        )

        # Search parameters
        search_limit = st.slider("Number of Results:", min_value=3, max_value=10, value=5)
        score_threshold = st.slider("Relevance Threshold:", min_value=0.5, max_value=0.9, value=0.7, step=0.1)

        # Advanced options
        with st.expander("Advanced Options", expanded=False):
            use_streaming = st.checkbox("Enable Streaming Response", value=False)
            show_chunks = st.checkbox("Show Retrieved Chunks", value=True)

        # System information
        st.header("📊 System Status")
        display_document_info()

        # Clear chat button
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()

    # Prepare search filters
    search_filters = {
        "limit": search_limit,
        "score_threshold": score_threshold
    }

    if selected_doc_type != "All Documents":
        search_filters["document_type"] = selected_doc_type

    # Display chat messages
    for message in st.session_state.messages:
        display_message(message)

    # Chat input
    if prompt := st.chat_input("Ask about any legal document clause..."):
        # Add user message
        add_message("user", prompt)
        st.rerun()

    # Process the latest user message if it exists and hasn't been processed
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_message = st.session_state.messages[-1]

        # Check if this message has already been processed
        if not any(msg.get("metadata", {}).get("is_response_to") == user_message["timestamp"]
                  for msg in st.session_state.messages if msg["role"] == "assistant"):
            # Process the query
            with st.spinner("🔍 Analyzing legal documents..."):
                result = process_user_query(
                    query=user_message["content"],
                    search_filters=search_filters,
                    use_streaming=use_streaming
                )

            # Add assistant response
            metadata = {
                "chunks_count": result.get("chunks_count", 0),
                "processing_time": result.get("processing_time", 0),
                "is_response_to": user_message["timestamp"],
                "processing_status": result.get("processing_status", "")
            }

            add_message("assistant", result["response"], metadata)

            # Display retrieved chunks if enabled
            if show_chunks and result.get("retrieved_chunks"):
                display_retrieved_chunks(result["retrieved_chunks"])

            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
    **⚠️ Legal Disclaimer:** This AI assistant provides general information about legal documents for educational purposes only.
    It is not a substitute for professional legal advice. Always consult qualified legal professionals for your specific situation.
    """)

    st.markdown("""
    **📚 Supported Document Types:**
    - Rent Control Acts
    - Contract Acts
    - Banking Regulations
    - Consumer Protection Laws
    - Housing Finance Guidelines
    - Information Technology Laws
    - Model Tenancy Agreements
    """)


if __name__ == "__main__":
    main()
