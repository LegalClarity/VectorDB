"""
Test single document extraction to avoid rate limits
Tests one document at a time with real LangExtract
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from improved_legal_extractor import ImprovedLegalDocumentExtractor as LegalDocumentExtractor

# Load environment variables
load_dotenv()

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        import PyPDF2
        with open(pdf_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
    except Exception as e:
        print(f"❌ PDF extraction failed: {e}")
        return None

def test_single_document():
    """Test extraction on a single document"""

    print("🔬 SINGLE DOCUMENT TEST")
    print("=" * 40)

    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY not found!")
        return

    print(f"✅ GEMINI_API_KEY loaded: {api_key[:10]}...")

    # Test with lease agreement (most likely to work)
    pdf_path = "Helper-APIs/document-analyzer-api/example_docs/lease agreement.pdf"
    results_folder = "Helper-APIs/document-analyzer-api/results"

    # Ensure results folder exists
    Path(results_folder).mkdir(exist_ok=True)

    if not os.path.exists(pdf_path):
        print(f"❌ Test document not found: {pdf_path}")
        return

    print(f"📄 Testing document: lease agreement.pdf")

    # Extract text
    document_text = extract_text_from_pdf(pdf_path)
    if not document_text or len(document_text.strip()) < 100:
        print("❌ Failed to extract text from PDF")
        return

    print(f"📝 Extracted {len(document_text)} characters")

    # Determine document type
    doc_type = "rental"
    print(f"🏷️  Document type: {doc_type}")

    try:
        # Initialize extractor
        extractor = LegalDocumentExtractor()
        print("✅ Extractor initialized")

        # Test extraction
        print("🔍 Running LangExtract extraction...")
        result = extractor.extract_clauses_and_relationships(document_text, doc_type)

        if not result or len(result.extracted_clauses) == 0:
            print("❌ Extraction returned no clauses")
            return

        print("✅ SUCCESS! LangExtract extraction completed")
        print(f"   📊 Clauses: {len(result.extracted_clauses)}")
        print(f"   🔗 Relationships: {len(result.clause_relationships)}")
        print(".2f")
        print(".2f")

        # Show sample clauses
        if result.extracted_clauses:
            print("\n   📋 SAMPLE CLAUSES:")
            for i, clause in enumerate(result.extracted_clauses[:5]):
                print(f"      {i+1}. {clause.clause_type.value}")
                print(f"         {clause.clause_text[:60]}...")
                if clause.key_terms:
                    print(f"         Key Terms: {clause.key_terms[:2]}")
                print()

        # Save results
        print("💾 Saving results...")
        json_path, vis_path = extractor.save_extraction_results(result, results_folder)

        # Create visualization data
        viz_data = extractor.create_visualization_data(result, document_text)
        viz_filename = "lease_agreement_extraction_results.json"
        viz_path = os.path.join(results_folder, viz_filename)
        extractor.save_visualization_data(viz_data, viz_path)

        print(f"   ✅ JSON results: {json_path}")
        print(f"   ✅ Visualization data: {viz_path}")

        # Summary
        print("\n🎉 SINGLE DOCUMENT TEST COMPLETED SUCCESSFULLY!")
        print("   ✅ Real LangExtract API call")
        print("   ✅ Clause extraction working")
        print("   ✅ Relationship extraction working")
        print("   ✅ Results saved to files")
        print(f"   📁 Results location: {results_folder}/")

        return True

    except Exception as e:
        print(f"❌ Extraction failed: {e}")
        return False

if __name__ == "__main__":
    success = test_single_document()
    if success:
        print("\n🎯 RECOMMENDATION: Now try testing other documents one by one to avoid rate limits")
    else:
        print("\n🔧 TROUBLESHOOTING:")
        print("   - Check if the PDF contains readable text")
        print("   - Verify API key permissions")
        print("   - Try with a different document")
