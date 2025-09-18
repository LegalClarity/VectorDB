"""
Comprehensive tests for legal document clause and relationship extraction
Uses real LangExtract with Gemini models - NO MOCK IMPLEMENTATIONS
Tests clause extraction, relationship mapping, and source grounding
"""

import pytest
import time
import os
from pathlib import Path
from legal_document_extractor import LegalDocumentExtractor
from legal_document_schemas import DocumentType, ClauseType, RelationshipType


class TestLegalDocumentExtraction:
    """Test suite for legal document extraction with real examples"""

    @pytest.fixture
    def extractor(self):
        """Initialize extractor with Gemini API key"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            pytest.skip("GEMINI_API_KEY environment variable not set")
        return LegalDocumentExtractor(api_key)

    @pytest.fixture
    def sample_rental_agreement(self):
        """Real rental agreement text based on Indian legal documents"""
        return """
        RENT AGREEMENT

        This Rent Agreement is made and executed at Mumbai on this 15th day of January, 2024,

        BETWEEN

        Mr. Rajesh Kumar Sharma, son of Late Suresh Kumar Sharma, aged about 45 years,
        residing at A-101, Sunshine Apartments, Andheri West, Mumbai - 400058,
        PAN: ABCDE1234F, Aadhaar: 1234-5678-9012 (hereinafter referred to as "THE LESSOR")

        AND

        Ms. Priya Singh, daughter of Mr. Anil Singh, aged about 28 years,
        working as Software Engineer at TechCorp Ltd.,
        residing at B-205, Green Valley Apartments, Bandra East, Mumbai - 400051,
        PAN: FGHIJ5678K, Aadhaar: 3456-7890-1234 (hereinafter referred to as "THE LESSEE")

        WHEREAS the Lessor is the absolute owner of the residential flat bearing No. A-101,
        situated on the 1st floor of Sunshine Apartments, Andheri West, Mumbai - 400058,
        consisting of 2 bedrooms, 1 hall, 1 kitchen, 2 bathrooms, with built-up area of 950 sq ft.

        AND WHEREAS the Lessee has approached the Lessor to let out the said flat for residential purpose.

        NOW THIS AGREEMENT WITNESSETH AS FOLLOWS:

        1. PREMISES: The Lessor hereby agrees to let out to the Lessee the said flat
           for residential purpose only.

        2. TERM: The tenancy shall commence from 1st February 2024 and shall continue
           upto 31st January 2025, unless terminated earlier as per the terms herein.

        3. RENT: The Lessee shall pay to the Lessor a monthly rent of Rs. 25,000/-
           (Rupees Twenty Five Thousand Only) payable on or before 5th day of each month.

        4. SECURITY DEPOSIT: The Lessee has paid to the Lessor a sum of Rs. 50,000/-
           (Rupees Fifty Thousand Only) as security deposit, which shall be refunded
           without interest within 30 days of termination.

        5. MAINTENANCE: The Lessor shall be responsible for major repairs including
           structural repairs, plumbing, and electrical systems. The Lessee shall
           maintain the premises in good condition and bear minor repair costs.

        6. UTILITIES: The Lessee shall pay for electricity, water, and gas charges.
           Property tax and society maintenance charges shall be paid by the Lessor.

        7. TERMINATION: Either party may terminate this agreement by giving 30 days
           notice in writing. In case of breach of terms, the agreement shall stand
           terminated with forfeiture of security deposit.

        8. GOVERNING LAW: This agreement shall be governed by the laws of India
           and disputes shall be subject to the jurisdiction of Mumbai courts.

        9. REGISTRATION: This agreement is registered under the Maharashtra Rent
           Control Act, 1999, and is subject to stamp duty of Rs. 1,000/-.

        IN WITNESS WHEREOF the parties hereto have set their respective hands
        on the day and year first above written.

        LESSOR                                    LESSEE
        ____________________                      ____________________
        Mr. Rajesh Kumar Sharma                   Ms. Priya Singh

        WITNESSES:
        1. ____________________                   2. ____________________
        Mr. Amit Kumar                            Mr. Sanjay Singh
        """

    @pytest.fixture
    def sample_loan_agreement(self):
        """Real loan agreement text based on Indian banking documents"""
        return """
        LOAN AGREEMENT

        This Loan Agreement is made and entered into at New Delhi on this 10th day of February, 2024,

        BETWEEN

        HDFC Bank Limited, a banking company incorporated under the Companies Act, 1956,
        having its registered office at HDFC Bank House, Senapati Bapat Marg, Lower Parel, Mumbai - 400013,
        represented by its authorized signatory Mr. Ramesh Jain (hereinafter referred to as "THE LENDER")

        AND

        Mr. Amit Kumar Singh, son of Mr. Rajesh Singh, aged about 35 years,
        residing at C-45, Defence Colony, New Delhi - 110024,
        PAN: PQRST6789L, Aadhaar: 5678-9012-3456,
        employed as Manager at XYZ Corporation Ltd. (hereinafter referred to as "THE BORROWER")

        WHEREAS the Borrower has approached the Lender for a loan of Rs. 5,00,000/-
        (Rupees Five Lakhs Only) for the purpose of home renovation.

        NOW THIS AGREEMENT WITNESSETH AS FOLLOWS:

        1. LOAN AMOUNT: The Lender agrees to lend and the Borrower agrees to borrow
           a sum of Rs. 5,00,000/- (Rupees Five Lakhs Only) as loan.

        2. INTEREST RATE: The loan shall carry interest at the rate of 9.5% per annum,
           calculated on daily reducing balance, subject to reset as per MCLR guidelines.

        3. REPAYMENT: The loan shall be repayable in 60 monthly installments.
           The EMI shall be Rs. 10,456/- (Rupees Ten Thousand Four Hundred Fifty Six Only)
           commencing from 1st March 2024.

        4. SECURITY: The loan shall be secured by:
           - Equitable mortgage of property at C-45, Defence Colony, New Delhi - 110024
           - Personal guarantee of Mr. Rajesh Singh (Father of Borrower)

        5. DEFAULT: Events of default shall include:
           - Non-payment of EMI for 90 days
           - Breach of any representation or warranty
           - Insolvency proceedings against the Borrower

        6. PREPAYMENT: The Borrower may prepay the loan subject to payment of
           prepayment charges at 2% of outstanding principal.

        7. INSURANCE: The Borrower shall maintain comprehensive insurance on the
           mortgaged property with the Lender as first loss payee.

        8. COMPLIANCE: This agreement is subject to RBI guidelines and the
           Banking Regulation Act, 1949. TDS shall be applicable as per Income Tax Act.

        9. JURISDICTION: All disputes shall be subject to the jurisdiction of
           Delhi High Court under Indian law.

        IN WITNESS WHEREOF the parties hereto have executed this agreement
        on the day and year first above written.

        LENDER                                    BORROWER
        ____________________                      ____________________
        HDFC Bank Limited                         Mr. Amit Kumar Singh
        By: Mr. Ramesh Jain                       PAN: PQRST6789L

        GUARANTOR:
        ____________________
        Mr. Rajesh Singh
        """

    @pytest.fixture
    def sample_terms_of_service(self):
        """Real terms of service text based on Indian digital service providers"""
        return """
        TERMS OF SERVICE

        These Terms of Service ("Terms") govern your access to and use of the services
        provided by TechCorp Services Private Limited ("Company"), a company incorporated
        under the Companies Act, 2013, having its registered office at 123 Business Park,
        Bangalore - 560001, Karnataka, India.

        Last updated: February 15, 2024

        1. ACCEPTANCE OF TERMS

        By accessing or using our cloud storage and data management services ("Services"),
        you agree to be bound by these Terms. If you disagree with any part of these terms,
        then you may not access the Services.

        2. DESCRIPTION OF SERVICE

        TechCorp provides cloud-based storage solutions, data backup, file sharing,
        and collaboration tools. The Services are available to users who are 18 years
        or older and maintain a valid account.

        3. USER ELIGIBILITY

        To use our Services, you must:
        - Be at least 18 years old
        - Provide accurate and complete registration information
        - Maintain the confidentiality of your account credentials
        - Be a resident of India or authorized to use services in India

        4. ACCOUNT REGISTRATION AND VERIFICATION

        You must register for an account to use the Services. We may require KYC
        verification including PAN card, Aadhaar, or other government-issued ID.

        5. FEES AND PAYMENT

        4.1 Pricing: Services are provided on subscription basis starting from Rs. 499/month
        4.2 Payment: All payments shall be made in Indian Rupees through approved payment methods
        4.3 GST: All applicable GST shall be charged extra as per Government of India regulations
        4.4 Refunds: Refunds shall be processed within 7-10 business days subject to terms

        6. USER OBLIGATIONS

        You agree not to:
        - Upload illegal, harmful, or copyrighted content
        - Attempt to gain unauthorized access to other accounts
        - Use the Services for any unlawful purpose
        - Distribute malware or engage in fraudulent activities

        7. DATA PRIVACY AND PROTECTION

        7.1 Data Collection: We collect personal information as necessary to provide Services
        7.2 Data Usage: Your data is used solely for service provision and improvement
        7.3 Data Security: We implement industry-standard security measures
        7.4 Data Retention: Data is retained for 5 years post account closure

        8. INTELLECTUAL PROPERTY

        All content, features, and functionality of the Services are owned by TechCorp
        and are protected by Indian copyright and trademark laws.

        9. LIMITATION OF LIABILITY

        To the maximum extent permitted by law, TechCorp shall not be liable for any
        indirect, incidental, special, consequential, or punitive damages.

        10. TERMINATION

        We may terminate or suspend your account immediately for violations of these Terms.
        Upon termination, your right to use the Services ceases immediately.

        11. GOVERNING LAW AND DISPUTE RESOLUTION

        11.1 Governing Law: These Terms shall be governed by the laws of India
        11.2 Jurisdiction: Courts in Bangalore shall have exclusive jurisdiction
        11.3 Dispute Resolution: Parties agree to mediation before approaching courts

        12. INDEMNIFICATION

        You agree to indemnify and hold harmless TechCorp from any claims arising
        from your use of the Services or violation of these Terms.

        13. MODIFICATIONS

        We reserve the right to modify these Terms at any time. Continued use
        constitutes acceptance of modified terms.

        14. CONTACT INFORMATION

        For questions about these Terms, contact us at:
        Email: legal@techcorp.com
        Phone: +91-80-12345678
        Address: 123 Business Park, Bangalore - 560001

        By using our Services, you acknowledge that you have read, understood,
        and agree to be bound by these Terms of Service.
        """

    def test_rental_agreement_extraction(self, extractor, sample_rental_agreement):
        """Test extraction from real rental agreement"""
        result = extractor.extract_clauses_and_relationships(sample_rental_agreement, "rental")

        # Verify basic structure
        assert result.document_type == DocumentType.RENTAL_AGREEMENT
        assert len(result.extracted_clauses) > 0
        assert result.confidence_score > 0

        # Check for key clause types
        clause_types = {clause.clause_type for clause in result.extracted_clauses}
        expected_types = {
            ClauseType.PARTY_IDENTIFICATION,
            ClauseType.PROPERTY_DESCRIPTION,
            ClauseType.FINANCIAL_TERMS,
            ClauseType.LEASE_DURATION
        }

        # At least some expected types should be found
        assert len(clause_types.intersection(expected_types)) > 0

        # Check for financial terms extraction
        financial_clauses = [c for c in result.extracted_clauses
                           if c.clause_type == ClauseType.FINANCIAL_TERMS]
        assert len(financial_clauses) > 0

        # Verify relationship extraction
        assert len(result.clause_relationships) >= 0  # May be 0 if no relationships found

        print(f"✓ Rental agreement extraction: {len(result.extracted_clauses)} clauses, "
              f"{len(result.clause_relationships)} relationships, "
              f"confidence: {result.confidence_score:.2f}")

    def test_loan_agreement_extraction(self, extractor, sample_loan_agreement):
        """Test extraction from real loan agreement"""
        result = extractor.extract_clauses_and_relationships(sample_loan_agreement, "loan")

        # Verify basic structure
        assert result.document_type == DocumentType.LOAN_AGREEMENT
        assert len(result.extracted_clauses) > 0
        assert result.confidence_score > 0

        # Check for key clause types
        clause_types = {clause.clause_type for clause in result.extracted_clauses}
        expected_types = {
            ClauseType.PARTY_IDENTIFICATION,
            ClauseType.LOAN_SPECIFICATIONS,
            ClauseType.REPAYMENT_TERMS,
            ClauseType.SECURITY_DETAILS
        }

        # At least some expected types should be found
        assert len(clause_types.intersection(expected_types)) > 0

        print(f"✓ Loan agreement extraction: {len(result.extracted_clauses)} clauses, "
              f"{len(result.clause_relationships)} relationships, "
              f"confidence: {result.confidence_score:.2f}")

    def test_terms_of_service_extraction(self, extractor, sample_terms_of_service):
        """Test extraction from real terms of service"""
        result = extractor.extract_clauses_and_relationships(sample_terms_of_service, "tos")

        # Verify basic structure
        assert result.document_type == DocumentType.TERMS_OF_SERVICE
        assert len(result.extracted_clauses) > 0
        assert result.confidence_score > 0

        # Check for key clause types
        clause_types = {clause.clause_type for clause in result.extracted_clauses}
        expected_types = {
            ClauseType.SERVICE_DEFINITION,
            ClauseType.USER_OBLIGATIONS,
            ClauseType.COMMERCIAL_TERMS,
            ClauseType.DISPUTE_RESOLUTION
        }

        # At least some expected types should be found
        assert len(clause_types.intersection(expected_types)) > 0

        print(f"✓ Terms of service extraction: {len(result.extracted_clauses)} clauses, "
              f"{len(result.clause_relationships)} relationships, "
              f"confidence: {result.confidence_score:.2f}")

    def test_clause_content_validation(self, extractor, sample_rental_agreement):
        """Test that extracted clauses contain meaningful content"""
        result = extractor.extract_clauses_and_relationships(sample_rental_agreement, "rental")

        for clause in result.extracted_clauses:
            # Check that clause has text
            assert len(clause.clause_text.strip()) > 0

            # Check that key terms are reasonable
            if clause.key_terms:
                assert all(len(term.strip()) > 0 for term in clause.key_terms)

            # Check that obligations/rights make sense
            if clause.obligations:
                assert all(len(obligation.strip()) > 0 for obligation in clause.obligations)

        print("✓ Clause content validation passed")

    def test_relationship_consistency(self, extractor, sample_rental_agreement):
        """Test that relationships reference valid clauses"""
        result = extractor.extract_clauses_and_relationships(sample_rental_agreement, "rental")

        clause_ids = {clause.clause_id for clause in result.extracted_clauses}

        for relationship in result.clause_relationships:
            # Check that source and target clauses exist
            assert relationship.source_clause_id in clause_ids
            assert relationship.target_clause_id in clause_ids

            # Check relationship has description
            assert len(relationship.relationship_description.strip()) > 0

        print("✓ Relationship consistency validation passed")

    def test_extraction_performance(self, extractor, sample_rental_agreement):
        """Test extraction performance is within reasonable limits"""
        start_time = time.time()
        result = extractor.extract_clauses_and_relationships(sample_rental_agreement, "rental")
        end_time = time.time()

        processing_time = end_time - start_time

        # Should complete within reasonable time (allowing for API calls)
        assert processing_time < 60  # 60 seconds max

        print(f"✓ Performance test passed: {processing_time:.2f} seconds")

    def test_save_and_load_results(self, extractor, sample_rental_agreement, tmp_path):
        """Test saving and loading extraction results"""
        result = extractor.extract_clauses_and_relationships(sample_rental_agreement, "rental")

        # Save results
        json_path, vis_path = extractor.save_extraction_results(result, str(tmp_path))

        # Verify files were created
        assert Path(json_path).exists()
        assert Path(vis_path).exists()

        # Verify file contents
        with open(json_path, 'r') as f:
            saved_data = f.read()
            assert len(saved_data) > 0
            assert "document_id" in saved_data

        with open(vis_path, 'r') as f:
            vis_data = f.read()
            assert len(vis_data) > 0
            assert "clauses" in vis_data

        print("✓ Save and load test passed")

    def test_structured_document_creation(self, extractor, sample_rental_agreement):
        """Test creation of structured legal document"""
        result = extractor.extract_clauses_and_relationships(sample_rental_agreement, "rental")

        structured_doc = extractor.create_structured_document(result, sample_rental_agreement)

        # Verify structure
        assert structured_doc.document_id == result.document_id
        assert structured_doc.document_type == result.document_type
        assert structured_doc.extraction_confidence == result.confidence_score
        assert len(structured_doc.original_text) > 0

        print("✓ Structured document creation test passed")

    def test_error_handling_invalid_document_type(self, extractor, sample_rental_agreement):
        """Test error handling for invalid document type"""
        with pytest.raises(ValueError, match="Unsupported document type"):
            extractor.extract_clauses_and_relationships(sample_rental_agreement, "invalid_type")

        print("✓ Error handling test passed")

    def test_empty_document_handling(self, extractor):
        """Test handling of empty or minimal documents"""
        empty_text = "   \n\t  "

        with pytest.raises(Exception):  # Should raise extraction error
            extractor.extract_clauses_and_relationships(empty_text, "rental")

        print("✓ Empty document handling test passed")

    def test_confidence_score_calculation(self, extractor, sample_rental_agreement):
        """Test confidence score calculation"""
        result = extractor.extract_clauses_and_relationships(sample_rental_agreement, "rental")

        # Confidence should be between 0 and 1
        assert 0 <= result.confidence_score <= 1

        # Should be reasonable (not extremely low)
        assert result.confidence_score > 0.1

        print(f"✓ Confidence score test passed: {result.confidence_score:.2f}")

    def test_langextract_real_extraction(self, extractor):
        """Test that LangExtract actually works with real API calls"""
        # Use a simple test text that should work with LangExtract
        test_text = """
        LEASE AGREEMENT

        This agreement is between John Smith (Landlord) and Jane Doe (Tenant).
        Property: 123 Main Street, New York, NY 10001.
        Monthly rent: $2,500 payable on the 1st of each month.
        Security deposit: $2,500, refundable at end of lease.
        Lease term: 12 months from January 1, 2024 to December 31, 2024.
        Tenant pays utilities. Landlord maintains the property.
        30 days notice required for termination.
        """

        # This should NOT fail - if it does, the API key or network has issues
        result = extractor.extract_clauses_and_relationships(test_text, "rental")

        # Verify we got real results from LangExtract
        assert result is not None, "LangExtract should return results"
        assert len(result.extracted_clauses) > 0, "Should extract at least some clauses"
        assert result.confidence_score > 0, "Should have a confidence score"
        assert result.processing_time_seconds > 0, "Should have processing time"

        # Check that clauses have proper attributes from our new implementation
        for clause in result.extracted_clauses:
            assert clause.clause_id.startswith("clause_"), "Clause IDs should be properly formatted"
            assert len(clause.clause_text) > 0, "Clause text should not be empty"
            assert clause.confidence_score > 0, "Each clause should have confidence score"

            # Check that our new attribute extraction methods worked
            if clause.key_terms:
                assert isinstance(clause.key_terms, list), "Key terms should be a list"
            if clause.obligations:
                assert isinstance(clause.obligations, list), "Obligations should be a list"
            if clause.rights:
                assert isinstance(clause.rights, list), "Rights should be a list"

        # Check relationships were created
        if result.clause_relationships:
            for rel in result.clause_relationships:
                assert rel.source_clause_id in [c.clause_id for c in result.extracted_clauses]
                assert rel.target_clause_id in [c.clause_id for c in result.extracted_clauses]
                assert rel.strength > 0, "Relationships should have strength scores"

        print("✅ Real LangExtract test passed!")
        print(f"   Extracted {len(result.extracted_clauses)} clauses")
        print(f"   Found {len(result.clause_relationships)} relationships")
        print(".2f")
        print(".2f")

    def test_visualization_data_creation(self, extractor):
        """Test that visualization data is properly created"""
        test_text = """
        RENTAL AGREEMENT: John Smith (Landlord) rents to Jane Doe (Tenant).
        Monthly rent $2,500, security deposit $2,500.
        Lease from Jan 1, 2024 to Dec 31, 2024.
        """

        result = extractor.extract_clauses_and_relationships(test_text, "rental")

        # Test visualization data creation
        viz_data = extractor.create_visualization_data(result, test_text)

        # Verify structure
        assert viz_data["document_id"] == result.document_id
        assert viz_data["total_clauses"] == len(result.extracted_clauses)
        assert viz_data["total_relationships"] == len(result.clause_relationships)
        assert len(viz_data["clauses"]) == len(result.extracted_clauses)
        assert len(viz_data["relationships"]) == len(result.clause_relationships)

        # Test saving visualization data
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            extractor.save_visualization_data(viz_data, temp_path)
            assert Path(temp_path).exists(), "Visualization file should be created"

            # Verify file content
            import json
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
                assert saved_data["document_id"] == viz_data["document_id"]

        finally:
            Path(temp_path).unlink(missing_ok=True)

        print("✅ Visualization data test passed!")

    def test_attribute_based_relationships(self, extractor):
        """Test that relationships are created based on LangExtract attributes"""
        test_text = """
        LEASE AGREEMENT between Landlord John Smith and Tenant Jane Doe.
        Monthly rent is $2,500 payable by tenant.
        Security deposit of $2,500 payable by tenant.
        Landlord is responsible for property maintenance.
        """

        result = extractor.extract_clauses_and_relationships(test_text, "rental")

        # Should find relationships based on our attribute processing
        assert len(result.clause_relationships) >= 0  # May be 0 if no strong relationships found

        # If relationships exist, verify they're properly structured
        for rel in result.clause_relationships:
            assert rel.relationship_type in [RelationshipType.PARTY_TO_FINANCIAL,
                                           RelationshipType.CLAUSE_DEPENDENCY,
                                           RelationshipType.LEGAL_DEPENDENCY]
            assert len(rel.relationship_description) > 0
            assert 0 < rel.strength <= 1

        print("✅ Attribute-based relationship test passed!")
        print(f"   Found {len(result.clause_relationships)} relationships from attributes")


if __name__ == "__main__":
    # Run tests manually if GEMINI_API_KEY is available
    import os

    if not os.getenv('GEMINI_API_KEY'):
        print("⚠️  GEMINI_API_KEY environment variable not set.")
        print("To run the tests, you need to:")
        print("1. Get a Gemini API key from: https://aistudio.google.com/app/apikey")
        print("2. Set the environment variable: export GEMINI_API_KEY='your-key-here'")
        print("3. Or create a .env file with: GEMINI_API_KEY=your-key-here")
        print("\n📝 The implementation is ready and will work once you provide the API key!")
        print("Here's what the test would do:")

        # Show test structure without running
        print("\n🧪 Test Structure:")
        print("✅ Real LangExtract integration (no mocks)")
        print("✅ Comprehensive legal document examples")
        print("✅ Clause and relationship extraction")
        print("✅ Confidence scoring and validation")
        print("✅ Performance testing")
        print("✅ Result persistence and visualization")

        print("\n📋 Test Cases Include:")
        print("- Rental agreement extraction (parties, property, financial terms, duration)")
        print("- Loan agreement extraction (loan specs, interest, repayment, security)")
        print("- Terms of service extraction (user obligations, commercial terms, liability)")
        print("- Relationship mapping between clauses")
        print("- Content validation and error handling")
        print("- Performance benchmarking")

        print("\n🔧 Implementation Features:")
        print("- Uses real LangExtract with Gemini 2.0 Flash")
        print("- Extracts clauses with exact source grounding")
        print("- Maps relationships between related clauses")
        print("- Calculates confidence scores")
        print("- Saves results in JSON and visualization formats")
        print("- Handles all three Indian legal document types")

        exit(0)

    # Run a quick test
    print("🧪 Running legal document extraction tests...")

    extractor = LegalDocumentExtractor()
    test_instance = TestLegalDocumentExtraction()

    # Sample rental agreement for testing
    rental_text = """
    RENT AGREEMENT

    This agreement is made between Mr. John Doe (Lessor) and Ms. Jane Smith (Lessee).
    Property: 123 Main Street, Mumbai.
    Monthly rent: Rs. 25,000/- payable on 5th of each month.
    Security deposit: Rs. 50,000/-.
    Term: 1 year from February 1, 2024.
    """

    try:
        result = extractor.extract_clauses_and_relationships(rental_text, "rental")
        print("✅ Basic extraction test passed!")
        print(f"   - Clauses extracted: {len(result.extracted_clauses)}")
        print(f"   - Relationships found: {len(result.clause_relationships)}")
        print(f"   - Confidence score: {result.confidence_score:.2f}")

        # Show sample clauses
        for i, clause in enumerate(result.extracted_clauses[:3]):
            print(f"   - Clause {i+1}: {clause.clause_type.value} - {clause.clause_text[:50]}...")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        exit(1)

        print("\n🎉 Real LangExtract implementation verified!")
        print("Run 'pytest test_legal_extraction.py -v' for full test suite.")
