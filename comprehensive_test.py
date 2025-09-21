#!/usr/bin/env python3
"""
Comprehensive Test Suite for Document Upload, Extraction, and MongoDB Storage
Tests the entire pipeline from document upload to LangExtract processing to MongoDB storage
"""

import asyncio
import aiohttp
import json
import os
import uuid
from pathlib import Path
import time
from typing import Dict, List, Any

# Test configuration
MAIN_API_BASE_URL = "http://localhost:8001"  # Main API with document upload
ANALYZER_API_BASE_URL = "http://localhost:8000"  # Document analyzer API
EXAMPLE_DOCS_PATH = Path("Helper-APIs/document-analyzer-api/example_docs")

class ComprehensiveTestSuite:
    def __init__(self):
        self.uploaded_documents = []
        self.test_results = {
            "upload_tests": [],
            "extraction_tests": [],
            "mongodb_tests": [],
            "errors": []
        }
        
    async def log_test_result(self, test_type: str, test_name: str, success: bool, details: Dict[str, Any]):
        """Log test results"""
        result = {
            "test_name": test_name,
            "success": success,
            "timestamp": time.time(),
            "details": details
        }
        self.test_results[test_type].append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details.get('message', 'No message')}")
        
        if not success and details.get('error'):
            self.test_results["errors"].append({
                "test": test_name,
                "error": str(details['error']),
                "timestamp": time.time()
            })

    async def check_api_health(self, base_url: str, api_name: str) -> bool:
        """Check if APIs are running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/health") as response:
                    if response.status == 200:
                        await self.log_test_result("upload_tests", f"{api_name} Health Check", True, {"message": f"{api_name} is running"})
                        return True
                    else:
                        await self.log_test_result("upload_tests", f"{api_name} Health Check", False, {"message": f"Status: {response.status}"})
                        return False
        except Exception as e:
            await self.log_test_result("upload_tests", f"{api_name} Health Check", False, {"error": e, "message": f"{api_name} is not accessible"})
            return False

    async def upload_document(self, file_path: Path, user_id: str) -> Dict[str, Any]:
        """Upload a document to the main API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare multipart form data
                with open(file_path, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('file', f, filename=file_path.name, content_type='application/pdf')
                    data.add_field('user_id', user_id)
                    data.add_field('document_type', 'legal')
                    data.add_field('description', f'Test upload of {file_path.name}')
                    
                    async with session.post(f"{MAIN_API_BASE_URL}/documents/upload", data=data) as response:
                        response_data = await response.json()
                        
                        if response.status == 200 and response_data.get('success'):
                            document_id = response_data.get('data', {}).get('document_id')
                            await self.log_test_result("upload_tests", f"Upload {file_path.name}", True, {
                                "message": f"Document uploaded successfully",
                                "document_id": document_id,
                                "file_name": file_path.name
                            })
                            return {
                                "success": True,
                                "document_id": document_id,
                                "file_name": file_path.name,
                                "user_id": user_id
                            }
                        else:
                            await self.log_test_result("upload_tests", f"Upload {file_path.name}", False, {
                                "error": response_data,
                                "message": f"Upload failed: {response_data.get('message', 'Unknown error')}"
                            })
                            return {"success": False, "error": response_data}
                            
        except Exception as e:
            await self.log_test_result("upload_tests", f"Upload {file_path.name}", False, {
                "error": str(e),
                "message": f"Exception during upload: {str(e)}"
            })
            return {"success": False, "error": str(e)}

    async def test_document_extraction(self, document_id: str, user_id: str, file_name: str) -> Dict[str, Any]:
        """Test document extraction using the analyzer API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare extraction request
                extract_data = {
                    "document_id": document_id,
                    "document_type": "legal",
                    "user_id": user_id,
                    "extraction_config": {
                        "extract_clauses": True,
                        "extract_parties": True,
                        "extract_dates": True,
                        "extract_amounts": True
                    }
                }
                
                async with session.post(
                    f"{ANALYZER_API_BASE_URL}/extract",
                    json=extract_data,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    response_data = await response.json()
                    
                    if response.status == 200 and response_data.get('success'):
                        extraction_result = response_data.get('data', {})
                        await self.log_test_result("extraction_tests", f"Extract {file_name}", True, {
                            "message": f"Extraction successful",
                            "document_id": document_id,
                            "extracted_fields": list(extraction_result.keys()) if extraction_result else []
                        })
                        return {
                            "success": True,
                            "extraction_result": extraction_result,
                            "document_id": document_id
                        }
                    else:
                        await self.log_test_result("extraction_tests", f"Extract {file_name}", False, {
                            "error": response_data,
                            "message": f"Extraction failed: {response_data.get('message', 'Unknown error')}"
                        })
                        return {"success": False, "error": response_data}
                        
        except Exception as e:
            await self.log_test_result("extraction_tests", f"Extract {file_name}", False, {
                "error": str(e),
                "message": f"Exception during extraction: {str(e)}"
            })
            return {"success": False, "error": str(e)}

    async def verify_mongodb_storage(self, document_id: str, file_name: str) -> Dict[str, Any]:
        """Verify that extraction results are stored in MongoDB"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{ANALYZER_API_BASE_URL}/processed/{document_id}") as response:
                    if response.status == 200:
                        response_data = await response.json()
                        processed_doc = response_data.get('data')
                        
                        if processed_doc and processed_doc.get('document_id') == document_id:
                            await self.log_test_result("mongodb_tests", f"MongoDB Storage {file_name}", True, {
                                "message": f"Document found in MongoDB",
                                "document_id": document_id,
                                "has_extraction_results": bool(processed_doc.get('extraction_results'))
                            })
                            return {"success": True, "processed_doc": processed_doc}
                        else:
                            await self.log_test_result("mongodb_tests", f"MongoDB Storage {file_name}", False, {
                                "message": f"Document not found or incomplete in MongoDB",
                                "document_id": document_id
                            })
                            return {"success": False, "error": "Document not found"}
                    else:
                        response_data = await response.json() if response.content_type == 'application/json' else {"error": "Non-JSON response"}
                        await self.log_test_result("mongodb_tests", f"MongoDB Storage {file_name}", False, {
                            "error": response_data,
                            "message": f"Failed to retrieve document: Status {response.status}"
                        })
                        return {"success": False, "error": response_data}
                        
        except Exception as e:
            await self.log_test_result("mongodb_tests", f"MongoDB Storage {file_name}", False, {
                "error": str(e),
                "message": f"Exception during MongoDB verification: {str(e)}"
            })
            return {"success": False, "error": str(e)}

    async def test_predefined_document_ids(self):
        """Test with predefined document IDs provided by user"""
        predefined_ids = [
            "e12829e2-268a-4aa2-acfe-7bb4710c0e30",
            "4a2f8446-b236-4ba6-9f49-05366def62a7"
        ]
        
        print(f"\n🔍 Testing predefined document IDs...")
        
        for doc_id in predefined_ids:
            user_id = str(uuid.uuid4())
            
            # Test extraction
            extraction_result = await self.test_document_extraction(doc_id, user_id, f"predefined-{doc_id[:8]}")
            
            # Test MongoDB storage
            if extraction_result.get('success'):
                await self.verify_mongodb_storage(doc_id, f"predefined-{doc_id[:8]}")
            
            # Small delay between tests
            await asyncio.sleep(1)

    async def run_comprehensive_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Comprehensive Test Suite")
        print("=" * 50)
        
        # 1. Check API health
        print("\n1️⃣ Checking API Health...")
        main_api_healthy = await self.check_api_health(MAIN_API_BASE_URL, "Main API")
        analyzer_api_healthy = await self.check_api_health(ANALYZER_API_BASE_URL, "Analyzer API")
        
        if not (main_api_healthy and analyzer_api_healthy):
            print("❌ APIs are not healthy. Please start both APIs before running tests.")
            return
        
        # 2. Test document uploads
        print("\n2️⃣ Testing Document Uploads...")
        if EXAMPLE_DOCS_PATH.exists():
            pdf_files = list(EXAMPLE_DOCS_PATH.glob("*.pdf"))
            print(f"Found {len(pdf_files)} PDF files to test")
            
            for pdf_file in pdf_files[:3]:  # Test first 3 files
                user_id = str(uuid.uuid4())
                upload_result = await self.upload_document(pdf_file, user_id)
                
                if upload_result.get('success'):
                    self.uploaded_documents.append(upload_result)
                
                # Small delay between uploads
                await asyncio.sleep(2)
        else:
            print(f"❌ Example documents path not found: {EXAMPLE_DOCS_PATH}")
        
        # 3. Test extractions on uploaded documents
        print("\n3️⃣ Testing Document Extractions...")
        for doc_info in self.uploaded_documents:
            extraction_result = await self.test_document_extraction(
                doc_info['document_id'], 
                doc_info['user_id'], 
                doc_info['file_name']
            )
            
            # 4. Verify MongoDB storage
            if extraction_result.get('success'):
                await self.verify_mongodb_storage(doc_info['document_id'], doc_info['file_name'])
            
            # Small delay between extractions
            await asyncio.sleep(3)
        
        # 5. Test predefined document IDs
        await self.test_predefined_document_ids()
        
        # 6. Generate final report
        await self.generate_final_report()

    async def generate_final_report(self):
        """Generate and display final test report"""
        print("\n" + "="*50)
        print("📊 FINAL TEST REPORT")
        print("="*50)
        
        # Summary statistics
        total_upload_tests = len(self.test_results["upload_tests"])
        successful_uploads = sum(1 for test in self.test_results["upload_tests"] if test["success"])
        
        total_extraction_tests = len(self.test_results["extraction_tests"])
        successful_extractions = sum(1 for test in self.test_results["extraction_tests"] if test["success"])
        
        total_mongodb_tests = len(self.test_results["mongodb_tests"])
        successful_mongodb = sum(1 for test in self.test_results["mongodb_tests"] if test["success"])
        
        print(f"📤 Upload Tests: {successful_uploads}/{total_upload_tests} passed")
        print(f"🔍 Extraction Tests: {successful_extractions}/{total_extraction_tests} passed")
        print(f"🗃️ MongoDB Tests: {successful_mongodb}/{total_mongodb_tests} passed")
        print(f"❌ Total Errors: {len(self.test_results['errors'])}")
        
        # Show errors if any
        if self.test_results["errors"]:
            print("\n🚨 ERRORS ENCOUNTERED:")
            for error in self.test_results["errors"]:
                print(f"  - {error['test']}: {error['error']}")
        
        # Save detailed results to file
        results_file = "test_results_comprehensive.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
        
        # Overall success
        total_tests = total_upload_tests + total_extraction_tests + total_mongodb_tests
        successful_tests = successful_uploads + successful_extractions + successful_mongodb
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}% ({successful_tests}/{total_tests})")
        
        if success_rate >= 80:
            print("✅ Test suite PASSED! System is working well.")
        else:
            print("❌ Test suite FAILED. Please review errors and fix issues.")

async def main():
    """Main test execution function"""
    test_suite = ComprehensiveTestSuite()
    await test_suite.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())