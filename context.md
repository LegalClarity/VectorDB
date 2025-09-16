# Legal Document RAG Chatbot - Complete Implementation Context

## Project Overview

You are building a **Legal Document Understanding RAG Chatbot** for the **Google GenAI Exchange 2025 hackathon** to help general users understand legal document clauses better. The system processes legal documents (loan agreements, terms of service, rental agreements) and provides intelligent assistance through a RAG-based architecture.

## Core Architecture Components

### 1. Vector Database Setup (QdrantDB)
- **Purpose**: Store and retrieve document embeddings for semantic search
- **Configuration**: Use provided `.env` file with Qdrant API key and URL
- **Integration**: Connect with Google's EmbeddingGemma model for vectorization

### 2. Embedding Model Integration
**Google EmbeddingGemma-300M** - State-of-the-art multilingual embedding model:
```python
from sentence_transformers import SentenceTransformer

# Core model setup
model = SentenceTransformer("google/embeddinggemma-300m")

# Task-specific prompts for legal documents
# Use "retrieval_document" for indexing legal documents
# Use "retrieval_query" for user questions
query_embeddings = model.encode(query, prompt_name="Retrieval-query")
document_embeddings = model.encode(documents, prompt_name="Retrieval-document")
```

### 3. Google Gemini Integration
**Gemini 2.5 Flash** with thinking capabilities:
```python
import os
from google import genai
from google.genai import types

def generate_legal_response(context, user_query):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=f"""
                Context: {context}
                User Question: {user_query}
                
                You are a legal document assistant. Explain legal clauses in simple terms 
                for general users. Focus on practical implications and user rights.
                """),
            ],
        ),
    ]
    
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=-1),
        tools=[types.Tool(googleSearch=types.GoogleSearch())],
    )
    
    return client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=contents,
        config=generate_content_config,
    )
```

### 4. LangGraph Multi-Agent Architecture
Implement sophisticated agent coordination:
```python
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.types import Command

def document_processor_agent(state):
    # Process and chunk legal documents
    # Extract key clauses and legal terms
    return Command(goto="embedding_agent", update={"processed_docs": chunks})

def embedding_agent(state):
    # Generate embeddings using EmbeddingGemma
    # Store in QdrantDB with metadata
    return Command(goto="retrieval_agent", update={"embeddings_stored": True})

def retrieval_agent(state):
    # Retrieve relevant context for user queries
    # Implement hybrid search (dense + sparse)
    return Command(goto="response_agent", update={"context": retrieved_docs})

def response_agent(state):
    # Generate user-friendly explanations using Gemini
    # Format legal information for general audience
    return Command(goto=END, update={"final_response": response})
```

## Environment Configuration

### Required .env Variables
```env
# QdrantDB Configuration
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key

# Google Gemini Configuration  
GEMINI_API_KEY=your_gemini_api_key

# Optional: Additional service configurations
LANGSMITH_API_KEY=your_langsmith_key  # For monitoring
```

## Legal Document Processing Pipeline

### 1. Document Ingestion
```python
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter

def process_legal_documents(folder_path):
    documents = []
    
    for file_path in glob.glob(f"{folder_path}/**/*.pdf", recursive=True):
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        
        # Legal-specific text splitting
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", ";", ",", " ", ""]
        )
        
        chunks = splitter.split_text(text)
        for chunk in chunks:
            documents.append({
                "content": chunk,
                "source": file_path,
                "doc_type": classify_legal_document(chunk)
            })
    
    return documents
```

### 2. QdrantDB Integration
```python
from qdrant_client import QdrantClient, models
from qdrant_client.models import Distance, VectorParams

def setup_qdrant_collection():
    client = QdrantClient(
        url=os.getenv("QDRANT_URL"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    collection_name = "legal_documents"
    
    # Create collection with EmbeddingGemma dimensions
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )
    
    return client, collection_name

def store_embeddings(client, collection_name, documents, model):
    points = []
    
    for idx, doc in enumerate(documents):
        # Generate embedding with legal document prompt
        embedding = model.encode([doc["content"]], prompt_name="Retrieval-document")[0]
        
        points.append(models.PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={
                "content": doc["content"],
                "source": doc["source"],
                "doc_type": doc["doc_type"],
                "legal_entities": extract_legal_entities(doc["content"])
            }
        ))
    
    client.upsert(collection_name=collection_name, points=points)
```

### 3. Retrieval System
```python
def retrieve_legal_context(client, collection_name, model, query, top_k=5):
    # Generate query embedding
    query_embedding = model.encode([query], prompt_name="Retrieval-query")[0]
    
    # Search similar documents
    search_results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding.tolist(),
        limit=top_k,
        with_payload=True
    )
    
    # Format context for legal explanation
    context_docs = []
    for result in search_results:
        context_docs.append({
            "content": result.payload["content"],
            "relevance_score": result.score,
            "source": result.payload["source"],
            "doc_type": result.payload["doc_type"]
        })
    
    return context_docs
```

## Streamlit User Interface

### Legal Chatbot Interface
```python
import streamlit as st
from streamlit_chat import message

def main():
    st.set_page_config(
        page_title="Legal Document Assistant",
        page_icon="⚖️",
        layout="wide"
    )
    
    st.title("🏛️ Legal Document Assistant")
    st.markdown("*Understanding legal documents made simple*")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.rag_system = initialize_rag_system()
    
    # Chat interface
    with st.container():
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                message(msg["content"], is_user=True, key=f"user_{i}")
            else:
                message(msg["content"], key=f"bot_{i}")
    
    # User input
    if prompt := st.chat_input("Ask about any legal document clause..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Get RAG response
        with st.spinner("Analyzing legal documents..."):
            response = st.session_state.rag_system.get_response(prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    
    # Sidebar for document upload
    with st.sidebar:
        st.header("📄 Upload Legal Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF documents",
            type=["pdf"],
            accept_multiple_files=True
        )
        
        if uploaded_files and st.button("Process Documents"):
            process_uploaded_documents(uploaded_files)
            st.success("Documents processed and indexed!")
```

## Advanced Features for Hackathon Success

### 1. Legal Entity Recognition
```python
import spacy
from transformers import pipeline

def extract_legal_entities(text):
    # Use legal-specific NER model
    nlp = spacy.load("en_legal_ner_trf")  # Hypothetical legal NER model
    doc = nlp(text)
    
    entities = {
        "parties": [],
        "dates": [],
        "monetary_amounts": [],
        "legal_terms": [],
        "locations": []
    }
    
    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG"]:
            entities["parties"].append(ent.text)
        elif ent.label_ == "DATE":
            entities["dates"].append(ent.text)
        elif ent.label_ == "MONEY":
            entities["monetary_amounts"].append(ent.text)
        elif ent.label_ == "GPE":
            entities["locations"].append(ent.text)
    
    return entities
```

### 2. Document Classification
```python
def classify_legal_document(text_chunk):
    # Simple classification based on keywords
    classification_rules = {
        "loan_agreement": ["loan", "borrower", "lender", "interest", "repayment"],
        "rental_agreement": ["rent", "lease", "tenant", "landlord", "property"],
        "terms_of_service": ["service", "user", "agreement", "terms", "privacy"],
        "contract": ["contract", "agreement", "parties", "obligations"],
        "policy": ["policy", "procedure", "guidelines", "rules"]
    }
    
    text_lower = text_chunk.lower()
    scores = {}
    
    for doc_type, keywords in classification_rules.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        scores[doc_type] = score
    
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "general_legal"
```

### 3. Context-Aware Prompting
```python
def create_legal_context_prompt(user_query, retrieved_docs):
    context = "\n\n".join([
        f"Document Type: {doc['doc_type']}\n"
        f"Source: {doc['source']}\n"
        f"Content: {doc['content']}\n"
        f"Relevance: {doc['relevance_score']:.2f}"
        for doc in retrieved_docs
    ])
    
    return f"""
You are an expert legal assistant helping general users understand legal documents.

CONTEXT FROM LEGAL DOCUMENTS:
{context}

USER QUESTION: {user_query}

INSTRUCTIONS:
1. Explain legal concepts in simple, everyday language
2. Highlight potential risks or benefits for the user
3. Provide practical advice when appropriate
4. Reference specific clauses when relevant
5. Use analogies to make complex concepts understandable
6. Always include a disclaimer about seeking professional legal advice

FORMAT YOUR RESPONSE:
- Start with a clear, direct answer
- Provide detailed explanation with examples
- Include "What this means for you:" section
- End with relevant disclaimers
"""
```

## Hackathon Success Strategies

### 1. Technical Excellence
- **Performance**: Implement caching for embeddings and responses
- **Scalability**: Use async operations for document processing
- **Reliability**: Add error handling and fallback mechanisms
- **Security**: Implement proper data sanitization and access controls

### 2. User Experience
- **Intuitive Interface**: Clean, professional Streamlit design
- **Interactive Features**: Document highlighting, clause explanation
- **Multi-modal Support**: PDF viewer with clickable clauses
- **Accessibility**: Support for different user experience levels

### 3. Innovation Points
- **Multi-Agent Architecture**: Demonstrate sophisticated AI orchestration
- **Legal Specialization**: Show deep understanding of legal document processing
- **Real-world Applicability**: Focus on genuine user problems
- **Technical Integration**: Seamless combination of multiple Google AI services

### 4. Demo Preparation
- **Sample Documents**: Curate diverse legal document examples
- **User Scenarios**: Prepare realistic use cases and questions
- **Performance Metrics**: Demonstrate response quality and speed
- **Technical Architecture**: Clear explanation of system design

## Implementation Timeline

### Phase 1: Core Setup (Day 1)
- Environment configuration
- QdrantDB setup and connection
- Basic embedding pipeline
- Simple document ingestion

### Phase 2: RAG Implementation (Day 2)
- Document processing pipeline
- Embedding generation and storage
- Retrieval system implementation
- Basic Gemini integration

### Phase 3: Advanced Features (Day 3)
- LangGraph multi-agent architecture
- Streamlit interface development
- Legal entity recognition
- Document classification

### Phase 4: Polish & Demo (Day 4)
- UI/UX improvements
- Performance optimization
- Demo preparation
- Documentation

## Key Success Factors

1. **Solve Real Problems**: Focus on genuine legal document understanding challenges
2. **Technical Sophistication**: Demonstrate advanced AI architecture knowledge
3. **User-Centric Design**: Prioritize accessibility and ease of use
4. **Google AI Integration**: Showcase deep integration with Google's AI ecosystem
5. **Practical Applicability**: Build something that could be deployed in production

