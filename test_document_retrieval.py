#!/usr/bin/env python3
"""
Test script to verify document retrieval flow from MongoDB and GCS
Using the provided document ID: c0133bb6-f25a-4114-a4c3-1b1e8630e27f
"""

import os
import asyncio
import json
from pymongo import MongoClient
from google.cloud import storage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_document_retrieval(document_id: str):
    """Test the complete document retrieval flow"""
    
    print(f"🔍 Testing document retrieval for ID: {document_id}")
    
    # Test 1: MongoDB Connection and Document Lookup
    print("\n1. Testing MongoDB connection...")
    try:
        mongo_uri = os.getenv('MONGO_URI')
        mongo_db = os.getenv('MONGO_DB')
        mongo_docs_collection = os.getenv('MONGO_DOCS_COLLECTION')
        
        if not all([mongo_uri, mongo_db, mongo_docs_collection]):
            print("❌ Missing MongoDB environment variables")
            return
        
        print(f"   URI: {mongo_uri}")
        print(f"   DB: {mongo_db}")
        print(f"   Collection: {mongo_docs_collection}")
        
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[mongo_db]
        collection = db[mongo_docs_collection]
        
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        # Look up the document
        print(f"\n2. Looking up document with ID: {document_id}")
        query = {"document_id": document_id}
        document = collection.find_one(query)
        
        if not document:
            print("❌ Document not found in MongoDB")
            return
        
        print("✅ Document found in MongoDB!")
        print("   Document details:")
        print(f"     - Original filename: {document.get('original_filename')}")
        print(f"     - Stored filename: {document.get('stored_filename')}")
        print(f"     - GCS bucket: {document.get('gcs_bucket_name')}")
        print(f"     - GCS path: {document.get('gcs_object_path')}")
        print(f"     - File size: {document.get('file_metadata', {}).get('file_size')} bytes")
        print(f"     - Content type: {document.get('file_metadata', {}).get('content_type')}")
        print(f"     - Upload status: {document.get('status', {}).get('upload_status')}")
        print(f"     - Processing status: {document.get('status', {}).get('processing_status')}")
        
    except Exception as e:
        print(f"❌ MongoDB error: {e}")
        return
    
    # Test 2: Google Cloud Storage Access
    print("\n3. Testing GCS access...")
    try:
        gcs_bucket_name = document.get('gcs_bucket_name')
        gcs_object_path = document.get('gcs_object_path')
        
        if not gcs_bucket_name or not gcs_object_path:
            print("❌ Missing GCS bucket or object path in document")
            return
        
        # Initialize GCS client
        service_account_path = os.getenv('GCS_SERVICE_ACCOUNT_PATH', 'service-account.json')
        if os.path.exists(service_account_path):
            print(f"   Using service account: {service_account_path}")
            gcs_client = storage.Client.from_service_account_json(service_account_path)
        else:
            print("   Using default credentials")
            gcs_client = storage.Client()
        
        # Get bucket
        bucket = gcs_client.bucket(gcs_bucket_name)
        print(f"✅ GCS bucket '{gcs_bucket_name}' accessible")
        
        # Check if object exists
        blob = bucket.blob(gcs_object_path)
        if not blob.exists():
            print(f"❌ Object '{gcs_object_path}' not found in bucket")
            return
        
        print(f"✅ Object '{gcs_object_path}' found in GCS!")
        
        # Get object metadata
        blob.reload()
        print("   Object details:")
        print(f"     - Size: {blob.size} bytes")
        print(f"     - Content type: {blob.content_type}")
        print(f"     - Created: {blob.time_created}")
        print(f"     - Updated: {blob.updated}")
        
        # Test download (first few bytes)
        print("\n4. Testing file download...")
        content_sample = blob.download_as_bytes(start=0, end=1023)  # First 1KB
        print(f"✅ Successfully downloaded first {len(content_sample)} bytes")
        print(f"   Content preview: {content_sample[:100]}...")
        
    except Exception as e:
        print(f"❌ GCS error: {e}")
        return
    
    # Test 3: Environment Variables Check
    print("\n5. Checking required environment variables...")
    required_vars = [
        'MONGO_URI', 'MONGO_DB', 'MONGO_DOCS_COLLECTION', 'MONGO_PROCESSED_DOCS_COLLECTION',
        'USER_DOC_BUCKET', 'GOOGLE_PROJECT_ID', 'GEMINI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 10)}")
        else:
            missing_vars.append(var)
            print(f"❌ {var}: Not set")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
    else:
        print("\n✅ All required environment variables are set!")
    
    print("\n🎉 Document retrieval flow test completed!")
    
    return document

def test_langextract_import():
    """Test LangExtract import and basic setup"""
    print("\n6. Testing LangExtract import and setup...")
    
    try:
        import langextract as lx
        print("✅ LangExtract imported successfully")
        
        # Check API key
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('LANGEXTRACT_API_KEY')
        if api_key:
            print("✅ API key is available")
            os.environ['LANGEXTRACT_API_KEY'] = api_key
        else:
            print("❌ No API key found (GEMINI_API_KEY or LANGEXTRACT_API_KEY)")
        
        # Test basic extraction (if API key available)
        if api_key:
            print("   Testing basic extraction...")
            try:
                result = lx.extract(
                    text_or_documents="John Smith rents apartment for $1200/month from Jane Doe.",
                    prompt_description="Extract landlord and tenant names with rental amount",
                    examples=[
                        lx.data.ExampleData(
                            text="Alice rents house for $800 from Bob",
                            extractions=[
                                lx.data.Extraction(
                                    extraction_class="tenant",
                                    extraction_text="Alice",
                                    attributes={"role": "tenant"}
                                ),
                                lx.data.Extraction(
                                    extraction_class="landlord", 
                                    extraction_text="Bob",
                                    attributes={"role": "landlord"}
                                ),
                                lx.data.Extraction(
                                    extraction_class="rent_amount",
                                    extraction_text="$800",
                                    attributes={"currency": "USD"}
                                )
                            ]
                        )
                    ],
                    model_id="gemini-2.5-flash"
                )
                print(f"✅ Basic extraction successful: {len(result.extractions)} entities found")
                for extraction in result.extractions:
                    print(f"     - {extraction.extraction_class}: '{extraction.extraction_text}'")
            except Exception as e:
                print(f"❌ Basic extraction failed: {e}")
        
    except ImportError as e:
        print(f"❌ LangExtract import failed: {e}")
    except Exception as e:
        print(f"❌ LangExtract setup error: {e}")

async def main():
    """Main test function"""
    document_id = "c0133bb6-f25a-4114-a4c3-1b1e8630e27f"
    
    print("🚀 Legal Clarity API - Document Retrieval Flow Test")
    print("=" * 60)
    
    # Test document retrieval flow
    document = await test_document_retrieval(document_id)
    
    # Test LangExtract setup
    test_langextract_import()
    
    if document:
        print(f"\n📄 Document Summary:")
        print(f"   ID: {document.get('document_id')}")
        print(f"   File: {document.get('original_filename')}")
        print(f"   Size: {document.get('file_metadata', {}).get('file_size')} bytes")
        print(f"   Type: {document.get('file_metadata', {}).get('content_type')}")
        print(f"   Status: {document.get('status', {}).get('processing_status')}")

if __name__ == "__main__":
    asyncio.run(main())