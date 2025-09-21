"""
Enhanced Document Processor with Real PDF Processing and LangExtract Integration
"""

import os
import io
import logging
import textwrap
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import langextract as lx
from google.cloud import storage
import PyPDF2
import fitz  # PyMuPDF for better PDF text extraction
from enhanced_models import (
    ExtractedEntity, LegalClause, ClauseRelationship, 
    RiskAssessment, ComplianceCheck, AnalysisResult, ExtractionResult
)

logger = logging.getLogger(__name__)

class EnhancedDocumentProcessor:
    """Enhanced document processor with real PDF processing and legal extraction"""
    
    def __init__(self, gcs_client: storage.Client, settings):
        self.gcs_client = gcs_client
        self.settings = settings
        
        # Legal extraction prompts based on LangExtract best practices
        self.rental_analysis_prompt = textwrap.dedent("""
            Analyze this rental/lease agreement and extract comprehensive legal information:
            
            Extract in order of appearance:
            1. Party identification (landlord, tenant, guarantors with full names, addresses)
            2. Property details (address, type, specifications, condition)
            3. Financial terms (rent, deposits, fees, payment schedule)
            4. Lease duration (start date, end date, renewal terms)
            5. Maintenance responsibilities and obligations
            6. Termination conditions and notice requirements
            7. Legal compliance and regulatory requirements
            8. Rights and obligations of each party
            
            Use exact text from the document. Provide meaningful attributes.
            Do not paraphrase or overlap entities.
        """)
        
        self.rental_extraction_examples = [
            lx.data.ExampleData(
                text=textwrap.dedent("""
                    This lease agreement is between landlord Jane Smith, 456 Oak Avenue, NYC, NY 10001
                    and tenant John Doe, 789 Pine Street, NYC, NY 10002.
                    
                    Property: 123 Main Street, Apartment 4B, NYC, NY 10001
                    Monthly Rent: $1,200.00 due on the 1st of each month
                    Security Deposit: $2,400.00
                    Lease Term: January 1, 2024 to December 31, 2024
                    
                    Tenant responsible for utilities. Landlord responsible for major repairs.
                    30 days written notice required for termination.
                """),
                extractions=[
                    lx.data.Extraction(
                        extraction_class="landlord",
                        extraction_text="Jane Smith, 456 Oak Avenue, NYC, NY 10001",
                        attributes={"role": "landlord", "name": "Jane Smith", "address": "456 Oak Avenue, NYC, NY 10001"}
                    ),
                    lx.data.Extraction(
                        extraction_class="tenant",
                        extraction_text="John Doe, 789 Pine Street, NYC, NY 10002",
                        attributes={"role": "tenant", "name": "John Doe", "address": "789 Pine Street, NYC, NY 10002"}
                    ),
                    lx.data.Extraction(
                        extraction_class="property_address",
                        extraction_text="123 Main Street, Apartment 4B, NYC, NY 10001",
                        attributes={"type": "rental_property", "unit": "4B"}
                    ),
                    lx.data.Extraction(
                        extraction_class="monthly_rent",
                        extraction_text="$1,200.00",
                        attributes={"amount": 1200.00, "currency": "USD", "frequency": "monthly"}
                    ),
                    lx.data.Extraction(
                        extraction_class="security_deposit",
                        extraction_text="$2,400.00",
                        attributes={"amount": 2400.00, "currency": "USD", "type": "security_deposit"}
                    ),
                    lx.data.Extraction(
                        extraction_class="lease_start_date",
                        extraction_text="January 1, 2024",
                        attributes={"date_type": "lease_start", "formatted_date": "2024-01-01"}
                    ),
                    lx.data.Extraction(
                        extraction_class="lease_end_date",
                        extraction_text="December 31, 2024",
                        attributes={"date_type": "lease_end", "formatted_date": "2024-12-31"}
                    ),
                    lx.data.Extraction(
                        extraction_class="tenant_responsibility",
                        extraction_text="Tenant responsible for utilities",
                        attributes={"party": "tenant", "responsibility_type": "utilities"}
                    ),
                    lx.data.Extraction(
                        extraction_class="landlord_responsibility", 
                        extraction_text="Landlord responsible for major repairs",
                        attributes={"party": "landlord", "responsibility_type": "major_repairs"}
                    ),
                    lx.data.Extraction(
                        extraction_class="termination_notice",
                        extraction_text="30 days written notice required for termination",
                        attributes={"notice_period": 30, "notice_type": "written", "requirement": "termination"}
                    )
                ]
            )
        ]
        
    async def extract_pdf_text(self, gcs_path: str) -> str:
        """Extract text from PDF stored in GCS using multiple methods"""
        try:
            # Get bucket and blob
            bucket = self.gcs_client.bucket(self.settings.gcs_bucket)
            blob = bucket.blob(gcs_path)
            
            if not blob.exists():
                raise Exception(f"File not found in GCS: {gcs_path}")
            
            # Download PDF content
            pdf_bytes = blob.download_as_bytes()
            logger.info(f"Downloaded {len(pdf_bytes)} bytes from GCS")
            
            # Try PyMuPDF first (better for complex PDFs)
            try:
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                text_parts = []
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    text = page.get_text()
                    if text.strip():
                        text_parts.append(f"--- PAGE {page_num + 1} ---\n{text}")
                
                doc.close()
                
                if text_parts:
                    extracted_text = "\n\n".join(text_parts)
                    logger.info(f"PyMuPDF extracted {len(extracted_text)} characters")
                    return extracted_text
                    
            except Exception as e:
                logger.warning(f"PyMuPDF extraction failed: {e}, trying PyPDF2")
            
            # Fallback to PyPDF2
            try:
                pdf_file = io.BytesIO(pdf_bytes)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                text_parts = []
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        text_parts.append(f"--- PAGE {page_num + 1} ---\n{text}")
                
                if text_parts:
                    extracted_text = "\n\n".join(text_parts)
                    logger.info(f"PyPDF2 extracted {len(extracted_text)} characters")
                    return extracted_text
                    
            except Exception as e:
                logger.error(f"PyPDF2 extraction failed: {e}")
            
            raise Exception("Could not extract text using any PDF processor")
            
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            raise
    
    def _langextract_to_entities(self, extractions: List, extraction_type: str = "analysis") -> List[ExtractedEntity]:
        """Convert LangExtract results to our ExtractedEntity models"""
        entities = []
        
        for extraction in extractions:
            # Get source location if available
            source_location = None
            if hasattr(extraction, 'char_interval') and extraction.char_interval:
                source_location = {
                    "start_pos": extraction.char_interval.start_pos,
                    "end_pos": extraction.char_interval.end_pos,
                    "source_text": extraction.extraction_text
                }
            
            entity = ExtractedEntity(
                entity_class=extraction.extraction_class,
                entity_text=extraction.extraction_text,
                confidence=getattr(extraction, 'confidence', 0.9),  # Default confidence
                attributes=extraction.attributes or {},
                source_location=source_location
            )
            entities.append(entity)
        
        return entities
    
    def _generate_legal_clauses(self, entities: List[ExtractedEntity], document_text: str) -> List[LegalClause]:
        """Generate legal clauses from extracted entities"""
        clauses = []
        clause_id_counter = 1
        
        # Group entities by type to form clauses
        entity_groups = {}
        for entity in entities:
            entity_type = entity.entity_class
            if entity_type not in entity_groups:
                entity_groups[entity_type] = []
            entity_groups[entity_type].append(entity)
        
        # Create clauses from entity groups
        for clause_type, group_entities in entity_groups.items():
            if len(group_entities) > 0:
                # Combine related entities into clauses
                clause_text_parts = []
                key_terms = []
                obligations = []
                rights = []
                
                for entity in group_entities:
                    clause_text_parts.append(entity.entity_text)
                    key_terms.append(entity.entity_text)
                    
                    # Extract obligations and rights based on entity type
                    if 'responsibility' in clause_type.lower():
                        obligations.append(entity.entity_text)
                    elif 'right' in clause_type.lower():
                        rights.append(entity.entity_text)
                
                clause = LegalClause(
                    clause_id=f"clause_{clause_id_counter:03d}",
                    clause_type=clause_type,
                    clause_text=" | ".join(clause_text_parts),
                    clause_summary=f"Clause regarding {clause_type.replace('_', ' ')}",
                    key_terms=key_terms,
                    obligations=obligations,
                    rights=rights,
                    conditions=[],
                    source_location=group_entities[0].source_location,
                    confidence_score=sum(e.confidence for e in group_entities) / len(group_entities)
                )
                clauses.append(clause)
                clause_id_counter += 1
        
        return clauses
    
    def _assess_document_risk(self, entities: List[ExtractedEntity], document_type: str) -> RiskAssessment:
        """Assess risk based on extracted entities"""
        risk_factors = []
        risk_score = 50.0  # Default medium risk
        
        # Check for missing critical information
        entity_types = [e.entity_class for e in entities]
        
        if document_type == "rental_agreement":
            critical_types = ["landlord", "tenant", "monthly_rent", "security_deposit", "lease_start_date"]
            missing_critical = [t for t in critical_types if t not in entity_types]
            
            if missing_critical:
                risk_factors.append({
                    "factor": "missing_critical_information",
                    "description": f"Missing critical information: {', '.join(missing_critical)}",
                    "severity": "high",
                    "impact": "Could lead to disputes or legal issues"
                })
                risk_score += 20
        
        # Check for high financial amounts
        for entity in entities:
            if "amount" in entity.attributes and isinstance(entity.attributes["amount"], (int, float)):
                amount = entity.attributes["amount"]
                if amount > 5000:
                    risk_factors.append({
                        "factor": "high_financial_amount",
                        "description": f"High financial amount: ${amount}",
                        "severity": "medium",
                        "impact": "Requires careful verification"
                    })
        
        # Determine overall risk level
        if risk_score >= 70:
            risk_level = "high"
        elif risk_score >= 40:
            risk_level = "medium" 
        else:
            risk_level = "low"
        
        return RiskAssessment(
            overall_risk_level=risk_level,
            risk_score=min(risk_score, 100.0),
            risk_factors=risk_factors,
            recommendations=[
                "Review all extracted information carefully",
                "Verify critical terms and amounts",
                "Consider legal consultation for high-risk items"
            ],
            high_risk_clauses=[]
        )
    
    def _check_compliance(self, entities: List[ExtractedEntity], document_type: str) -> ComplianceCheck:
        """Check document compliance"""
        compliant_areas = []
        non_compliant_areas = []
        compliance_score = 75.0  # Default score
        
        entity_types = [e.entity_class for e in entities]
        
        if document_type == "rental_agreement":
            # Check for required elements
            if "landlord" in entity_types and "tenant" in entity_types:
                compliant_areas.append("Party identification complete")
            else:
                non_compliant_areas.append("Missing party identification")
                compliance_score -= 15
                
            if "monthly_rent" in entity_types:
                compliant_areas.append("Rental amount specified")
            else:
                non_compliant_areas.append("Rental amount not clearly specified")
                compliance_score -= 10
        
        recommendations = []
        if non_compliant_areas:
            recommendations.append("Address non-compliant areas to improve document validity")
        
        return ComplianceCheck(
            compliance_score=max(compliance_score, 0.0),
            compliant_areas=compliant_areas,
            non_compliant_areas=non_compliant_areas,
            recommendations=recommendations,
            legal_framework="Standard Contract Law"
        )
    
    async def analyze_document(
        self, 
        document_id: str, 
        gcs_path: str, 
        document_type: str, 
        user_id: str,
        analysis_options: Dict[str, Any] = None
    ) -> AnalysisResult:
        """Perform comprehensive document analysis with real PDF processing"""
        
        start_time = datetime.utcnow()
        logger.info(f"Starting analysis for document {document_id}")
        
        try:
            # Extract text from PDF
            document_text = await self.extract_pdf_text(gcs_path)
            logger.info(f"Extracted {len(document_text)} characters from PDF")
            
            # Use LangExtract for comprehensive analysis
            result = lx.extract(
                text_or_documents=document_text,
                prompt_description=self.rental_analysis_prompt,
                examples=self.rental_extraction_examples,
                model_id=self.settings.gemini_model or "gemini-2.5-flash"
            )
            
            logger.info(f"LangExtract found {len(result.extractions)} entities")
            
            # Convert to our entities
            entities = self._langextract_to_entities(result.extractions)
            
            # Perform risk assessment
            risk_assessment = self._assess_document_risk(entities, document_type)
            
            # Check compliance
            compliance_check = self._check_compliance(entities, document_type)
            
            # Generate key terms
            key_terms = list(set([e.entity_text for e in entities if len(e.entity_text) > 3]))
            
            # Create analysis result
            analysis_result = AnalysisResult(
                document_id=document_id,
                document_type=document_type,
                processing_timestamp=datetime.utcnow(),
                extracted_entities=entities,
                key_terms=key_terms[:20],  # Limit to top 20
                risk_assessment=risk_assessment,
                compliance_check=compliance_check,
                summary=f"Analysis completed for {document_type}. Found {len(entities)} entities with {risk_assessment.overall_risk_level} risk level and {compliance_check.compliance_score}% compliance score.",
                actionable_insights=[
                    f"Document contains {len(entities)} extracted entities",
                    f"Risk level: {risk_assessment.overall_risk_level}",
                    f"Compliance score: {compliance_check.compliance_score}%"
                ],
                processing_metadata={
                    "processing_time_seconds": (datetime.utcnow() - start_time).total_seconds(),
                    "document_length": len(document_text),
                    "model_used": self.settings.gemini_model or "gemini-2.5-flash",
                    "extraction_count": len(entities)
                }
            )
            
            logger.info(f"Analysis completed for document {document_id}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Document analysis failed for {document_id}: {e}")
            raise
    
    async def extract_legal_clauses(
        self, 
        document_id: str, 
        gcs_path: str, 
        document_type: str, 
        user_id: str,
        extraction_options: Dict[str, Any] = None
    ) -> ExtractionResult:
        """Perform comprehensive legal clause extraction"""
        
        start_time = datetime.utcnow()
        logger.info(f"Starting extraction for document {document_id}")
        
        try:
            # Extract text from PDF
            document_text = await self.extract_pdf_text(gcs_path)
            logger.info(f"Extracted {len(document_text)} characters from PDF")
            
            # Enhanced extraction prompt for clauses
            extraction_prompt = textwrap.dedent(f"""
                Extract comprehensive legal clauses and relationships from this {document_type}:
                
                Extract detailed information about:
                1. All parties involved (with complete details)
                2. Financial terms and payment obligations
                3. Important dates and deadlines
                4. Rights and obligations of each party
                5. Conditions and requirements
                6. Termination and renewal clauses
                7. Legal compliance requirements
                
                Use exact text. Group related information by party or topic.
                Provide meaningful attributes for structured analysis.
            """)
            
            # Use LangExtract for detailed extraction
            result = lx.extract(
                text_or_documents=document_text,
                prompt_description=extraction_prompt,
                examples=self.rental_extraction_examples,
                model_id=self.settings.gemini_model or "gemini-2.5-flash",
                extraction_passes=2,  # Multiple passes for better recall
                max_char_buffer=2000  # Larger buffer for context
            )
            
            logger.info(f"LangExtract found {len(result.extractions)} extractions")
            
            # Convert to entities
            all_entities = self._langextract_to_entities(result.extractions)
            
            # Separate entities by type
            parties = [e for e in all_entities if 'landlord' in e.entity_class.lower() or 'tenant' in e.entity_class.lower() or 'party' in e.entity_class.lower()]
            financial_terms = [e for e in all_entities if any(term in e.entity_class.lower() for term in ['rent', 'deposit', 'fee', 'amount', 'payment'])]
            dates = [e for e in all_entities if 'date' in e.entity_class.lower() or 'term' in e.entity_class.lower()]
            obligations = [e for e in all_entities if any(term in e.entity_class.lower() for term in ['responsibility', 'obligation', 'duty', 'requirement'])]
            
            # Generate legal clauses
            legal_clauses = self._generate_legal_clauses(all_entities, document_text)
            
            # Generate relationships (simplified)
            relationships = []
            
            # Create extraction result
            extraction_result = ExtractionResult(
                document_id=document_id,
                document_type=document_type,
                processing_timestamp=datetime.utcnow(),
                extracted_clauses=legal_clauses,
                clause_relationships=relationships,
                parties_identified=parties,
                financial_terms=financial_terms,
                important_dates=dates,
                obligations_and_rights=obligations,
                source_grounding={
                    "total_extractions": len(result.extractions),
                    "document_length": len(document_text),
                    "source_file": gcs_path
                },
                extraction_confidence=0.85,  # Average confidence
                processing_metadata={
                    "processing_time_seconds": (datetime.utcnow() - start_time).total_seconds(),
                    "document_length": len(document_text),
                    "model_used": self.settings.gemini_model or "gemini-2.5-flash",
                    "extraction_passes": 2,
                    "total_entities": len(all_entities),
                    "legal_clauses_count": len(legal_clauses)
                }
            )
            
            logger.info(f"Extraction completed for document {document_id}")
            return extraction_result
            
        except Exception as e:
            logger.error(f"Document extraction failed for {document_id}: {e}")
            raise