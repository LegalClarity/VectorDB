"""
Loan Agreement Schema for Indian Legal Documents
Based on Indian Contract Act, 1872 and RBI guidelines for lending
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal


class LenderDetails(BaseModel):
    """Details of the lending institution/individual"""

    institution_name: str = Field(..., description="Name of lending institution")
    institution_type: str = Field(..., description="Bank/NBFC/Housing Finance/Cooperative")
    license_number: Optional[str] = Field(None, description="RBI license/registration number")
    registered_office: Dict[str, Any] = Field(..., description="Registered office address")
    authorized_signatory: Optional[Dict[str, Any]] = Field(None, description="Details of authorized signatory")
    branch_details: Optional[Dict[str, Any]] = Field(None, description="Branch office details")


class BorrowerDetails(BaseModel):
    """Primary borrower information"""

    name: str = Field(..., description="Full legal name of borrower")
    father_name: Optional[str] = Field(None, description="Father's name")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    pan_number: Optional[str] = Field(None, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", description="PAN number")
    aadhaar_number: Optional[str] = Field(None, pattern=r"^\d{12}$", description="Aadhaar number")
    address: Dict[str, Any] = Field(..., description="Complete residential address")
    occupation: str = Field(..., description="Occupation/profession")
    annual_income: Decimal = Field(..., ge=0, description="Annual income in INR")
    employment_details: Optional[Dict[str, Any]] = Field(None, description="Employment information")
    credit_score: Optional[int] = Field(None, ge=300, le=900, description="CIBIL credit score")
    existing_obligations: List[Dict[str, Any]] = Field(default_factory=list, description="Existing loan obligations")


class CoBorrowerDetails(BaseModel):
    """Co-borrower information"""

    name: str = Field(..., description="Full legal name")
    relationship: str = Field(..., description="Relationship to primary borrower")
    pan_number: Optional[str] = Field(None, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", description="PAN number")
    annual_income: Optional[Decimal] = Field(None, ge=0, description="Annual income in INR")
    contact_details: Optional[Dict[str, Any]] = Field(None, description="Contact information")


class GuarantorDetails(BaseModel):
    """Guarantor information"""

    name: str = Field(..., description="Full legal name")
    relationship: str = Field(..., description="Relationship to borrower")
    pan_number: Optional[str] = Field(None, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", description="PAN number")
    annual_income: Optional[Decimal] = Field(None, ge=0, description="Annual income in INR")
    net_worth: Optional[Decimal] = Field(None, ge=0, description="Net worth in INR")
    contact_details: Optional[Dict[str, Any]] = Field(None, description="Contact information")
    guarantee_type: str = Field(..., description="Personal/Corporate guarantee")


class PrincipalDetails(BaseModel):
    """Loan principal and disbursement information"""

    sanctioned_amount: Decimal = Field(..., ge=0, description="Sanctioned loan amount in INR")
    disbursement_schedule: List[Dict[str, Any]] = Field(default_factory=list, description="Disbursement schedule")
    loan_purpose: str = Field(..., description="Purpose of the loan")
    end_use_monitoring: bool = Field(False, description="Whether end use will be monitored")


class InterestStructure(BaseModel):
    """Interest rate and calculation structure"""

    interest_rate_type: str = Field(..., description="Fixed/Floating/Hybrid")
    base_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="Base interest rate percentage")
    spread_margin: Optional[Decimal] = Field(None, ge=0, le=100, description="Spread over base rate")
    current_rate: Decimal = Field(..., ge=0, le=100, description="Current applicable rate")
    rate_reset_frequency: Optional[str] = Field(None, description="Monthly/Quarterly/Annually")
    benchmark: Optional[str] = Field(None, description="Repo rate/MCLR/External benchmark")
    compounding_frequency: str = Field(..., description="Monthly/Quarterly/Annually")

    @validator('current_rate')
    def validate_interest_rate(cls, v):
        """Validate interest rate is within reasonable bounds"""
        if v > 50:  # Extremely high interest rate
            raise ValueError("Interest rate seems unreasonably high")
        return v


class TenureDetails(BaseModel):
    """Loan tenure and repayment structure"""

    loan_tenure_months: int = Field(..., ge=1, le=360, description="Loan tenure in months")
    moratorium_period: Optional[int] = Field(None, ge=0, description="Moratorium period in months")
    prepayment_allowed: bool = Field(True, description="Whether prepayment is allowed")
    prepayment_charges: Optional[Dict[str, Any]] = Field(None, description="Prepayment penalty structure")
    part_payment_facility: bool = Field(False, description="Part payment facility available")


class RepaymentStructure(BaseModel):
    """Repayment terms and schedule"""

    repayment_method: str = Field(..., description="EMI/Bullet/Step-up/Step-down/Seasonal")
    emi_amount: Decimal = Field(..., ge=0, description="Equated Monthly Installment amount")
    repayment_frequency: str = Field(..., description="Monthly/Quarterly/Annually")
    repayment_start_date: date = Field(..., description="First EMI due date")
    repayment_mode: str = Field(..., description="ECS/NACH/Cheque/Online")
    bank_account_details: Optional[Dict[str, Any]] = Field(None, description="Repayment account details")
    holiday_treatment: Optional[Dict[str, Any]] = Field(None, description="Holiday payment treatment")


class ProcessingFees(BaseModel):
    """Loan processing and documentation charges"""

    processing_fee: Optional[Decimal] = Field(None, ge=0, description="Processing fee amount")
    documentation_charges: Optional[Decimal] = Field(None, ge=0, description="Documentation charges")
    valuation_charges: Optional[Decimal] = Field(None, ge=0, description="Property valuation charges")
    legal_charges: Optional[Decimal] = Field(None, ge=0, description="Legal documentation charges")
    stamp_duty: Optional[Decimal] = Field(None, ge=0, description="Stamp duty amount")
    insurance_premiums: Optional[Dict[str, Any]] = Field(None, description="Insurance premium details")


class PenalCharges(BaseModel):
    """Penalty charges and default provisions"""

    overdue_interest_rate: Decimal = Field(..., ge=0, le=100, description="Overdue interest rate percentage")
    bounce_charges: Optional[Decimal] = Field(None, ge=0, description="Cheque/ECS bounce charges")
    late_payment_penalty: Optional[Dict[str, Any]] = Field(None, description="Late payment penalty structure")


class PrimarySecurity(BaseModel):
    """Primary security/collateral details"""

    security_type: str = Field(..., description="Mortgage/Hypothecation/Pledge/Assignment")
    asset_description: Dict[str, Any] = Field(..., description="Detailed asset description")
    asset_valuation: Optional[Decimal] = Field(None, ge=0, description="Asset valuation amount")
    valuation_date: Optional[date] = Field(None, description="Valuation date")
    loan_to_value_ratio: Optional[Decimal] = Field(None, ge=0, le=100, description="LTV ratio percentage")
    insurance_requirements: Optional[Dict[str, Any]] = Field(None, description="Insurance requirements")


class CollateralSecurity(BaseModel):
    """Additional collateral security"""

    security_type: str = Field(..., description="Type of collateral security")
    asset_description: Dict[str, Any] = Field(..., description="Collateral asset description")
    asset_valuation: Optional[Decimal] = Field(None, ge=0, description="Collateral valuation")
    priority_ranking: Optional[str] = Field(None, description="Security interest ranking")


class PersonalGuarantees(BaseModel):
    """Personal guarantee details"""

    guarantor_name: str = Field(..., description="Name of personal guarantor")
    relationship: str = Field(..., description="Relationship to borrower")
    net_worth: Optional[Decimal] = Field(None, ge=0, description="Guarantor's net worth")
    guarantee_coverage: Optional[Decimal] = Field(None, ge=0, description="Guarantee coverage amount")


class CorporateGuarantees(BaseModel):
    """Corporate guarantee details"""

    company_name: str = Field(..., description="Name of guaranteeing company")
    cin_number: Optional[str] = Field(None, description="Corporate Identification Number")
    authorized_signatory: Dict[str, Any] = Field(..., description="Authorized signatory details")
    guarantee_coverage: Optional[Decimal] = Field(None, ge=0, description="Corporate guarantee amount")


class BankGuarantees(BaseModel):
    """Bank guarantee details"""

    bank_name: str = Field(..., description="Issuing bank name")
    guarantee_amount: Decimal = Field(..., ge=0, description="Guarantee amount")
    validity_period: str = Field(..., description="Guarantee validity period")
    guarantee_number: Optional[str] = Field(None, description="Guarantee reference number")


class BorrowerObligations(BaseModel):
    """Borrower's financial obligations and covenants"""

    minimum_turnover: Optional[Decimal] = Field(None, ge=0, description="Minimum turnover requirement")
    debt_service_coverage_ratio: Optional[Decimal] = Field(None, ge=0, description="DSCR requirement")
    current_ratio_minimum: Optional[Decimal] = Field(None, ge=0, description="Minimum current ratio")
    debt_equity_ratio_maximum: Optional[Decimal] = Field(None, ge=0, description="Maximum debt-equity ratio")
    tangible_net_worth_minimum: Optional[Decimal] = Field(None, ge=0, description="Minimum tangible net worth")


class ReportingRequirements(BaseModel):
    """Financial reporting and compliance requirements"""

    financial_statements_frequency: str = Field(..., description="Monthly/Quarterly/Annually")
    audit_requirements: bool = Field(False, description="Whether audit is required")
    compliance_certificates: List[str] = Field(default_factory=list, description="Required compliance certificates")
    stock_statements: bool = Field(False, description="Stock statement requirements")


class RestrictiveCovenants(BaseModel):
    """Restrictive covenants and conditions"""

    additional_borrowing_restrictions: Optional[str] = Field(None, description="Additional borrowing restrictions")
    asset_disposal_restrictions: Optional[str] = Field(None, description="Asset disposal restrictions")
    change_in_management_restrictions: Optional[str] = Field(None, description="Management change restrictions")
    dividend_payment_restrictions: Optional[str] = Field(None, description="Dividend payment restrictions")


class EventsOfDefault(BaseModel):
    """Events that constitute default under the agreement"""

    non_payment_of_dues: bool = Field(True, description="Non-payment of dues")
    breach_of_covenants: bool = Field(True, description="Breach of financial covenants")
    cross_default: bool = Field(True, description="Cross-default provisions")
    material_adverse_change: bool = Field(False, description="Material adverse change clause")
    insolvency_proceedings: bool = Field(True, description="Insolvency proceedings")


class RecoveryMechanisms(BaseModel):
    """Recovery and enforcement mechanisms"""

    sarfaesi_applicable: bool = Field(True, description="Whether SARFAESI Act applies")
    arbitration_clause: bool = Field(False, description="Presence of arbitration clause")
    jurisdiction: str = Field(..., description="Applicable court jurisdiction")
    asset_reconstruction: bool = Field(False, description="Asset reconstruction provisions")


class LoanAgreementSchema(BaseModel):
    """
    Comprehensive schema for Indian loan agreements
    Based on RBI guidelines, SARFAESI Act, and banking regulations
    """

    # Document Metadata
    loan_metadata: Dict[str, Any] = Field(..., description="Loan agreement metadata")
    loan_agreement_number: str = Field(..., description="Unique loan agreement number")
    loan_type: str = Field(..., description="Personal/Home/Vehicle/Business/Education/Gold")
    lending_institution: Dict[str, Any] = Field(..., description="Lending institution details")
    sanction_letter_reference: Optional[str] = Field(None, description="Sanction letter reference")
    agreement_date: date = Field(..., description="Agreement execution date")
    execution_location: str = Field(..., description="Place of execution")
    applicable_rbi_guidelines: str = Field(..., description="Applicable RBI guidelines version")

    # Parties Information
    borrower_details: BorrowerDetails = Field(..., description="Primary borrower details")
    co_borrowers: List[CoBorrowerDetails] = Field(default_factory=list, description="Co-borrower details")
    guarantors: List[GuarantorDetails] = Field(default_factory=list, description="Guarantor details")

    # Lender Information
    lender_details: LenderDetails = Field(..., description="Lending institution details")

    # Loan Terms
    loan_terms: Dict[str, Any] = Field(..., description="Principal, interest, and tenure details")
    principal_details: PrincipalDetails = Field(..., description="Loan principal details")
    interest_structure: InterestStructure = Field(..., description="Interest rate structure")
    tenure_details: TenureDetails = Field(..., description="Loan tenure details")

    # Repayment Terms
    repayment_structure: RepaymentStructure = Field(..., description="Repayment terms and schedule")

    # Charges and Fees
    charges_and_fees: Dict[str, Any] = Field(..., description="All applicable charges and fees")
    processing_fees: Optional[ProcessingFees] = Field(None, description="Processing and documentation fees")
    penal_charges: PenalCharges = Field(..., description="Penalty charges structure")

    # Security Details
    security_details: Dict[str, Any] = Field(..., description="Security and collateral details")
    primary_security: Optional[PrimarySecurity] = Field(None, description="Primary security details")
    collateral_security: List[CollateralSecurity] = Field(default_factory=list, description="Additional collateral")
    guarantees: Dict[str, Any] = Field(default_factory=dict, description="Guarantee details")
    personal_guarantees: List[PersonalGuarantees] = Field(default_factory=list, description="Personal guarantees")
    corporate_guarantees: List[CorporateGuarantees] = Field(default_factory=list, description="Corporate guarantees")
    bank_guarantees: List[BankGuarantees] = Field(default_factory=list, description="Bank guarantees")

    # Financial Covenants
    financial_covenants: Dict[str, Any] = Field(..., description="Financial covenants and restrictions")
    borrower_obligations: BorrowerObligations = Field(..., description="Borrower's financial obligations")
    reporting_requirements: ReportingRequirements = Field(..., description="Reporting and compliance requirements")
    restrictive_covenants: RestrictiveCovenants = Field(..., description="Restrictive covenants")

    # Default and Recovery
    default_and_recovery: Dict[str, Any] = Field(..., description="Default events and recovery mechanisms")
    events_of_default: EventsOfDefault = Field(..., description="Events constituting default")
    cure_period: int = Field(..., ge=0, description="Cure period in days")
    acceleration_clause: Optional[str] = Field(None, description="Acceleration clause details")
    recovery_mechanisms: RecoveryMechanisms = Field(..., description="Recovery and enforcement mechanisms")

    model_config = {
        "json_encoders": {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }
            "example": {
                "loan_metadata": {
                    "document_type": "loan_agreement",
                    "title": "Home Loan Agreement"
                },
                "loan_agreement_number": "HL/2024/001234",
                "loan_type": "home",
                "lending_institution": {
                    "name": "HDFC Bank Limited",
                    "type": "bank",
                    "license_number": "RBI License No. XYZ"
                },
                "agreement_date": "2024-01-15",
                "execution_location": "Mumbai, Maharashtra",
                "applicable_rbi_guidelines": "RBI Master Directions 2023",
                "borrower_details": {
                    "name": "Amit Kumar Singh",
                    "father_name": "Rajesh Kumar Singh",
                    "pan_number": "ABCDE1234F",
                    "annual_income": 1200000.0,
                    "occupation": "Software Engineer",
                    "credit_score": 750
                },
                "lender_details": {
                    "institution_name": "HDFC Bank Limited",
                    "institution_type": "bank",
                    "registered_office": {
                        "street_address": "HDFC Bank House, Senapati Bapat Marg",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400013"
                    }
                },
                "principal_details": {
                    "sanctioned_amount": 5000000.0,
                    "loan_purpose": "Purchase of residential property"
                },
                "interest_structure": {
                    "interest_rate_type": "floating",
                    "base_rate": 6.5,
                    "spread_margin": 0.5,
                    "current_rate": 7.0,
                    "benchmark": "repo_rate",
                    "compounding_frequency": "monthly"
                },
                "tenure_details": {
                    "loan_tenure_months": 240,
                    "prepayment_allowed": True
                },
                "repayment_structure": {
                    "repayment_method": "emi",
                    "emi_amount": 33245.0,
                    "repayment_frequency": "monthly",
                    "repayment_start_date": "2024-03-01",
                    "repayment_mode": "ecs"
                },
                "penal_charges": {
                    "overdue_interest_rate": 2.0,
                    "bounce_charges": 500.0
                },
                "primary_security": {
                    "security_type": "mortgage",
                    "asset_description": {
                        "property_address": "A-101, Sunshine Apartments, Andheri West, Mumbai",
                        "property_value": 7000000.0
                    },
                    "loan_to_value_ratio": 71.4
                },
                "borrower_obligations": {
                    "debt_service_coverage_ratio": 1.5,
                    "debt_equity_ratio_maximum": 4.0
                },
                "reporting_requirements": {
                    "financial_statements_frequency": "annually",
                    "audit_requirements": True
                },
                "events_of_default": {
                    "non_payment_of_dues": True,
                    "breach_of_covenants": True,
                    "cross_default": True,
                    "insolvency_proceedings": True
                },
                "recovery_mechanisms": {
                    "sarfaesi_applicable": True,
                    "jurisdiction": "Mumbai",
                    "arbitration_clause": False
                }
            }
        }
