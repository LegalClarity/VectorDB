#!/usr/bin/env python3
"""
Test MongoDB storage by checking retrieval after extraction
"""

import requests
import time

def test_mongodb_storage():
    """Test if documents are being stored in MongoDB"""
    
    print("🔍 Testing MongoDB storage...")
    
    # Step 1: Extract a document
    test_request = {
        "document_text": "RENTAL AGREEMENT\n\nTenant: John Doe\nRent: $1200/month",
        "document_type": "rental_agreement", 
        "user_id": "storage_test_user",
        "document_id": "storage_test_doc"
    }
    
    print("📤 Step 1: Extracting document...")
    response = requests.post(
        "http://localhost:8000/api/extractor/extract",
        json=test_request,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ Extraction failed: {response.status_code}")
        print(response.text)
        return
    
    extraction_result = response.json()
    document_id = extraction_result["data"]["document_id"]
    print(f"✅ Extraction successful, Document ID: {document_id}")
    
    # Wait a moment for async storage
    time.sleep(1)
    
    # Step 2: Try to retrieve the document
    print("\n📥 Step 2: Retrieving document from MongoDB...")
    retrieval_response = requests.get(
        f"http://localhost:8000/api/analyzer/results/{document_id}?user_id={test_request['user_id']}"
    )
    
    print(f"📊 Retrieval Status: {retrieval_response.status_code}")
    
    if retrieval_response.status_code == 200:
        print("✅ Document found in MongoDB!")
        retrieved_doc = retrieval_response.json()
        print(f"Retrieved Document ID: {retrieved_doc.get('document_id', 'N/A')}")
    elif retrieval_response.status_code == 404:
        print("❌ Document not found in MongoDB - storage failed!")
    elif retrieval_response.status_code == 500:
        print("❌ Server error during retrieval")
        print(f"Response: {retrieval_response.text}")
    else:
        print(f"❓ Unexpected status: {retrieval_response.status_code}")
        print(f"Response: {retrieval_response.text}")
    
    # Step 3: Check database health
    print("\n🏥 Step 3: Checking MongoDB health...")
    health_response = requests.get("http://localhost:8000/api/analyzer/health")
    
    if health_response.status_code == 200:
        health = health_response.json()
        mongodb_health = health.get("mongodb", {})
        print(f"MongoDB Status: {mongodb_health.get('status', 'unknown')}")
        print(f"Database: {mongodb_health.get('database', 'unknown')}")
    else:
        print(f"Health check failed: {health_response.status_code}")

if __name__ == "__main__":
    test_mongodb_storage()