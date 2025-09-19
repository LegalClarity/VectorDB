# Document Analyzer Schemas Package
"""
Pydantic models for legal document schemas and analysis results.
"""

from .rental_agreement import RentalAgreementSchema
from .loan_agreement import LoanAgreementSchema
from .terms_of_service import TermsOfServiceSchema
from .processed_document import ProcessedDocumentSchema, DocumentAnalysisResult

__all__ = [
    "RentalAgreementSchema",
    "LoanAgreementSchema",
    "TermsOfServiceSchema",
    "ProcessedDocumentSchema",
    "DocumentAnalysisResult"
]
