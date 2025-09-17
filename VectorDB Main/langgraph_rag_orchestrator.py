"""
LangGraph Multi-Agent RAG Orchestrator for Legal Documents
Coordinates document processing, retrieval, and response generation agents.
"""

import logging
from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

# Import our custom modules
from legal_document_processor import LegalDocumentProcessor
from qdrant_vector_store import QdrantVectorStore
from gemini_legal_assistant import GeminiLegalAssistant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGState(TypedDict):
    """
    State object for the RAG orchestration graph.
    """
    query: str
    processed_documents: Optional[List[Dict[str, Any]]]
    retrieved_chunks: Optional[List[Dict[str, Any]]]
    generated_response: Optional[str]
    conversation_history: Optional[List[Dict[str, str]]]
    search_filters: Optional[Dict[str, Any]]
    processing_status: str
    error_message: Optional[str]


class DocumentProcessingAgent:
    """
    Agent responsible for processing legal documents.
    """

    def __init__(self, document_folder: str = "Rag Documents"):
        self.document_folder = document_folder
        self.processor = LegalDocumentProcessor()

    def process(self, state: RAGState) -> RAGState:
        """
        Process documents and update state.

        Args:
            state: Current graph state

        Returns:
            Updated state
        """
        try:
            logger.info("Document Processing Agent: Starting document processing")

            # Process all documents in the folder
            processed_docs = self.processor.process_documents(self.document_folder)

            if not processed_docs:
                logger.warning("No documents were processed successfully")
                return {
                    **state,
                    "processed_documents": [],
                    "processing_status": "no_documents",
                    "error_message": "No documents could be processed"
                }

            logger.info(f"Document Processing Agent: Processed {len(processed_docs)} documents")

            return {
                **state,
                "processed_documents": processed_docs,
                "processing_status": "documents_processed"
            }

        except Exception as e:
            logger.error(f"Document Processing Agent error: {e}")
            return {
                **state,
                "processed_documents": [],
                "processing_status": "error",
                "error_message": str(e)
            }


class EmbeddingStorageAgent:
    """
    Agent responsible for generating embeddings and storing in vector database.
    """

    def __init__(self):
        self.vector_store = QdrantVectorStore()

    def process(self, state: RAGState) -> RAGState:
        """
        Generate embeddings and store documents.

        Args:
            state: Current graph state

        Returns:
            Updated state
        """
        try:
            logger.info("Embedding Storage Agent: Starting embedding generation")

            processed_docs = state.get("processed_documents", [])

            if not processed_docs:
                logger.warning("No processed documents found for embedding")
                return {
                    **state,
                    "processing_status": "no_documents_for_embedding"
                }

            # Store document chunks in vector database
            chunks_stored = self.vector_store.store_document_chunks(processed_docs)

            logger.info(f"Embedding Storage Agent: Stored {chunks_stored} chunks")

            return {
                **state,
                "processing_status": "embeddings_stored",
                "chunks_stored": chunks_stored
            }

        except Exception as e:
            logger.error(f"Embedding Storage Agent error: {e}")
            return {
                **state,
                "processing_status": "embedding_error",
                "error_message": str(e)
            }


class RetrievalAgent:
    """
    Agent responsible for retrieving relevant document chunks.
    """

    def __init__(self):
        self.vector_store = QdrantVectorStore()

    def process(self, state: RAGState) -> RAGState:
        """
        Retrieve relevant chunks for the query.

        Args:
            state: Current graph state

        Returns:
            Updated state
        """
        try:
            logger.info("Retrieval Agent: Starting document retrieval")

            query = state.get("query", "")
            search_filters = state.get("search_filters", {})

            if not query:
                logger.warning("No query provided for retrieval")
                return {
                    **state,
                    "retrieved_chunks": [],
                    "processing_status": "no_query"
                }

            # Extract search parameters
            limit = search_filters.get("limit", 5)
            score_threshold = search_filters.get("score_threshold", 0.7)
            filter_doc_type = search_filters.get("document_type")

            # Perform search
            retrieved_chunks = self.vector_store.search_similar_chunks(
                query=query,
                limit=limit,
                score_threshold=score_threshold,
                filter_doc_type=filter_doc_type
            )

            logger.info(f"Retrieval Agent: Retrieved {len(retrieved_chunks)} relevant chunks")

            return {
                **state,
                "retrieved_chunks": retrieved_chunks,
                "processing_status": "chunks_retrieved"
            }

        except Exception as e:
            logger.error(f"Retrieval Agent error: {e}")
            return {
                **state,
                "retrieved_chunks": [],
                "processing_status": "retrieval_error",
                "error_message": str(e)
            }


class ResponseGenerationAgent:
    """
    Agent responsible for generating legal responses using Gemini.
    """

    def __init__(self):
        self.gemini_assistant = GeminiLegalAssistant()

    def process(self, state: RAGState) -> RAGState:
        """
        Generate response using retrieved context.

        Args:
            state: Current graph state

        Returns:
            Updated state
        """
        try:
            logger.info("Response Generation Agent: Starting response generation")

            query = state.get("query", "")
            retrieved_chunks = state.get("retrieved_chunks", [])
            conversation_history = state.get("conversation_history", [])

            if not query:
                logger.warning("No query provided for response generation")
                return {
                    **state,
                    "generated_response": "I apologize, but no query was provided.",
                    "processing_status": "no_query_for_response"
                }

            # Generate response using Gemini
            response = self.gemini_assistant.generate_legal_response(
                query=query,
                context_chunks=retrieved_chunks,
                conversation_history=conversation_history,
                streaming=False
            )

            logger.info("Response Generation Agent: Response generated successfully")

            return {
                **state,
                "generated_response": response,
                "processing_status": "response_generated"
            }

        except Exception as e:
            logger.error(f"Response Generation Agent error: {e}")
            fallback_response = f"""I apologize, but I encountered an error while generating a response to your question: "{state.get('query', '')}"

Please try rephrasing your question or contact support if the problem persists."""

            return {
                **state,
                "generated_response": fallback_response,
                "processing_status": "response_error",
                "error_message": str(e)
            }


class RAGOrchestrator:
    """
    Main orchestrator for the RAG pipeline using LangGraph.
    """

    def __init__(self):
        # Initialize agents
        self.doc_processor = DocumentProcessingAgent()
        self.embedding_agent = EmbeddingStorageAgent()
        self.retrieval_agent = RetrievalAgent()
        self.response_agent = ResponseGenerationAgent()

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state graph.

        Returns:
            Configured StateGraph
        """
        # Define the graph
        graph = StateGraph(RAGState)

        # Add nodes
        graph.add_node("document_processor", self.doc_processor.process)
        graph.add_node("embedding_agent", self.embedding_agent.process)
        graph.add_node("retrieval_agent", self.retrieval_agent.process)
        graph.add_node("response_agent", self.response_agent.process)

        # Define the flow
        graph.add_edge(START, "document_processor")
        graph.add_edge("document_processor", "embedding_agent")
        graph.add_edge("embedding_agent", "retrieval_agent")
        graph.add_edge("retrieval_agent", "response_agent")
        graph.add_edge("response_agent", END)

        # Add conditional edges for error handling
        def route_based_on_status(state: RAGState):
            status = state.get("processing_status", "")
            if status in ["error", "no_documents", "embedding_error"]:
                return Command(goto=END, update={"final_status": "error"})
            return Command(goto="retrieval_agent")

        # Note: Conditional routing would be added here in a full implementation
        # For now, we use the simple linear flow

        return graph

    def process_query(self,
                     query: str,
                     conversation_history: Optional[List[Dict[str, str]]] = None,
                     search_filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user query through the complete RAG pipeline.

        Args:
            query: User's legal question
            conversation_history: Previous conversation turns
            search_filters: Search filtering options

        Returns:
            Complete processing result
        """
        try:
            logger.info(f"RAG Orchestrator: Processing query: {query[:50]}...")

            # Initialize state
            initial_state = RAGState(
                query=query,
                processed_documents=None,
                retrieved_chunks=None,
                generated_response=None,
                conversation_history=conversation_history or [],
                search_filters=search_filters or {},
                processing_status="starting",
                error_message=None
            )

            # Run the graph
            compiled_graph = self.graph.compile()
            final_state = compiled_graph.invoke(initial_state)

            logger.info("RAG Orchestrator: Query processing completed")

            return {
                "query": query,
                "response": final_state.get("generated_response", ""),
                "retrieved_chunks": final_state.get("retrieved_chunks", []),
                "processing_status": final_state.get("processing_status", ""),
                "error_message": final_state.get("error_message"),
                "chunks_count": len(final_state.get("retrieved_chunks", []))
            }

        except Exception as e:
            logger.error(f"RAG Orchestrator error: {e}")
            return {
                "query": query,
                "response": f"I apologize, but I encountered an error processing your query. Error: {str(e)}",
                "retrieved_chunks": [],
                "processing_status": "orchestrator_error",
                "error_message": str(e),
                "chunks_count": 0
            }

    def initialize_documents(self) -> Dict[str, Any]:
        """
        Initialize the document processing pipeline (run once).

        Returns:
            Initialization result
        """
        try:
            logger.info("RAG Orchestrator: Initializing document processing")

            # Create a dummy state for initialization
            init_state = RAGState(
                query="",
                processed_documents=None,
                retrieved_chunks=None,
                generated_response=None,
                conversation_history=[],
                search_filters={},
                processing_status="initializing",
                error_message=None
            )

            # Run document processing and embedding pipeline
            compiled_graph = self.graph.compile()

            # Run only document processing and embedding steps
            # (In a full implementation, you'd modify the graph for this)
            result_state = compiled_graph.invoke(init_state)

            return {
                "status": "initialized",
                "documents_processed": len(result_state.get("processed_documents", [])),
                "chunks_stored": result_state.get("chunks_stored", 0),
                "processing_status": result_state.get("processing_status")
            }

        except Exception as e:
            logger.error(f"Document initialization error: {e}")
            return {
                "status": "error",
                "error_message": str(e)
            }


# Standalone query processing (for when documents are already processed)
class QueryProcessor:
    """
    Simplified processor for handling queries when documents are already indexed.
    """

    def __init__(self):
        self.retrieval_agent = RetrievalAgent()
        self.response_agent = ResponseGenerationAgent()

    def process_query(self,
                     query: str,
                     conversation_history: Optional[List[Dict[str, str]]] = None,
                     search_filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a query using pre-indexed documents.

        Args:
            query: User's legal question
            conversation_history: Previous conversation turns
            search_filters: Search filtering options

        Returns:
            Query result
        """
        try:
            # Retrieval step
            retrieval_state = RAGState(
                query=query,
                search_filters=search_filters or {}
            )

            retrieval_result = self.retrieval_agent.process(retrieval_state)

            # Response generation step
            response_state = RAGState(
                query=query,
                retrieved_chunks=retrieval_result.get("retrieved_chunks", []),
                conversation_history=conversation_history or []
            )

            response_result = self.response_agent.process(response_state)

            return {
                "query": query,
                "response": response_result.get("generated_response", ""),
                "retrieved_chunks": retrieval_result.get("retrieved_chunks", []),
                "processing_status": "completed",
                "chunks_count": len(retrieval_result.get("retrieved_chunks", []))
            }

        except Exception as e:
            logger.error(f"Query processing error: {e}")
            return {
                "query": query,
                "response": f"I apologize, but I encountered an error processing your query. Error: {str(e)}",
                "retrieved_chunks": [],
                "processing_status": "error",
                "error_message": str(e)
            }


# Usage example
if __name__ == "__main__":
    # For initial setup (run once)
    orchestrator = RAGOrchestrator()
    init_result = orchestrator.initialize_documents()
    print(f"Initialization result: {init_result}")

    # For query processing
    processor = QueryProcessor()
    result = processor.process_query(
        "What are tenant rights under rent control acts?",
        search_filters={"document_type": "rent_control_act", "limit": 3}
    )

    print(f"Query result: {result['response'][:200]}...")
