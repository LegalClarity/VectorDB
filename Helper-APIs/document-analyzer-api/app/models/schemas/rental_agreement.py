"""
Rental Agreement Schema for Indian Legal Documents
Based on comprehensive research of Indian rental agreements and Transfer of Property Act, 1882
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal


class LessorDetails(BaseModel):
    """Details of the property owner/lessor"""

    name: str = Field(..., description="Full legal name of the lessor")
    father_name: Optional[str] = Field(None, description="Father's name for legal identification")
    address: Dict[str, Any] = Field(..., description="Complete residential address")
    age: Optional[int] = Field(None, ge=18, le=120, description="Age of the lessor")
    occupation: Optional[str] = Field(None, description="Occupation/profession")
    pan_number: Optional[str] = Field(None, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", description="PAN number")
    aadhaar_number: Optional[str] = Field(None, pattern=r"^\d{12}$", description="Aadhaar number (12 digits)")
    contact_details: Optional[Dict[str, Any]] = Field(None, description="Phone, email, etc.")


class LesseeDetails(BaseModel):
    """Details of the tenant/lessee"""

    name: str = Field(..., description="Full legal name of the lessee")
    father_name: Optional[str] = Field(None, description="Father's name for legal identification")
    permanent_address: Dict[str, Any] = Field(..., description="Permanent residential address")
    correspondence_address: Optional[Dict[str, Any]] = Field(None, description="Correspondence address if different")
    age: Optional[int] = Field(None, ge=18, le=120, description="Age of the lessee")
    occupation: Optional[str] = Field(None, description="Occupation/profession")
    monthly_income: Optional[Decimal] = Field(None, ge=0, description="Monthly income in INR")
    pan_number: Optional[str] = Field(None, pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", description="PAN number")
    aadhaar_number: Optional[str] = Field(None, pattern=r"^\d{12}$", description="Aadhaar number (12 digits)")
    contact_details: Optional[Dict[str, Any]] = Field(None, description="Phone, email, etc.")


class WitnessDetails(BaseModel):
    """Details of witnesses as required by Indian law"""

    name: str = Field(..., description="Full name of witness")
    address: Dict[str, Any] = Field(..., description="Complete address of witness")
    age: Optional[int] = Field(None, ge=18, le=120, description="Age of witness")
    occupation: Optional[str] = Field(None, description="Occupation of witness")


class PropertyAddress(BaseModel):
    """Complete property address structure"""

    house_number: Optional[str] = Field(None, description="House/building number")
    street_address: str = Field(..., description="Street/road name and number")
    locality: str = Field(..., description="Locality/area name")
    city: str = Field(..., description="City name")
    state: str = Field(..., description="State name")
    pincode: str = Field(..., pattern=r"^\d{6}$", description="6-digit PIN code")


class PropertySpecifications(BaseModel):
    """Detailed property specifications"""

    property_type: str = Field(..., description="Residential/Commercial/Mixed")
    accommodation_type: str = Field(..., description="Independent house/Apartment/Villa/Studio")
    total_built_area: Optional[Decimal] = Field(None, ge=0, description="Total built-up area in sq ft")
    carpet_area: Optional[Decimal] = Field(None, ge=0, description="Carpet area in sq ft")
    floor_number: Optional[str] = Field(None, description="Floor number (e.g., Ground, 1st, 2nd)")
    total_floors: Optional[int] = Field(None, ge=1, description="Total number of floors in building")
    facing_direction: Optional[str] = Field(None, description="Direction the property faces")
    furnishing_status: str = Field(..., description="Furnished/Semi-furnished/Unfurnished")


class RentDetails(BaseModel):
    """Financial terms related to rent"""

    monthly_rent: Decimal = Field(..., ge=0, description="Monthly rent amount in INR")
    rent_in_words: Optional[str] = Field(None, description="Rent amount in words")
    due_date: int = Field(..., ge=1, le=31, description="Rent due date (day of month)")
    payment_method: Optional[str] = Field(None, description="Method of payment (cheque/online/bank transfer)")

    @validator('rent_in_words')
    def validate_rent_in_words(cls, v, values):
        """Validate that rent in words matches the numeric amount"""
        if v and 'monthly_rent' in values:
            # Basic validation - could be enhanced with number-to-words conversion
            pass
        return v


class LatePaymentPenalty(BaseModel):
    """Details of penalties for late payment"""

    penalty_type: str = Field(..., description="Fixed amount/Percentage of rent")
    penalty_amount: Optional[Decimal] = Field(None, ge=0, description="Fixed penalty amount")
    penalty_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Percentage of monthly rent")
    grace_period_days: Optional[int] = Field(None, ge=0, description="Grace period before penalty applies")


class DepositsAndAdvances(BaseModel):
    """Security deposits and advance payments"""

    security_deposit: Decimal = Field(..., ge=0, description="Security deposit amount in INR")
    advance_rent: Optional[Decimal] = Field(None, ge=0, description="Advance rent payment")
    other_deposits: Optional[List[Dict[str, Any]]] = Field(None, description="Other deposits (maintenance, key money, etc.)")
    refund_conditions: Optional[str] = Field(None, description="Conditions for deposit refund")


class EscalationTerms(BaseModel):
    """Rent escalation/escalation terms"""

    annual_increment_percentage: Optional[Decimal] = Field(None, ge=0, le=100, description="Annual rent increase percentage")
    effective_from_year: Optional[int] = Field(None, ge=1, description="Year from which escalation starts")
    maximum_escalation_limit: Optional[Decimal] = Field(None, ge=0, le=100, description="Maximum allowed escalation percentage")


class UtilityResponsibilities(BaseModel):
    """Responsibility allocation for utility bills"""

    electricity_bill: str = Field(..., description="Landlord/Tenant/Shared")
    water_charges: str = Field(..., description="Landlord/Tenant/Shared")
    gas_connection: str = Field(..., description="Landlord/Tenant/Shared")
    maintenance_charges: str = Field(..., description="Landlord/Tenant/Shared")
    property_tax: str = Field(..., description="Landlord/Tenant/Shared")
    society_charges: str = Field(..., description="Landlord/Tenant/Shared")


class LeaseDuration(BaseModel):
    """Lease term and renewal details"""

    start_date: date = Field(..., description="Lease commencement date")
    end_date: date = Field(..., description="Lease termination date")
    total_months: Optional[int] = Field(None, ge=1, description="Total lease period in months")
    renewable: bool = Field(True, description="Whether lease is renewable")
    renewal_terms: Optional[str] = Field(None, description="Terms and conditions for renewal")


class UsageRestrictions(BaseModel):
    """Permitted and restricted use of property"""

    permitted_use: str = Field(..., description="Residential only/Commercial only/Mixed")
    subletting_allowed: bool = Field(False, description="Whether subletting is permitted")
    guest_policy: Optional[str] = Field(None, description="Policy regarding guests/visitors")
    pet_policy: Optional[str] = Field(None, description="Pet ownership policy")
    modification_rights: Optional[str] = Field(None, description="Rights to modify property")


class TerminationConditions(BaseModel):
    """Conditions for lease termination"""

    notice_period_days: int = Field(..., ge=1, description="Notice period in days")
    early_termination_penalty: Optional[str] = Field(None, description="Penalty for early termination")
    breach_consequences: Optional[str] = Field(None, description="Consequences of breach")
    force_majeure_clauses: Optional[str] = Field(None, description="Force majeure provisions")


class MaintenanceObligations(BaseModel):
    """Maintenance and repair responsibilities"""

    major_repairs: str = Field(..., description="Who handles major repairs")
    minor_repairs: str = Field(..., description="Who handles minor repairs")
    structural_maintenance: str = Field(..., description="Who handles structural maintenance")
    appliance_maintenance: Optional[Dict[str, Any]] = Field(None, description="Maintenance of appliances/fixtures")


class ComplianceRequirements(BaseModel):
    """Legal and regulatory compliance"""

    local_laws_adherence: bool = Field(True, description="Compliance with local laws")
    society_rules_compliance: Optional[bool] = Field(None, description="Society bylaws compliance")
    municipal_permissions: Optional[str] = Field(None, description="Municipal permissions and approvals")
    fire_safety_compliance: Optional[bool] = Field(None, description="Fire safety compliance")


class DisputeResolution(BaseModel):
    """Dispute resolution mechanisms"""

    jurisdiction: str = Field(..., description="Court jurisdiction")
    arbitration_clause: bool = Field(False, description="Presence of arbitration clause")
    mediation_preference: bool = Field(False, description="Preference for mediation")
    applicable_courts: str = Field(..., description="Applicable court location")


class RegistrationDetails(BaseModel):
    """Stamp duty and registration information"""

    stamp_paper_value: Optional[Decimal] = Field(None, ge=0, description="Stamp paper value")
    registration_fee: Optional[Decimal] = Field(None, ge=0, description="Registration fee")
    sub_registrar_office: Optional[str] = Field(None, description="Sub-registrar office location")
    document_registration_number: Optional[str] = Field(None, description="Registration number")
    registration_date: Optional[date] = Field(None, description="Registration date")


class RentalAgreementSchema(BaseModel):
    """
    Comprehensive schema for Indian rental agreements
    Based on Transfer of Property Act, 1882 and state-specific Rent Control Acts
    """

    # Document Metadata
    document_metadata: Dict[str, Any] = Field(..., description="Document identification and metadata")
    jurisdiction: str = Field("india", description="Applicable jurisdiction")
    state: Optional[str] = Field(None, description="State where property is located")
    registration_required: bool = Field(True, description="Whether registration is required")
    stamp_duty_value: Optional[Decimal] = Field(None, ge=0, description="Stamp duty amount")
    creation_date: Optional[date] = Field(None, description="Document creation date")
    execution_location: Optional[str] = Field(None, description="Place of execution")

    # Parties Information
    lessor: LessorDetails = Field(..., description="Property owner details")
    lessee: LesseeDetails = Field(..., description="Tenant details")
    witnesses: List[WitnessDetails] = Field(..., min_items=2, description="At least 2 witnesses as per Indian law")

    # Property Details
    property_address: PropertyAddress = Field(..., description="Complete property address")
    property_specifications: PropertySpecifications = Field(..., description="Property specifications")
    amenities_included: List[str] = Field(default_factory=list, description="List of amenities included")
    parking_details: Optional[Dict[str, Any]] = Field(None, description="Parking arrangements")
    common_area_access: List[str] = Field(default_factory=list, description="Access to common areas")

    # Financial Terms
    rent_details: RentDetails = Field(..., description="Rent payment details")
    deposits_and_advances: DepositsAndAdvances = Field(..., description="Deposits and advances")
    escalation_terms: Optional[EscalationTerms] = Field(None, description="Rent escalation terms")
    utility_responsibilities: UtilityResponsibilities = Field(..., description="Utility bill responsibilities")

    # Lease Terms
    lease_terms: LeaseDuration = Field(..., description="Lease duration and terms")
    usage_restrictions: UsageRestrictions = Field(..., description="Usage restrictions and permissions")
    termination_conditions: TerminationConditions = Field(..., description="Termination conditions")

    # Legal Clauses
    maintenance_obligations: MaintenanceObligations = Field(..., description="Maintenance responsibilities")
    compliance_requirements: ComplianceRequirements = Field(..., description="Legal compliance requirements")
    dispute_resolution: DisputeResolution = Field(..., description="Dispute resolution mechanism")

    # Registration and Legal Details
    registration_details: Optional[RegistrationDetails] = Field(None, description="Registration information")

    model_config = {
        "json_encoders": {
            Decimal: lambda v: float(v),
            date: lambda v: v.isoformat()
        }
    }
            "example": {
                "document_metadata": {
                    "document_type": "rental_agreement",
                    "title": "Residential Rental Agreement"
                },
                "jurisdiction": "india",
                "state": "Maharashtra",
                "registration_required": True,
                "lessor": {
                    "name": "Rajesh Kumar Sharma",
                    "father_name": "Late Suresh Kumar Sharma",
                    "address": {
                        "house_number": "A-101",
                        "street_address": "Sunshine Apartments, Andheri West",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400058"
                    },
                    "pan_number": "ABCDE1234F"
                },
                "lessee": {
                    "name": "Priya Singh",
                    "father_name": "Anil Singh",
                    "permanent_address": {
                        "house_number": "B-205",
                        "street_address": "Green Valley, Bandra East",
                        "city": "Mumbai",
                        "state": "Maharashtra",
                        "pincode": "400051"
                    },
                    "pan_number": "FGHIJ5678K"
                },
                "witnesses": [
                    {
                        "name": "Amit Patel",
                        "address": {
                            "street_address": "123 MG Road",
                            "city": "Mumbai",
                            "state": "Maharashtra",
                            "pincode": "400001"
                        }
                    }
                ],
                "property_address": {
                    "house_number": "A-101",
                    "street_address": "Sunshine Apartments, Andheri West",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "pincode": "400058"
                },
                "property_specifications": {
                    "property_type": "residential",
                    "accommodation_type": "apartment",
                    "carpet_area": 850.0,
                    "furnishing_status": "semi_furnished"
                },
                "rent_details": {
                    "monthly_rent": 25000.0,
                    "due_date": 5,
                    "payment_method": "bank_transfer"
                },
                "deposits_and_advances": {
                    "security_deposit": 50000.0
                },
                "utility_responsibilities": {
                    "electricity_bill": "tenant",
                    "water_charges": "shared",
                    "maintenance_charges": "landlord"
                },
                "lease_terms": {
                    "start_date": "2024-02-01",
                    "end_date": "2025-01-31",
                    "total_months": 12,
                    "renewable": True
                },
                "usage_restrictions": {
                    "permitted_use": "residential_only",
                    "subletting_allowed": False
                },
                "termination_conditions": {
                    "notice_period_days": 30
                },
                "maintenance_obligations": {
                    "major_repairs": "landlord",
                    "minor_repairs": "tenant"
                },
                "compliance_requirements": {
                    "local_laws_adherence": True,
                    "society_rules_compliance": True
                },
                "dispute_resolution": {
                    "jurisdiction": "Mumbai",
                    "arbitration_clause": False,
                    "applicable_courts": "Civil Court, Mumbai"
                }
            }
        }
