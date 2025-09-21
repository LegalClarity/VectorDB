#!/usr/bin/env python3
"""
Focused Document Extraction Test
Tests only the document analyzer API functionality
"""

import asyncio
import aiohttp
import json
import uuid
import time
from pathlib import Path
from typing import Dict, Any

# Configuration
ANALYZER_API_BASE_URL = "http://localhost:8000"
EXAMPLE_DOCS_PATH = Path("Helper-APIs/document-analyzer-api/example_docs")

class ExtractionTestSuite:
    def __init__(self):
        self.test_results = []
        
    async def log_result(self, test_name: str, success: bool, details: Dict[str, Any]):
        """Log test results"""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": time.time(),
            "details": details
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details.get('message'):
            print(f"   📝 {details['message']}")
        if not success and details.get('error'):
            print(f"   ⚠️ Error: {details['error']}")
        print()

    async def test_api_health(self):
        """Test analyzer API health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{ANALYZER_API_BASE_URL}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.log_result("API Health Check", True, {
                            "message": f"API is healthy - Version: {data.get('version', 'unknown')}",
                            "status": data
                        })
                        return True
                    else:
                        await self.log_result("API Health Check", False, {
                            "message": f"API returned status {response.status}",
                            "error": f"Status {response.status}"
                        })
                        return False
        except Exception as e:
            await self.log_result("API Health Check", False, {
                "message": "Could not connect to API",
                "error": str(e)
            })
            return False

    async def test_extraction_with_document_id(self, document_id: str, document_name: str):
        """Test extraction using a specific document ID"""
        try:
            async with aiohttp.ClientSession() as session:
                user_id = str(uuid.uuid4())
                extract_data = {
                    "document_text": f"Sample legal document text for document ID: {document_id}. This is a rental agreement between landlord and tenant with terms and conditions.",
                    "document_type": "rental_agreement",
                    "user_id": user_id
                }
                
                print(f"🔍 Extracting from document: {document_name} (ID: {document_id[:8]}...)")
                
                async with session.post(
                    f"{ANALYZER_API_BASE_URL}/api/extractor/extract",
                    json=extract_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and response_data.get('success'):
                        extraction_data = response_data.get('data', {})
                        await self.log_result(f"Extract {document_name}", True, {
                            "message": f"Successfully extracted data",
                            "document_id": document_id,
                            "extracted_fields": len(extraction_data) if extraction_data else 0,
                            "sample_data": str(extraction_data)[:200] + "..." if extraction_data else "No data"
                        })
                        return {"success": True, "data": extraction_data, "document_id": document_id}
                    else:
                        await self.log_result(f"Extract {document_name}", False, {
                            "message": f"Extraction failed",
                            "error": response_data.get('message', 'Unknown error'),
                            "response": response_data
                        })
                        return {"success": False, "error": response_data}
                        
        except Exception as e:
            await self.log_result(f"Extract {document_name}", False, {
                "message": f"Exception during extraction",
                "error": str(e)
            })
            return {"success": False, "error": str(e)}

    async def test_mongodb_retrieval(self, document_id: str, document_name: str):
        """Test MongoDB retrieval of processed document"""
        try:
            async with aiohttp.ClientSession() as session:
                user_id = str(uuid.uuid4())
                async with session.get(f"{ANALYZER_API_BASE_URL}/api/extractor/results/{document_id}?user_id={user_id}") as response:
                    if response.status == 200:
                        response_data = await response.json()
                        processed_doc = response_data.get('data')
                        
                        if processed_doc:
                            await self.log_result(f"MongoDB Retrieval {document_name}", True, {
                                "message": f"Document found in MongoDB",
                                "document_id": document_id,
                                "has_extraction_results": bool(processed_doc.get('extraction_results')),
                                "created_at": processed_doc.get('created_at'),
                                "updated_at": processed_doc.get('updated_at')
                            })
                            return {"success": True, "data": processed_doc}
                        else:
                            await self.log_result(f"MongoDB Retrieval {document_name}", False, {
                                "message": f"Document not found in MongoDB",
                                "response": response_data
                            })
                            return {"success": False, "error": "Document not found"}
                    elif response.status == 404:
                        await self.log_result(f"MongoDB Retrieval {document_name}", False, {
                            "message": f"Document not found in database (404)",
                            "document_id": document_id
                        })
                        return {"success": False, "error": "Document not found (404)"}
                    else:
                        response_data = await response.json() if response.content_type == 'application/json' else {"error": "Non-JSON response"}
                        await self.log_result(f"MongoDB Retrieval {document_name}", False, {
                            "message": f"Failed to retrieve document: Status {response.status}",
                            "error": response_data
                        })
                        return {"success": False, "error": response_data}
                        
        except Exception as e:
            await self.log_result(f"MongoDB Retrieval {document_name}", False, {
                "message": f"Exception during MongoDB retrieval",
                "error": str(e)
            })
            return {"success": False, "error": str(e)}

    async def test_document_list(self):
        """Test listing processed documents"""
        try:
            user_id = str(uuid.uuid4())
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{ANALYZER_API_BASE_URL}/api/extractor/documents?user_id={user_id}&limit=10") as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        documents = response_data.get('data', {}).get('documents', [])
                        await self.log_result("List Processed Documents", True, {
                            "message": f"Retrieved {len(documents)} processed documents",
                            "count": len(documents)
                        })
                        return {"success": True, "data": documents}
                    else:
                        await self.log_result("List Processed Documents", False, {
                            "message": f"Failed to list documents: Status {response.status}",
                            "error": response_data
                        })
                        return {"success": False, "error": response_data}
                        
        except Exception as e:
            await self.log_result("List Processed Documents", False, {
                "message": f"Exception during document listing",
                "error": str(e)
            })
            return {"success": False, "error": str(e)}

    async def run_extraction_tests(self):
        """Run all extraction tests"""
        print("🧪 Document Extraction Test Suite")
        print("=" * 50)
        
        # 1. Health check
        print("\n1️⃣ Checking API Health...")
        api_healthy = await self.test_api_health()
        
        if not api_healthy:
            print("❌ API is not healthy. Cannot proceed with tests.")
            return
        
        # 2. Test predefined document IDs
        print("\n2️⃣ Testing Predefined Document IDs...")
        predefined_ids = [
            ("e12829e2-268a-4aa2-acfe-7bb4710c0e30", "Document 1"),
            ("4a2f8446-b236-4ba6-9f49-05366def62a7", "Document 2")
        ]
        
        extraction_results = []
        
        for doc_id, doc_name in predefined_ids:
            # Test extraction
            result = await self.test_extraction_with_document_id(doc_id, doc_name)
            extraction_results.append(result)
            
            # If extraction successful, test MongoDB storage
            if result.get('success'):
                await asyncio.sleep(2)  # Wait for MongoDB write
                await self.test_mongodb_retrieval(doc_id, doc_name)
            
            await asyncio.sleep(1)  # Delay between tests
        
        # 3. Test document listing
        print("\n3️⃣ Testing Document Listing...")
        await self.test_document_list()
        
        # 4. Generate report
        await self.generate_report()

    async def generate_report(self):
        """Generate final test report"""
        print("\n" + "="*50)
        print("📊 EXTRACTION TEST REPORT")
        print("="*50)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print(f"\n🚨 Failed Tests:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details'].get('error', 'Unknown error')}")
        
        # Save results to file
        results_file = "extraction_test_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        if success_rate >= 70:
            print("\n✅ Extraction tests PASSED! System is working.")
        else:
            print("\n❌ Extraction tests FAILED. Please review issues.")

async def main():
    """Main test execution"""
    test_suite = ExtractionTestSuite()
    await test_suite.run_extraction_tests()

if __name__ == "__main__":
    asyncio.run(main())