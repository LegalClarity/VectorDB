#!/usr/bin/env python3
"""
Test extraction with improved logging to identify MongoDB storage issue
"""

import asyncio
import json
import requests
import time

def test_extraction_with_logging():
    """Test the extraction endpoint with detailed logging"""
    
    print("🔍 Testing extraction with improved logging...")
    
    # Test data
    test_request = {
        "document_text": """
        RENTAL AGREEMENT
        
        Property Address: 123 Main Street, Suite 4B, Anytown, ST 12345
        Tenant: John Doe
        Landlord: ABC Property Management LLC
        
        1. RENT: The monthly rent is $1,200, due on the 1st of each month.
        2. SECURITY DEPOSIT: Tenant shall pay a security deposit of $1,200.
        3. LEASE TERM: This lease begins on January 1, 2024 and ends on December 31, 2024.
        4. PET POLICY: No pets allowed without written consent.
        5. UTILITIES: Tenant is responsible for electricity and water.
        
        Tenant signature: _________________ Date: _____________
        Landlord signature: _______________ Date: _____________
        """,
        "document_type": "rental_agreement",
        "user_id": "test_user_123",
        "document_id": "test_rental_doc_001"
    }
    
    try:
        # Make the API request
        print("📤 Sending extraction request...")
        response = requests.post(
            "http://localhost:8000/api/extractor/extract",
            json=test_request,
            timeout=30
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Extraction successful!")
            print(f"📋 Document ID: {result.get('document_id', 'N/A')}")
            print(f"💯 Confidence Score: {result.get('confidence_score', 'N/A')}")
            print(f"🔍 Clauses Found: {len(result.get('extracted_clauses', []))}")
            print(f"🔗 Relationships Found: {len(result.get('clause_relationships', []))}")
            
            # Now test retrieval to see if it was stored
            print("\n🔍 Testing document retrieval...")
            retrieval_response = requests.get(
                f"http://localhost:8000/api/analyzer/results/{test_request['document_id']}?user_id={test_request['user_id']}"
            )
            
            print(f"📊 Retrieval Status: {retrieval_response.status_code}")
            
            if retrieval_response.status_code == 200:
                print("✅ Document successfully stored and retrieved from MongoDB!")
                stored_doc = retrieval_response.json()
                print(f"📋 Stored Document ID: {stored_doc.get('document_id', 'N/A')}")
            elif retrieval_response.status_code == 404:
                print("❌ Document not found in MongoDB - storage failed!")
                print("🔍 This confirms the MongoDB insertion is not working")
            else:
                print(f"❓ Unexpected retrieval status: {retrieval_response.status_code}")
                print(f"Response: {retrieval_response.text}")
                
        else:
            print(f"❌ Extraction failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    test_extraction_with_logging()