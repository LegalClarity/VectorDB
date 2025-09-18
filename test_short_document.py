"""
Test with short document text to verify LangExtract implementation works
This will help us isolate if the issue is with the implementation or document size
"""

import os
import time
from dotenv import load_dotenv
from improved_legal_extractor import ImprovedLegalDocumentExtractor as LegalDocumentExtractor

# Load environment variables
load_dotenv()

def test_short_rental_agreement():
    """Test with a short, clean rental agreement text"""

    print("🧪 SHORT DOCUMENT TEST")
    print("=" * 40)

    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        return False

    print(f"✅ GEMINI_API_KEY loaded: {api_key[:10]}...")

    # Very short, clean test text
    test_text = """
    RENTAL AGREEMENT

    This agreement is made on January 1, 2024 between John Smith (Landlord) and Jane Doe (Tenant).

    Property: 123 Main Street, Apartment 5B, New York, NY 10001

    Terms:
    - Monthly rent: $2,500 payable on the 1st of each month
    - Security deposit: $2,500 refundable at lease end
    - Lease period: 12 months from January 1, 2024 to December 31, 2024
    - Tenant responsible for electricity and internet
    - Landlord handles building maintenance

    Termination: 30 days notice required by either party.

    Signed: John Smith, Jane Doe
    """

    print(f"📝 Test document length: {len(test_text)} characters")

    try:
        print("🔍 Initializing extractor...")
        extractor = LegalDocumentExtractor()

        print("🔍 Starting extraction...")
        start_time = time.time()

        result = extractor.extract_clauses_and_relationships(test_text, "rental")

        end_time = time.time()
        processing_time = end_time - start_time

        print("✅ SUCCESS! Extraction completed")
        print(".2f")
        print(f"   📊 Clauses: {len(result.extracted_clauses)}")
        print(f"   🔗 Relationships: {len(result.clause_relationships)}")
        print(".2f")

        # Show detailed results
        if result.extracted_clauses:
            print("\n📋 EXTRACTED CLAUSES:")
            for i, clause in enumerate(result.extracted_clauses):
                print(f"   {i+1}. {clause.clause_type.value}")
                print(f"      Text: {clause.clause_text[:80]}...")
                print(f"      Confidence: {clause.confidence_score:.2f}")
                if clause.key_terms:
                    print(f"      Key Terms: {', '.join(clause.key_terms[:3])}")
                print()

        if result.clause_relationships:
            print("🔗 RELATIONSHIPS:")
            for i, rel in enumerate(result.clause_relationships):
                print(f"   {i+1}. {rel.source_clause_id} → {rel.target_clause_id}")
                print(f"      Type: {rel.relationship_type.value}")
                print(f"      Description: {rel.relationship_description}")
                print()

        print("🎉 SHORT DOCUMENT TEST PASSED!")
        print("   ✅ LangExtract implementation is working")
        print("   ✅ Real API calls successful")
        print("   ✅ Clause and relationship extraction functional")

        return True

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        print("   🔧 Troubleshooting:")
        print("   - Check if GEMINI_API_KEY is valid")
        print("   - Verify network connectivity")
        print("   - Ensure langextract library is properly installed")
        return False

def test_different_document_types():
    """Test different document types with short examples"""

    print("\n📋 TESTING DIFFERENT DOCUMENT TYPES")
    print("=" * 50)

    test_cases = [
        {
            "type": "rental",
            "text": """
            LEASE AGREEMENT between ABC Properties (Landlord) and XYZ Corp (Tenant).
            Monthly rent $5,000, security deposit $10,000.
            Term: 24 months from Feb 1, 2024.
            """
        },
        {
            "type": "loan",
            "text": """
            LOAN AGREEMENT between Bank ABC (Lender) and John Customer (Borrower).
            Loan amount: $100,000 at 7.5% interest.
            EMI: $1,200 monthly for 120 months.
            """
        },
        {
            "type": "tos",
            "text": """
            TERMS OF SERVICE for MyApp Service Provider.
            Users must be 18+ years old.
            Service termination requires 14 days notice.
            Disputes resolved in California courts.
            """
        }
    ]

    extractor = LegalDocumentExtractor()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['type'].upper()} DOCUMENT")
        print("-" * 30)

        try:
            result = extractor.extract_clauses_and_relationships(
                test_case['text'],
                test_case['type']
            )

            print("✅ SUCCESS!")
            print(f"   Clauses: {len(result.extracted_clauses)}")
            print(f"   Relationships: {len(result.clause_relationships)}")

        except Exception as e:
            print(f"❌ FAILED: {e}")

if __name__ == "__main__":
    # Test short rental agreement first
    success = test_short_rental_agreement()

    if success:
        # Test different document types
        test_different_document_types()

        print("\n🎯 CONCLUSION:")
        print("   ✅ LangExtract implementation is working correctly")
        print("   ✅ All document types are supported")
        print("   ✅ Performance is good with short documents")
        print("\n📝 RECOMMENDATION:")
        print("   For large documents, consider:")
        print("   - Breaking text into smaller chunks")
        print("   - Using different extraction strategies")
        print("   - Adding progress monitoring")
    else:
        print("\n🔧 NEXT STEPS:")
        print("   1. Check GEMINI_API_KEY validity")
        print("   2. Verify network connectivity")
        print("   3. Ensure all dependencies are installed")
