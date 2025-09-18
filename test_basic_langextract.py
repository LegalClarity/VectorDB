"""
Test basic LangExtract functionality to isolate the issue
Using the exact example from LangExtract documentation
"""

import os
from dotenv import load_dotenv
import langextract as lx

# Load environment variables
load_dotenv()

def test_basic_langextract():
    """Test the most basic LangExtract functionality"""

    print("🧪 BASIC LANGEXTRACT TEST")
    print("=" * 40)

    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        return

    print(f"✅ GEMINI_API_KEY loaded: {api_key[:10]}...")

    # Use the EXACT example from LangExtract documentation
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

    print("📝 Test text:", input_text)
    print(f"📝 Text length: {len(input_text)} characters")

    try:
        print("🔄 Calling basic LangExtract...")
        result = lx.extract(
            text_or_documents=input_text,
            prompt_description=prompt,
            examples=examples,
            model_id="gemini-2.5-flash",
            api_key=api_key
        )

        print("✅ SUCCESS! Basic LangExtract worked")
        print(f"   Extractions: {len(result.extractions) if result.extractions else 0}")

        # Show results
        if result.extractions:
            for i, extraction in enumerate(result.extractions):
                print(f"   {i+1}. {extraction.extraction_class}: '{extraction.extraction_text}'")
                if extraction.attributes:
                    for key, value in extraction.attributes.items():
                        print(f"      {key}: {value}")

        return True

    except Exception as e:
        print(f"❌ Basic LangExtract failed: {e}")
        print("   This indicates an issue with:")
        print("   - API key validity")
        print("   - Network connectivity")
        print("   - LangExtract library installation")
        print("   - Gemini API access")
        return False

def test_with_shorter_legal_text():
    """Test with a very short legal text using basic extraction"""

    print("\n📄 SHORT LEGAL TEXT TEST")
    print("=" * 40)

    # Very short legal text
    legal_text = "John Smith agrees to rent apartment 5B from ABC Properties for $2,500 monthly."

    prompt = "Extract parties, amounts, and property details."

    examples = [
        lx.data.ExampleData(
            text="Jane Doe rents apartment 3A from XYZ Corp for $1,800 per month.",
            extractions=[
                lx.data.Extraction(
                    extraction_class="party",
                    extraction_text="Jane Doe",
                    attributes={"role": "tenant"}
                ),
                lx.data.Extraction(
                    extraction_class="party",
                    extraction_text="XYZ Corp",
                    attributes={"role": "landlord"}
                ),
                lx.data.Extraction(
                    extraction_class="amount",
                    extraction_text="$1,800 per month",
                    attributes={"type": "rent", "frequency": "monthly"}
                )
            ]
        )
    ]

    print("📝 Legal text:", legal_text)
    print(f"📝 Text length: {len(legal_text)} characters")

    try:
        api_key = os.getenv('GEMINI_API_KEY')
        result = lx.extract(
            text_or_documents=legal_text,
            prompt_description=prompt,
            examples=examples,
            model_id="gemini-2.5-flash",
            api_key=api_key
        )

        print("✅ SUCCESS! Short legal text extraction worked")
        print(f"   Extractions: {len(result.extractions) if result.extractions else 0}")

        if result.extractions:
            for i, extraction in enumerate(result.extractions):
                print(f"   {i+1}. {extraction.extraction_class}: '{extraction.extraction_text}'")

        return True

    except Exception as e:
        print(f"❌ Short legal text extraction failed: {e}")
        return False

if __name__ == "__main__":
    # Test basic functionality first
    basic_success = test_basic_langextract()

    if basic_success:
        # Test with short legal text
        legal_success = test_with_shorter_legal_text()

        if legal_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("   ✅ LangExtract is working correctly")
            print("   ✅ Gemini API access confirmed")
            print("   ✅ Basic legal text extraction functional")
        else:
            print("\n⚠️ BASIC TEST PASSED, but legal text extraction failed")
            print("   This suggests an issue with our legal examples or prompts")
    else:
        print("\n❌ BASIC LANGEXTRACT TEST FAILED")
        print("   Check API key, network, and LangExtract installation")
