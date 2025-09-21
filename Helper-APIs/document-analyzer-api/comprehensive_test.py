#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Script for Legal Document Analyzer API
Tests the complete pipeline: Upload → Extract → Store → Verify
"""

import asyncio
import os
import sys
import uuid
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

import aiohttp
import aiofiles

# Configuration
API_BASE_URL = "http://localhost:8001"  # Main API (document upload)
ANALYZER_API_BASE_URL = "http://localhost:8000"  # Document analyzer API 
TEST_USER_ID = str(uuid.uuid4())  # Generate random test user ID

# Test documents
EXAMPLE_DOCS_DIR = Path(__file__).parent / "example_docs"
TEST_DOCUMENTS = [
    {"filename": "lease agreement.pdf", "expected_type": "rental"},
    {"filename": "Group-Loan-Agreement.pdf", "expected_type": "loan"}, 
    {"filename": "PL-Agreement.pdf", "expected_type": "loan"},
    {"filename": "website-terms-and-conditions-format.pdf", "expected_type": "tos"},
    {"filename": "Independent-Contractor_Freelancer.pdf", "expected_type": "tos"}
]


class APITestClient:
    """Test client for API operations"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        async with self.session.get(f"{self.base_url}/health") as response:
            return await response.json()
    
    async def upload_document(self, file_path: Path, user_id: str) -> Dict[str, Any]:
        """Upload a document"""
        data = aiohttp.FormData()
        data.add_field('user_id', user_id)
        
        async with aiofiles.open(file_path, 'rb') as f:
            file_content = await f.read()
            data.add_field('file', file_content, filename=file_path.name, 
                         content_type='application/pdf')
        
        async with self.session.post(f"{self.base_url}/documents/upload", 
                                   data=data) as response:
            result = await response.json()
            if response.status != 200:
                raise Exception(f"Upload failed: {result}")
            return result
    
    async def extract_document_text(self, document_text: str, document_type: str, 
                                  user_id: str) -> Dict[str, Any]:
        """Extract clauses from document text using LangExtract"""
        payload = {
            "document_text": document_text,
            "document_type": document_type,
            "user_id": user_id
        }
        
        async with self.session.post(f"{ANALYZER_API_BASE_URL}/api/extractor/extract", 
                                   json=payload) as response:
            result = await response.json()
            if response.status != 200:
                raise Exception(f"Extraction failed: {result}")
            return result
    
    async def get_extraction_results(self, document_id: str, user_id: str) -> Dict[str, Any]:
        """Get extraction results for a document"""
        params = {"user_id": user_id}
        async with self.session.get(f"{ANALYZER_API_BASE_URL}/api/extractor/results/{document_id}",
                                  params=params) as response:
            result = await response.json()
            if response.status != 200:
                raise Exception(f"Get results failed: {result}")
            return result
    
    async def list_processed_documents(self, user_id: str) -> Dict[str, Any]:
        """List processed documents for a user"""
        params = {"user_id": user_id, "limit": 50}
        async with self.session.get(f"{ANALYZER_API_BASE_URL}/api/extractor/documents",
                                  params=params) as response:
            result = await response.json()
            if response.status != 200:
                raise Exception(f"List documents failed: {result}")
            return result
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user extraction statistics"""
        async with self.session.get(f"{ANALYZER_API_BASE_URL}/api/extractor/stats/{user_id}") as response:
            result = await response.json()
            if response.status != 200:
                raise Exception(f"Get stats failed: {result}")
            return result
    
    async def analyze_document(self, document_id: str, document_type: str, user_id: str) -> Dict[str, Any]:
        """Analyze a document (from main API)"""
        payload = {
            "document_id": document_id,
            "document_type": document_type,
            "user_id": user_id
        }
        
        async with self.session.post(f"{self.base_url}/analyzer/analyze", json=payload) as response:
            result = await response.json()
            if response.status != 200:
                raise Exception(f"Document analysis failed: {result}")
            return result


class TestRunner:
    """Main test runner"""
    
    def __init__(self):
        self.results = {
            "uploads": [],
            "extractions": [], 
            "verifications": [],
            "errors": [],
            "summary": {}
        }
        self.uploaded_documents = []
    
    async def run_all_tests(self):
        """Run all test phases"""
        print("🚀 Starting Legal Document Analyzer End-to-End Tests")
        print(f"📝 Test User ID: {TEST_USER_ID}")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Phase 1: Health checks
            await self.test_health_checks()
            
            # Phase 2: Document uploads
            await self.test_document_uploads()
            
            # Phase 3: Document extractions using text content
            await self.test_document_extractions_with_text()
            
            # Phase 4: Test with provided document IDs
            await self.test_provided_document_ids()
            
            # Phase 5: MongoDB verification
            await self.test_mongodb_storage()
            
            # Phase 6: End-to-end verification
            await self.test_end_to_end_pipeline()
            
        except Exception as e:
            print(f"❌ Critical test failure: {e}")
            self.results["errors"].append(f"Critical failure: {e}")
        
        finally:
            total_time = time.time() - start_time
            await self.generate_test_report(total_time)
    
    async def test_health_checks(self):
        """Test API health endpoints"""
        print("\n🔍 Phase 1: Health Checks")
        print("-" * 30)
        
        async with APITestClient(API_BASE_URL) as client:
            try:
                # Main API health
                health = await client.health_check()
                print(f"✅ Main API Health: {health.get('status', 'unknown')}")
                
                # Check services
                services = health.get('services', {})
                for service, status in services.items():
                    print(f"   📊 {service}: {status}")
                
                self.results["summary"]["health_checks"] = "PASSED"
                
            except Exception as e:
                print(f"❌ Health check failed: {e}")
                self.results["errors"].append(f"Health check failed: {e}")
                self.results["summary"]["health_checks"] = "FAILED"
    
    async def test_document_uploads(self):
        """Test document upload functionality"""
        print("\n📤 Phase 2: Document Uploads")
        print("-" * 30)
        
        async with APITestClient(API_BASE_URL) as client:
            for test_doc in TEST_DOCUMENTS:
                try:
                    file_path = EXAMPLE_DOCS_DIR / test_doc["filename"]
                    if not file_path.exists():
                        print(f"⚠️  Skipping {test_doc['filename']} - file not found")
                        continue
                    
                    print(f"📁 Uploading: {test_doc['filename']}")
                    
                    upload_result = await client.upload_document(file_path, TEST_USER_ID)
                    
                    if upload_result.get("success"):
                        document_id = upload_result["data"]["document_id"]
                        print(f"   ✅ Uploaded successfully - Document ID: {document_id}")
                        
                        self.uploaded_documents.append({
                            "document_id": document_id,
                            "filename": test_doc["filename"],
                            "expected_type": test_doc["expected_type"],
                            "upload_result": upload_result
                        })
                        
                        self.results["uploads"].append({
                            "filename": test_doc["filename"],
                            "document_id": document_id,
                            "status": "SUCCESS"
                        })
                    else:
                        print(f"   ❌ Upload failed: {upload_result}")
                        self.results["errors"].append(f"Upload failed for {test_doc['filename']}")
                
                except Exception as e:
                    print(f"   ❌ Upload error for {test_doc['filename']}: {e}")
                    self.results["errors"].append(f"Upload error for {test_doc['filename']}: {e}")
        
        print(f"\n📊 Upload Results: {len(self.uploaded_documents)} documents uploaded successfully")
        self.results["summary"]["uploads"] = f"{len(self.uploaded_documents)}/{len(TEST_DOCUMENTS)}"
    
    async def test_document_extractions_with_text(self):
        """Test document extraction using sample text"""
        print("\n🔍 Phase 3: Document Extractions with Sample Text")
        print("-" * 30)
        
        # Sample texts for different document types
        sample_texts = {
            "rental": """
            RENTAL AGREEMENT
            
            This rental agreement is between John Smith (Tenant) and ABC Properties (Landlord).
            
            Property: 123 Main Street, Mumbai, Maharashtra
            Monthly Rent: Rs. 25,000
            Security Deposit: Rs. 50,000
            Lease Period: 11 months from February 1, 2024 to December 31, 2024
            
            The tenant agrees to pay rent on the 1st of each month. The landlord is responsible 
            for major repairs. Either party may terminate with 30 days written notice.
            """,
            
            "loan": """
            LOAN AGREEMENT
            
            This loan agreement is between HDFC Bank Limited (Lender) and Amit Kumar (Borrower).
            
            Loan Amount: Rs. 5,00,000 (Five Lakh Rupees)
            Interest Rate: 8.75% per annum
            EMI Amount: Rs. 10,500 per month
            Loan Tenure: 5 years
            Processing Fee: Rs. 5,000
            
            The borrower agrees to repay the loan in monthly installments. The property at 
            456 Park Avenue shall serve as collateral. Default in payment may result in 
            legal action and asset seizure.
            """,
            
            "tos": """
            TERMS OF SERVICE
            
            Welcome to TechCorp Services ("Company", "we", "us").
            
            Eligibility: Users must be 18 years or older to use our services.
            Services: We provide cloud storage and data processing services.
            Pricing: Monthly subscription fees apply as per the pricing page.
            
            User Obligations:
            - Comply with all applicable laws
            - Do not upload illegal or harmful content
            - Maintain account security
            
            Termination: Either party may terminate the account with 30 days notice.
            Disputes shall be resolved in Mumbai courts under Indian law.
            """
        }
        
        async with APITestClient(API_BASE_URL) as client:
            for doc_type, sample_text in sample_texts.items():
                try:
                    print(f"🔍 Extracting from {doc_type} document...")
                    
                    extraction_result = await client.extract_document_text(
                        sample_text, doc_type, TEST_USER_ID
                    )
                    
                    if extraction_result.get("success"):
                        data = extraction_result["data"]
                        clauses = data.get("extracted_clauses", [])
                        relationships = data.get("clause_relationships", [])
                        confidence = data.get("confidence_score", 0.0)
                        
                        print(f"   ✅ Extraction successful:")
                        print(f"      📋 Clauses: {len(clauses)}")
                        print(f"      🔗 Relationships: {len(relationships)}")
                        print(f"      🎯 Confidence: {confidence:.2f}")
                        
                        self.results["extractions"].append({
                            "document_type": doc_type,
                            "clauses_count": len(clauses),
                            "relationships_count": len(relationships),
                            "confidence_score": confidence,
                            "status": "SUCCESS"
                        })
                    else:
                        print(f"   ❌ Extraction failed: {extraction_result}")
                        self.results["errors"].append(f"Extraction failed for {doc_type}")
                
                except Exception as e:
                    print(f"   ❌ Extraction error for {doc_type}: {e}")
                    self.results["errors"].append(f"Extraction error for {doc_type}: {e}")
        
        print(f"\n📊 Extraction Results: {len(self.results['extractions'])} successful extractions")
        self.results["summary"]["text_extractions"] = len(self.results["extractions"])
    
    async def test_provided_document_ids(self):
        """Test extraction with provided document IDs"""
        print("\n🆔 Phase 4: Testing Provided Document IDs")
        print("-" * 30)
        
        provided_ids = [
            "e12829e2-268a-4aa2-acfe-7bb4710c0e30",
            "4a2f8446-b236-4ba6-9f49-05366def62a7"
        ]
        
        async with APITestClient(API_BASE_URL) as client:
            for doc_id in provided_ids:
                try:
                    print(f"🔍 Testing document ID: {doc_id}")
                    
                    # Try to get extraction results
                    try:
                        results = await client.get_extraction_results(doc_id, TEST_USER_ID)
                        if results.get("success"):
                            print(f"   ✅ Found existing results for {doc_id}")
                            self.results["verifications"].append({
                                "document_id": doc_id,
                                "status": "FOUND",
                                "data": results["data"]
                            })
                        else:
                            print(f"   ℹ️  No existing results for {doc_id}")
                    except Exception as e:
                        if "404" in str(e):
                            print(f"   ℹ️  Document {doc_id} not found (expected for new test)")
                        else:
                            print(f"   ⚠️  Error checking {doc_id}: {e}")
                
                except Exception as e:
                    print(f"   ❌ Error testing document ID {doc_id}: {e}")
                    self.results["errors"].append(f"Error testing document ID {doc_id}: {e}")
        
        print(f"\n📊 Document ID Tests: {len(self.results['verifications'])} documents verified")
    
    async def test_mongodb_storage(self):
        """Test MongoDB storage verification"""
        print("\n🗄️  Phase 5: MongoDB Storage Verification")
        print("-" * 30)
        
        async with APITestClient(API_BASE_URL) as client:
            try:
                # List processed documents for the test user
                documents = await client.list_processed_documents(TEST_USER_ID)
                
                if documents.get("success"):
                    doc_list = documents["data"]["documents"]
                    print(f"✅ Found {len(doc_list)} processed documents in MongoDB")
                    
                    for doc in doc_list:
                        doc_id = doc.get("document_id", "unknown")
                        doc_type = doc.get("document_type", "unknown")
                        status = doc.get("processing_status", "unknown")
                        clauses_count = doc.get("metadata", {}).get("total_clauses", 0)
                        
                        print(f"   📄 {doc_id[:8]}... - Type: {doc_type}, Status: {status}, Clauses: {clauses_count}")
                    
                    self.results["summary"]["mongodb_documents"] = len(doc_list)
                else:
                    print(f"❌ Failed to list processed documents: {documents}")
                    self.results["errors"].append("Failed to list processed documents")
                
                # Get user statistics
                stats = await client.get_user_stats(TEST_USER_ID)
                if stats.get("success"):
                    stats_data = stats["data"]
                    total_docs = stats_data.get("total_documents", 0)
                    avg_confidence = stats_data.get("average_confidence_score", 0.0)
                    by_type = stats_data.get("documents_by_type", {})
                    
                    print(f"📊 User Statistics:")
                    print(f"   📄 Total Documents: {total_docs}")
                    print(f"   🎯 Average Confidence: {avg_confidence:.3f}")
                    print(f"   📋 By Type: {by_type}")
                    
                    self.results["summary"]["user_stats"] = stats_data
                
            except Exception as e:
                print(f"❌ MongoDB verification error: {e}")
                self.results["errors"].append(f"MongoDB verification error: {e}")
    
    async def test_end_to_end_pipeline(self):
        """Test complete end-to-end pipeline"""
        print("\n🔄 Phase 6: End-to-End Pipeline Test")
        print("-" * 30)
        
        # Test with a simple rental agreement
        test_text = """
        RESIDENTIAL LEASE AGREEMENT
        
        Landlord: Sarah Johnson, 789 Oak Street, Delhi
        Tenant: Michael Brown, Current Address: 321 Pine Avenue
        
        Property Address: Apartment 4B, Green Valley Complex, Sector 18, Noida
        Monthly Rent: Rs. 18,000 (Eighteen Thousand Rupees)
        Security Deposit: Rs. 36,000 (Two months rent)
        
        Lease Term: 12 months starting January 15, 2024
        Utilities: Tenant responsible for electricity and water
        Maintenance: Landlord handles major repairs, tenant handles minor repairs
        
        Termination: Either party may terminate with 60 days written notice.
        Late Fee: Rs. 500 for payments received after the 5th of the month.
        """
        
        async with APITestClient(API_BASE_URL) as client:
            try:
                print("🔄 Running complete pipeline test...")
                
                # Step 1: Extract clauses
                extraction_result = await client.extract_document_text(
                    test_text, "rental", TEST_USER_ID
                )
                
                if extraction_result.get("success"):
                    data = extraction_result["data"]
                    document_id = data.get("document_id")
                    clauses = data.get("extracted_clauses", [])
                    
                    print(f"   ✅ Step 1 - Extraction: {len(clauses)} clauses extracted")
                    
                    # Step 2: Verify storage
                    if document_id:
                        try:
                            stored_result = await client.get_extraction_results(document_id, TEST_USER_ID)
                            if stored_result.get("success"):
                                print(f"   ✅ Step 2 - Storage: Document stored and retrievable")
                                self.results["summary"]["end_to_end"] = "SUCCESS"
                            else:
                                print(f"   ⚠️  Step 2 - Storage: Document not found in storage")
                                self.results["summary"]["end_to_end"] = "PARTIAL"
                        except Exception as e:
                            print(f"   ⚠️  Step 2 - Storage: Error retrieving document: {e}")
                            self.results["summary"]["end_to_end"] = "PARTIAL"
                    
                    print("   ✅ End-to-End Pipeline: COMPLETED")
                else:
                    print(f"   ❌ Step 1 - Extraction failed: {extraction_result}")
                    self.results["summary"]["end_to_end"] = "FAILED"
            
            except Exception as e:
                print(f"❌ End-to-end pipeline error: {e}")
                self.results["errors"].append(f"End-to-end pipeline error: {e}")
                self.results["summary"]["end_to_end"] = "FAILED"
    
    async def generate_test_report(self, total_time: float):
        """Generate comprehensive test report"""
        print("\n" + "=" * 60)
        print("📋 COMPREHENSIVE TEST REPORT")
        print("=" * 60)
        
        # Summary
        print(f"🕒 Total Test Time: {total_time:.2f} seconds")
        print(f"👤 Test User ID: {TEST_USER_ID}")
        print(f"📊 Test Results Summary:")
        
        summary = self.results["summary"]
        for phase, result in summary.items():
            status_emoji = "✅" if result not in ["FAILED", "0"] else "❌"
            print(f"   {status_emoji} {phase.replace('_', ' ').title()}: {result}")
        
        # Detailed Results
        if self.results["uploads"]:
            print(f"\n📤 Upload Results ({len(self.results['uploads'])} documents):")
            for upload in self.results["uploads"]:
                print(f"   • {upload['filename']}: {upload['status']} (ID: {upload['document_id'][:8]}...)")
        
        if self.results["extractions"]:
            print(f"\n🔍 Extraction Results ({len(self.results['extractions'])} extractions):")
            for extraction in self.results["extractions"]:
                print(f"   • {extraction['document_type']}: {extraction['clauses_count']} clauses, "
                      f"{extraction['relationships_count']} relationships, "
                      f"confidence: {extraction['confidence_score']:.2f}")
        
        # Errors
        if self.results["errors"]:
            print(f"\n❌ Errors ({len(self.results['errors'])} total):")
            for error in self.results["errors"]:
                print(f"   • {error}")
        else:
            print(f"\n✅ No errors encountered during testing!")
        
        # Save detailed report
        report_file = f"test_report_{int(time.time())}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump({
                    "test_run_id": str(uuid.uuid4()),
                    "timestamp": time.time(),
                    "test_user_id": TEST_USER_ID,
                    "total_time_seconds": total_time,
                    "results": self.results
                }, f, indent=2)
            print(f"\n💾 Detailed report saved to: {report_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save detailed report: {e}")
        
        # Final status
        error_count = len(self.results["errors"])
        if error_count == 0:
            print(f"\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        else:
            print(f"\n⚠️  TESTS COMPLETED WITH {error_count} ERRORS")
        
        print("=" * 60)


async def main():
    """Main test execution function"""
    runner = TestRunner()
    await runner.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())