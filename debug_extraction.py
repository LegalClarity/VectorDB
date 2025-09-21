#!/usr/bin/env python3
"""
Debug Extraction Test - Check what's actually happening
"""

import asyncio
import aiohttp
import json

async def debug_extraction():
    """Debug the extraction process"""
    
    print("🔍 Debug Extraction Test")
    print("=" * 30)
    
    # Test data
    user_id = "debug_user_123"
    test_data = {
        "document_text": "This is a rental agreement between John Doe (landlord) and Jane Smith (tenant). The monthly rent is $1000. The lease term is 12 months starting from January 1, 2024.",
        "document_type": "rental_agreement",
        "user_id": user_id
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📤 Sending extraction request...")
            print(f"   📝 Document Type: {test_data['document_type']}")
            print(f"   👤 User ID: {user_id}")
            print(f"   📄 Text Length: {len(test_data['document_text'])} chars")
            
            async with session.post(
                "http://localhost:8000/api/extractor/extract",
                json=test_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"\n📥 Response Status: {response.status}")
                print(f"   📋 Content Type: {response.content_type}")
                
                response_data = await response.json()
                
                print(f"\n📊 Response Data:")
                print(json.dumps(response_data, indent=2))
                
                # Check if successful
                if response_data.get('success'):
                    extraction_data = response_data.get('data', {})
                    print(f"\n✅ Extraction Success!")
                    print(f"   📄 Document ID: {extraction_data.get('document_id', 'N/A')}")
                    print(f"   📊 Confidence: {extraction_data.get('confidence_score', 'N/A')}")
                    print(f"   ⏱️ Processing Time: {response_data.get('processing_time', 'N/A')}s")
                    print(f"   🔍 Clauses Found: {len(extraction_data.get('extracted_clauses', []))}")
                    print(f"   🔗 Relationships: {len(extraction_data.get('clause_relationships', []))}")
                    
                    # Show first clause if any
                    clauses = extraction_data.get('extracted_clauses', [])
                    if clauses:
                        first_clause = clauses[0]
                        print(f"\n📋 First Clause:")
                        print(f"   🆔 ID: {first_clause.get('clause_id', 'N/A')}")
                        print(f"   📝 Type: {first_clause.get('clause_type', 'N/A')}")
                        print(f"   💯 Confidence: {first_clause.get('confidence_score', 'N/A')}")
                else:
                    print(f"\n❌ Extraction Failed!")
                    print(f"   ⚠️ Error: {response_data.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"\n💥 Exception: {e}")

if __name__ == "__main__":
    asyncio.run(debug_extraction())