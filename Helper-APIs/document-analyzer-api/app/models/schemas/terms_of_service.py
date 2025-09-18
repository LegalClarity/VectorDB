"""
Terms of Service Schema for Indian Legal Documents
Based on Information Technology Act, 2000 and Consumer Protection Act, 2019
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal


class ServiceProvider(BaseModel):
    """Service provider company details"""

    company_name: str = Field(..., description="Legal name of the service provider")
    incorporation_details: Optional[Dict[str, Any]] = Field(None, description="Incorporation details")
    registered_address: Dict[str, Any] = Field(..., description="Registered office address")
    cin_number: Optional[str] = Field(None, description="Corporate Identification Number")
    gstin: Optional[str] = Field(None, pattern=r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}\d{1}[A-Z]{1}\d{1}$", description="GST Identification Number")
    contact_information: Optional[Dict[str, Any]] = Field(None, description="Contact details")


class DocumentDetails(BaseModel):
    """Document versioning and jurisdiction details"""

    version_number: str = Field(..., description="Document version number")
    effective_date: date = Field(..., description="Date when terms become effective")
    last_updated: date = Field(..., description="Last update date")
    supersedes_version: Optional[str] = Field(None, description="Previous version superseded")
    applicable_jurisdiction: str = Field("india", description="Applicable jurisdiction")
    governing_state_laws: str = Field(..., description="Governing state laws")


class PlatformDescription(BaseModel):
    """Platform and service description"""

    service_category: str = Field(..., description="Digital platform/Mobile app/Web service/SaaS/Marketplace")
    core_functionality: str = Field(..., description="Primary service functions")
    target_user_base: str = Field(..., description="B2C/B2B/B2B2C")
    geographic_availability: List[str] = Field(..., description="Countries/regions where service is available")
    minimum_age_requirement: int = Field(..., ge=13, le=21, description="Minimum user age")
    kyc_requirements: bool = Field(False, description="Whether KYC is required")


class UserEligibility(BaseModel):
    """User eligibility criteria"""

    citizenship_requirements: str = Field(..., description="Indian residents/Global/Specific countries")
    age_restrictions: Optional[Dict[str, Any]] = Field(None, description="Age-based restrictions")
    professional_requirements: Optional[Dict[str, Any]] = Field(None, description="Professional eligibility criteria")
    verification_process: Optional[str] = Field(None, description="User verification process")
    prohibited_users: List[str] = Field(default_factory=list, description="Categories of prohibited users")


class AccountManagement(BaseModel):
    """Account creation and management terms"""

    registration_process: Optional[str] = Field(None, description="Account registration process")
    verification_requirements: Optional[str] = Field(None, description="Account verification requirements")
    account_types: List[str] = Field(..., description="Available account types")
    suspension_grounds: List[str] = Field(default_factory=list, description="Grounds for account suspension")
    data_retention_post_closure: Optional[str] = Field(None, description="Data retention after account closure")


class UserRights(BaseModel):
    """User rights and entitlements"""

    service_access_rights: Optional[str] = Field(None, description="Rights to access services")
    data_portability: bool = Field(False, description="Data portability rights")
    grievance_redressal: Optional[str] = Field(None, description="Grievance redressal mechanism")
    privacy_controls: Optional[str] = Field(None, description="Privacy control options")
    content_ownership: Optional[str] = Field(None, description="User content ownership rights")


class AcceptableUsePolicy(BaseModel):
    """Acceptable use policy and restrictions"""

    permitted_activities: List[str] = Field(..., description="Permitted user activities")
    prohibited_activities: List[str] = Field(..., description="Prohibited activities")
    content_guidelines: Optional[str] = Field(None, description="Content posting guidelines")
    community_standards: Optional[str] = Field(None, description="Community standards")


class ComplianceObligations(BaseModel):
    """Legal and regulatory compliance obligations"""

    indian_law_compliance: bool = Field(True, description="Compliance with Indian laws")
    tax_obligations: Optional[Dict[str, Any]] = Field(None, description="Tax compliance requirements")
    regulatory_reporting: Optional[str] = Field(None, description="Regulatory reporting obligations")
    data_localization: bool = Field(False, description="Data localization requirements")


class PricingStructure(BaseModel):
    """Service pricing and billing structure"""

    pricing_model: str = Field(..., description="Free/Freemium/Subscription/Transaction-based/Usage-based")
    base_charges: Optional[Decimal] = Field(None, ge=0, description="Base pricing amount")
    variable_charges: Optional[Dict[str, Any]] = Field(None, description="Variable pricing components")
    currency: str = Field("INR", description="Billing currency")
    billing_cycle: str = Field(..., description="Monthly/Quarterly/Annually/Per transaction")
    price_change_policy: Optional[str] = Field(None, description="Price change notification policy")


class PaymentProcessing(BaseModel):
    """Payment processing and security"""

    accepted_payment_methods: List[str] = Field(..., description="Accepted payment methods")
    payment_gateway_partners: List[str] = Field(default_factory=list, description="Payment gateway partners")
    auto_debit_authorization: bool = Field(False, description="Auto-debit facility")
    payment_security_standards: Optional[str] = Field(None, description="PCI DSS/ISO 27001 compliance")
    transaction_limits: Optional[Dict[str, Any]] = Field(None, description="Transaction limits")


class RefundCancellation(BaseModel):
    """Refund and cancellation policies"""

    refund_policy: Optional[str] = Field(None, description="Refund policy details")
    cancellation_process: Optional[str] = Field(None, description="Account cancellation process")
    cooling_off_period: Optional[int] = Field(None, ge=0, description="Cooling off period in days")
    pro_rata_adjustments: bool = Field(False, description="Pro-rata refund calculations")
    dispute_resolution_timeline: Optional[int] = Field(None, ge=0, description="Dispute resolution timeline")


class Taxation(BaseModel):
    """Taxation and GST implications"""

    gst_applicability: bool = Field(True, description="GST applicability")
    tds_implications: Optional[Dict[str, Any]] = Field(None, description="TDS implications")
    foreign_exchange_compliance: Optional[Dict[str, Any]] = Field(None, description="Foreign exchange compliance")
    tax_invoice_generation: bool = Field(False, description="Automatic tax invoice generation")


class ServiceAvailability(BaseModel):
    """Service availability and uptime commitments"""

    uptime_commitment: Optional[Decimal] = Field(None, ge=0, le=100, description="Uptime percentage commitment")
    scheduled_maintenance: Optional[str] = Field(None, description="Scheduled maintenance policy")
    force_majeure_events: List[str] = Field(default_factory=list, description="Force majeure events")
    service_discontinuation_notice: Optional[int] = Field(None, ge=0, description="Advance notice for discontinuation")


class ContentModeration(BaseModel):
    """Content moderation and safety policies"""

    moderation_policy: Optional[str] = Field(None, description="Content moderation policy")
    automated_filtering: bool = Field(False, description="Automated content filtering")
    human_review_process: Optional[str] = Field(None, description="Human review process")
    appeal_mechanism: Optional[str] = Field(None, description="Content appeal mechanism")
    transparency_reporting: bool = Field(False, description="Moderation transparency reporting")


class IntellectualProperty(BaseModel):
    """Intellectual property rights and licensing"""

    platform_ip_ownership: Optional[str] = Field(None, description="Platform IP ownership")
    user_content_licensing: Optional[str] = Field(None, description="User content licensing terms")
    dmca_compliance: bool = Field(False, description="DMCA compliance")
    trademark_policy: Optional[str] = Field(None, description="Trademark usage policy")
    third_party_ip_respect: Optional[str] = Field(None, description="Third-party IP respect")


class LimitationOfLiability(BaseModel):
    """Limitation of liability clauses"""

    liability_cap: str = Field(..., description="Unlimited/Revenue-based/Fixed amount")
    excluded_damages: List[str] = Field(default_factory=list, description="Types of excluded damages")
    force_majeure_protection: Optional[str] = Field(None, description="Force majeure protection")
    third_party_claims: Optional[str] = Field(None, description="Third-party claims protection")


class Indemnification(BaseModel):
    """Indemnification obligations"""

    user_indemnification_obligations: Optional[str] = Field(None, description="User indemnification obligations")
    platform_indemnification_scope: Optional[str] = Field(None, description="Platform indemnification scope")
    defense_obligations: Optional[str] = Field(None, description="Defense obligations")
    settlement_authority: Optional[str] = Field(None, description="Settlement authority")


class InsuranceCoverage(BaseModel):
    """Insurance coverage details"""

    professional_indemnity: bool = Field(False, description="Professional indemnity insurance")
    cyber_liability: bool = Field(False, description="Cyber liability insurance")
    coverage_amounts: Optional[Dict[str, Any]] = Field(None, description="Coverage amounts")


class DataCollection(BaseModel):
    """Data collection practices"""

    personal_data_categories: List[str] = Field(..., description="Categories of personal data collected")
    collection_methods: List[str] = Field(..., description="Methods of data collection")
    legal_basis: str = Field(..., description="Consent/Contract/Legitimate interest/Legal obligation")
    third_party_data_sources: List[str] = Field(default_factory=list, description="Third-party data sources")


class DataProcessing(BaseModel):
    """Data processing and usage"""

    processing_purposes: List[str] = Field(..., description="Purposes for data processing")
    data_sharing_practices: Optional[str] = Field(None, description="Data sharing practices")
    cross_border_transfers: Optional[str] = Field(None, description="Cross-border data transfer policies")
    retention_periods: Optional[str] = Field(None, description="Data retention periods")
    automated_decision_making: bool = Field(False, description="Automated decision making")


class UserControls(BaseModel):
    """User data control options"""

    access_rights: bool = Field(False, description="Data access rights")
    correction_rights: bool = Field(False, description="Data correction rights")
    deletion_rights: bool = Field(False, description="Data deletion rights")
    portability_rights: bool = Field(False, description="Data portability rights")
    consent_withdrawal: bool = Field(False, description="Consent withdrawal rights")


class GrievanceMechanism(BaseModel):
    """Grievance redressal mechanism"""

    internal_complaint_process: Optional[str] = Field(None, description="Internal complaint process")
    response_timeline: int = Field(..., ge=1, description="Response timeline in days")
    escalation_matrix: Optional[str] = Field(None, description="Complaint escalation matrix")
    grievance_officer_details: Optional[str] = Field(None, description="Grievance officer contact details")


class LegalFramework(BaseModel):
    """Legal framework and governing law"""

    governing_law: str = Field("indian_law", description="Governing law")
    jurisdiction: str = Field(..., description="Applicable jurisdiction")
    arbitration_clause: Dict[str, Any] = Field(..., description="Arbitration clause details")
    class_action_waiver: bool = Field(False, description="Class action waiver")


class AlternativeDisputeResolution(BaseModel):
    """Alternative dispute resolution mechanisms"""

    mediation_preference: bool = Field(False, description="Preference for mediation")
    online_dispute_resolution: bool = Field(False, description="Online dispute resolution")
    sector_specific_ombudsman: Optional[str] = Field(None, description="Sector-specific ombudsman")


class TermsOfServiceSchema(BaseModel):
    """
    Comprehensive schema for Indian Terms of Service agreements
    Based on Information Technology Act, 2000 and Consumer Protection Act, 2019
    """

    # Document Metadata
    tos_metadata: Dict[str, Any] = Field(..., description="Terms of Service metadata")

    # Service Provider Details
    service_provider: ServiceProvider = Field(..., description="Service provider company details")

    # Document Details
    document_details: DocumentDetails = Field(..., description="Document versioning and jurisdiction")

    # Service Definition
    service_definition: Dict[str, Any] = Field(..., description="Service definition and scope")
    platform_description: PlatformDescription = Field(..., description="Platform and service description")
    user_eligibility: UserEligibility = Field(..., description="User eligibility criteria")
    account_management: AccountManagement = Field(..., description="Account management terms")

    # User Rights and Obligations
    user_rights_obligations: Dict[str, Any] = Field(..., description="User rights and obligations")
    user_rights: UserRights = Field(..., description="User rights and entitlements")
    acceptable_use_policy: AcceptableUsePolicy = Field(..., description="Acceptable use policy")
    compliance_obligations: ComplianceObligations = Field(..., description="Legal compliance obligations")

    # Commercial Terms
    commercial_terms: Dict[str, Any] = Field(..., description="Commercial and pricing terms")
    pricing_structure: PricingStructure = Field(..., description="Pricing and billing structure")
    payment_processing: PaymentProcessing = Field(..., description="Payment processing details")
    refund_cancellation: RefundCancellation = Field(..., description="Refund and cancellation policies")
    taxation: Taxation = Field(..., description="Taxation and GST details")

    # Platform Governance
    platform_governance: Dict[str, Any] = Field(..., description="Platform governance and operations")
    service_availability: ServiceAvailability = Field(..., description="Service availability commitments")
    content_moderation: ContentModeration = Field(..., description="Content moderation policies")
    intellectual_property: IntellectualProperty = Field(..., description="Intellectual property terms")

    # Liability and Indemnification
    liability_indemnification: Dict[str, Any] = Field(..., description="Liability and indemnification terms")
    limitation_of_liability: LimitationOfLiability = Field(..., description="Limitation of liability")
    indemnification: Indemnification = Field(..., description="Indemnification obligations")
    insurance_coverage: InsuranceCoverage = Field(..., description="Insurance coverage details")

    # Data Privacy
    data_privacy: Dict[str, Any] = Field(..., description="Data privacy and protection")
    data_collection: DataCollection = Field(..., description="Data collection practices")
    data_processing: DataProcessing = Field(..., description="Data processing practices")
    user_controls: UserControls = Field(..., description="User data controls")

    # Dispute Resolution
    dispute_resolution: Dict[str, Any] = Field(..., description="Dispute resolution mechanisms")
    grievance_mechanism: GrievanceMechanism = Field(..., description="Grievance redressal mechanism")
    legal_framework: LegalFramework = Field(..., description="Legal framework and jurisdiction")
    alternative_dispute_resolution: AlternativeDisputeResolution = Field(..., description="Alternative dispute resolution")

    model_config = {
        "json_encoders": {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }
    }
        schema_extra = {
            "example": {
                "tos_metadata": {
                    "document_type": "terms_of_service",
                    "title": "Terms of Service - TechCorp Platform"
                },
                "service_provider": {
                    "company_name": "TechCorp Services Private Limited",
                    "registered_address": {
                        "street_address": "123 Business Park, Whitefield",
                        "city": "Bangalore",
                        "state": "Karnataka",
                        "pincode": "560066"
                    },
                    "cin_number": "U72900KA2020PTC123456",
                    "gstin": "29ABCDE1234F1Z5"
                },
                "document_details": {
                    "version_number": "2.1",
                    "effective_date": "2024-01-01",
                    "last_updated": "2024-01-01",
                    "applicable_jurisdiction": "india",
                    "governing_state_laws": "Karnataka"
                },
                "platform_description": {
                    "service_category": "saas",
                    "core_functionality": "Cloud-based project management platform",
                    "target_user_base": "b2b",
                    "geographic_availability": ["India", "Singapore", "UAE"],
                    "minimum_age_requirement": 18
                },
                "user_eligibility": {
                    "citizenship_requirements": "indian_residents",
                    "prohibited_users": ["competitors", "minors"]
                },
                "account_management": {
                    "account_types": ["free", "premium", "enterprise"],
                    "suspension_grounds": ["policy_violation", "non_payment"]
                },
                "user_rights": {
                    "service_access_rights": "24/7 access to platform features",
                    "data_portability": True,
                    "grievance_redressal": "Email support within 48 hours"
                },
                "acceptable_use_policy": {
                    "permitted_activities": ["business_collaboration", "project_management"],
                    "prohibited_activities": ["illegal_content", "spam_activities", "copyright_infringement"]
                },
                "compliance_obligations": {
                    "indian_law_compliance": True,
                    "tax_obligations": {"gst_compliance": True},
                    "data_localization": True
                },
                "pricing_structure": {
                    "pricing_model": "subscription",
                    "base_charges": 999.0,
                    "billing_cycle": "monthly",
                    "currency": "INR"
                },
                "payment_processing": {
                    "accepted_payment_methods": ["credit_card", "net_banking", "upi"],
                    "payment_gateway_partners": ["Razorpay", "PayU"],
                    "payment_security_standards": "pci_dss"
                },
                "refund_cancellation": {
                    "cooling_off_period": 7,
                    "pro_rata_adjustments": True
                },
                "taxation": {
                    "gst_applicability": True,
                    "tax_invoice_generation": True
                },
                "service_availability": {
                    "uptime_commitment": 99.9,
                    "scheduled_maintenance": "Sunday 2-4 AM IST"
                },
                "content_moderation": {
                    "automated_filtering": True,
                    "human_review_process": "For reported content"
                },
                "limitation_of_liability": {
                    "liability_cap": "revenue_based",
                    "excluded_damages": ["consequential_damages", "lost_profits"]
                },
                "data_collection": {
                    "personal_data_categories": ["name", "email", "company_details"],
                    "legal_basis": "consent",
                    "collection_methods": ["user_input", "cookies"]
                },
                "data_processing": {
                    "processing_purposes": ["service_provision", "analytics", "communication"],
                    "retention_periods": "Account active + 2 years"
                },
                "user_controls": {
                    "access_rights": True,
                    "deletion_rights": True,
                    "consent_withdrawal": True
                },
                "grievance_mechanism": {
                    "response_timeline": 3,
                    "escalation_matrix": "L1 -> L2 -> L3 support"
                },
                "legal_framework": {
                    "governing_law": "indian_law",
                    "jurisdiction": "Bangalore Civil Court",
                    "arbitration_clause": {
                        "arbitration_mandatory": True,
                        "arbitration_seat": "Bangalore",
                        "arbitration_rules": "Indian Arbitration Act"
                    }
                }
            }
        }
