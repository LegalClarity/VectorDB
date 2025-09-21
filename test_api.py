"""
Test script for the Legal Clarity API endpoints
Tests analyzer and extractor functionality with the provided document ID
"""
import requests
import json
import time

# API configuration
BASE_URL = "http://localhost:8001"
TEST_DOCUMENT_ID = "c0133bb6-f25a-4114-a4c3-1b1e8630e27f"
TEST_USER_ID = "e0722091-aaeb-43f3-8cac-d6562c85ec79"

def test_health():
    """Test health endpoint"""
    print("🩺 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   MongoDB: {data['services']['mongodb']}")
            print(f"   GCS: {data['services']['gcs']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_analyzer_endpoint():
    """Test analyzer endpoint"""
    print("\n🔍 Testing analyzer endpoint...")
    try:
        # Test analyze request
        analyze_data = {
            "document_id": TEST_DOCUMENT_ID,
            "user_id": TEST_USER_ID,
            "document_type": "rental"
        }
        
        print(f"   Requesting analysis for document: {TEST_DOCUMENT_ID}")
        response = requests.post(f"{BASE_URL}/api/analyzer/analyze", json=analyze_data)
        print(f"✅ Analysis request: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data['data']['status']}")
            print(f"   Document type: {data['data']['document_type']}")
            print(f"   Filename: {data['data']['original_filename']}")
            
            # Wait a moment for background processing
            print("   Waiting for processing...")
            time.sleep(5)
            
            # Check results
            results_response = requests.get(f"{BASE_URL}/api/analyzer/results/{TEST_DOCUMENT_ID}?user_id={TEST_USER_ID}")
            print(f"✅ Results retrieval: {results_response.status_code}")
            
            if results_response.status_code == 200:
                results_data = results_response.json()
                print(f"   Analysis status: {results_data['data']['status']}")
                if 'analysis_result' in results_data['data']:
                    analysis = results_data['data']['analysis_result']
                    print(f"   Entities extracted: {len(analysis.get('extracted_entities', []))}")
                    print(f"   Key terms: {len(analysis.get('key_terms', []))}")
                    print(f"   Confidence: {analysis.get('confidence_score', 'N/A')}")
            else:
                print(f"   Results not ready yet: {results_response.text}")
                
        return True
    except Exception as e:
        print(f"❌ Analyzer test failed: {e}")
        return False

def test_extractor_endpoint():
    """Test extractor endpoint"""
    print("\n⚖️ Testing extractor endpoint...")
    try:
        # Test extract request
        extract_data = {
            "document_id": TEST_DOCUMENT_ID,
            "user_id": TEST_USER_ID,
            "document_type": "rental_agreement"
        }
        
        print(f"   Requesting extraction for document: {TEST_DOCUMENT_ID}")
        response = requests.post(f"{BASE_URL}/api/extractor/extract", json=extract_data)
        print(f"✅ Extraction request: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data['data']['status']}")
            print(f"   Document type: {data['data']['document_type']}")
            print(f"   Filename: {data['data']['original_filename']}")
            
            # Wait for processing
            print("   Waiting for processing...")
            time.sleep(8)  # Extraction takes a bit longer
            
            # Check results
            results_response = requests.get(f"{BASE_URL}/api/extractor/results/{TEST_DOCUMENT_ID}?user_id={TEST_USER_ID}")
            print(f"✅ Results retrieval: {results_response.status_code}")
            
            if results_response.status_code == 200:
                results_data = results_response.json()
                print(f"   Extraction status: {results_data['data']['status']}")
                if 'extraction_result' in results_data['data']:
                    extraction = results_data['data']['extraction_result']
                    print(f"   Clauses extracted: {len(extraction.get('extracted_clauses', []))}")
                    print(f"   Confidence score: {extraction.get('confidence_score', 'N/A')}")
                    
                    # Show some extracted entities
                    entities = extraction.get('entities', {})
                    for category, items in entities.items():
                        if items:
                            print(f"   {category}: {len(items)} items")
            else:
                print(f"   Results not ready yet: {results_response.text}")
                
        return True
    except Exception as e:
        print(f"❌ Extractor test failed: {e}")
        return False

def test_api_documentation():
    """Test if API documentation is accessible"""
    print("\n📚 Testing API documentation...")
    try:
        docs_response = requests.get(f"{BASE_URL}/docs")
        print(f"✅ API docs accessibility: {docs_response.status_code}")
        
        # Test root endpoint
        root_response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {root_response.status_code}")
        if root_response.status_code == 200:
            data = root_response.json()
            print(f"   API version: {data.get('version', 'Unknown')}")
            
        return True
    except Exception as e:
        print(f"❌ Documentation test failed: {e}")
        return False

def main():
    """Run all API tests"""
    print("🚀 Starting Legal Clarity API Tests")
    print("=" * 50)
    
    # Check if server is running
    if not test_health():
        print("❌ Server is not running. Please start the API first with: python main_fixed.py")
        return
    
    # Run all tests
    tests = [
        test_api_documentation,
        test_analyzer_endpoint,
        test_extractor_endpoint
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Tests completed: {passed}/{len(tests) + 1} passed")
    
    if passed == len(tests) + 1:
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️ Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    main()