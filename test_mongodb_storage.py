#!/usr/bin/env python3
"""
Test MongoDB Storage After Extraction
"""

import asyncio
import aiohttp
import json
import time

async def test_mongodb_storage():
    """Test if extraction results are stored in MongoDB"""
    
    print("🧪 MongoDB Storage Test")
    print("=" * 30)
    
    # Step 1: Perform extraction
    user_id = "mongodb_test_user_456"
    test_data = {
        "document_text": "This is a loan agreement between ABC Bank (lender) and John Smith (borrower). The loan amount is $10,000 with 8% interest rate. The loan term is 24 months.",
        "document_type": "loan_agreement",
        "user_id": user_id
    }
    
    document_id = None
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📤 Step 1: Performing extraction...")
            
            async with session.post(
                "http://localhost:8000/api/extractor/extract",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_data = await response.json()
                
                if response_data.get('success'):
                    document_id = response_data.get('data', {}).get('document_id')
                    print(f"   ✅ Extraction successful! Document ID: {document_id}")
                    print(f"   📊 Clauses found: {len(response_data.get('data', {}).get('extracted_clauses', []))}")
                else:
                    print(f"   ❌ Extraction failed: {response_data.get('error')}")
                    return
            
            print("\n⏱️  Waiting 3 seconds for MongoDB write...")
            await asyncio.sleep(3)
            
            # Step 2: Try to retrieve from MongoDB  
            print("📥 Step 2: Checking MongoDB storage...")
            
            async with session.get(
                f"http://localhost:8000/api/extractor/results/{document_id}?user_id={user_id}"
            ) as response:
                print(f"   📊 Status: {response.status}")
                
                if response.status == 200:
                    response_data = await response.json()
                    
                    if response_data.get('success'):
                        stored_data = response_data.get('data', {})
                        print(f"   ✅ Found in MongoDB!")
                        print(f"      🆔 Document ID: {stored_data.get('document_id', 'N/A')}")
                        print(f"      👤 User ID: {stored_data.get('user_id', 'N/A')}")
                        print(f"      📝 Document Type: {stored_data.get('document_type', 'N/A')}")
                        print(f"      📄 Original Filename: {stored_data.get('original_filename', 'N/A')}")
                        print(f"      🕒 Created At: {stored_data.get('created_at', 'N/A')}")
                        
                        # Check extraction results
                        extraction_result = stored_data.get('extraction_result', {})
                        if extraction_result:
                            clauses = extraction_result.get('extracted_clauses', [])
                            print(f"      🔍 Stored Clauses: {len(clauses)}")
                            if clauses:
                                first_clause = clauses[0]
                                print(f"         📋 First Clause ID: {first_clause.get('clause_id', 'N/A')}")
                                print(f"         📝 First Clause Type: {first_clause.get('clause_type', 'N/A')}")
                        
                    else:
                        print(f"   ❌ MongoDB response failed: {response_data.get('error')}")
                        
                elif response.status == 404:
                    print(f"   ❌ Document not found in MongoDB (404)")
                    print(f"      This suggests the extraction result was not stored")
                    
                else:
                    response_text = await response.text()
                    print(f"   ❌ Unexpected status {response.status}: {response_text}")
            
            # Step 3: List documents for the user
            print("\n📋 Step 3: Listing all documents for user...")
            
            async with session.get(
                f"http://localhost:8000/api/extractor/documents?user_id={user_id}&limit=10"
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    if response_data.get('success'):
                        documents = response_data.get('data', {}).get('documents', [])
                        print(f"   📊 Total documents found: {len(documents)}")
                        
                        for i, doc in enumerate(documents):
                            print(f"      📄 Document {i+1}:")
                            print(f"         🆔 ID: {doc.get('document_id', 'N/A')}")
                            print(f"         📝 Type: {doc.get('document_type', 'N/A')}")
                            print(f"         🕒 Created: {doc.get('created_at', 'N/A')}")
                    else:
                        print(f"   ❌ Failed to list documents: {response_data.get('error')}")
                else:
                    print(f"   ❌ Failed to list documents: Status {response.status}")
                    
    except Exception as e:
        print(f"\n💥 Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_mongodb_storage())