#!/usr/bin/env python3
"""
Debug MongoDB Service Test
"""

import asyncio
import aiohttp
import json

async def debug_mongodb_service():
    """Debug the MongoDB service"""
    
    print("🧪 MongoDB Service Debug Test")
    print("=" * 35)
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test extraction with debug logging
            user_id = "debug_mongodb_service_789"
            test_data = {
                "document_text": "This is a test rental agreement for debugging MongoDB storage. The tenant John Smith agrees to rent from landlord Jane Doe.",
                "document_type": "rental_agreement",
                "user_id": user_id
            }
            
            print("📤 Step 1: Performing extraction with detailed logging...")
            print(f"   👤 User ID: {user_id}")
            print(f"   📝 Document Type: {test_data['document_type']}")
            
            # Make extraction request
            async with session.post(
                "http://localhost:8000/api/extractor/extract",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"\n📥 Response Status: {response.status}")
                response_data = await response.json()
                
                if response_data.get('success'):
                    document_id = response_data.get('data', {}).get('document_id')
                    print(f"   ✅ Extraction successful!")
                    print(f"   🆔 Document ID: {document_id}")
                    
                    extraction_data = response_data.get('data', {})
                    print(f"   📊 Extraction Results:")
                    print(f"      🔍 Clauses: {len(extraction_data.get('extracted_clauses', []))}")
                    print(f"      🔗 Relationships: {len(extraction_data.get('clause_relationships', []))}")
                    print(f"      💯 Confidence: {extraction_data.get('confidence_score', 'N/A')}")
                    
                    # Check if MongoDB service is working by testing direct insertion
                    print(f"\n📊 Step 2: Testing direct MongoDB connection...")
                    
                    # Try to access the health endpoint to check MongoDB service
                    async with session.get("http://localhost:8000/health") as health_response:
                        if health_response.status == 200:
                            health_data = await health_response.json()
                            config = health_data.get('configuration', {})
                            print(f"   ✅ API Health: OK")
                            print(f"   🗄️ MongoDB DB: {config.get('mongo_db', 'N/A')}")
                        else:
                            print(f"   ❌ API Health: Status {health_response.status}")
                    
                    print(f"\n⏱️  Step 3: Waiting 5 seconds for any background processing...")
                    await asyncio.sleep(5)
                    
                    # Try to retrieve the document
                    print(f"📥 Step 4: Attempting to retrieve from MongoDB...")
                    
                    async with session.get(
                        f"http://localhost:8000/api/extractor/results/{document_id}?user_id={user_id}"
                    ) as retrieve_response:
                        print(f"   📊 Retrieval Status: {retrieve_response.status}")
                        
                        if retrieve_response.status == 200:
                            retrieve_data = await retrieve_response.json()
                            if retrieve_data.get('success'):
                                print(f"   ✅ Document found in MongoDB!")
                                stored_data = retrieve_data.get('data', {})
                                print(f"   📋 Stored Data Preview:")
                                print(f"      🆔 ID: {stored_data.get('document_id', 'N/A')}")
                                print(f"      📝 Type: {stored_data.get('document_type', 'N/A')}")
                                print(f"      📄 Filename: {stored_data.get('original_filename', 'N/A')}")
                                print(f"      🕒 Created: {stored_data.get('created_at', 'N/A')}")
                            else:
                                print(f"   ❌ Retrieval failed: {retrieve_data.get('error', 'Unknown')}")
                        elif retrieve_response.status == 404:
                            print(f"   ❌ Document not found in MongoDB (404)")
                            print(f"      This confirms the document was not stored")
                        else:
                            retrieve_text = await retrieve_response.text()
                            print(f"   ❌ Unexpected retrieval status: {retrieve_text}")
                    
                    # List all documents to see what's actually in MongoDB
                    print(f"\n📋 Step 5: Listing all documents for user...")
                    async with session.get(
                        f"http://localhost:8000/api/extractor/documents?user_id={user_id}&limit=20"
                    ) as list_response:
                        if list_response.status == 200:
                            list_data = await list_response.json()
                            if list_data.get('success'):
                                documents = list_data.get('data', {}).get('documents', [])
                                print(f"   📊 Total documents in MongoDB: {len(documents)}")
                                
                                if documents:
                                    for i, doc in enumerate(documents):
                                        print(f"      📄 Document {i+1}:")
                                        print(f"         🆔 ID: {doc.get('document_id', 'N/A')}")
                                        print(f"         📝 Type: {doc.get('document_type', 'N/A')}")
                                        print(f"         🕒 Created: {doc.get('created_at', 'N/A')}")
                                else:
                                    print(f"   ❌ No documents found for user {user_id}")
                            else:
                                print(f"   ❌ List failed: {list_data.get('error', 'Unknown')}")
                        else:
                            print(f"   ❌ List request failed: Status {list_response.status}")
                else:
                    print(f"   ❌ Extraction failed: {response_data.get('error', 'Unknown')}")
                    print(f"   📋 Full Response: {json.dumps(response_data, indent=2)}")
                    
    except Exception as e:
        print(f"\n💥 Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_mongodb_service())