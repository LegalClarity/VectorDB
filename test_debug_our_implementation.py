"""
Debug our LangExtract implementation to find the issue
Compare our implementation with working basic LangExtract
"""

import os
from dotenv import load_dotenv
import langextract as lx
from improved_legal_extractor import ImprovedLegalDocumentExtractor as LegalDocumentExtractor

# Load environment variables
load_dotenv()

def test_our_vs_basic():
    """Compare our implementation vs basic LangExtract"""

    print("🔍 DEBUGGING OUR IMPLEMENTATION")
    print("=" * 50)

    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        return

    print(f"✅ GEMINI_API_KEY loaded: {api_key[:10]}...")

    # Test text
    test_text = """
    RENTAL AGREEMENT

    This agreement is made on January 1, 2024 between John Smith (Landlord) and Jane Doe (Tenant).

    Property: 123 Main Street, Apartment 5B, New York, NY 10001

    Terms:
    - Monthly rent: $2,500 payable on the 1st of each month
    - Security deposit: $2,500 refundable at lease end
    - Lease period: 12 months from January 1, 2024 to December 31, 2024

    Termination: 30 days notice required by either party.

    Signed: John Smith, Jane Doe
    """

    print(f"📝 Test text length: {len(test_text)} characters")

    # Test 1: Basic LangExtract (known working)
    print("\n🧪 TEST 1: BASIC LANGEXTRACT (should work)")
    print("-" * 40)

    try:
        basic_result = lx.extract(
            text_or_documents=test_text,
            prompt_description="Extract parties, financial terms, and property details from this rental agreement.",
            examples=[
                lx.data.ExampleData(
                    text="ABC Properties rents apartment 3A to XYZ Corp for $1,800 monthly.",
                    extractions=[
                        lx.data.Extraction(
                            extraction_class="party",
                            extraction_text="ABC Properties",
                            attributes={"role": "landlord"}
                        ),
                        lx.data.Extraction(
                            extraction_class="party",
                            extraction_text="XYZ Corp",
                            attributes={"role": "tenant"}
                        ),
                        lx.data.Extraction(
                            extraction_class="financial",
                            extraction_text="$1,800 monthly",
                            attributes={"type": "rent"}
                        )
                    ]
                )
            ],
            model_id="gemini-2.5-flash",
            api_key=api_key
        )

        print("✅ Basic LangExtract succeeded")
        print(f"   Extractions: {len(basic_result.extractions) if basic_result.extractions else 0}")

    except Exception as e:
        print(f"❌ Basic LangExtract failed: {e}")

    # Test 2: Our implementation
    print("\n🧪 TEST 2: OUR IMPLEMENTATION")
    print("-" * 40)

    try:
        extractor = LegalDocumentExtractor()
        print("✅ Extractor initialized")

        our_result = extractor.extract_clauses_and_relationships(test_text, "rental")

        print("✅ Our implementation succeeded")
        print(f"   Clauses: {len(our_result.extracted_clauses)}")
        print(f"   Relationships: {len(our_result.clause_relationships)}")

    except Exception as e:
        print(f"❌ Our implementation failed: {e}")
        print("   This suggests the issue is in our custom logic")

def test_minimal_our_implementation():
    """Test our implementation with minimal configuration"""

    print("\n🔧 MINIMAL CONFIGURATION TEST")
    print("=" * 50)

    # Create minimal extractor with simpler config
    from improved_legal_extractor import ImprovedLegalDocumentExtractor as LegalDocumentExtractor

    # Temporarily modify the config to be minimal
    original_configs = LegalDocumentExtractor._initialize_extraction_configs

    def minimal_configs(self):
        return {
            "rental": {
                "model_id": "gemini-2.5-flash",
                "extraction_passes": 1,  # Minimal passes
                "max_char_buffer": 1000,  # Smaller buffer
                "max_workers": 1,
                "temperature": 0.1,
                "fence_output": False,
                "prompts": "Extract landlord, tenant, rent amount, and property from this rental agreement.",
                "examples": [
                    lx.data.ExampleData(
                        text="John rents apartment from Mary for $1,000 monthly.",
                        extractions=[
                            lx.data.Extraction(
                                extraction_class="party_lessor",
                                extraction_text="Mary",
                                attributes={"role": "landlord"}
                            ),
                            lx.data.Extraction(
                                extraction_class="party_lessee",
                                extraction_text="John",
                                attributes={"role": "tenant"}
                            ),
                            lx.data.Extraction(
                                extraction_class="financial_terms",
                                extraction_text="$1,000 monthly",
                                attributes={"amount": 1000}
                            )
                        ]
                    )
                ]
            }
        }

    # Monkey patch for testing
    LegalDocumentExtractor._initialize_extraction_configs = minimal_configs

    try:
        extractor = LegalDocumentExtractor()

        test_text = "John Smith rents apartment 5B from ABC Properties for $2,500 monthly."

        print("📝 Minimal test text:", test_text)
        print(f"📝 Text length: {len(test_text)} characters")

        result = extractor.extract_clauses_and_relationships(test_text, "rental")

        print("✅ Minimal configuration succeeded")
        print(f"   Clauses: {len(result.extracted_clauses)}")
        print(f"   Relationships: {len(result.clause_relationships)}")

    except Exception as e:
        print(f"❌ Minimal configuration failed: {e}")

    finally:
        # Restore original method
        LegalDocumentExtractor._initialize_extraction_configs = original_configs

if __name__ == "__main__":
    # Compare implementations
    test_our_vs_basic()

    # Test minimal configuration
    test_minimal_our_implementation()

    print("\n📋 ANALYSIS:")
    print("   If basic LangExtract works but our implementation fails,")
    print("   the issue is in our custom examples, prompts, or processing logic.")
    print("   If both fail, it's an API or library issue.")
