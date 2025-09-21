#!/usr/bin/env python3
"""
Test script for the running Legal Clarity API
Tests basic connectivity and endpoint functionality
"""

import requests
import json
import time

# API configuration
BASE_URL = 'http://localhost:8001'
TEST_DOCUMENT_ID = 'c0133bb6-f25a-4114-a4c3-1b1e8630e27f'
TEST_USER_ID = 'e0722091-aaeb-43f3-8cac-d6562c85ec79'

def test_basic_connectivity():
    """Test basic API connectivity"""
    print('🚀 Testing Legal Clarity API endpoints...')
    print('=' * 50)
    
    # Test 1: Health check
    print('🩺 Testing health endpoint...')
    try:
        response = requests.get(f'{BASE_URL}/health', timeout=10)
        print(f'✅ Health check: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   MongoDB: {data.get("services", {}).get("mongodb", "N/A")}')
            print(f'   GCS: {data.get("services", {}).get("gcs", "N/A")}')
            return True
        else:
            print(f'   Response: {response.text[:200]}')
    except Exception as e:
        print(f'❌ Health check failed: {e}')
    
    # Test 2: Root endpoint
    print('\n📚 Testing root endpoint...')
    try:
        response = requests.get(f'{BASE_URL}/', timeout=10)
        print(f'✅ Root endpoint: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'   Message: {data.get("message", "N/A")}')
            print(f'   Version: {data.get("version", "N/A")}')
        else:
            print(f'   Response: {response.text[:200]}')
    except Exception as e:
        print(f'❌ Root endpoint failed: {e}')
    
    return False

def test_analyzer_endpoint():
    """Test the document analyzer endpoint"""
    print('\n🔍 Testing analyzer endpoint...')
    
    payload = {
        "document_id": TEST_DOCUMENT_ID,
        "user_id": TEST_USER_ID,
        "analysis_type": "comprehensive",
        "include_metadata": True
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/analyzer/analyze', 
            json=payload,
            timeout=30
        )
        
        print(f'✅ Analyzer request: {response.status_code}')
        
        if response.status_code == 202:
            data = response.json()
            task_id = data.get('task_id')
            print(f'   Task ID: {task_id}')
            print('   Status: Analysis started in background')
            return task_id
        elif response.status_code == 200:
            data = response.json()
            print(f'   Analysis completed immediately')
            print(f'   Document type: {data.get("document_type", "N/A")}')
        else:
            print(f'   Error response: {response.text[:300]}')
            
    except Exception as e:
        print(f'❌ Analyzer test failed: {e}')
    
    return None

def test_extractor_endpoint():
    """Test the document extractor endpoint (main functionality)"""
    print('\n🔧 Testing extractor endpoint...')
    
    payload = {
        "document_id": TEST_DOCUMENT_ID,
        "user_id": TEST_USER_ID,
        "extraction_type": "comprehensive",
        "include_clauses": True,
        "include_entities": True,
        "include_relationships": True
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/extractor/extract', 
            json=payload,
            timeout=60  # Allow more time for extraction
        )
        
        print(f'✅ Extractor request: {response.status_code}')
        
        if response.status_code == 202:
            data = response.json()
            task_id = data.get('task_id')
            print(f'   Task ID: {task_id}')
            print('   Status: Extraction started in background')
            return task_id
        elif response.status_code == 200:
            data = response.json()
            print(f'   Extraction completed immediately')
            print(f'   Key clauses found: {len(data.get("key_clauses", []))}')
            print(f'   Entities found: {len(data.get("entities", []))}')
        else:
            print(f'   Error response: {response.text[:300]}')
            
    except Exception as e:
        print(f'❌ Extractor test failed: {e}')
    
    return None

def main():
    """Run all API tests"""
    print('🧪 Legal Clarity API Test Suite')
    print('================================\n')
    
    # Test basic connectivity first
    if not test_basic_connectivity():
        print('\n❌ Basic connectivity failed - skipping endpoint tests')
        return
    
    # Test main endpoints
    analyzer_task = test_analyzer_endpoint()
    extractor_task = test_extractor_endpoint()
    
    # Summary
    print('\n📊 Test Summary')
    print('=' * 30)
    if analyzer_task:
        print(f'✅ Analyzer task started: {analyzer_task}')
    if extractor_task:
        print(f'✅ Extractor task started: {extractor_task}')
    
    print(f'\n🎯 Testing document: {TEST_DOCUMENT_ID}')
    print('💡 Check server logs for detailed processing information')

if __name__ == '__main__':
    main()