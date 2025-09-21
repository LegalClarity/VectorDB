"""
Test Enhanced API Implementation
Tests the analyzer and extractor endpoints with enhanced schemas
"""

import json
import requests
import time
from datetime import datetime

# Test configuration
BASE_URL = "http://127.0.0.1:8001/api"
DOCUMENT_ID = "c0133bb6-f25a-4114-a4c3-1b1e8630e27f"  # Your test document
USER_ID = "e0722091-aaeb-43f3-8cac-d6562c85ec79"  # Correct user_id from MongoDB

def test_enhanced_analyzer():
    """Test the enhanced analyzer endpoint with comprehensive schema"""
    print("🔍 Testing Enhanced Analyzer Endpoint")
    print("=" * 50)
    
    # Test request with comprehensive analysis options
    request_data = {
        "document_id": DOCUMENT_ID,
        "user_id": USER_ID,
        "document_type": "rental_agreement",  # Fixed to match enum
        "analysis_options": {
            "include_risk_assessment": True,
            "include_compliance_check": True,
            "extract_entities": True,
            "analyze_financial_terms": True,
            "detailed_analysis": True
        }
    }
    
    try:
        print(f"📤 Sending analyzer request:")
        print(json.dumps(request_data, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/analyzer/analyze",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analyzer request successful!")
            print(json.dumps(result, indent=2))
            return result.get("data", {}).get("document_id")
        else:
            print(f"❌ Analyzer request failed:")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error testing analyzer: {e}")
        return None

def test_enhanced_extractor():
    """Test the enhanced extractor endpoint with comprehensive schema"""
    print("\n🔧 Testing Enhanced Extractor Endpoint")
    print("=" * 50)
    
    # Test request with comprehensive extraction options
    request_data = {
        "document_id": DOCUMENT_ID,
        "user_id": USER_ID,
        "document_type": "rental_agreement",  # Fixed to match enum
        "extraction_options": {
            "extract_clauses": True,
            "extract_parties": True,
            "extract_financial_terms": True,
            "extract_dates": True,
            "extract_relationships": True,
            "include_legal_references": True,
            "detailed_extraction": True
        }
    }
    
    try:
        print(f"📤 Sending extractor request:")
        print(json.dumps(request_data, indent=2))
        
        response = requests.post(
            f"{BASE_URL}/extractor/extract",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Extractor request successful!")
            print(json.dumps(result, indent=2))
            return result.get("data", {}).get("document_id")
        else:
            print(f"❌ Extractor request failed:")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error testing extractor: {e}")
        return None

def test_processing_status(document_id):
    """Test the processing status endpoint"""
    print(f"\n📊 Testing Processing Status for Document: {document_id}")
    print("=" * 50)
    
    try:
        # Wait a bit for processing to start
        print("⏳ Waiting 3 seconds for processing to start...")
        time.sleep(3)
        
        response = requests.get(
            f"{BASE_URL}/analyzer/{document_id}/status",
            params={"user_id": USER_ID}
        )
        
        print(f"📥 Status Response: {response.status_code}")
        
        if response.status_code == 200:
            status = response.json()
            print("✅ Status check successful!")
            print(json.dumps(status, indent=2))
        else:
            print(f"❌ Status check failed:")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")

def test_results_retrieval(document_id):
    """Test retrieving analysis/extraction results"""
    print(f"\n📋 Testing Results Retrieval for Document: {document_id}")
    print("=" * 50)
    
    # Wait for processing to complete
    print("⏳ Waiting 10 seconds for processing to complete...")
    time.sleep(10)
    
    try:
        # Test analyzer results
        print("\n🔍 Checking Analyzer Results:")
        response = requests.get(
            f"{BASE_URL}/analyzer/{document_id}/results",
            params={"user_id": USER_ID}
        )
        
        print(f"📥 Analyzer Results Status: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print("✅ Analyzer results retrieved!")
            print(json.dumps(results, indent=2)[:1000] + "...")  # Truncate for readability
        else:
            print(f"❌ Failed to get analyzer results: {response.text}")
        
        # Test extractor results
        print("\n🔧 Checking Extractor Results:")
        response = requests.get(
            f"{BASE_URL}/extractor/{document_id}/results",
            params={"user_id": USER_ID}
        )
        
        print(f"📥 Extractor Results Status: {response.status_code}")
        if response.status_code == 200:
            results = response.json()
            print("✅ Extractor results retrieved!")
            print(json.dumps(results, indent=2)[:1000] + "...")  # Truncate for readability
        else:
            print(f"❌ Failed to get extractor results: {response.text}")
            
    except Exception as e:
        print(f"❌ Error retrieving results: {e}")

def main():
    """Main test function"""
    print(f"🚀 Enhanced API Test Suite")
    print(f"📅 Started at: {datetime.now()}")
    print("=" * 60)
    
    # Test analyzer endpoint
    analyzer_doc_id = test_enhanced_analyzer()
    
    # Test extractor endpoint
    extractor_doc_id = test_enhanced_extractor()
    
    # Use analyzer doc_id for status and results testing
    if analyzer_doc_id:
        test_processing_status(analyzer_doc_id)
        test_results_retrieval(analyzer_doc_id)
    
    print(f"\n✅ Enhanced API Test Suite Completed!")
    print(f"📅 Finished at: {datetime.now()}")

if __name__ == "__main__":
    main()