# Legal Clarity - Comprehensive Implementation Guide for Coding Agent

## Project Overview

**Project Name:** Legal Clarity
**Target:** Google GenAI Exchange 2025 Hackathon
**Problem Statement:** Generative AI for Demystifying Legal Documents
**Primary Technology Stack:** LangExtract, LangGraph, LangChain, FastAPI, MongoDB, QdrantDB, Google Gemini

## Executive Summary

You are tasked with building a comprehensive legal document processing API system that extracts, analyzes, and structures information from three primary types of Indian legal documents: **Rental Agreements**, **Loan Agreements**, and **Terms of Service**. The system should leverage Google's LangExtract library with Gemini models to perform intelligent extraction, store results in MongoDB, and optionally create vector embeddings in QdrantDB for enhanced retrieval capabilities.

## Architecture Overview

### Core System Components

1. **Document Processing Pipeline**
   - PDF/Text document ingestion
   - OCR processing if needed
   - Text preprocessing and cleaning
   - Document type classification

2. **Extraction Engine**
   - LangExtract-powered structured data extraction
   - Gemini model integration for legal text understanding
   - Schema-based extraction with mandatory/optional fields
   - Source grounding for legal compliance

3. **Storage Layer**
   - MongoDB for structured document data and metadata
   - QdrantDB for vector embeddings and semantic search
   - Document versioning and change tracking

4. **API Layer**
   - FastAPI-based REST endpoints
   - Authentication and authorization
   - Rate limiting and error handling
   - Response formatting and validation

5. **Workflow Orchestration**
   - LangGraph for complex multi-step processing
   - LangChain for document loading and text operations
   - Parallel processing capabilities
   - Error recovery and retry logic

## Detailed Implementation Instructions

### Phase 1: Project Setup and Dependencies

```python
# Required packages - install these
pip install langextract langchain langgraph fastapi uvicorn
pip install pymongo qdrant-client google-generativeai
pip install pydantic python-multipart python-jose[cryptography]
pip install pytesseract pdf2image PyPDF2 python-docx
```

**Environment Configuration:**
- Set up Google AI API key for Gemini access
- Configure MongoDB connection string
- Set up QdrantDB instance (local or cloud)
- Define logging and error handling configurations

### Phase 2: Document Schema Definition

Based on analysis of actual Indian legal documents, implement these schemas:

#### Rental Agreement Schema
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date

class RentalAgreementSchema(BaseModel):
    # Mandatory Fields
    lessor_name: str = Field(..., description="Full name of property owner")
    lessor_address: str = Field(..., description="Complete address of lessor")
    lessor_contact: Optional[str] = Field(None, description="Phone/email contact")
    
    lessee_name: str = Field(..., description="Full name of tenant")
    lessee_address: str = Field(..., description="Complete address of lessee")
    lessee_contact: Optional[str] = Field(None, description="Phone/email contact")
    
    property_address: str = Field(..., description="Complete property address with landmarks")
    property_description: str = Field(..., description="Type, size, and features of property")
    
    monthly_rent: float = Field(..., description="Monthly rent amount in INR")
    security_deposit: float = Field(..., description="Security deposit amount in INR")
    
    lease_start_date: date = Field(..., description="Lease commencement date")
    lease_end_date: date = Field(..., description="Lease termination date")
    notice_period_days: int = Field(..., description="Notice period for termination in days")
    
    # Optional Fields
    annual_escalation: Optional[float] = Field(None, description="Annual rent increase percentage")
    utility_responsibility: Optional[str] = Field(None, description="Who pays utility bills")
    pet_policy: Optional[str] = Field(None, description="Pet permissions and restrictions")
    subletting_allowed: Optional[bool] = Field(None, description="Subletting permission")
    lock_in_period: Optional[int] = Field(None, description="Lock-in period in months")
    late_payment_penalty: Optional[float] = Field(None, description="Late payment penalty percentage")
    maintenance_charges: Optional[float] = Field(None, description="Monthly maintenance charges")
    
    # India-Specific Legal Clauses
    registration_required: Optional[bool] = Field(None, description="Whether registration is required")
    stamp_duty_paid: Optional[bool] = Field(None, description="Stamp duty payment status")
    tds_applicable: Optional[bool] = Field(None, description="TDS deduction applicable")
    society_noc: Optional[bool] = Field(None, description="Society NOC obtained")
```

#### Loan Agreement Schema  
```python
class LoanAgreementSchema(BaseModel):
    # Mandatory Fields
    lender_name: str = Field(..., description="Name of lending institution/individual")
    lender_registration: Optional[str] = Field(None, description="Registration/license details")
    
    borrower_name: str = Field(..., description="Full name of borrower")
    borrower_address: str = Field(..., description="Complete address of borrower")
    borrower_pan: Optional[str] = Field(None, description="PAN number of borrower")
    borrower_aadhaar: Optional[str] = Field(None, description="Aadhaar number (if mentioned)")
    
    principal_amount: float = Field(..., description="Principal loan amount in INR")
    interest_rate: float = Field(..., description="Interest rate percentage per annum")
    interest_type: str = Field(..., description="Fixed, Floating, or Flexi rate")
    loan_tenure_months: int = Field(..., description="Loan tenure in months")
    emi_amount: float = Field(..., description="Equated Monthly Installment amount")
    emi_frequency: str = Field(..., description="Payment frequency - monthly, quarterly")
    
    loan_purpose: str = Field(..., description="Purpose for which loan is taken")
    repayment_start_date: date = Field(..., description="First EMI due date")
    collateral_details: Optional[str] = Field(None, description="Security/collateral offered")
    
    # Optional Fields
    processing_fees: Optional[float] = Field(None, description="Processing fee amount")
    prepayment_charges: Optional[float] = Field(None, description="Prepayment penalty percentage")
    penal_interest: Optional[float] = Field(None, description="Penal interest rate for defaults")
    insurance_required: Optional[bool] = Field(None, description="Insurance requirement")
    guarantor_details: Optional[str] = Field(None, description="Guarantor information")
    moratorium_period: Optional[int] = Field(None, description="Moratorium period in months")
    
    # India-Specific Compliance
    rbi_guidelines_followed: Optional[bool] = Field(None, description="RBI compliance")
    sarfaesi_applicable: Optional[bool] = Field(None, description="SARFAESI Act applicability")
    tds_compliance: Optional[bool] = Field(None, description="TDS on interest payments")
    cibil_reporting: Optional[bool] = Field(None, description="CIBIL reporting mentioned")
```

#### Terms of Service Schema
```python
class TermsOfServiceSchema(BaseModel):
    # Mandatory Fields
    service_provider: str = Field(..., description="Company/service provider name")
    provider_address: str = Field(..., description="Registered address of provider")
    
    service_description: str = Field(..., description="Description of services offered")
    user_eligibility: str = Field(..., description="User eligibility criteria")
    payment_terms: Optional[str] = Field(None, description="Payment terms and pricing")
    termination_conditions: str = Field(..., description="Conditions for service termination")
    
    liability_limitations: str = Field(..., description="Limitation of liability clauses")
    governing_law: str = Field(..., description="Applicable governing law")
    dispute_contact: str = Field(..., description="Contact for dispute resolution")
    
    # Optional Fields
    refund_policy: Optional[str] = Field(None, description="Refund terms and conditions")
    sla_terms: Optional[str] = Field(None, description="Service level agreements")
    beta_disclaimers: Optional[str] = Field(None, description="Beta features disclaimers")
    third_party_integrations: Optional[str] = Field(None, description="Third-party services")
    content_policies: Optional[str] = Field(None, description="User content usage policies")
    suspension_procedures: Optional[str] = Field(None, description="Account suspension terms")
    data_retention: Optional[str] = Field(None, description="Data retention policies")
    
    # India-Specific Legal Clauses
    it_act_compliance: Optional[bool] = Field(None, description="IT Act 2000 compliance")
    data_protection_compliance: Optional[bool] = Field(None, description="DPDP Act compliance")
    consumer_protection: Optional[bool] = Field(None, description="Consumer Protection Act")
    indian_contract_act: Optional[bool] = Field(None, description="Indian Contract Act applicability")
    gst_implications: Optional[bool] = Field(None, description="GST applicability mentioned")
```

### Phase 3: LangExtract Integration and Prompt Engineering

#### Core Extraction Function
```python
import langextract as lx
from typing import Dict, Any, Type, List
import json

class LegalDocumentExtractor:
    def __init__(self, gemini_api_key: str):
        self.gemini_api_key = gemini_api_key
        
    def create_extraction_examples(self, document_type: str) -> List[lx.data.ExampleData]:
        """Create few-shot examples for each document type"""
        
        if document_type == "rental":
            return [
                lx.data.ExampleData(
                    text="This Rent Agreement made at Mumbai on 15th January 2024 between Mr. Rajesh Kumar S/o Late Suresh Kumar R/o A-101, Sunshine Apartments, Andheri West, Mumbai - 400058 (Lessor) and Ms. Priya Sharma D/o Mr. Anil Sharma R/o B-205, Green Valley, Bandra East, Mumbai - 400051 (Lessee). Monthly rent Rs. 25,000/- payable on 5th of every month. Security deposit Rs. 50,000/-. Lease period from 1st February 2024 to 31st January 2025.",
                    extractions=[
                        lx.data.Extraction(
                            extraction_class="lessor_details",
                            extraction_text="Mr. Rajesh Kumar S/o Late Suresh Kumar R/o A-101, Sunshine Apartments, Andheri West, Mumbai - 400058",
                            attributes={
                                "lessor_name": "Mr. Rajesh Kumar",
                                "lessor_address": "A-101, Sunshine Apartments, Andheri West, Mumbai - 400058"
                            }
                        ),
                        lx.data.Extraction(
                            extraction_class="financial_terms",
                            extraction_text="Monthly rent Rs. 25,000/- payable on 5th of every month. Security deposit Rs. 50,000/-",
                            attributes={
                                "monthly_rent": 25000.0,
                                "security_deposit": 50000.0
                            }
                        )
                    ]
                )
            ]
        
        elif document_type == "loan":
            return [
                lx.data.ExampleData(
                    text="Loan Agreement between HDFC Bank Limited, a banking company (Lender) and Mr. Amit Singh, PAN: ABCDE1234F (Borrower). Principal amount: Rs. 5,00,000/- at 9.5% per annum for 60 months. EMI: Rs. 10,456/- starting from 1st March 2024. Purpose: Home renovation.",
                    extractions=[
                        lx.data.Extraction(
                            extraction_class="loan_details",
                            extraction_text="Principal amount: Rs. 5,00,000/- at 9.5% per annum for 60 months",
                            attributes={
                                "principal_amount": 500000.0,
                                "interest_rate": 9.5,
                                "loan_tenure_months": 60
                            }
                        ),
                        lx.data.Extraction(
                            extraction_class="borrower_details",
                            extraction_text="Mr. Amit Singh, PAN: ABCDE1234F",
                            attributes={
                                "borrower_name": "Mr. Amit Singh",
                                "borrower_pan": "ABCDE1234F"
                            }
                        )
                    ]
                )
            ]
        
        elif document_type == "tos":
            return [
                lx.data.ExampleData(
                    text="Terms of Service for TechCorp Services Private Limited, registered office at 123 Business Park, Bangalore 560001. These terms govern your use of our cloud storage services. Users must be 18+ years old. Service can be terminated with 30 days notice. Disputes subject to Bangalore jurisdiction under Indian law.",
                    extractions=[
                        lx.data.Extraction(
                            extraction_class="provider_details",
                            extraction_text="TechCorp Services Private Limited, registered office at 123 Business Park, Bangalore 560001",
                            attributes={
                                "service_provider": "TechCorp Services Private Limited",
                                "provider_address": "123 Business Park, Bangalore 560001"
                            }
                        ),
                        lx.data.Extraction(
                            extraction_class="legal_terms",
                            extraction_text="Disputes subject to Bangalore jurisdiction under Indian law",
                            attributes={
                                "governing_law": "Indian law",
                                "jurisdiction": "Bangalore"
                            }
                        )
                    ]
                )
            ]
        
        return []
    
    def extract_structured_data(self, document_text: str, document_type: str) -> Dict[str, Any]:
        """Extract structured data using LangExtract"""
        
        # Define extraction prompts for each document type
        prompts = {
            "rental": """
            Extract key information from this rental/lease agreement document. Focus on:
            
            1. PARTIES: Names, addresses, and contact details of lessor and lessee
            2. PROPERTY: Complete address, description, and boundaries
            3. FINANCIAL: Rent amount, security deposit, payment terms
            4. DURATION: Lease start date, end date, notice period
            5. TERMS: Maintenance, utilities, restrictions, renewal terms
            6. LEGAL: Registration requirements, stamp duty, compliance clauses
            
            Return structured JSON with accurate extraction of monetary values, dates, and legal terms.
            Pay special attention to Indian legal terminology and compliance requirements.
            """,
            
            "loan": """
            Extract key information from this loan agreement document. Focus on:
            
            1. PARTIES: Lender details, borrower name, address, PAN, Aadhaar
            2. LOAN DETAILS: Principal amount, interest rate, tenure, EMI amount
            3. REPAYMENT: Payment schedule, start date, frequency
            4. SECURITY: Collateral, guarantor, insurance requirements
            5. CHARGES: Processing fees, penalties, prepayment charges
            6. COMPLIANCE: RBI guidelines, SARFAESI, TDS, CIBIL reporting
            7. DEFAULT: Events of default, remedies, recovery procedures
            
            Return structured JSON with accurate financial calculations and legal compliance terms.
            Pay attention to Indian banking regulations and legal requirements.
            """,
            
            "tos": """
            Extract key information from this Terms of Service/Terms and Conditions document. Focus on:
            
            1. PROVIDER: Company name, registered address, contact details
            2. SERVICES: Description of services offered, eligibility criteria
            3. PAYMENT: Pricing, billing terms, refund policies
            4. USER RIGHTS: Permissions, restrictions, account terms
            5. LIABILITY: Disclaimers, limitations, indemnification
            6. TERMINATION: Conditions, procedures, data handling
            7. LEGAL: Governing law, dispute resolution, Indian compliance
            
            Return structured JSON with clear categorization of rights, obligations, and legal terms.
            Pay attention to Indian digital laws and consumer protection regulations.
            """
        }
        
        examples = self.create_extraction_examples(document_type)
        
        try:
            result = lx.extract(
                text_or_documents=document_text,
                prompt_description=prompts.get(document_type, prompts["rental"]),
                examples=examples,
                model_id="gemini-2.0-flash-exp",  # Use latest Gemini model
                api_key=self.gemini_api_key,
                max_char_buffer=8000,  # Optimize for legal documents
                extraction_passes=2,   # Multiple passes for better recall
                fence_output=True,
                use_schema_constraint=True
            )
            
            return self._process_extraction_result(result, document_type)
            
        except Exception as e:
            raise Exception(f"Extraction failed: {str(e)}")
    
    def _process_extraction_result(self, result: lx.data.ExtractResults, document_type: str) -> Dict[str, Any]:
        """Process and structure the extraction results"""
        
        structured_data = {
            "document_type": document_type,
            "extraction_confidence": getattr(result, 'confidence', 0.0),
            "extracted_entities": [],
            "source_grounding": {},
            "metadata": {
                "total_extractions": len(result.extractions) if result.extractions else 0,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
        }
        
        if result.extractions:
            for extraction in result.extractions:
                entity = {
                    "class": extraction.extraction_class,
                    "text": extraction.extraction_text,
                    "attributes": extraction.attributes,
                    "confidence": getattr(extraction, 'confidence', 0.0),
                    "source_location": {
                        "start_char": getattr(extraction, 'start_char', 0),
                        "end_char": getattr(extraction, 'end_char', 0)
                    }
                }
                structured_data["extracted_entities"].append(entity)
                
                # Build source grounding for legal verification
                if hasattr(extraction, 'source_text'):
                    structured_data["source_grounding"][extraction.extraction_class] = {
                        "original_text": extraction.source_text,
                        "extracted_value": extraction.extraction_text,
                        "verification_needed": True
                    }
        
        return structured_data
```

### Phase 4: Database Integration

#### MongoDB Schema and Operations
```python
from pymongo import MongoClient
from datetime import datetime
from typing import Optional
import uuid

class LegalDocumentDB:
    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string)
        self.db = self.client["legal_clarity"]
        self.documents_collection = self.db["documents"]
        self.extractions_collection = self.db["extractions"]
        self.audit_collection = self.db["audit_log"]
        
        # Create indexes for efficient querying
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        # Document collection indexes
        self.documents_collection.create_index("document_id")
        self.documents_collection.create_index("document_type")
        self.documents_collection.create_index("upload_timestamp")
        self.documents_collection.create_index("user_id")
        
        # Extraction collection indexes
        self.extractions_collection.create_index("document_id")
        self.extractions_collection.create_index("document_type")
        self.extractions_collection.create_index("extraction_timestamp")
        self.extractions_collection.create_index("confidence_score")
    
    def store_document(self, file_content: bytes, filename: str, document_type: str, user_id: str) -> str:
        """Store uploaded document with metadata"""
        
        document_id = str(uuid.uuid4())
        
        document_record = {
            "document_id": document_id,
            "filename": filename,
            "document_type": document_type,
            "user_id": user_id,
            "file_content": file_content,
            "file_size": len(file_content),
            "upload_timestamp": datetime.utcnow(),
            "processing_status": "uploaded",
            "metadata": {
                "original_filename": filename,
                "content_type": self._detect_content_type(filename)
            }
        }
        
        result = self.documents_collection.insert_one(document_record)
        
        # Log audit trail
        self._log_audit_event("document_upload", document_id, user_id, {
            "filename": filename,
            "document_type": document_type,
            "file_size": len(file_content)
        })
        
        return document_id
    
    def store_extraction_results(self, document_id: str, extraction_data: Dict[str, Any], 
                               processing_time: float) -> str:
        """Store extraction results with full traceability"""
        
        extraction_id = str(uuid.uuid4())
        
        extraction_record = {
            "extraction_id": extraction_id,
            "document_id": document_id,
            "document_type": extraction_data.get("document_type"),
            "extracted_data": extraction_data,
            "extraction_timestamp": datetime.utcnow(),
            "processing_time_seconds": processing_time,
            "confidence_score": extraction_data.get("extraction_confidence", 0.0),
            "total_entities": len(extraction_data.get("extracted_entities", [])),
            "status": "completed",
            "version": "1.0"
        }
        
        result = self.extractions_collection.insert_one(extraction_record)
        
        # Update document processing status
        self.documents_collection.update_one(
            {"document_id": document_id},
            {
                "$set": {
                    "processing_status": "completed",
                    "last_extraction_id": extraction_id,
                    "processing_completed_at": datetime.utcnow()
                }
            }
        )
        
        return extraction_id
    
    def get_extraction_by_document_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve extraction results by document ID"""
        
        result = self.extractions_collection.find_one(
            {"document_id": document_id},
            sort=[("extraction_timestamp", -1)]  # Get latest extraction
        )
        
        if result:
            result.pop("_id", None)  # Remove MongoDB ObjectID
            return result
        
        return None
    
    def search_documents(self, query_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search documents with advanced filtering"""
        
        filter_criteria = {}
        
        if query_params.get("document_type"):
            filter_criteria["document_type"] = query_params["document_type"]
        
        if query_params.get("user_id"):
            filter_criteria["user_id"] = query_params["user_id"]
        
        if query_params.get("date_from") or query_params.get("date_to"):
            date_filter = {}
            if query_params.get("date_from"):
                date_filter["$gte"] = query_params["date_from"]
            if query_params.get("date_to"):
                date_filter["$lte"] = query_params["date_to"]
            filter_criteria["upload_timestamp"] = date_filter
        
        results = list(self.documents_collection.find(
            filter_criteria,
            {"file_content": 0}  # Exclude file content from search results
        ).sort("upload_timestamp", -1))
        
        # Remove MongoDB ObjectIDs
        for result in results:
            result.pop("_id", None)
        
        return results
    
    def _detect_content_type(self, filename: str) -> str:
        """Detect content type from filename"""
        extension = filename.lower().split('.')[-1]
        content_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        return content_types.get(extension, 'application/octet-stream')
    
    def _log_audit_event(self, event_type: str, document_id: str, user_id: str, details: Dict[str, Any]):
        """Log audit events for compliance tracking"""
        
        audit_record = {
            "audit_id": str(uuid.uuid4()),
            "event_type": event_type,
            "document_id": document_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "details": details,
            "ip_address": None,  # Add from request context
            "user_agent": None   # Add from request context
        }
        
        self.audit_collection.insert_one(audit_record)
```

#### QdrantDB Vector Integration (Optional)
```python
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorSearchDB:
    def __init__(self, qdrant_url: str, collection_name: str = "legal_documents"):
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight model
        self._ensure_collection()
    
    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        collections = self.client.get_collections()
        
        if self.collection_name not in [col.name for col in collections.collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE)
            )
    
    def add_document_embeddings(self, document_id: str, text_chunks: List[str], 
                              metadata: Dict[str, Any]) -> List[str]:
        """Add document embeddings for semantic search"""
        
        embeddings = self.encoder.encode(text_chunks)
        
        points = []
        point_ids = []
        
        for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
            point_id = f"{document_id}_{i}"
            point_ids.append(point_id)
            
            points.append({
                "id": point_id,
                "vector": embedding.tolist(),
                "payload": {
                    "document_id": document_id,
                    "chunk_index": i,
                    "text": chunk,
                    "document_type": metadata.get("document_type"),
                    "created_at": datetime.utcnow().isoformat(),
                    **metadata
                }
            })
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return point_ids
    
    def semantic_search(self, query: str, document_type: Optional[str] = None, 
                       limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search across documents"""
        
        query_embedding = self.encoder.encode([query])[0]
        
        filter_conditions = {}
        if document_type:
            filter_conditions["document_type"] = document_type
        
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            query_filter=filter_conditions if filter_conditions else None,
            limit=limit,
            with_payload=True
        )
        
        results = []
        for hit in search_result:
            results.append({
                "document_id": hit.payload["document_id"],
                "text": hit.payload["text"],
                "score": hit.score,
                "document_type": hit.payload.get("document_type"),
                "chunk_index": hit.payload.get("chunk_index")
            })
        
        return results
```

### Phase 5: FastAPI Implementation

#### Main API Structure
```python
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import asyncio
import time
from typing import List, Optional

# Initialize FastAPI app
app = FastAPI(
    title="Legal Clarity API",
    description="AI-powered legal document processing and analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global instances (initialize these with proper configuration)
extractor = None
document_db = None
vector_db = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global extractor, document_db, vector_db
    
    # Initialize extractor with Gemini API key
    extractor = LegalDocumentExtractor(gemini_api_key=GEMINI_API_KEY)
    
    # Initialize databases
    document_db = LegalDocumentDB(MONGODB_CONNECTION_STRING)
    vector_db = VectorSearchDB(QDRANT_URL) if ENABLE_VECTOR_SEARCH else None

# Request/Response Models
class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    document_type: str
    status: str
    message: str

class ExtractionResponse(BaseModel):
    extraction_id: str
    document_id: str
    document_type: str
    confidence_score: float
    extracted_entities: List[Dict[str, Any]]
    processing_time: float
    status: str

class SearchRequest(BaseModel):
    query: str
    document_type: Optional[str] = None
    limit: int = 10

# API Endpoints
@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    document_type: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload and process legal document"""
    
    # Validate document type
    valid_types = ["rental", "loan", "tos"]
    if document_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid document type. Must be one of: {valid_types}"
        )
    
    # Validate file type
    if file.content_type not in ["application/pdf", "text/plain", "image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload PDF, text, or image files."
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Extract user ID from token (implement proper JWT validation)
        user_id = "user_123"  # Replace with actual user extraction
        
        # Store document in database
        document_id = document_db.store_document(
            file_content=file_content,
            filename=file.filename,
            document_type=document_type,
            user_id=user_id
        )
        
        # Schedule background processing
        background_tasks.add_task(
            process_document_async, 
            document_id, 
            file_content, 
            document_type
        )
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            document_type=document_type,
            status="processing",
            message="Document uploaded successfully. Processing in background."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_document_async(document_id: str, file_content: bytes, document_type: str):
    """Background task for document processing"""
    
    try:
        # Convert file to text (implement OCR for images, PDF parsing, etc.)
        document_text = await convert_to_text(file_content)
        
        # Measure processing time
        start_time = time.time()
        
        # Extract structured data
        extraction_results = extractor.extract_structured_data(document_text, document_type)
        
        processing_time = time.time() - start_time
        
        # Store extraction results
        extraction_id = document_db.store_extraction_results(
            document_id=document_id,
            extraction_data=extraction_results,
            processing_time=processing_time
        )
        
        # Optional: Create vector embeddings
        if vector_db and document_text:
            # Split text into chunks for better search
            text_chunks = split_text_into_chunks(document_text)
            
            vector_db.add_document_embeddings(
                document_id=document_id,
                text_chunks=text_chunks,
                metadata={
                    "document_type": document_type,
                    "extraction_id": extraction_id
                }
            )
        
    except Exception as e:
        # Log error and update document status
        print(f"Processing failed for document {document_id}: {str(e)}")
        # Update document status to failed in database

@app.get("/api/documents/{document_id}/extraction", response_model=ExtractionResponse)
async def get_extraction_results(
    document_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get extraction results for a document"""
    
    try:
        extraction_data = document_db.get_extraction_by_document_id(document_id)
        
        if not extraction_data:
            raise HTTPException(status_code=404, detail="Extraction not found")
        
        return ExtractionResponse(
            extraction_id=extraction_data["extraction_id"],
            document_id=extraction_data["document_id"],
            document_type=extraction_data["document_type"],
            confidence_score=extraction_data["confidence_score"],
            extracted_entities=extraction_data["extracted_data"]["extracted_entities"],
            processing_time=extraction_data["processing_time_seconds"],
            status=extraction_data["status"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve extraction: {str(e)}")

@app.post("/api/search/semantic")
async def semantic_search(
    search_request: SearchRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Perform semantic search across documents"""
    
    if not vector_db:
        raise HTTPException(status_code=404, detail="Vector search not enabled")
    
    try:
        results = vector_db.semantic_search(
            query=search_request.query,
            document_type=search_request.document_type,
            limit=search_request.limit
        )
        
        return {
            "query": search_request.query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/documents/search")
async def search_documents(
    document_type: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Search documents with filters"""
    
    try:
        # Extract user ID from credentials
        user_id = "user_123"  # Replace with actual user extraction
        
        query_params = {
            "user_id": user_id,
            "document_type": document_type,
            "date_from": date_from,
            "date_to": date_to
        }
        
        # Remove None values
        query_params = {k: v for k, v in query_params.items() if v is not None}
        
        results = document_db.search_documents(query_params)
        
        return {
            "documents": results,
            "total_count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# Utility Functions
async def convert_to_text(file_content: bytes) -> str:
    """Convert various file formats to text"""
    # Implement OCR for images, PDF parsing, etc.
    # This is a placeholder - implement actual conversion logic
    return file_content.decode('utf-8', errors='ignore')

def split_text_into_chunks(text: str, max_chunk_size: int = 1000) -> List[str]:
    """Split text into overlapping chunks for vector search"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), max_chunk_size - 100):  # 100 word overlap
        chunk = ' '.join(words[i:i + max_chunk_size])
        chunks.append(chunk)
    
    return chunks
```

### Phase 6: LangGraph Workflow Integration

```python
from langgraph.graph import StateGraph, START, END
from langgraph.constants import Send
from typing import TypedDict, List, Annotated
import operator

class DocumentProcessingState(TypedDict):
    document_id: str
    document_content: str
    document_type: str
    processing_step: str
    extracted_data: dict
    confidence_scores: List[float]
    errors: List[str]
    final_result: dict

def validate_document(state: DocumentProcessingState) -> DocumentProcessingState:
    """Validate document format and content"""
    
    if not state["document_content"]:
        state["errors"].append("Empty document content")
        return state
    
    if len(state["document_content"]) < 100:
        state["errors"].append("Document too short for meaningful extraction")
        return state
    
    # Check for legal document indicators
    legal_indicators = ["agreement", "contract", "terms", "conditions", "party", "parties"]
    content_lower = state["document_content"].lower()
    
    if not any(indicator in content_lower for indicator in legal_indicators):
        state["errors"].append("Document may not be a legal document")
    
    state["processing_step"] = "validated"
    return state

def classify_document_type(state: DocumentProcessingState) -> DocumentProcessingState:
    """Classify document type using Gemini"""
    
    classification_prompt = f"""
    Analyze this document and classify it as one of:
    1. rental - Rental/Lease agreement
    2. loan - Loan agreement/contract  
    3. tos - Terms of Service/Terms and Conditions
    
    Document excerpt: {state["document_content"][:2000]}
    
    Return only the classification: rental, loan, or tos
    """
    
    try:
        # Use Gemini for classification
        classified_type = "rental"  # Placeholder - implement actual Gemini call
        
        if state["document_type"] and state["document_type"] != classified_type:
            state["errors"].append(f"Document type mismatch: expected {state['document_type']}, detected {classified_type}")
        
        state["document_type"] = classified_type
        state["processing_step"] = "classified"
        
    except Exception as e:
        state["errors"].append(f"Classification failed: {str(e)}")
    
    return state

def extract_entities(state: DocumentProcessingState) -> DocumentProcessingState:
    """Extract structured entities using LangExtract"""
    
    try:
        extraction_results = extractor.extract_structured_data(
            state["document_content"], 
            state["document_type"]
        )
        
        state["extracted_data"] = extraction_results
        state["confidence_scores"].append(extraction_results.get("extraction_confidence", 0.0))
        state["processing_step"] = "extracted"
        
    except Exception as e:
        state["errors"].append(f"Entity extraction failed: {str(e)}")
    
    return state

def validate_extractions(state: DocumentProcessingState) -> DocumentProcessingState:
    """Validate extracted data for completeness and accuracy"""
    
    if not state["extracted_data"]:
        state["errors"].append("No data extracted")
        return state
    
    # Check confidence score
    confidence = state["extracted_data"].get("extraction_confidence", 0.0)
    if confidence < 0.7:
        state["errors"].append(f"Low extraction confidence: {confidence}")
    
    # Validate mandatory fields based on document type
    mandatory_fields = {
        "rental": ["lessor_name", "lessee_name", "property_address", "monthly_rent"],
        "loan": ["lender_name", "borrower_name", "principal_amount", "interest_rate"],
        "tos": ["service_provider", "service_description", "governing_law"]
    }
    
    required = mandatory_fields.get(state["document_type"], [])
    entities = state["extracted_data"].get("extracted_entities", [])
    
    extracted_classes = set(entity["class"] for entity in entities)
    missing_fields = [field for field in required if field not in extracted_classes]
    
    if missing_fields:
        state["errors"].append(f"Missing mandatory fields: {missing_fields}")
    
    state["processing_step"] = "validated"
    return state

def finalize_results(state: DocumentProcessingState) -> DocumentProcessingState:
    """Finalize processing results"""
    
    state["final_result"] = {
        "document_id": state["document_id"],
        "document_type": state["document_type"],
        "processing_status": "completed" if not state["errors"] else "completed_with_errors",
        "extracted_data": state["extracted_data"],
        "confidence_score": state["extracted_data"].get("extraction_confidence", 0.0),
        "errors": state["errors"],
        "processing_metadata": {
            "total_entities": len(state["extracted_data"].get("extracted_entities", [])),
            "processing_steps": state["processing_step"]
        }
    }
    
    state["processing_step"] = "finalized"
    return state

def should_continue_processing(state: DocumentProcessingState) -> str:
    """Determine next step in processing"""
    
    if state["processing_step"] == "validated" and not state["errors"]:
        return "classify"
    elif state["processing_step"] == "classified" and not any("critical" in error for error in state["errors"]):
        return "extract"
    elif state["processing_step"] == "extracted":
        return "validate_extractions"
    elif state["processing_step"] == "validated":
        return "finalize"
    else:
        return "finalize"  # Handle errors

# Build the workflow graph
def create_document_processing_workflow():
    """Create LangGraph workflow for document processing"""
    
    workflow = StateGraph(DocumentProcessingState)
    
    # Add nodes
    workflow.add_node("validate", validate_document)
    workflow.add_node("classify", classify_document_type)  
    workflow.add_node("extract", extract_entities)
    workflow.add_node("validate_extractions", validate_extractions)
    workflow.add_node("finalize", finalize_results)
    
    # Add edges
    workflow.add_edge(START, "validate")
    workflow.add_conditional_edges(
        "validate",
        should_continue_processing,
        {
            "classify": "classify",
            "finalize": "finalize"
        }
    )
    workflow.add_conditional_edges(
        "classify",
        should_continue_processing,
        {
            "extract": "extract",
            "finalize": "finalize"
        }
    )
    workflow.add_conditional_edges(
        "extract",
        should_continue_processing,
        {
            "validate_extractions": "validate_extractions",
            "finalize": "finalize"
        }
    )
    workflow.add_conditional_edges(
        "validate_extractions",
        should_continue_processing,
        {
            "finalize": "finalize"
        }
    )
    workflow.add_edge("finalize", END)
    
    return workflow.compile()

# Usage in the processing pipeline
document_processor = create_document_processing_workflow()

async def process_with_langgraph(document_id: str, content: str, doc_type: str) -> dict:
    """Process document using LangGraph workflow"""
    
    initial_state = DocumentProcessingState(
        document_id=document_id,
        document_content=content,
        document_type=doc_type,
        processing_step="initial",
        extracted_data={},
        confidence_scores=[],
        errors=[],
        final_result={}
    )
    
    try:
        result = document_processor.invoke(initial_state)
        return result["final_result"]
    except Exception as e:
        return {
            "document_id": document_id,
            "processing_status": "failed",
            "error": str(e)
        }
```

### Phase 7: Testing and Validation

Create comprehensive test cases:

```python
import pytest
from fastapi.testclient import TestClient
import io

client = TestClient(app)

def test_document_upload():
    """Test document upload endpoint"""
    
    # Create sample PDF content
    test_content = b"Sample rental agreement content..."
    
    response = client.post(
        "/api/documents/upload?document_type=rental",
        files={"file": ("test.pdf", io.BytesIO(test_content), "application/pdf")},
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert response.status_code == 200
    assert "document_id" in response.json()

def test_extraction_retrieval():
    """Test extraction results retrieval"""
    
    # First upload a document
    test_content = b"Sample loan agreement with principal amount Rs. 500000..."
    
    upload_response = client.post(
        "/api/documents/upload?document_type=loan", 
        files={"file": ("test.pdf", io.BytesIO(test_content), "application/pdf")},
        headers={"Authorization": "Bearer test_token"}
    )
    
    document_id = upload_response.json()["document_id"]
    
    # Wait for processing (in real implementation, use proper async testing)
    time.sleep(2)
    
    # Get extraction results
    extraction_response = client.get(
        f"/api/documents/{document_id}/extraction",
        headers={"Authorization": "Bearer test_token"}
    )
    
    assert extraction_response.status_code == 200
    assert "extracted_entities" in extraction_response.json()
```

## Deployment Instructions

### Environment Setup
```bash
# Production environment variables
export GEMINI_API_KEY="your_gemini_api_key"
export MONGODB_CONNECTION_STRING="mongodb://localhost:27017"
export QDRANT_URL="http://localhost:6333"
export JWT_SECRET_KEY="your_jwt_secret"
export ENABLE_VECTOR_SEARCH="true"

# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn for production
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

## Performance Optimization Guidelines

1. **Caching Strategy**: Implement Redis for caching extraction results
2. **Batch Processing**: Process multiple documents in parallel
3. **Rate Limiting**: Implement proper rate limiting for API endpoints
4. **Database Indexing**: Ensure proper MongoDB indexes for fast queries
5. **Memory Management**: Monitor memory usage during large document processing
6. **Error Handling**: Implement comprehensive error handling and retry logic

## Security Considerations

1. **Authentication**: Implement proper JWT-based authentication
2. **Input Validation**: Validate all inputs thoroughly
3. **File Security**: Scan uploaded files for malware
4. **Data Encryption**: Encrypt sensitive data at rest and in transit
5. **Audit Logging**: Maintain comprehensive audit trails
6. **Access Control**: Implement role-based access control

## Monitoring and Logging

1. **Application Metrics**: Monitor API response times, error rates
2. **Processing Metrics**: Track extraction success rates, processing times
3. **Database Metrics**: Monitor MongoDB and QdrantDB performance
4. **Business Metrics**: Track document types processed, user engagement
5. **Alert Configuration**: Set up alerts for critical failures

## Success Metrics for Hackathon

1. **Accuracy**: >90% extraction accuracy for key fields
2. **Performance**: <30 seconds average processing time
3. **Coverage**: Support for all three document types
4. **User Experience**: Intuitive API design and error handling
5. **Scalability**: Ability to process multiple documents concurrently

This comprehensive implementation guide provides you with everything needed to build Legal Clarity - a production-ready legal document processing system. Focus on implementing the core extraction pipeline first, then add advanced features like vector search and complex workflows.

The system is designed to be modular, scalable, and maintainable while leveraging the best of Google's AI technologies for legal document understanding.