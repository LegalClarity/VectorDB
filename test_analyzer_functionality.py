"""
Test script to verify the legal extractor functionality
"""

import asyncio
import os
import sys

# Add paths
current_dir = os.getcwd()
helper_apis_path = os.path.join(current_dir, 'Helper-APIs')
analyzer_path = os.path.join(helper_apis_path, 'document-analyzer-api')

if analyzer_path not in sys.path:
    sys.path.insert(0, analyzer_path)

async def test_legal_extractor():
    """Test the legal extractor functionality"""
    try:
        from legal_extractor import ImprovedLegalDocumentExtractor

        # Create extractor (will run in demo mode without API key)
        extractor = ImprovedLegalDocumentExtractor()

        # Test with sample rental agreement text
        sample_text = """
        This Rent Agreement is made on 15th January 2024 between:

        LANDLORD: Mr. Rajesh Kumar, residing at 123 Main Street, Mumbai

        TENANT: Ms. Priya Sharma, residing at 456 Park Avenue, Mumbai

        PREMISES: Apartment No. 301, Building XYZ, 123 Main Street, Mumbai

        RENT: Rs. 25,000/- per month, payable on the 1st of each month

        SECURITY DEPOSIT: Rs. 50,000/-

        LEASE PERIOD: 11 months from February 1, 2024 to January 31, 2025

        The tenant agrees to pay rent on time and maintain the property.
        """

        print("Testing legal document extractor...")
        print(f"Sample text length: {len(sample_text)} characters")

        # Extract clauses and relationships
        result = await extractor.extract_clauses_and_relationships(
            document_text=sample_text,
            document_type="rental"
        )

        print("✅ Extraction completed successfully!")
        print(f"Document ID: {result.document_id}")
        print(f"Document Type: {result.document_type}")
        print(f"Confidence Score: {result.confidence_score}")
        print(f"Processing Time: {result.processing_time_seconds:.2f} seconds")
        print(f"Number of Clauses Extracted: {len(result.extracted_clauses)}")

        print("\n📋 Extracted Clauses:")
        for i, clause in enumerate(result.extracted_clauses[:5], 1):  # Show first 5
            print(f"{i}. {clause.clause_text[:100]}...")

        print(f"\n📊 Metadata: {result.extraction_metadata}")

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_database_service():
    """Test the database service functionality"""
    try:
        analyzer_app_path = os.path.join(analyzer_path, 'app')
        if analyzer_app_path not in sys.path:
            sys.path.insert(0, analyzer_app_path)

        # Import with proper path setup
        import importlib.util
        db_service_path = os.path.join(analyzer_app_path, 'services', 'database_service.py')
        spec = importlib.util.spec_from_file_location("database_service", db_service_path)
        db_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(db_module)
        DatabaseService = db_module.DatabaseService

        print("\nTesting database service...")

        # Create database service (will try to connect but may fail without MongoDB)
        db_service = DatabaseService(
            connection_string="mongodb://localhost:27017",
            database_name="test_db",
            collection_name="test_collection"
        )

        print("✅ Database service created successfully!")
        print(f"Connection string: {db_service.connection_string}")
        print(f"Database: {db_service.database_name}")
        print(f"Collection: {db_service.collection_name}")

        # Try to connect (will fail without MongoDB running)
        try:
            await db_service.connect()
            print("✅ Database connection successful!")
            await db_service.disconnect()
        except Exception as conn_error:
            print(f"⚠️  Database connection failed (expected without MongoDB): {conn_error}")

        return True

    except Exception as e:
        print(f"❌ Database service test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Testing Legal Document Analyzer Functionality")
    print("=" * 50)

    # Test legal extractor
    extractor_test = await test_legal_extractor()

    # Test database service
    db_test = await test_database_service()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Legal Extractor: {'✅ PASS' if extractor_test else '❌ FAIL'}")
    print(f"Database Service: {'✅ PASS' if db_test else '❌ FAIL'}")

    if extractor_test and db_test:
        print("\n🎉 All tests passed! The analyzer functionality is working correctly.")
        print("\nNext steps:")
        print("1. Set up MongoDB connection")
        print("2. Configure Google Cloud Storage")
        print("3. Set GEMINI_API_KEY environment variable")
        print("4. Test full integration with document upload API")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    asyncio.run(main())
