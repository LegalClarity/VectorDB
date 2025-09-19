"""
Legal Document Schemas for Clause and Relationship Extraction
Based on comprehensive analysis of Indian legal documents from Context.md and Data.md
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import date
from enum import Enum


class DocumentType(str, Enum):
    RENTAL_AGREEMENT = "rental_agreement"
    LOAN_AGREEMENT = "loan_agreement"
    TERMS_OF_SERVICE = "terms_of_service"


class ClauseType(str, Enum):
    # Rental Agreement Clauses
    PARTY_IDENTIFICATION = "party_identification"
    PROPERTY_DESCRIPTION = "property_description"
    FINANCIAL_TERMS = "financial_terms"
    LEASE_DURATION = "lease_duration"
    MAINTENANCE_RESPONSIBILITIES = "maintenance_responsibilities"
    TERMINATION_CONDITIONS = "termination_conditions"
    LEGAL_COMPLIANCE = "legal_compliance"

    # Loan Agreement Clauses
    LOAN_SPECIFICATIONS = "loan_specifications"
    INTEREST_STRUCTURE = "interest_structure"
    REPAYMENT_TERMS = "repayment_terms"
    SECURITY_DETAILS = "security_details"
    DEFAULT_PROVISIONS = "default_provisions"
    COMPLIANCE_REQUIREMENTS = "compliance_requirements"

    # Terms of Service Clauses
    SERVICE_DEFINITION = "service_definition"
    USER_OBLIGATIONS = "user_obligations"
    COMMERCIAL_TERMS = "commercial_terms"
    LIABILITY_LIMITATIONS = "liability_limitations"
    DISPUTE_RESOLUTION = "dispute_resolution"


class RelationshipType(str, Enum):
    PARTY_TO_PROPERTY = "party_to_property"
    PARTY_TO_FINANCIAL = "party_to_financial"
    CLAUSE_TO_CLAUSE = "clause_to_clause"
    OBLIGATION_TO_RIGHT = "obligation_to_right"
    CONDITION_TO_CONSEQUENCE = "condition_to_consequence"
    COMPLIANCE_TO_PENALTY = "compliance_to_penalty"


# Base Classes
class Address(BaseModel):
    house_number: Optional[str] = None
    street_address: Optional[str] = None
    locality: Optional[str] = None
    city: str
    state: str
    pincode: str
    country: str = "India"


class Person(BaseModel):
    name: str
    father_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    pan_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    address: Address
    contact_details: Optional[Dict[str, str]] = None


class Organization(BaseModel):
    name: str
    registration_number: Optional[str] = None
    incorporation_details: Optional[Dict[str, Any]] = None
    registered_address: Address
    gstin: Optional[str] = None
    cin_number: Optional[str] = None
    contact_information: Optional[Dict[str, str]] = None


# Clause Base Class
class LegalClause(BaseModel):
    clause_id: str
    clause_type: ClauseType
    clause_text: str
    clause_summary: Optional[str] = None
    key_terms: List[str] = []
    obligations: List[str] = []
    rights: List[str] = []
    conditions: List[str] = []
    consequences: List[str] = []
    compliance_requirements: List[str] = []
    source_location: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None


class ClauseRelationship(BaseModel):
    relationship_id: str
    relationship_type: RelationshipType
    source_clause_id: str
    target_clause_id: str
    relationship_description: str
    strength: Optional[float] = None
    conditions: List[str] = []


# Rental Agreement Schemas
class RentalPartyIdentification(LegalClause):
    clause_type: ClauseType = ClauseType.PARTY_IDENTIFICATION
    lessor: Person
    lessee: Person
    witnesses: Optional[List[Person]] = []


class RentalPropertyDescription(LegalClause):
    clause_type: ClauseType = ClauseType.PROPERTY_DESCRIPTION
    property_address: Address
    property_type: str  # residential/commercial/mixed
    accommodation_type: str  # independent_house/apartment/villa/studio
    total_built_area: Optional[float] = None
    carpet_area: Optional[float] = None
    floor_number: Optional[str] = None
    total_floors: Optional[int] = None
    facing_direction: Optional[str] = None
    furnishing_status: str  # furnished/semi_furnished/unfurnished
    amenities_included: List[str] = []
    parking_details: Optional[Dict[str, Any]] = None
    common_area_access: List[str] = []


class RentalFinancialTerms(LegalClause):
    clause_type: ClauseType = ClauseType.FINANCIAL_TERMS
    monthly_rent: float
    rent_in_words: Optional[str] = None
    due_date: int  # Day of month
    payment_method: Optional[str] = None
    late_payment_penalty: Optional[Dict[str, Any]] = None

    security_deposit: float
    advance_rent: Optional[float] = None
    other_deposits: Optional[Dict[str, float]] = None
    refund_conditions: Optional[Dict[str, Any]] = None

    annual_escalation_percentage: Optional[float] = None
    escalation_effective_from_year: Optional[int] = None
    maximum_escalation_limit: Optional[float] = None

    utility_responsibilities: Dict[str, str] = {}  # service -> landlord/tenant/shared
    maintenance_charges: Optional[float] = None


class RentalLeaseDuration(LegalClause):
    clause_type: ClauseType = ClauseType.LEASE_DURATION
    start_date: date
    end_date: date
    total_months: int
    renewable: bool = False
    renewal_terms: Optional[Dict[str, Any]] = None

    lock_in_period_months: Optional[int] = None
    notice_period_days: int = 30

    permitted_use: str = "residential_only"  # residential_only/commercial_only/mixed
    subletting_allowed: bool = False
    guest_policy: Optional[Dict[str, Any]] = None
    pet_policy: Optional[Dict[str, Any]] = None
    modification_rights: Optional[Dict[str, Any]] = None


class RentalMaintenanceResponsibilities(LegalClause):
    clause_type: ClauseType = ClauseType.MAINTENANCE_RESPONSIBILITIES
    major_repairs_responsibility: str  # landlord/tenant
    minor_repairs_responsibility: str  # landlord/tenant
    structural_maintenance: str  # landlord/tenant
    appliance_maintenance: Optional[Dict[str, str]] = None


class RentalTerminationConditions(LegalClause):
    clause_type: ClauseType = ClauseType.TERMINATION_CONDITIONS
    notice_period_days: int
    early_termination_penalty: Optional[Dict[str, Any]] = None
    breach_consequences: List[str] = []
    force_majeure_clauses: List[str] = []


class RentalLegalCompliance(LegalClause):
    clause_type: ClauseType = ClauseType.LEGAL_COMPLIANCE
    registration_required: bool = False
    stamp_duty_value: Optional[float] = None
    stamp_paper_value: Optional[float] = None
    registration_fee: Optional[float] = None
    sub_registrar_office: Optional[str] = None
    document_registration_number: Optional[str] = None
    registration_date: Optional[date] = None

    local_laws_adherence: bool = True
    society_rules_compliance: bool = True
    municipal_permissions: Optional[Dict[str, Any]] = None
    fire_safety_compliance: bool = False

    governing_law: str = "Indian Contract Act, 1872"
    jurisdiction: str = "Local courts"
    arbitration_clause: bool = False


# Loan Agreement Schemas
class LoanPartyIdentification(LegalClause):
    clause_type: ClauseType = ClauseType.PARTY_IDENTIFICATION
    lender: Organization
    borrower: Person
    co_borrowers: Optional[List[Person]] = []
    guarantors: Optional[List[Person]] = []


class LoanSpecifications(LegalClause):
    clause_type: ClauseType = ClauseType.LOAN_SPECIFICATIONS
    loan_agreement_number: str
    loan_type: str  # personal/home/vehicle/business/education/gold
    sanctioned_amount: float
    disbursed_amount: Optional[float] = None
    disbursement_schedule: Optional[List[Dict[str, Any]]] = None
    loan_purpose: str
    end_use_monitoring: bool = False


class LoanInterestStructure(LegalClause):
    clause_type: ClauseType = ClauseType.INTEREST_STRUCTURE
    interest_rate_type: str  # fixed/floating/hybrid
    base_rate: float
    spread_margin: Optional[float] = None
    current_rate: float
    rate_reset_frequency: Optional[str] = None  # monthly/quarterly/annually
    benchmark: Optional[str] = None  # repo_rate/mclr/external_benchmark
    compounding_frequency: str = "monthly"


class LoanRepaymentTerms(LegalClause):
    clause_type: ClauseType = ClauseType.REPAYMENT_TERMS
    repayment_method: str  # emi/bullet/step_up/step_down/seasonal
    loan_tenure_months: int
    emi_amount: float
    repayment_frequency: str = "monthly"
    repayment_start_date: date
    repayment_mode: str = "online"  # ecs/nach/cheque/online

    moratorium_period_months: Optional[int] = None
    prepayment_allowed: bool = True
    prepayment_charges: Optional[Dict[str, Any]] = None
    part_payment_facility: bool = False

    bank_account_details: Optional[Dict[str, str]] = None
    holiday_treatment: Optional[Dict[str, Any]] = None


class LoanSecurityDetails(LegalClause):
    clause_type: ClauseType = ClauseType.SECURITY_DETAILS
    primary_security_type: str  # mortgage/hypothecation/pledge/assignment
    asset_description: Dict[str, Any]
    asset_valuation: float
    valuation_date: Optional[date] = None
    loan_to_value_ratio: float

    collateral_security: Optional[List[Dict[str, Any]]] = []
    guarantees: Optional[Dict[str, List[Dict[str, Any]]]] = None

    insurance_requirements: Optional[Dict[str, Any]] = None


class LoanDefaultProvisions(LegalClause):
    clause_type: ClauseType = ClauseType.DEFAULT_PROVISIONS
    events_of_default: List[str] = [
        "non_payment_of_dues",
        "breach_of_covenants",
        "cross_default",
        "material_adverse_change",
        "insolvency_proceedings"
    ]
    cure_period_days: Optional[int] = None
    acceleration_clause: Optional[Dict[str, Any]] = None
    recovery_mechanisms: Dict[str, Any] = {}
    sarfaesi_applicable: bool = False


class LoanComplianceRequirements(LegalClause):
    clause_type: ClauseType = ClauseType.COMPLIANCE_REQUIREMENTS
    rbi_guidelines_followed: bool = True
    applicable_rbi_guidelines: Optional[str] = None
    tds_applicable: bool = False
    cibil_reporting: bool = True
    financial_reporting_frequency: Optional[str] = None

    borrower_obligations: Dict[str, Any] = {}
    reporting_requirements: Dict[str, Any] = {}
    restrictive_covenants: Dict[str, Any] = {}


# Terms of Service Schemas
class ToSServiceDefinition(LegalClause):
    clause_type: ClauseType = ClauseType.SERVICE_DEFINITION
    service_provider: Organization
    platform_description: Dict[str, Any]
    service_category: str  # digital_platform/mobile_app/web_service/saas/marketplace
    core_functionality: str
    target_user_base: str  # b2c/b2b/b2b2c
    geographic_availability: List[str] = ["India"]
    minimum_age_requirement: int = 18
    kyc_requirements: bool = False


class ToSUserObligations(LegalClause):
    clause_type: ClauseType = ClauseType.USER_OBLIGATIONS
    acceptable_use_policy: Dict[str, Any]
    prohibited_activities: List[str]
    content_guidelines: Optional[Dict[str, Any]] = None
    community_standards: Optional[Dict[str, Any]] = None
    compliance_obligations: Dict[str, Any] = {}


class ToSCommercialTerms(LegalClause):
    clause_type: ClauseType = ClauseType.COMMERCIAL_TERMS
    pricing_structure: Dict[str, Any]
    payment_processing: Dict[str, Any]
    refund_cancellation: Dict[str, Any]
    taxation: Dict[str, Any] = {}


class ToSLiabilityLimitations(LegalClause):
    clause_type: ClauseType = ClauseType.LIABILITY_LIMITATIONS
    limitation_of_liability: Dict[str, Any]
    indemnification: Dict[str, Any]
    insurance_coverage: Optional[Dict[str, Any]] = None


class ToSDisputeResolution(LegalClause):
    clause_type: ClauseType = ClauseType.DISPUTE_RESOLUTION
    grievance_mechanism: Dict[str, Any]
    legal_framework: Dict[str, Any]
    alternative_dispute_resolution: Optional[Dict[str, Any]] = None


# Main Document Schemas
class RentalAgreement(BaseModel):
    document_metadata: Dict[str, Any]
    parties: RentalPartyIdentification
    property_details: RentalPropertyDescription
    financial_terms: RentalFinancialTerms
    lease_terms: RentalLeaseDuration
    maintenance_responsibilities: RentalMaintenanceResponsibilities
    termination_conditions: RentalTerminationConditions
    legal_compliance: RentalLegalCompliance
    extracted_clauses: List[LegalClause] = []
    clause_relationships: List[ClauseRelationship] = []


class LoanAgreement(BaseModel):
    loan_metadata: Dict[str, Any]
    parties: LoanPartyIdentification
    loan_terms: LoanSpecifications
    interest_structure: LoanInterestStructure
    repayment_terms: LoanRepaymentTerms
    security_details: LoanSecurityDetails
    default_provisions: LoanDefaultProvisions
    compliance_requirements: LoanComplianceRequirements
    extracted_clauses: List[LegalClause] = []
    clause_relationships: List[ClauseRelationship] = []


class TermsOfService(BaseModel):
    tos_metadata: Dict[str, Any]
    service_definition: ToSServiceDefinition
    user_obligations: ToSUserObligations
    commercial_terms: ToSCommercialTerms
    liability_limitations: ToSLiabilityLimitations
    dispute_resolution: ToSDisputeResolution
    extracted_clauses: List[LegalClause] = []
    clause_relationships: List[ClauseRelationship] = []


# Unified Document Schema
class LegalDocument(BaseModel):
    document_id: str
    document_type: DocumentType
    original_text: str
    extracted_data: Union[RentalAgreement, LoanAgreement, TermsOfService]
    processing_metadata: Dict[str, Any] = {}
    extraction_confidence: float = 0.0
    source_grounding: Dict[str, Any] = {}


# Extraction Result
class ExtractionResult(BaseModel):
    document_id: str
    document_type: DocumentType
    extracted_clauses: List[LegalClause]
    clause_relationships: List[ClauseRelationship]
    confidence_score: float
    processing_time_seconds: float
    extraction_metadata: Dict[str, Any] = {}
