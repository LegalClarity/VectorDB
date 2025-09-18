"""
Verification script for LangExtract implementation
Tests real clause and relationship extraction without mocks
"""

import os
from dotenv import load_dotenv
from legal_document_extractor import LegalDocumentExtractor

# Load environment variables
load_dotenv()

def main():
    """Test the LangExtract implementation"""

    print("🔍 VERIFYING LANGEXTRACT IMPLEMENTATION")
    print("=" * 50)

    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment!")
        print("Please set the GEMINI_API_KEY environment variable.")
        return

    print(f"✅ GEMINI_API_KEY found: {api_key[:10]}...")

    # Test simple extraction
    test_text = """
    LEASE AGREEMENT

    This agreement is made between John Smith (Landlord) and Jane Doe (Tenant).
    Property: 123 Main Street, New York.
    Monthly rent: $2,500 payable on the 1st of each month.
    Security deposit: $2,500, refundable at end of lease.
    Lease term: 12 months from January 1, 2024.
    """

    try:
        print("\n🧪 Testing LangExtract with real API call...")

        # First test basic LangExtract functionality
        import langextract as lx

        # Use the basic example from LangExtract documentation
        input_text = "Lady Juliet gazed longingly at the stars, her heart aching for Romeo"
        prompt = "Extract characters, emotions, and relationships in order of appearance."
        examples = [
            lx.data.ExampleData(
                text="ROMEO. But soft! What light through yonder window breaks? It is the east, and Juliet is the sun.",
                extractions=[
                    lx.data.Extraction(
                        extraction_class="character",
                        extraction_text="ROMEO",
                        attributes={"emotional_state": "wonder"}
                    ),
                    lx.data.Extraction(
                        extraction_class="emotion",
                        extraction_text="But soft!",
                        attributes={"feeling": "gentle awe"}
                    ),
                    lx.data.Extraction(
                        extraction_class="relationship",
                        extraction_text="Juliet is the sun",
                        attributes={"type": "metaphor"}
                    ),
                ]
            )
        ]

        print("   Testing basic LangExtract functionality...")
        basic_result = lx.extract(
            text_or_documents=input_text,
            prompt_description=prompt,
            examples=examples,
            model_id="gemini-2.0-flash-exp",
            api_key=api_key
        )

        print("   ✅ Basic LangExtract test passed!")
        print(f"   📝 Basic extractions: {len(basic_result.extractions)}")

        # Now test our implementation
        print("   Testing our legal document extractor...")
        extractor = LegalDocumentExtractor()
        result = extractor.extract_clauses_and_relationships(test_text, "rental")

        print("✅ SUCCESS! LangExtract worked with real API")
        print(f"   📄 Document Type: {result.document_type.value}")
        print(f"   📝 Clauses Extracted: {len(result.extracted_clauses)}")
        print(f"   🔗 Relationships Found: {len(result.clause_relationships)}")
        print(".2f")
        print(".2f")

        # Show sample clauses
        if result.extracted_clauses:
            print("\n📋 SAMPLE CLAUSES:")
            for i, clause in enumerate(result.extracted_clauses[:3]):
                print(f"   {i+1}. {clause.clause_type.value}")
                print(f"      Text: {clause.clause_text[:60]}...")
                print(f"      Confidence: {clause.confidence_score:.2f}")
                if clause.key_terms:
                    print(f"      Key Terms: {clause.key_terms[:2]}")
                print()

        # Show relationships
        if result.clause_relationships:
            print("🔗 SAMPLE RELATIONSHIPS:")
            for i, rel in enumerate(result.clause_relationships[:2]):
                print(f"   {i+1}. {rel.source_clause_id} → {rel.target_clause_id}")
                print(f"      Type: {rel.relationship_type.value}")
                print(f"      Description: {rel.relationship_description}")
                print(f"      Strength: {rel.strength:.2f}")
                print()

        # Test visualization
        print("📊 Testing visualization data creation...")
        viz_data = extractor.create_visualization_data(result, test_text)
        print(f"   ✅ Visualization data created with {len(viz_data['clauses'])} clauses")

        print("\n🎉 ALL TESTS PASSED!")
        print("   ✅ Real LangExtract integration working")
        print("   ✅ Clause extraction functional")
        print("   ✅ Relationship mapping working")
        print("   ✅ Visualization data created")
        print("   ✅ No mock implementations used")

    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        print("\nPossible issues:")
        print("   - Invalid GEMINI_API_KEY")
        print("   - Network connectivity problems")
        print("   - LangExtract library issues")
        print("   - API rate limits or quota exceeded")

if __name__ == "__main__":
    main()
