"""
Legal Document Extractor using LangExtract with Real Implementation
Extracts clauses and relationships from legal documents using proper LangExtract patterns
No mock implementations - uses real LangExtract with Gemini models
"""

import langextract as lx
from typing import Dict, Any, List, Optional, Type
import json
import time
from datetime import datetime
import os
from pathlib import Path
import textwrap

from legal_document_schemas import (
    DocumentType, ClauseType, RelationshipType, LegalClause,
    ClauseRelationship, LegalDocument, ExtractionResult,
    RentalAgreement, LoanAgreement, TermsOfService
)


class LegalDocumentExtractor:
    """
    Extracts clauses and relationships from legal documents using LangExtract
    with real Gemini models and comprehensive legal document understanding
    """

    def __init__(self, gemini_api_key: Optional[str] = None):
        """
        Initialize the extractor with Gemini API key

        Args:
            gemini_api_key: Gemini API key (optional if set in environment)
        """
        self.gemini_api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable or pass directly.")

        # Initialize extraction configurations for each document type
        self.extraction_configs = self._initialize_extraction_configs()

    def _initialize_extraction_configs(self) -> Dict[str, Dict[str, Any]]:
        """Initialize extraction configurations for each document type with LangExtract best practices"""

        return {
            "rental": {
                "model_id": "gemini-2.5-flash",  # More stable model with better rate limits
                "extraction_passes": 2,  # Reduced to avoid rate limits
                "max_char_buffer": 6000,  # Larger buffer for better context
                "max_workers": 1,  # Sequential processing to avoid rate limits
                "temperature": 0.1,
                "fence_output": False,  # Disable for better compatibility
                "prompts": self._get_rental_prompts(),
                "examples": self._get_rental_examples()
            },
            "loan": {
                "model_id": "gemini-2.5-flash",
                "extraction_passes": 2,
                "max_char_buffer": 6000,
                "max_workers": 1,
                "temperature": 0.1,
                "fence_output": False,
                "prompts": self._get_loan_prompts(),
                "examples": self._get_loan_examples()
            },
            "tos": {
                "model_id": "gemini-2.5-flash",
                "extraction_passes": 2,
                "max_char_buffer": 6000,
                "max_workers": 1,
                "temperature": 0.1,
                "fence_output": False,
                "prompts": self._get_tos_prompts(),
                "examples": self._get_tos_examples()
            }
        }

    def _get_rental_prompts(self) -> str:
        """Get comprehensive prompts for rental agreement extraction using LangExtract patterns"""
        return textwrap.dedent("""
        Extract clauses and relationships from this rental/lease agreement document.

        Focus on identifying key legal clauses and their relationships. Use exact text from the document
        for extraction_text. Do not paraphrase or overlap entities. Extract entities in order of appearance.

        Key extraction classes:
        - party_lessor: Landlord/lessor party details
        - party_lessee: Tenant/lessee party details
        - property_details: Property description and specifications
        - financial_terms: Rent, deposits, payments
        - lease_duration: Term dates and renewal conditions
        - maintenance_responsibilities: Who handles repairs and maintenance
        - termination_conditions: Termination rights and procedures
        - legal_compliance: Registration, stamp duty, governing law

        For relationships, use attributes to link related clauses:
        - link_to_party: Connects financial terms to specific parties
        - depends_on_duration: Links clauses that depend on lease term
        - legal_requirement: Marks legally required clauses

        Return structured extractions with meaningful attributes for context.
        """)

    def _get_loan_prompts(self) -> str:
        """Get comprehensive prompts for loan agreement extraction"""
        return """
        Extract ALL clauses and relationships from this loan agreement document.
        Focus on identifying and extracting:

        1. PARTY IDENTIFICATION:
           - Lender details: institution name, registration, contact
           - Borrower details: name, address, PAN, Aadhaar, employment
           - Co-borrowers and guarantors information

        2. LOAN SPECIFICATIONS:
           - Principal amount and sanctioned amount
           - Loan purpose and end-use verification
           - Disbursement schedule and conditions

        3. INTEREST STRUCTURE:
           - Interest rate type (fixed/floating/hybrid)
           - Base rate, spread, and current rate
           - Reset frequency and compounding method

        4. REPAYMENT TERMS:
           - EMI amount and repayment schedule
           - Tenure, frequency, and payment mode
           - Prepayment terms and charges
           - Moratorium and part-payment facilities

        5. SECURITY AND COLLATERAL:
           - Primary security type and asset details
           - Valuation and loan-to-value ratio
           - Insurance requirements and guarantees

        6. DEFAULT PROVISIONS:
           - Events of default and cure periods
           - Acceleration clauses and recovery mechanisms
           - SARFAESI Act applicability

        7. COMPLIANCE REQUIREMENTS:
           - RBI guidelines and TDS applicability
           - Financial covenants and reporting requirements
           - Restrictive covenants and conditions

        RELATIONSHIPS TO IDENTIFY:
        - Link repayment obligations to security provisions
        - Connect default events to recovery mechanisms
        - Associate financial covenants to penalties
        - Map compliance requirements to loan conditions

        Extract each clause with its exact text, key terms, obligations, rights, conditions, and consequences.
        Use relationship_group attributes to connect related clauses.
        Provide source grounding for all extractions with character positions.
        """

    def _get_tos_prompts(self) -> str:
        """Get comprehensive prompts for terms of service extraction"""
        return """
        Extract ALL clauses and relationships from this Terms of Service document.
        Focus on identifying and extracting:

        1. SERVICE DEFINITION:
           - Service provider details and registration
           - Service description and target users
           - Geographic availability and age restrictions

        2. USER OBLIGATIONS:
           - Acceptable use policies and prohibited activities
           - Content guidelines and community standards
           - Compliance requirements and user responsibilities

        3. COMMERCIAL TERMS:
           - Pricing structure and billing cycles
           - Payment methods and refund policies
           - Taxation implications and currency terms

        4. USER RIGHTS:
           - Service access and usage rights
           - Data portability and privacy controls
           - Termination rights and account management

        5. LIABILITY LIMITATIONS:
           - Limitation of liability clauses
           - Indemnification requirements
           - Warranty disclaimers and exclusions

        6. DISPUTE RESOLUTION:
           - Grievance redressal mechanisms
           - Governing law and jurisdiction
           - Arbitration clauses and ADR preferences

        RELATIONSHIPS TO IDENTIFY:
        - Link user obligations to service access rights
        - Connect commercial terms to payment obligations
        - Associate liability limitations to user responsibilities
        - Map dispute resolution to breach consequences

        Extract each clause with its exact text, key terms, obligations, rights, conditions, and consequences.
        Use relationship_group attributes to connect related clauses.
        Provide source grounding for all extractions with character positions.
        """

    def _get_rental_examples(self) -> List[lx.data.ExampleData]:
        """Get example extractions for rental agreements using LangExtract best practices"""
        return [
            lx.data.ExampleData(
                text="""This Agreement is made between the Landlord and the Tenant. The monthly rent is $1,200 payable on the 1st of each month. Security deposit is $1,200. The lease term is 12 months from January 1, 2024.""",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="party_lessor",
                        extraction_text="the Landlord",
                        attributes={
                            "party_role": "landlord"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="party_lessee",
                        extraction_text="the Tenant",
                        attributes={
                            "party_role": "tenant"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="financial_terms",
                        extraction_text="monthly rent is $1,200 payable on the 1st of each month. Security deposit is $1,200",
                        attributes={
                            "rent_amount": 1200.0,
                            "payment_frequency": "monthly"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="lease_duration",
                        extraction_text="lease term is 12 months from January 1, 2024",
                        attributes={
                            "duration_months": 12,
                            "start_date": "2024-01-01"
                        }
                    )
                ]
            )
        ]

    def _get_loan_examples(self) -> List[lx.data.ExampleData]:
        """Get example extractions for loan agreements using LangExtract best practices"""
        return [
            lx.data.ExampleData(
                text="""This Loan Agreement is between the Bank (Lender) and the Customer (Borrower). The loan amount is $50,000 at 8.5% interest per annum. Monthly EMI is $1,200 starting from March 1, 2024.""",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="party_lender",
                        extraction_text="the Bank (Lender)",
                        attributes={
                            "party_role": "financial_institution"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="party_borrower",
                        extraction_text="the Customer (Borrower)",
                        attributes={
                            "party_role": "loan_recipient"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="loan_specifications",
                        extraction_text="loan amount is $50,000 at 8.5% interest per annum",
                        attributes={
                            "loan_amount": 50000.0,
                            "interest_rate": 8.5
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="repayment_terms",
                        extraction_text="Monthly EMI is $1,200 starting from March 1, 2024",
                        attributes={
                            "emi_amount": 1200.0,
                            "payment_frequency": "monthly"
                        }
                    )
                ]
            )
        ]

    def _get_tos_examples(self) -> List[lx.data.ExampleData]:
        """Get example extractions for terms of service using LangExtract best practices"""
        return [
            lx.data.ExampleData(
                text="""These Terms of Service govern your use of our website. Users must be 18 years or older. We may terminate your account with 30 days notice. All disputes shall be resolved in the courts of California.""",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="service_provider",
                        extraction_text="our website",
                        attributes={
                            "party_role": "service_provider"
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="user_eligibility",
                        extraction_text="Users must be 18 years or older",
                        attributes={
                            "minimum_age": 18
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="termination_conditions",
                        extraction_text="terminate your account with 30 days notice",
                        attributes={
                            "notice_period_days": 30
                        }
                    ),
                    lx.data.Extraction(
                        extraction_class="dispute_resolution",
                        extraction_text="disputes shall be resolved in the courts of California",
                        attributes={
                            "jurisdiction": "california"
                        }
                    )
                ]
            )
        ]

    def extract_clauses_and_relationships(self, document_text: str, document_type: str) -> ExtractionResult:
        """
        Extract clauses and relationships from legal document using LangExtract

        Args:
            document_text: Raw text of the legal document
            document_type: Type of document ("rental", "loan", or "tos")

        Returns:
            ExtractionResult with extracted clauses and relationships
        """

        if document_type not in self.extraction_configs:
            raise ValueError(f"Unsupported document type: {document_type}")

        config = self.extraction_configs[document_type]
        start_time = time.time()

        print(f"🔍 LangExtract Debug Info:")
        print(f"   Document type: {document_type}")
        print(f"   Text length: {len(document_text)} characters")
        print(f"   Model: {config['model_id']}")
        print(f"   Max buffer: {config['max_char_buffer']}")
        print(f"   Extraction passes: {config['extraction_passes']}")
        print(f"   Max workers: {config['max_workers']}")

        try:
            print("🔄 Calling LangExtract API...")
            # Perform extraction using LangExtract with optimized parameters
            result = lx.extract(
                text_or_documents=document_text,
                prompt_description=config["prompts"],
                examples=config["examples"],
                model_id=config["model_id"],
                api_key=self.gemini_api_key,
                max_char_buffer=config["max_char_buffer"],
                extraction_passes=config["extraction_passes"],
                max_workers=config["max_workers"]
            )

            print(f"✅ LangExtract completed successfully")
            print(f"   Extractions found: {len(result.extractions) if result.extractions else 0}")

            # Process and structure the results
            clauses, relationships = self._process_extraction_results(result, document_type)

            processing_time = time.time() - start_time

            # Calculate overall confidence score
            confidence_score = self._calculate_confidence_score(clauses)

            # Map document type string to enum
            doc_type_mapping = {
                "rental": DocumentType.RENTAL_AGREEMENT,
                "loan": DocumentType.LOAN_AGREEMENT,
                "tos": DocumentType.TERMS_OF_SERVICE
            }

            mapped_doc_type = doc_type_mapping.get(document_type, DocumentType.RENTAL_AGREEMENT)

            return ExtractionResult(
                document_id=f"doc_{int(time.time())}",
                document_type=mapped_doc_type,
                extracted_clauses=clauses,
                clause_relationships=relationships,
                confidence_score=confidence_score,
                processing_time_seconds=processing_time,
                extraction_metadata={
                    "total_extractions": len(result.extractions) if result.extractions else 0,
                    "processing_timestamp": datetime.utcnow().isoformat(),
                    "model_used": config["model_id"]
                }
            )

        except Exception as e:
            raise Exception(f"Extraction failed: {str(e)}")

    def _process_extraction_results(self, result, document_type: str) -> tuple[List[LegalClause], List[ClauseRelationship]]:
        """
        Process LangExtract results into structured clauses and relationships

        Args:
            result: LangExtract results
            document_type: Type of document

        Returns:
            Tuple of (clauses, relationships)
        """

        clauses = []
        relationships = []

        if not result.extractions:
            print("⚠️ No extractions found in LangExtract result")
            return clauses, relationships

        print(f"🔄 Processing {len(result.extractions)} extractions...")

        clause_counter = 0

        for extraction in result.extractions:
            try:
                clause_counter += 1
                clause_id = f"clause_{clause_counter}"

                # Safely extract attributes
                attributes = extraction.attributes or {}

                # Create LegalClause with safe attribute handling
                legal_clause = LegalClause(
                    clause_id=clause_id,
                    clause_type=self._map_clause_type_safe(extraction.extraction_class),
                    clause_text=extraction.extraction_text or "",
                    key_terms=self._extract_key_terms_safe(attributes),
                    obligations=self._extract_obligations_safe(attributes),
                    rights=self._extract_rights_safe(attributes),
                    conditions=self._extract_conditions_safe(attributes),
                    consequences=self._extract_consequences_safe(attributes),
                    compliance_requirements=self._extract_compliance_safe(attributes),
                    source_location={
                        "start_char": getattr(extraction, 'start_char', 0),
                        "end_char": getattr(extraction, 'end_char', 0)
                    },
                    confidence_score=getattr(extraction, 'confidence', 0.8)
                )

                clauses.append(legal_clause)
                print(f"   ✅ Processed clause {clause_counter}: {extraction.extraction_class}")

            except Exception as e:
                print(f"   ⚠️ Failed to process extraction {clause_counter}: {e}")
                continue

        print(f"✅ Successfully processed {len(clauses)} clauses")

        # Create simple relationships based on clause types
        relationships = self._create_simple_relationships(clauses)

        return clauses, relationships

    def _map_clause_type_safe(self, extraction_class: str) -> ClauseType:
        """Safely map extraction class to ClauseType"""
        try:
            return self._map_clause_type(extraction_class)
        except Exception:
            return ClauseType.PARTY_IDENTIFICATION

    def _extract_key_terms_safe(self, attributes: Dict[str, Any]) -> List[str]:
        """Safely extract key terms"""
        try:
            return self._extract_key_terms_from_attributes(attributes)
        except Exception:
            return []

    def _extract_obligations_safe(self, attributes: Dict[str, Any]) -> List[str]:
        """Safely extract obligations"""
        try:
            return self._extract_obligations_from_attributes(attributes)
        except Exception:
            return []

    def _extract_rights_safe(self, attributes: Dict[str, Any]) -> List[str]:
        """Safely extract rights"""
        try:
            return self._extract_rights_from_attributes(attributes)
        except Exception:
            return []

    def _extract_conditions_safe(self, attributes: Dict[str, Any]) -> List[str]:
        """Safely extract conditions"""
        try:
            return self._extract_conditions_from_attributes(attributes)
        except Exception:
            return []

    def _extract_consequences_safe(self, attributes: Dict[str, Any]) -> List[str]:
        """Safely extract consequences"""
        try:
            return self._extract_consequences_from_attributes(attributes)
        except Exception:
            return []

    def _extract_compliance_safe(self, attributes: Dict[str, Any]) -> List[str]:
        """Safely extract compliance requirements"""
        try:
            return self._extract_compliance_from_attributes(attributes)
        except Exception:
            return []

    def _create_simple_relationships(self, clauses: List[LegalClause]) -> List[ClauseRelationship]:
        """Create simple relationships based on clause types"""
        relationships = []

        # Group clauses by type
        party_clauses = [c for c in clauses if c.clause_type == ClauseType.PARTY_IDENTIFICATION]
        financial_clauses = [c for c in clauses if c.clause_type == ClauseType.FINANCIAL_TERMS]

        # Create relationships between parties and financial terms
        for party in party_clauses:
            for financial in financial_clauses:
                relationship = ClauseRelationship(
                    relationship_id=f"rel_{party.clause_id}_{financial.clause_id}",
                    relationship_type=RelationshipType.PARTY_TO_FINANCIAL,
                    source_clause_id=party.clause_id,
                    target_clause_id=financial.clause_id,
                    relationship_description="Party connected to financial terms",
                    strength=0.7
                )
                relationships.append(relationship)

        return relationships

    def _map_clause_type(self, extraction_class: str) -> ClauseType:
        """Map LangExtract class to our ClauseType enum"""
        mapping = {
            # Rental agreement classes
            "party_lessor": ClauseType.PARTY_IDENTIFICATION,
            "party_lessee": ClauseType.PARTY_IDENTIFICATION,
            "property_details": ClauseType.PROPERTY_DESCRIPTION,
            "financial_terms": ClauseType.FINANCIAL_TERMS,
            "lease_duration": ClauseType.LEASE_DURATION,
            "maintenance_responsibilities": ClauseType.MAINTENANCE_RESPONSIBILITIES,
            "termination_conditions": ClauseType.TERMINATION_CONDITIONS,
            "legal_compliance": ClauseType.LEGAL_COMPLIANCE,

            # Loan agreement classes
            "party_lender": ClauseType.PARTY_IDENTIFICATION,
            "party_borrower": ClauseType.PARTY_IDENTIFICATION,
            "loan_specifications": ClauseType.LOAN_SPECIFICATIONS,
            "interest_structure": ClauseType.INTEREST_STRUCTURE,
            "repayment_terms": ClauseType.REPAYMENT_TERMS,
            "security_details": ClauseType.SECURITY_DETAILS,
            "default_provisions": ClauseType.DEFAULT_PROVISIONS,
            "compliance_requirements": ClauseType.COMPLIANCE_REQUIREMENTS,

            # Terms of service classes
            "service_provider": ClauseType.PARTY_IDENTIFICATION,
            "user_eligibility": ClauseType.USER_OBLIGATIONS,
            "service_definition": ClauseType.SERVICE_DEFINITION,
            "commercial_terms": ClauseType.COMMERCIAL_TERMS,
            "termination_conditions": ClauseType.TERMINATION_CONDITIONS,
            "dispute_resolution": ClauseType.DISPUTE_RESOLUTION,
            "liability_limitations": ClauseType.LIABILITY_LIMITATIONS,

            # Legacy mappings for backward compatibility
            "party_identification": ClauseType.PARTY_IDENTIFICATION,
            "property_description": ClauseType.PROPERTY_DESCRIPTION,
            "user_obligations": ClauseType.USER_OBLIGATIONS
        }
        return mapping.get(extraction_class, ClauseType.PARTY_IDENTIFICATION)

    def _extract_key_terms_from_attributes(self, attributes: Dict[str, Any]) -> List[str]:
        """Extract key terms from LangExtract attributes"""
        key_terms = []

        # Extract specific attribute values as key terms
        for attr_key, attr_value in attributes.items():
            if isinstance(attr_value, str) and len(attr_value) < 50:
                key_terms.append(attr_value)
            elif isinstance(attr_value, list) and len(attr_value) > 0:
                # Add list items if they're short strings
                for item in attr_value:
                    if isinstance(item, str) and len(item) < 30:
                        key_terms.append(item)

        return key_terms[:5]  # Limit to top 5 key terms

    def _extract_obligations_from_attributes(self, attributes: Dict[str, Any]) -> List[str]:
        """Extract obligations from LangExtract attributes"""
        obligations = []

        # Look for obligation-related attributes
        if attributes.get("party_role") == "landlord" or attributes.get("party_role") == "lender":
            obligations.append("Primary party obligations")
        elif attributes.get("party_role") == "tenant" or attributes.get("party_role") == "borrower":
            obligations.append("Secondary party obligations")

        # Extract monetary obligations
        if "monthly_rent" in attributes:
            obligations.append(f"Monthly rent payment: Rs. {attributes['monthly_rent']}")
        if "emi_amount" in attributes:
            obligations.append(f"EMI payment: Rs. {attributes['emi_amount']}")

        return obligations

    def _extract_rights_from_attributes(self, attributes: Dict[str, Any]) -> List[str]:
        """Extract rights from LangExtract attributes"""
        rights = []

        # Extract rights based on party roles
        if attributes.get("party_role") in ["landlord", "lender", "service_provider"]:
            rights.append("Contract enforcement rights")
        elif attributes.get("party_role") in ["tenant", "borrower"]:
            rights.append("Service usage rights")

        # Extract specific rights
        if attributes.get("refundable_deposit"):
            rights.append("Security deposit refund rights")

        return rights

    def _extract_conditions_from_attributes(self, attributes: Dict[str, Any]) -> List[str]:
        """Extract conditions from LangExtract attributes"""
        conditions = []

        # Extract temporal conditions
        if "start_date" in attributes:
            conditions.append(f"Effective from: {attributes['start_date']}")
        if "end_date" in attributes:
            conditions.append(f"Expires on: {attributes['end_date']}")

        # Extract dependency conditions
        if attributes.get("depends_on_duration"):
            conditions.append("Subject to contract duration")

        return conditions

    def _extract_consequences_from_attributes(self, attributes: Dict[str, Any]) -> List[str]:
        """Extract consequences from LangExtract attributes"""
        consequences = []

        # Extract breach consequences
        if "notice_period_days" in attributes:
            days = attributes["notice_period_days"]
            consequences.append(f"Notice period: {days} days")

        # Extract financial consequences
        if "late_payment_penalty" in attributes:
            consequences.append("Late payment penalties apply")

        return consequences

    def _extract_compliance_from_attributes(self, attributes: Dict[str, Any]) -> List[str]:
        """Extract compliance requirements from LangExtract attributes"""
        compliance = []

        # Extract legal compliance requirements
        if attributes.get("legal_requirement"):
            compliance.append("Legal compliance mandatory")

        if attributes.get("governing_law"):
            compliance.append(f"Governed by {attributes['governing_law']}")

        if attributes.get("jurisdiction"):
            compliance.append(f"Jurisdiction: {attributes['jurisdiction']}")

        return compliance

    def create_visualization_data(self, result: ExtractionResult, document_text: str) -> Dict[str, Any]:
        """Create visualization data for extracted clauses and relationships"""
        visualization_data = {
            "document_id": result.document_id,
            "document_type": result.document_type.value,
            "total_clauses": len(result.extracted_clauses),
            "total_relationships": len(result.clause_relationships),
            "confidence_score": result.confidence_score,
            "clauses": [],
            "relationships": [],
            "document_length": len(document_text)
        }

        # Add clause data
        for clause in result.extracted_clauses:
            clause_data = {
                "id": clause.clause_id,
                "type": clause.clause_type.value,
                "text": clause.clause_text[:100] + "..." if len(clause.clause_text) > 100 else clause.clause_text,
                "confidence": clause.confidence_score or 0.5,
                "key_terms": clause.key_terms[:3] if clause.key_terms else [],
                "obligations": clause.obligations[:2] if clause.obligations else [],
                "rights": clause.rights[:2] if clause.rights else [],
                "source_location": clause.source_location
            }
            visualization_data["clauses"].append(clause_data)

        # Add relationship data
        for rel in result.clause_relationships:
            rel_data = {
                "id": rel.relationship_id,
                "type": rel.relationship_type.value,
                "source": rel.source_clause_id,
                "target": rel.target_clause_id,
                "description": rel.relationship_description,
                "strength": rel.strength
            }
            visualization_data["relationships"].append(rel_data)

        return visualization_data

    def save_visualization_data(self, visualization_data: Dict[str, Any], output_path: str):
        """Save visualization data to JSON file"""
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(visualization_data, f, indent=2, ensure_ascii=False)

    def _infer_party_relationship_type(self, clause1: LegalClause, clause2: LegalClause, party_group: str) -> RelationshipType:
        """Infer relationship type based on party groupings"""
        if "lessor" in party_group or "landlord" in party_group:
            return RelationshipType.PARTY_TO_FINANCIAL
        elif "lessee" in party_group or "tenant" in party_group:
            return RelationshipType.PARTY_TO_FINANCIAL
        elif "lender" in party_group:
            return RelationshipType.PARTY_TO_FINANCIAL
        elif "borrower" in party_group:
            return RelationshipType.PARTY_TO_FINANCIAL
        elif "service_provider" in party_group:
            return RelationshipType.PARTY_TO_FINANCIAL
        elif "both_parties" in party_group:
            return RelationshipType.PARTY_TO_FINANCIAL
        else:
            return RelationshipType.CLAUSE_DEPENDENCY

    def _infer_relationship_type(self, clause1: LegalClause, clause2: LegalClause, group_name: str) -> RelationshipType:
        """Infer relationship type based on clause types and group"""
        if "party" in group_name.lower():
            return RelationshipType.PARTY_TO_FINANCIAL
        elif "financial" in group_name.lower():
            return RelationshipType.PARTY_TO_FINANCIAL
        elif "obligation" in group_name.lower():
            return RelationshipType.OBLIGATION_TO_RIGHT
        elif "condition" in group_name.lower():
            return RelationshipType.CONDITION_TO_CONSEQUENCE
        else:
            return RelationshipType.CLAUSE_TO_CLAUSE

    def _calculate_confidence_score(self, clauses: List[LegalClause]) -> float:
        """Calculate overall confidence score for extraction"""
        if not clauses:
            return 0.0

        total_confidence = sum(clause.confidence_score or 0.5 for clause in clauses)
        return total_confidence / len(clauses)

    def save_extraction_results(self, result: ExtractionResult, output_dir: str = "extraction_results"):
        """
        Save extraction results to JSON and create visualization

        Args:
            result: ExtractionResult to save
            output_dir: Directory to save results
        """

        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)

        # Save JSON results
        json_path = Path(output_dir) / f"{result.document_id}_extraction.json"
        with open(json_path, 'w') as f:
            json.dump(result.dict(), f, indent=2, default=str)

        # Create visualization data
        visualization_data = {
            "document_id": result.document_id,
            "document_type": result.document_type.value,
            "clauses": [
                {
                    "id": clause.clause_id,
                    "type": clause.clause_type.value,
                    "text": clause.clause_text[:100] + "..." if len(clause.clause_text) > 100 else clause.clause_text,
                    "confidence": clause.confidence_score
                }
                for clause in result.extracted_clauses
            ],
            "relationships": [
                {
                    "source": rel.source_clause_id,
                    "target": rel.target_clause_id,
                    "type": rel.relationship_type.value,
                    "description": rel.relationship_description
                }
                for rel in result.clause_relationships
            ]
        }

        vis_path = Path(output_dir) / f"{result.document_id}_visualization.json"
        with open(vis_path, 'w') as f:
            json.dump(visualization_data, f, indent=2)

        print(f"✓ Extraction results saved to {json_path}")
        print(f"✓ Visualization data saved to {vis_path}")

        return str(json_path), str(vis_path)

    def create_structured_document(self, extraction_result: ExtractionResult, original_text: str) -> LegalDocument:
        """
        Create a structured LegalDocument from extraction results

        Args:
            extraction_result: Results from clause extraction
            original_text: Original document text

        Returns:
            Structured LegalDocument
        """

        # Map clauses to appropriate document structure based on type
        if extraction_result.document_type == DocumentType.RENTAL_AGREEMENT:
            structured_data = self._create_rental_structure(extraction_result)
        elif extraction_result.document_type == DocumentType.LOAN_AGREEMENT:
            structured_data = self._create_loan_structure(extraction_result)
        elif extraction_result.document_type == DocumentType.TERMS_OF_SERVICE:
            structured_data = self._create_tos_structure(extraction_result)
        else:
            raise ValueError(f"Unsupported document type: {extraction_result.document_type}")

        return LegalDocument(
            document_id=extraction_result.document_id,
            document_type=extraction_result.document_type,
            original_text=original_text,
            extracted_data=structured_data,
            processing_metadata=extraction_result.extraction_metadata,
            extraction_confidence=extraction_result.confidence_score
        )

    def _create_rental_structure(self, result: ExtractionResult) -> RentalAgreement:
        """Create RentalAgreement structure from clauses"""
        # This is a simplified implementation - in practice, you'd map clauses to specific schema fields
        return RentalAgreement(
            document_metadata={"type": "rental_agreement"},
            parties=None,  # Would be populated from relevant clauses
            property_details=None,
            financial_terms=None,
            lease_terms=None,
            maintenance_responsibilities=None,
            termination_conditions=None,
            legal_compliance=None,
            extracted_clauses=result.extracted_clauses,
            clause_relationships=result.clause_relationships
        )

    def _create_loan_structure(self, result: ExtractionResult) -> LoanAgreement:
        """Create LoanAgreement structure from clauses"""
        return LoanAgreement(
            loan_metadata={"type": "loan_agreement"},
            parties=None,
            loan_terms=None,
            interest_structure=None,
            repayment_terms=None,
            security_details=None,
            default_provisions=None,
            compliance_requirements=None,
            extracted_clauses=result.extracted_clauses,
            clause_relationships=result.clause_relationships
        )

    def _create_tos_structure(self, result: ExtractionResult) -> TermsOfService:
        """Create TermsOfService structure from clauses"""
        return TermsOfService(
            tos_metadata={"type": "terms_of_service"},
            service_definition=None,
            user_obligations=None,
            commercial_terms=None,
            liability_limitations=None,
            dispute_resolution=None,
            extracted_clauses=result.extracted_clauses,
            clause_relationships=result.clause_relationships
        )
