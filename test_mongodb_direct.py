#!/usr/bin/env python3
"""
Test MongoDB service directly via API
"""

import asyncio
import aiohttp
import json

async def test_mongodb_direct():
    """Test MongoDB insertion directly"""
    
    print("🧪 Direct MongoDB Test")
    print("=" * 25)
    
    # Create test data
    test_document = {
        "document_id": "test_direct_123",
        "user_id": "test_user_direct",
        "extraction_result": {
            "document_id": "test_direct_123",
            "document_type": "rental_agreement",
            "extracted_clauses": [
                {
                    "clause_id": "test_clause_1",
                    "clause_type": "financial_terms",
                    "clause_text": "Test clause for direct insertion",
                    "confidence_score": 0.95
                }
            ],
            "clause_relationships": [],
            "confidence_score": 0.95
        },
        "original_filename": "test_direct.txt",
        "document_type": "rental_agreement"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("📤 Testing direct MongoDB insertion via API...")
            
            # Try to create a simple test endpoint first
            # Let's test the health of individual components
            
            print("📊 Checking API components...")
            
            # Test health endpoint
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"   ✅ API Health: OK")
                    print(f"   📋 Config: {health_data.get('configuration', {})}")
                else:
                    print(f"   ❌ API Health: Status {response.status}")
                    return
            
            # Test extractor health
            async with session.get("http://localhost:8000/api/extractor/health") as response:
                if response.status == 200:
                    extractor_health = await response.json()
                    print(f"   ✅ Extractor Health: {extractor_health.get('status', 'Unknown')}")
                else:
                    print(f"   ❌ Extractor Health: Status {response.status}")
                    
    except Exception as e:
        print(f"\n💥 Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_mongodb_direct())