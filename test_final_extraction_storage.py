#!/usr/bin/env python3
"""
Test MongoDB storage using the correct extraction retrieval endpoint
"""

import requests
import time

def test_extraction_storage():
    """Test if documents are being stored via extraction endpoint"""
    
    print("🔍 Testing extraction and MongoDB storage...")
    
    # Step 1: Extract a document
    test_request = {
        "document_text": """
        RENTAL AGREEMENT
        
        This rental agreement is between John Doe (Tenant) and ABC Property Management (Landlord).
        
        Property: 123 Main Street, Apt 4B, Anytown, ST 12345
        
        TERMS:
        1. RENT: Monthly rent is $1,200, due on the 1st of each month.
        2. SECURITY DEPOSIT: Tenant shall pay $1,200 security deposit.
        3. LEASE TERM: 12 months starting January 1, 2024.
        4. UTILITIES: Tenant responsible for electricity and gas.
        5. PETS: No pets allowed without written permission.
        
        Tenant Signature: _________________ Date: _____________
        Landlord Signature: _______________ Date: _____________
        """,
        "document_type": "rental_agreement",
        "user_id": "final_test_user",
        "document_id": "final_test_document"
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
    confidence_score = extraction_result["data"]["confidence_score"]
    clauses_count = len(extraction_result["data"]["extracted_clauses"])
    
    print(f"✅ Extraction successful!")
    print(f"📋 Document ID: {document_id}")
    print(f"💯 Confidence Score: {confidence_score}")
    print(f"🔍 Clauses Found: {clauses_count}")
    
    # Wait a moment for async storage
    print("\n⏳ Waiting for storage to complete...")
    time.sleep(2)
    
    # Step 2: Try to retrieve using the correct extractor endpoint
    print("\n📥 Step 2: Retrieving document using extractor endpoint...")
    retrieval_response = requests.get(
        f"http://localhost:8000/api/extractor/results/{document_id}?user_id={test_request['user_id']}"
    )
    
    print(f"📊 Retrieval Status: {retrieval_response.status_code}")
    
    if retrieval_response.status_code == 200:
        print("✅ Document found in MongoDB!")
        retrieved_doc = retrieval_response.json()
        print(f"Retrieved Document ID: {retrieved_doc['data'].get('document_id', 'N/A')}")
        print(f"Retrieved Confidence: {retrieved_doc['data'].get('confidence_score', 'N/A')}")
        print(f"Retrieved Clauses: {len(retrieved_doc['data'].get('extracted_clauses', []))}")
        print("\n🎉 SUCCESS: Document extraction and MongoDB storage working correctly!")
        
    elif retrieval_response.status_code == 404:
        print("❌ Document not found in MongoDB - storage failed!")
        print("🔍 MongoDB insertion is not working properly")
        
    elif retrieval_response.status_code == 500:
        print("❌ Server error during retrieval")
        print(f"Response: {retrieval_response.text}")
        
    else:
        print(f"❓ Unexpected status: {retrieval_response.status_code}")
        print(f"Response: {retrieval_response.text}")
    
    # Step 3: Check extractor health
    print("\n🏥 Step 3: Checking extractor health...")
    health_response = requests.get("http://localhost:8000/api/extractor/health")
    
    if health_response.status_code == 200:
        health = health_response.json()
        print(f"Extractor Status: {health.get('status', 'unknown')}")
        print(f"Service: {health.get('service', 'unknown')}")
        mongodb_status = health.get('mongodb', {}).get('status', 'unknown')
        print(f"MongoDB Status: {mongodb_status}")
    else:
        print(f"Health check failed: {health_response.status_code}")

if __name__ == "__main__":
    test_extraction_storage()