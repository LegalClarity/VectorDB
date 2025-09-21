"""
Comprehensive test script for document upload, extraction, and storage
Tests the complete Legal Clarity document processing pipeline
"""
import asyncio
import os
import uuid
import time
import requests
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
EXAMPLE_DOCS_DIR = "Helper-APIs/document-analyzer-api/example_docs"

# Test user ID for all operations
TEST_USER_ID = "test-user-123"

class DocumentProcessingTester:
    """Comprehensive tester for the document processing pipeline"""

    def __init__(self):
        self.uploaded_documents = []
        self.extracted_documents = []

    async def upload_documents(self) -> List[Dict[str, Any]]:
        """Upload all documents from example_docs folder"""
        print("🚀 Starting document upload process...")

        docs_dir = Path(EXAMPLE_DOCS_DIR)
        if not docs_dir.exists():
            raise FileNotFoundError(f"Example docs directory not found: {EXAMPLE_DOCS_DIR}")

        uploaded_docs = []

        for pdf_file in docs_dir.glob("*.pdf"):
            try:
                print(f"📤 Uploading: {pdf_file.name}")

                # Generate random UUID for document
                document_uuid = str(uuid.uuid4())

                with open(pdf_file, 'rb') as file:
                    files = {'file': (pdf_file.name, file, 'application/pdf')}
                    data = {
                        'user_id': TEST_USER_ID
                    }

                    response = requests.post(
                        f"{API_BASE_URL}/documents/upload",
                        files=files,
                        data=data,
                        timeout=60
                    )

                    if response.status_code == 200:
                        result = response.json()
                        doc_info = {
                            'filename': pdf_file.name,
                            'document_id': result.get('document_id', document_uuid),
                            'gcs_url': result.get('gcs_url'),
                            'upload_time': datetime.now().isoformat()
                        }
                        uploaded_docs.append(doc_info)
                        print(f"✅ Successfully uploaded: {pdf_file.name} -> {doc_info['document_id']}")
                    else:
                        print(f"❌ Failed to upload {pdf_file.name}: {response.status_code} - {response.text}")

            except Exception as e:
                print(f"❌ Error uploading {pdf_file.name}: {str(e)}")

        self.uploaded_documents = uploaded_docs
        print(f"📊 Upload complete: {len(uploaded_docs)}/{len(list(docs_dir.glob('*.pdf')))} documents uploaded")
        return uploaded_docs

    async def test_document_extraction(self, document_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Test document extraction using LangExtract with real API calls"""
        print("\n🔍 Starting document extraction testing...")

        if document_ids is None:
            document_ids = [doc['document_id'] for doc in self.uploaded_documents]

        extracted_docs = []

        for doc_id in document_ids:
            try:
                print(f"🧠 Extracting from document: {doc_id}")

                # Test extraction endpoint
                extract_payload = {
                    "document_id": doc_id,
                    "user_id": TEST_USER_ID,
                    "extraction_config": {
                        "model_id": "gemini-2.5-flash",
                        "extraction_type": "legal_document",
                        "max_passes": 2
                    }
                }

                response = requests.post(
                    f"{API_BASE_URL}/analyzer/extract",
                    json=extract_payload,
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()
                    extraction_info = {
                        'document_id': doc_id,
                        'extraction_result': result,
                        'extraction_time': datetime.now().isoformat(),
                        'status': 'success'
                    }
                    extracted_docs.append(extraction_info)
                    print(f"✅ Successfully extracted from: {doc_id}")

                    # Print key extraction results
                    if 'data' in result and 'extractions' in result['data']:
                        extractions = result['data']['extractions']
                        print(f"   📄 Found {len(extractions)} extractions")
                        for i, extraction in enumerate(extractions[:3]):  # Show first 3
                            print(f"      {i+1}. {extraction.get('extraction_class', 'N/A')}: {extraction.get('extraction_text', '')[:50]}...")

                else:
                    print(f"❌ Failed to extract from {doc_id}: {response.status_code} - {response.text}")
                    extracted_docs.append({
                        'document_id': doc_id,
                        'extraction_result': None,
                        'extraction_time': datetime.now().isoformat(),
                        'status': 'failed',
                        'error': response.text
                    })

            except Exception as e:
                print(f"❌ Error extracting from {doc_id}: {str(e)}")
                extracted_docs.append({
                    'document_id': doc_id,
                    'extraction_result': None,
                    'extraction_time': datetime.now().isoformat(),
                    'status': 'error',
                    'error': str(e)
                })

        self.extracted_documents = extracted_docs
        success_count = len([doc for doc in extracted_docs if doc['status'] == 'success'])
        print(f"📊 Extraction complete: {success_count}/{len(document_ids)} documents successfully extracted")
        return extracted_docs

    async def verify_mongodb_storage(self) -> Dict[str, Any]:
        """Verify that extracted data is stored in MongoDB processed_documents collection"""
        print("\n💾 Verifying MongoDB storage...")

        verification_results = {
            'total_documents': len(self.uploaded_documents),
            'extraction_attempts': len(self.extracted_documents),
            'successful_extractions': 0,
            'mongodb_storage_status': [],
            'errors': []
        }

        for doc in self.extracted_documents:
            doc_id = doc['document_id']

            try:
                # Test analyzer results endpoint
                response = requests.get(
                    f"{API_BASE_URL}/analyzer/results/{doc_id}",
                    params={'user_id': TEST_USER_ID},
                    timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    verification_results['successful_extractions'] += 1
                    verification_results['mongodb_storage_status'].append({
                        'document_id': doc_id,
                        'status': 'stored',
                        'data_size': len(str(result))
                    })
                    print(f"✅ MongoDB storage verified for: {doc_id}")
                else:
                    verification_results['mongodb_storage_status'].append({
                        'document_id': doc_id,
                        'status': 'not_found',
                        'error': response.text
                    })
                    print(f"❌ MongoDB storage not found for: {doc_id}")

            except Exception as e:
                verification_results['errors'].append({
                    'document_id': doc_id,
                    'error': str(e)
                })
                print(f"❌ Error verifying MongoDB storage for {doc_id}: {str(e)}")

        print("📊 MongoDB verification complete:")
        print(f"   📄 Total uploaded: {verification_results['total_documents']}")
        print(f"   🔍 Extraction attempts: {verification_results['extraction_attempts']}")
        print(f"   ✅ Successful extractions: {verification_results['successful_extractions']}")
        print(f"   💾 MongoDB storage verified: {len([s for s in verification_results['mongodb_storage_status'] if s['status'] == 'stored'])}")

        return verification_results

    async def run_comprehensive_test(self, specific_document_ids: List[str] = None) -> Dict[str, Any]:
        """Run the complete test suite"""
        print("🧪 Starting comprehensive Legal Clarity document processing test...\n")

        test_results = {
            'test_start_time': datetime.now().isoformat(),
            'phases': {},
            'overall_status': 'pending'
        }

        try:
            # Phase 1: Upload documents
            print("=" * 60)
            print("PHASE 1: DOCUMENT UPLOAD")
            print("=" * 60)
            uploaded_docs = await self.upload_documents()
            test_results['phases']['upload'] = {
                'status': 'completed' if uploaded_docs else 'failed',
                'uploaded_count': len(uploaded_docs),
                'documents': uploaded_docs
            }

            if not uploaded_docs:
                raise Exception("No documents were successfully uploaded")

            # Phase 2: Extract document details
            print("\n" + "=" * 60)
            print("PHASE 2: DOCUMENT EXTRACTION")
            print("=" * 60)

            # Test with all uploaded documents first
            extracted_docs = await self.test_document_extraction()
            test_results['phases']['extraction'] = {
                'status': 'completed' if extracted_docs else 'failed',
                'extracted_count': len([d for d in extracted_docs if d['status'] == 'success']),
                'documents': extracted_docs
            }

            # Test with specific document IDs if provided
            if specific_document_ids:
                print(f"\n🔍 Testing with specific document IDs: {specific_document_ids}")
                specific_extractions = await self.test_document_extraction(specific_document_ids)
                test_results['phases']['specific_extraction'] = {
                    'document_ids': specific_document_ids,
                    'results': specific_extractions
                }

            # Phase 3: Verify MongoDB storage
            print("\n" + "=" * 60)
            print("PHASE 3: MONGODB STORAGE VERIFICATION")
            print("=" * 60)
            storage_verification = await self.verify_mongodb_storage()
            test_results['phases']['mongodb_verification'] = storage_verification

            # Overall assessment
            all_phases_successful = all(
                phase.get('status') in ['completed', 'success']
                for phase in test_results['phases'].values()
                if isinstance(phase, dict) and 'status' in phase
            )

            test_results['overall_status'] = 'success' if all_phases_successful else 'partial_success'
            test_results['test_end_time'] = datetime.now().isoformat()

            print("\n" + "=" * 60)
            print("TEST RESULTS SUMMARY")
            print("=" * 60)
            print(f"Overall Status: {'✅ SUCCESS' if all_phases_successful else '⚠️ PARTIAL SUCCESS'}")
            print(f"Uploaded Documents: {len(uploaded_docs)}")
            print(f"Successful Extractions: {len([d for d in extracted_docs if d['status'] == 'success'])}")
            print(f"MongoDB Storage Verified: {storage_verification['successful_extractions']}")

            return test_results

        except Exception as e:
            test_results['overall_status'] = 'failed'
            test_results['error'] = str(e)
            test_results['test_end_time'] = datetime.now().isoformat()
            print(f"\n❌ Test failed with error: {str(e)}")
            return test_results

    async def save_test_report(self, test_results: Dict[str, Any], filename: str = None) -> str:
        """Save test results to a JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)

        print(f"📄 Test report saved to: {filename}")
        return filename


async def main():
    """Main test execution function"""
    print("🚀 Legal Clarity Document Processing Test Suite")
    print("=" * 60)

    # Initialize tester
    tester = DocumentProcessingTester()

    # Document IDs provided by user for specific testing
    specific_doc_ids = [
        "e12829e2-268a-4aa2-acfe-7bb4710c0e30",
        "4a2f8446-b236-4ba6-9f49-05366def62a7"
    ]

    print(f"📋 Will test with specific document IDs: {specific_doc_ids}")

    # Run comprehensive test
    test_results = await tester.run_comprehensive_test(specific_doc_ids)

    # Save test report
    report_file = await tester.save_test_report(test_results)

    print(f"\n🎯 Test execution complete! Report saved to: {report_file}")

    # Print final status
    if test_results['overall_status'] == 'success':
        print("✅ All tests passed successfully!")
    elif test_results['overall_status'] == 'partial_success':
        print("⚠️ Some tests passed, but there were issues. Check the report for details.")
    else:
        print("❌ Test suite failed. Check the report for error details.")

    return test_results


if __name__ == "__main__":
    # Run the test suite
    asyncio.run(main())
