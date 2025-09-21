"""
Improved Legal Document Extractor - Modern LangExtract Integration
Updated with async support and proper import patterns
"""

import asyncio
import json
import logging
import os
import time
import uuid
import textwrap
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import LangExtract with modern patterns based on documentation
try:
    import langextract as lx
    LANGEXTRACT_AVAILABLE = True
except ImportError:
    LANGEXTRACT_AVAILABLE = False
    logging.warning("LangExtract not available - running in demo mode")

from ..models.schemas.legal_schemas import DocumentType, ExtractionResult, LegalClause, ClauseRelationship

# Demo mode results for testing without API key
DEMO_MODE_RESULTS = {
    "rental_agreement": {
        "parties": {
            "landlord": "John Doe",
            "tenant": "Jane Smith"
        },
        "property_details": {
            "address": "Sample Property Address",
            "type": "Residential"
        },
        "financial_terms": {
            "rent_amount": 50000,
            "security_deposit": 100000,
            "currency": "INR"
        },
        "lease_period": {
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "duration_months": 12
        },
        "clauses": [
            "Payment due on 1st of each month",
            "30 days notice required for termination",
            "Pet policy applies"
        ]
    },
    "loan_agreement": {
        "parties": {
            "lender": "ABC Bank",
            "borrower": "John Smith"
        },
        "loan_details": {
            "principal_amount": 500000,
            "interest_rate": 8.5,
            "currency": "INR"
        },
        "repayment_terms": {
            "tenure_months": 60,
            "emi_amount": 10273,
            "repayment_schedule": "Monthly"
        },
        "clauses": [
            "Late payment penalty applies",
            "Prepayment allowed after 12 months",
            "Collateral security required"
        ]
    },
    "terms_of_service": {
        "service_provider": "Sample Company",
        "effective_date": "2024-01-01",
        "key_terms": [
            "User responsibilities",
            "Service limitations",
            "Privacy policy compliance",
            "Termination conditions"
        ],
        "clauses": [
            "Service availability not guaranteed",
            "User data protection measures",
            "Dispute resolution mechanism"
        ]
    }
}

logger = logging.getLogger(__name__)


class ImprovedLegalDocumentExtractor:
    """
    Legal Document Extractor with demo mode support
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        """Initialize the extractor"""
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        self.demo_mode = not self.gemini_api_key
        
        if self.demo_mode:
            logger.warning("⚠️ No Gemini API key provided - running in DEMO mode")
            logger.warning("   Returning simulated extraction results")
        else:
            logger.info("✅ Gemini API key configured - real extraction mode")

    async def extract_clauses_and_relationships(
        self,
        document_text: str,
        document_type: str
    ) -> ExtractionResult:
        """
        Extract clauses and relationships from legal document
        
        Args:
            document_text: The document text to analyze
            document_type: Type of document (rental_agreement, loan_agreement, terms_of_service)
            
        Returns:
            ExtractionResult with extracted data
        """
        logger.info(f"Starting extraction for document type: {document_type}")
        start_time = time.time()

        try:
            # Validate document type
            if document_type not in ["rental_agreement", "loan_agreement", "terms_of_service"]:
                raise ValueError(f"Unsupported document type: {document_type}")

            # Map document type to enum
            doc_type_enum = self._map_document_type(document_type)

            if self.demo_mode:
                # Return demo results
                result = await self._get_demo_results(document_text, document_type, doc_type_enum)
            else:
                # Real extraction using LangExtract (simplified for now)
                result = await self._perform_real_extraction(document_text, document_type, doc_type_enum)

            processing_time = time.time() - start_time
            result.processing_time_seconds = processing_time
            
            logger.info(f"Extraction completed in {processing_time:.2f}s")
            return result

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            processing_time = time.time() - start_time
            
            # Return error result
            return ExtractionResult(
                document_id=f"error_{int(time.time())}",
                document_type=self._map_document_type(document_type) if document_type in ["rental_agreement", "loan_agreement", "terms_of_service"] else DocumentType.RENTAL_AGREEMENT,
                extracted_clauses=[],
                clause_relationships=[],
                confidence_score=0.0,
                processing_time_seconds=processing_time,
                extraction_metadata={
                    "error": str(e),
                    "processing_timestamp": datetime.utcnow().isoformat(),
                    "extraction_status": "failed"
                }
            )

    def _map_document_type(self, document_type: str) -> DocumentType:
        """Map string document type to enum"""
        mapping = {
            "rental_agreement": DocumentType.RENTAL_AGREEMENT,
            "loan_agreement": DocumentType.LOAN_AGREEMENT, 
            "terms_of_service": DocumentType.TERMS_OF_SERVICE
        }
        return mapping.get(document_type, DocumentType.RENTAL_AGREEMENT)

    async def _get_demo_results(
        self, 
        document_text: str, 
        document_type: str, 
        doc_type_enum: DocumentType
    ) -> ExtractionResult:
        """Generate demo extraction results"""
        
        # Simulate processing time
        await asyncio.sleep(0.5)

        demo_data = DEMO_MODE_RESULTS.get(document_type, DEMO_MODE_RESULTS["rental_agreement"])
        
        # Create demo clauses
        clauses = []
        clause_id = 1
        
        for clause_text in demo_data.get("clauses", []):
            clause = LegalClause(
                clause_id=f"clause_{clause_id}",
                clause_type="financial_terms" if clause_id == 1 else "party_identification",
                clause_text=clause_text,
                key_terms=["demo", "clause"],
                confidence_score=0.9
            )
            clauses.append(clause)
            clause_id += 1

        # Create demo relationships
        relationships = []
        if len(clauses) > 1:
            relationship = ClauseRelationship(
                relationship_id="rel_1",
                source_clause_id=clauses[0].clause_id,
                target_clause_id=clauses[1].clause_id,
                relationship_type="references",
                relationship_strength=0.8,
                description="Demo relationship between clauses"
            )
            relationships.append(relationship)

        return ExtractionResult(
            document_id=f"demo_{int(time.time())}",
            document_type=doc_type_enum,
            extracted_clauses=clauses,
            clause_relationships=relationships,
            confidence_score=0.85,
            processing_time_seconds=0.5,
            extraction_metadata={
                "total_extractions": len(clauses),
                "processing_timestamp": datetime.utcnow().isoformat(),
                "extraction_mode": "demo",
                "demo_data": demo_data
            }
        )

    async def _perform_real_extraction(
        self,
        document_text: str,
        document_type: str,
        doc_type_enum: DocumentType
    ) -> ExtractionResult:
        """Perform real extraction using modern LangExtract patterns"""
        
        if not LANGEXTRACT_AVAILABLE or self.demo_mode:
            logger.warning("LangExtract not available or in demo mode - using enhanced demo results")
            return await self._get_demo_results(document_text, document_type, doc_type_enum)
        
        logger.info("Performing real extraction with LangExtract and Gemini API")
        
        try:
            # Define extraction prompt based on modern LangExtract patterns
            prompt = textwrap.dedent(f"""
                Extract legal clauses, key terms, and relationships from this {document_type.replace('_', ' ')}.
                Identify parties, financial terms, obligations, conditions, and important clauses.
                Use exact text for extractions. Do not paraphrase or overlap entities.
                Provide meaningful attributes for each entity to add context.
            """)

            # Define examples based on document type (following LangExtract best practices)
            examples = self._get_langextract_examples(document_type)

            # Run LangExtract extraction
            result = lx.extract(
                text_or_documents=document_text,
                prompt_description=prompt,
                examples=examples,
                model_id="gemini-2.5-flash",
                api_key=self.gemini_api_key,
                max_workers=4,
                max_chunk_size=3000
            )

            # Convert LangExtract result to our schema
            return await self._convert_langextract_result(result, doc_type_enum, document_type)
            
        except Exception as e:
            logger.error(f"Real extraction failed, falling back to enhanced demo: {e}")
            return await self._get_demo_results(document_text, document_type, doc_type_enum)
    
    def _get_langextract_examples(self, document_type: str) -> List:
        """Get LangExtract examples based on document type"""
        
        if document_type == "rental_agreement":
            return [
                lx.data.ExampleData(
                    text="The Landlord agrees to rent the Property to the Tenant for $1,200 per month.",
                    extractions=[
                        lx.data.Extraction(
                            extraction_class="financial_term",
                            extraction_text="$1,200 per month",
                            attributes={"type": "rent_amount", "frequency": "monthly"}
                        ),
                        lx.data.Extraction(
                            extraction_class="party_identification",
                            extraction_text="Landlord",
                            attributes={"role": "property_owner"}
                        ),
                        lx.data.Extraction(
                            extraction_class="party_identification", 
                            extraction_text="Tenant",
                            attributes={"role": "property_renter"}
                        ),
                    ]
                )
            ]
        elif document_type == "loan_agreement":
            return [
                lx.data.ExampleData(
                    text="The Borrower agrees to repay the Principal Amount of $50,000 with interest at 8.5% per annum.",
                    extractions=[
                        lx.data.Extraction(
                            extraction_class="financial_term",
                            extraction_text="$50,000",
                            attributes={"type": "principal_amount"}
                        ),
                        lx.data.Extraction(
                            extraction_class="financial_term",
                            extraction_text="8.5% per annum", 
                            attributes={"type": "interest_rate", "frequency": "annual"}
                        ),
                        lx.data.Extraction(
                            extraction_class="party_identification",
                            extraction_text="Borrower",
                            attributes={"role": "loan_recipient"}
                        ),
                    ]
                )
            ]
        else:  # terms_of_service
            return [
                lx.data.ExampleData(
                    text="By using this service, you agree to these Terms of Service and our Privacy Policy.",
                    extractions=[
                        lx.data.Extraction(
                            extraction_class="obligation",
                            extraction_text="agree to these Terms of Service",
                            attributes={"type": "user_obligation", "scope": "terms_acceptance"}
                        ),
                        lx.data.Extraction(
                            extraction_class="obligation",
                            extraction_text="our Privacy Policy",
                            attributes={"type": "policy_reference", "scope": "privacy"}
                        ),
                    ]
                )
            ]

    async def _convert_langextract_result(
        self, 
        langextract_result, 
        doc_type_enum: DocumentType, 
        document_type: str
    ) -> ExtractionResult:
        """Convert LangExtract result to our ExtractionResult schema"""
        
        clauses = []
        relationships = []
        
        # Extract clauses from LangExtract result
        if hasattr(langextract_result, 'extractions'):
            for i, extraction in enumerate(langextract_result.extractions):
                clause = LegalClause(
                    clause_id=f"clause_{i+1}",
                    clause_type=extraction.extraction_class,
                    clause_text=extraction.extraction_text,
                    key_terms=list(extraction.attributes.keys()) if extraction.attributes else [],
                    confidence_score=getattr(extraction, 'confidence', 0.9)
                )
                clauses.append(clause)

        # Create relationships (simplified - could be enhanced)
        if len(clauses) > 1:
            for i in range(len(clauses) - 1):
                relationship = ClauseRelationship(
                    relationship_id=f"rel_{i+1}",
                    source_clause_id=clauses[i].clause_id,
                    target_clause_id=clauses[i+1].clause_id,
                    relationship_type="follows",
                    relationship_strength=0.7,
                    description=f"Sequential relationship between {clauses[i].clause_type} and {clauses[i+1].clause_type}"
                )
                relationships.append(relationship)

        return ExtractionResult(
            document_id=f"real_{int(time.time())}_{uuid.uuid4().hex[:8]}",
            document_type=doc_type_enum,
            extracted_clauses=clauses,
            clause_relationships=relationships,
            confidence_score=getattr(langextract_result, 'confidence_score', 0.85),
            processing_time_seconds=getattr(langextract_result, 'processing_time', 2.0),
            extraction_metadata={
                "total_extractions": len(clauses),
                "processing_timestamp": datetime.utcnow().isoformat(),
                "extraction_mode": "langextract_real",
                "model_used": "gemini-2.5-flash",
                "langextract_version": getattr(lx, '__version__', 'unknown') if LANGEXTRACT_AVAILABLE else None
            }
        )

    def create_structured_document(
        self, 
        extraction_result: Dict[str, Any], 
        original_text: str
    ) -> Dict[str, Any]:
        """
        Create a structured document from extraction results
        
        Args:
            extraction_result: Dictionary containing extraction results
            original_text: Original document text
            
        Returns:
            Structured document dictionary
        """
        logger.info("Creating structured document from extraction results")
        
        return {
            "structured_document": {
                "original_text": original_text,
                "extraction_summary": extraction_result,
                "structure_timestamp": datetime.utcnow().isoformat(),
                "document_metadata": {
                    "text_length": len(original_text),
                    "extraction_count": len(extraction_result.get("extracted_clauses", [])),
                    "processing_mode": extraction_result.get("extraction_metadata", {}).get("extraction_mode", "unknown")
                }
            }
        }