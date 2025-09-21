"""
Document Analyzer Service using LangExtract and Gemini Flash
Core service for processing legal documents and extracting structured information
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

try:
    import langextract as lx
    LANGEXTRACT_AVAILABLE = True
except ImportError:
    LANGEXTRACT_AVAILABLE = False
    logging.warning("LangExtract not available. Install with: pip install langextract")

import sys
import os
# Add the models directory to sys.path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
models_dir = os.path.join(parent_dir, 'models')
if models_dir not in sys.path:
    sys.path.insert(0, models_dir)

from schemas.processed_document import (
    DocumentAnalysisResult,
    ExtractedEntity,
    SourceGrounding,
    ExtractionMetadata,
    DocumentClauses,
    RiskAssessment,
    ComplianceCheck,
    FinancialAnalysis
)

logger = logging.getLogger(__name__)


class DocumentAnalyzerService:
    """Service for analyzing legal documents using LangExtract and Gemini"""

    def __init__(self, gemini_api_key: str, gemini_model: str = "gemini-2.0-flash-exp"):
        """
        Initialize document analyzer service

        Args:
            gemini_api_key: Gemini API key
            gemini_model: Gemini model to use
        """
        if not LANGEXTRACT_AVAILABLE:
            raise ImportError("LangExtract is required for document analysis. Install with: pip install langextract")

        self.gemini_api_key = gemini_api_key
        self.gemini_model = gemini_model
        from .legal_extractor_service import LegalExtractorService
        self.extractor = LegalExtractorService(gemini_api_key)

        logger.info(f"Document analyzer initialized with model: {gemini_model}")

    async def analyze_document(self, document_id: str, document_text: str,
                             document_type: str, user_id: str) -> DocumentAnalysisResult:
        """
        Analyze a legal document and extract structured information

        Args:
            document_id: Unique document identifier
            document_text: Text content of the document
            document_type: Type of document (rental/loan/tos)
            user_id: User who owns the document

        Returns:
            Complete analysis result
        """
        try:
            logger.info(f"Starting analysis for document: {document_id} (type: {document_type})")

            start_time = time.time()

            # Extract structured data using LangExtract
            extraction_result = await self.extractor.extract_structured_data(
                document_text, document_type
            )

            processing_time = time.time() - start_time

            # Process extraction results into structured analysis
            analysis_result = await self._process_extraction_results(
                document_id, document_type, user_id, extraction_result, processing_time
            )

            logger.info(".2f")
            return analysis_result

        except Exception as e:
            logger.error(f"Document analysis failed for {document_id}: {e}")
            raise Exception(f"Document analysis failed: {str(e)}")

    async def _process_extraction_results(self, document_id: str, document_type: str, user_id: str,
                                        extraction_result: Dict[str, Any], processing_time: float) -> DocumentAnalysisResult:
        """Process LangExtract results into structured analysis"""

        # Extract entities
        extracted_entities = []
        for entity_data in extraction_result.get("extracted_entities", []):
            entity = ExtractedEntity(**entity_data)
            extracted_entities.append(entity)

        # Create source grounding
        source_grounding = {}
        for entity_class, grounding_data in extraction_result.get("source_grounding", {}).items():
            source_grounding[entity_class] = SourceGrounding(**grounding_data)

        # Create extraction metadata
        extraction_metadata = ExtractionMetadata(
            total_extractions=len(extracted_entities),
            processing_timestamp=datetime.utcnow(),
            extraction_confidence=extraction_result.get("extraction_confidence", 0.0),
            processing_time_seconds=processing_time
        )

        # Categorize clauses
        document_clauses = await self._categorize_clauses(extracted_entities, document_type)

        # Perform risk assessment
        risk_assessment = await self._assess_risks(extracted_entities, document_type)

        # Check compliance
        compliance_check = await self._check_compliance(extracted_entities, document_type)

        # Analyze financial aspects
        financial_analysis = await self._analyze_financial_aspects(extracted_entities, document_type)

        # Generate summary and insights
        summary = await self._generate_summary(extracted_entities, document_type)
        key_terms = await self._extract_key_terms(extracted_entities, document_type)
        actionable_insights = await self._generate_insights(extracted_entities, document_type, risk_assessment)

        return DocumentAnalysisResult(
            document_id=document_id,
            document_type=document_type,
            user_id=user_id,
            extracted_entities=extracted_entities,
            source_grounding=source_grounding,
            extraction_metadata=extraction_metadata,
            document_clauses=document_clauses,
            risk_assessment=risk_assessment,
            compliance_check=compliance_check,
            financial_analysis=financial_analysis,
            summary=summary,
            key_terms=key_terms,
            actionable_insights=actionable_insights,
            processing_status="completed",
            processing_version="1.0",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            processed_by="legal_clarity_analyzer"
        )

    async def _categorize_clauses(self, entities: List[ExtractedEntity], document_type: str) -> DocumentClauses:
        """Categorize extracted entities into different clause types"""

        financial_clauses = []
        legal_clauses = []
        operational_clauses = []
        compliance_clauses = []
        termination_clauses = []
        dispute_resolution_clauses = []

        for entity in entities:
            entity_dict = entity.dict()

            # Categorize based on entity class and document type
            if document_type == "rental":
                if entity.class_name in ["monthly_rent", "security_deposit", "maintenance_charges", "utility_responsibility"]:
                    financial_clauses.append(entity_dict)
                elif entity.class_name in ["termination_conditions", "notice_period_days", "subletting_allowed"]:
                    termination_clauses.append(entity_dict)
                elif entity.class_name in ["registration_required", "stamp_duty_paid", "society_noc"]:
                    compliance_clauses.append(entity_dict)
                elif entity.class_name in ["jurisdiction", "arbitration_clause"]:
                    dispute_resolution_clauses.append(entity_dict)
                else:
                    operational_clauses.append(entity_dict)

            elif document_type == "loan":
                if entity.class_name in ["principal_amount", "interest_rate", "emi_amount", "processing_fees"]:
                    financial_clauses.append(entity_dict)
                elif entity.class_name in ["events_of_default", "termination_conditions"]:
                    termination_clauses.append(entity_dict)
                elif entity.class_name in ["rbi_guidelines_followed", "sarfaesi_applicable", "tds_compliance"]:
                    compliance_clauses.append(entity_dict)
                elif entity.class_name in ["jurisdiction", "arbitration_clause"]:
                    dispute_resolution_clauses.append(entity_dict)
                else:
                    operational_clauses.append(entity_dict)

            elif document_type == "tos":
                if entity.class_name in ["payment_terms", "refund_policy", "pricing_model"]:
                    financial_clauses.append(entity_dict)
                elif entity.class_name in ["termination_conditions", "termination_conditions"]:
                    termination_clauses.append(entity_dict)
                elif entity.class_name in ["it_act_compliance", "data_protection_compliance"]:
                    compliance_clauses.append(entity_dict)
                elif entity.class_name in ["governing_law", "dispute_resolution", "arbitration_clause"]:
                    dispute_resolution_clauses.append(entity_dict)
                else:
                    operational_clauses.append(entity_dict)

        return DocumentClauses(
            financial_clauses=financial_clauses,
            legal_clauses=legal_clauses,
            operational_clauses=operational_clauses,
            compliance_clauses=compliance_clauses,
            termination_clauses=termination_clauses,
            dispute_resolution_clauses=dispute_resolution_clauses
        )

    async def _assess_risks(self, entities: List[ExtractedEntity], document_type: str) -> RiskAssessment:
        """Assess risks based on extracted entities"""

        risk_factors = []
        risk_score = 5.0  # Base score
        recommendations = []

        if document_type == "rental":
            # Check for high security deposit
            for entity in entities:
                if entity.class_name == "security_deposit" and entity.attributes.get("amount", 0) > 50000:
                    risk_factors.append({
                        "type": "high_security_deposit",
                        "severity": "medium",
                        "description": "Security deposit is relatively high compared to monthly rent"
                    })
                    recommendations.append("Negotiate lower security deposit or ensure proper receipt")
                    risk_score += 1.0

            # Check for lack of registration
            registration_found = any(e.class_name == "registration_required" for e in entities)
            if not registration_found:
                risk_factors.append({
                    "type": "unregistered_agreement",
                    "severity": "high",
                    "description": "Agreement may not be registered as required by law"
                })
                recommendations.append("Ensure agreement is registered with sub-registrar office")
                risk_score += 2.0

        elif document_type == "loan":
            # Check for high interest rates
            for entity in entities:
                if entity.class_name == "interest_rate" and entity.attributes.get("rate", 0) > 15:
                    risk_factors.append({
                        "type": "high_interest_rate",
                        "severity": "medium",
                        "description": "Interest rate is relatively high"
                    })
                    recommendations.append("Compare rates with other lenders")
                    risk_score += 1.0

            # Check for personal guarantees
            guarantor_found = any(e.class_name in ["guarantor_details", "personal_guarantees"] for e in entities)
            if guarantor_found:
                risk_factors.append({
                    "type": "personal_guarantee_required",
                    "severity": "medium",
                    "description": "Personal guarantee may be required"
                })
                recommendations.append("Understand the implications of personal guarantee")
                risk_score += 1.5

        elif document_type == "tos":
            # Check for broad liability limitations
            liability_found = any(e.class_name == "liability_limitations" for e in entities)
            if liability_found:
                risk_factors.append({
                    "type": "broad_liability_exclusions",
                    "severity": "medium",
                    "description": "Service provider has broad liability limitations"
                })
                recommendations.append("Review liability clauses carefully")
                risk_score += 1.0

        # Determine overall risk level
        if risk_score < 4.0:
            risk_level = "low"
        elif risk_score < 7.0:
            risk_level = "medium"
        else:
            risk_level = "high"

        return RiskAssessment(
            overall_risk_level=risk_level,
            risk_factors=risk_factors,
            risk_score=risk_score,
            recommendations=recommendations
        )

    async def _check_compliance(self, entities: List[ExtractedEntity], document_type: str) -> ComplianceCheck:
        """Check legal compliance based on extracted entities"""

        compliance_data = {}
        mandatory_disclosures = []
        compliance_score = 100.0

        if document_type == "rental":
            # Check for mandatory Indian rental agreement elements
            mandatory_elements = ["stamp_duty_paid", "registration_required", "witnesses"]
            found_elements = [e.class_name for e in entities]

            for element in mandatory_elements:
                if element in found_elements:
                    compliance_data[element] = True
                else:
                    compliance_data[element] = False
                    compliance_score -= 20.0
                    mandatory_disclosures.append(f"Missing: {element.replace('_', ' ').title()}")

        elif document_type == "loan":
            # Check for mandatory RBI compliance elements
            rbi_elements = ["rbi_guidelines_followed", "interest_rate", "emi_amount"]
            found_elements = [e.class_name for e in entities]

            for element in rbi_elements:
                if element in found_elements:
                    compliance_data[element] = True
                else:
                    compliance_data[element] = False
                    compliance_score -= 25.0
                    mandatory_disclosures.append(f"Missing RBI requirement: {element.replace('_', ' ').title()}")

        elif document_type == "tos":
            # Check for mandatory consumer protection elements
            consumer_elements = ["governing_law", "dispute_resolution", "termination_conditions"]
            found_elements = [e.class_name for e in entities]

            for element in consumer_elements:
                if element in found_elements:
                    compliance_data[element] = True
                else:
                    compliance_data[element] = False
                    compliance_score -= 20.0
                    mandatory_disclosures.append(f"Missing consumer protection: {element.replace('_', ' ').title()}")

        return ComplianceCheck(
            indian_law_compliance=compliance_data,
            regulatory_requirements=[],
            mandatory_disclosures=mandatory_disclosures,
            compliance_score=max(0.0, compliance_score)
        )

    async def _analyze_financial_aspects(self, entities: List[ExtractedEntity], document_type: str) -> FinancialAnalysis:
        """Analyze financial implications"""

        monetary_values = []
        payment_obligations = []
        financial_risks = []

        for entity in entities:
            if "amount" in entity.attributes or "rent" in entity.class_name or "fee" in entity.class_name:
                monetary_values.append({
                    "type": entity.class_name,
                    "description": entity.text,
                    "attributes": entity.attributes
                })

            if entity.class_name in ["emi_amount", "monthly_rent", "processing_fees"]:
                payment_obligations.append({
                    "type": entity.class_name,
                    "description": entity.text,
                    "attributes": entity.attributes
                })

        # Identify financial risks
        if document_type == "rental":
            high_deposit = any(e.class_name == "security_deposit" and e.attributes.get("amount", 0) > 100000 for e in entities)
            if high_deposit:
                financial_risks.append("High security deposit amount")

        elif document_type == "loan":
            high_interest = any(e.class_name == "interest_rate" and e.attributes.get("rate", 0) > 20 for e in entities)
            if high_interest:
                financial_risks.append("High interest rate")

        return FinancialAnalysis(
            monetary_values=monetary_values,
            payment_obligations=payment_obligations,
            financial_risks=financial_risks,
            cost_benefit_analysis=None
        )

    async def _generate_summary(self, entities: List[ExtractedEntity], document_type: str) -> str:
        """Generate a human-readable summary"""

        if document_type == "rental":
            summary = "This is a residential rental agreement. "
            for entity in entities:
                if entity.class_name == "monthly_rent":
                    amount = entity.attributes.get("amount", "N/A")
                    summary += f"Monthly rent is ₹{amount}. "
                elif entity.class_name == "security_deposit":
                    amount = entity.attributes.get("amount", "N/A")
                    summary += f"Security deposit is ₹{amount}. "
                elif entity.class_name == "lease_start_date":
                    summary += f"Lease starts from {entity.attributes.get('date', 'N/A')}. "

        elif document_type == "loan":
            summary = "This is a loan agreement. "
            for entity in entities:
                if entity.class_name == "principal_amount":
                    amount = entity.attributes.get("amount", "N/A")
                    summary += f"Principal amount is ₹{amount}. "
                elif entity.class_name == "interest_rate":
                    rate = entity.attributes.get("rate", "N/A")
                    summary += f"Interest rate is {rate}%. "
                elif entity.class_name == "loan_tenure_months":
                    tenure = entity.attributes.get("months", "N/A")
                    summary += f"Loan tenure is {tenure} months. "

        elif document_type == "tos":
            summary = "This is a Terms of Service agreement. "
            for entity in entities:
                if entity.class_name == "service_provider":
                    summary += f"Service provider is {entity.attributes.get('name', 'N/A')}. "
                elif entity.class_name == "governing_law":
                    summary += f"Governed by {entity.attributes.get('law', 'N/A')}. "

        else:
            summary = f"This is a {document_type} document with {len(entities)} key entities extracted."

        return summary.strip()

    async def _extract_key_terms(self, entities: List[ExtractedEntity], document_type: str) -> List[str]:
        """Extract key terms and conditions"""

        key_terms = []

        for entity in entities:
            if entity.class_name in ["monthly_rent", "security_deposit", "interest_rate", "principal_amount"]:
                if "amount" in entity.attributes:
                    amount = entity.attributes["amount"]
                    key_terms.append(f"{entity.class_name.replace('_', ' ').title()}: ₹{amount}")
                elif "rate" in entity.attributes:
                    rate = entity.attributes["rate"]
                    key_terms.append(f"{entity.class_name.replace('_', ' ').title()}: {rate}%")

            elif entity.class_name in ["notice_period_days", "loan_tenure_months"]:
                if "days" in entity.attributes:
                    days = entity.attributes["days"]
                    key_terms.append(f"{entity.class_name.replace('_', ' ').title()}: {days} days")
                elif "months" in entity.attributes:
                    months = entity.attributes["months"]
                    key_terms.append(f"{entity.class_name.replace('_', ' ').title()}: {months} months")

        return key_terms[:10]  # Limit to top 10 key terms

    async def _generate_insights(self, entities: List[ExtractedEntity], document_type: str,
                               risk_assessment: RiskAssessment) -> List[str]:
        """Generate actionable insights"""

        insights = []

        if document_type == "rental":
            insights.extend([
                "Verify the property address and landlord details",
                "Ensure agreement is registered if lease period exceeds 11 months",
                "Check local rent control laws in your area",
                "Keep receipts for all payments made"
            ])

            if risk_assessment.overall_risk_level in ["medium", "high"]:
                insights.append("Consider consulting a legal expert before signing")

        elif document_type == "loan":
            insights.extend([
                "Calculate total interest payable over loan tenure",
                "Check prepayment charges before making early payments",
                "Understand all fees and charges mentioned",
                "Keep track of all payments and receipts"
            ])

            if risk_assessment.overall_risk_level in ["medium", "high"]:
                insights.append("Compare terms with other lenders")

        elif document_type == "tos":
            insights.extend([
                "Review cancellation and refund policies carefully",
                "Understand data collection and usage practices",
                "Check dispute resolution mechanisms",
                "Note any automatic renewal clauses"
            ])

        return insights


class LegalDocumentExtractor:
    """LangExtract wrapper for legal document processing"""

    def __init__(self, gemini_api_key: str, model_id: str = "gemini-2.0-flash-exp"):
        self.gemini_api_key = gemini_api_key
        self.model_id = model_id

    async def extract_structured_data(self, document_text: str, document_type: str) -> Dict[str, Any]:
        """
        Extract structured data using LangExtract

        Args:
            document_text: The document text to process
            document_type: Type of document (rental/loan/tos)

        Returns:
            Dictionary containing extracted data
        """
        try:
            # Define extraction prompts and examples for each document type
            prompts_and_examples = self._get_prompts_and_examples(document_type)

            # Use LangExtract for extraction
            result = lx.extract(
                text_or_documents=document_text,
                prompt_description=prompts_and_examples["prompt"],
                examples=prompts_and_examples["examples"],
                model_id=self.model_id,
                api_key=self.gemini_api_key,
                max_char_buffer=8000,
                extraction_passes=2,
                fence_output=True,
                use_schema_constraint=True
            )

            # Process and return results
            return await self._process_langextract_result(result, document_type)

        except Exception as e:
            logger.error(f"LangExtract processing failed: {e}")
            raise Exception(f"Extraction failed: {str(e)}")

    def _get_prompts_and_examples(self, document_type: str) -> Dict[str, Any]:
        """Get prompts and examples for document type"""

        if document_type == "rental":
            prompt = """
            Extract key information from this rental/lease agreement. Focus on:

            1. PARTIES: Names, addresses, and contact details of lessor and lessee
            2. PROPERTY: Complete address, description, and key details
            3. FINANCIAL: Rent amount, security deposit, payment terms
            4. DURATION: Lease start date, end date, notice period
            5. LEGAL: Registration requirements, compliance clauses

            Return structured data with accurate extraction of monetary values, dates, and legal terms.
            """

            examples = [
                lx.data.ExampleData(
                    text="This Rent Agreement made on 15th January 2024 between Mr. Rajesh Kumar (Lessor) and Ms. Priya Sharma (Lessee). Monthly rent Rs. 25,000/-. Security deposit Rs. 50,000/-. Lease from 1st February 2024 to 31st January 2025.",
                    extractions=[
                        lx.data.Extraction(
                            extraction_class="lessor_name",
                            extraction_text="Mr. Rajesh Kumar",
                            attributes={"name": "Mr. Rajesh Kumar"}
                        ),
                        lx.data.Extraction(
                            extraction_class="lessee_name",
                            extraction_text="Ms. Priya Sharma",
                            attributes={"name": "Ms. Priya Sharma"}
                        ),
                        lx.data.Extraction(
                            extraction_class="monthly_rent",
                            extraction_text="Monthly rent Rs. 25,000/-",
                            attributes={"amount": 25000.0}
                        ),
                        lx.data.Extraction(
                            extraction_class="security_deposit",
                            extraction_text="Security deposit Rs. 50,000/-",
                            attributes={"amount": 50000.0}
                        )
                    ]
                )
            ]

        elif document_type == "loan":
            prompt = """
            Extract key information from this loan agreement. Focus on:

            1. PARTIES: Lender and borrower details
            2. LOAN TERMS: Principal amount, interest rate, tenure
            3. REPAYMENT: EMI amount, frequency, start date
            4. LEGAL: Compliance with RBI guidelines, default provisions

            Return structured data with accurate financial calculations.
            """

            examples = [
                lx.data.ExampleData(
                    text="Loan Agreement between HDFC Bank and Mr. Amit Singh. Principal Rs. 5,00,000/- at 9.5% per annum for 60 months. EMI Rs. 10,456/- starting March 2024.",
                    extractions=[
                        lx.data.Extraction(
                            extraction_class="lender_name",
                            extraction_text="HDFC Bank",
                            attributes={"name": "HDFC Bank"}
                        ),
                        lx.data.Extraction(
                            extraction_class="borrower_name",
                            extraction_text="Mr. Amit Singh",
                            attributes={"name": "Mr. Amit Singh"}
                        ),
                        lx.data.Extraction(
                            extraction_class="principal_amount",
                            extraction_text="Principal Rs. 5,00,000/-",
                            attributes={"amount": 500000.0}
                        ),
                        lx.data.Extraction(
                            extraction_class="interest_rate",
                            extraction_text="9.5% per annum",
                            attributes={"rate": 9.5}
                        )
                    ]
                )
            ]

        elif document_type == "tos":
            prompt = """
            Extract key information from this Terms of Service agreement. Focus on:

            1. PROVIDER: Company details and service description
            2. USER TERMS: Eligibility, rights, obligations
            3. FINANCIAL: Pricing, payment, refund terms
            4. LEGAL: Governing law, liability, dispute resolution

            Return structured data with clear categorization of rights and obligations.
            """

            examples = [
                lx.data.ExampleData(
                    text="Terms of Service for TechCorp Private Limited. Users must be 18+. Service governed by Indian law. Disputes subject to Bangalore jurisdiction.",
                    extractions=[
                        lx.data.Extraction(
                            extraction_class="service_provider",
                            extraction_text="TechCorp Private Limited",
                            attributes={"name": "TechCorp Private Limited"}
                        ),
                        lx.data.Extraction(
                            extraction_class="governing_law",
                            extraction_text="Indian law",
                            attributes={"law": "Indian law"}
                        ),
                        lx.data.Extraction(
                            extraction_class="jurisdiction",
                            extraction_text="Bangalore jurisdiction",
                            attributes={"location": "Bangalore"}
                        )
                    ]
                )
            ]

        else:
            prompt = "Extract key information and entities from this document."
            examples = []

        return {
            "prompt": prompt,
            "examples": examples
        }

    async def _process_langextract_result(self, result: Any, document_type: str) -> Dict[str, Any]:
        """Process LangExtract result into our format"""

        structured_data = {
            "document_type": document_type,
            "extraction_confidence": getattr(result, 'confidence', 0.0),
            "extracted_entities": [],
            "source_grounding": {},
            "metadata": {
                "total_extractions": len(result.extractions) if hasattr(result, 'extractions') and result.extractions else 0,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
        }

        if hasattr(result, 'extractions') and result.extractions:
            for extraction in result.extractions:
                entity = {
                    "class_name": extraction.extraction_class,
                    "text": extraction.extraction_text,
                    "attributes": extraction.attributes,
                    "confidence": getattr(extraction, 'confidence', 0.0),
                    "source_location": {
                        "start_char": getattr(extraction, 'start_char', 0),
                        "end_char": getattr(extraction, 'end_char', 0)
                    }
                }
                structured_data["extracted_entities"].append(entity)

                # Build source grounding
                if hasattr(extraction, 'source_text'):
                    structured_data["source_grounding"][extraction.extraction_class] = {
                        "original_text": extraction.source_text,
                        "extracted_value": extraction.extraction_text,
                        "verification_needed": True
                    }

        return structured_data
