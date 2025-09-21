#!/usr/bin/env python3
"""
Test script to analyze current API endpoint issues
Tests both analyzer and extractor endpoints with the provided document ID
"""

import requests
import json
import time
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8001"
DOCUMENT_ID = "c0133bb6-f25a-4114-a4c3-1b1e8630e27f"
USER_ID = "e0722091-aaeb-43f3-8cac-d6562c85ec79"  # From the test

def test_health_endpoints():
    """Test all health endpoints"""
    print("🏥 Testing Health Endpoints")
    print("-" * 40)
    
    health_endpoints = [
        "/health",
        "/",
        "/api/analyzer/health",
        "/api/extractor/health"
    ]
    
    for endpoint in health_endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
            if endpoint == "/":
                data = response.json()
                print(f"   Endpoints: {list(data.get('endpoints', {}).keys())}")
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    print()

def test_analyzer_endpoint():
    """Test the analyzer endpoint"""
    print("🔍 Testing Analyzer Endpoint")
    print("-" * 40)
    
    # Test 1: Basic request structure
    analyzer_request = {
        "document_id": DOCUMENT_ID,
        "user_id": USER_ID,
        "document_type": "rental_agreement"
    }
    
    try:
        print("1. Testing analyzer analyze endpoint...")
        response = requests.post(
            f"{API_BASE_URL}/api/analyzer/analyze",
            json=analyzer_request,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            if data.get('data'):
                print(f"   Data keys: {list(data['data'].keys())}")
        else:
            print(f"   Error: {response.text}")
            
        # Test 2: Get results (should be processing)
        print("\n2. Testing analyzer results endpoint...")
        response = requests.get(
            f"{API_BASE_URL}/api/analyzer/results/{DOCUMENT_ID}",
            params={"user_id": USER_ID},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Analyzer endpoint error: {e}")
    print()

def test_extractor_endpoint():
    """Test the extractor endpoint"""
    print("⚗️ Testing Extractor Endpoint")
    print("-" * 40)
    
    # Test 1: Basic request structure
    extractor_request = {
        "document_id": DOCUMENT_ID,
        "user_id": USER_ID,
        "document_type": "rental_agreement"
    }
    
    try:
        print("1. Testing extractor extract endpoint...")
        response = requests.post(
            f"{API_BASE_URL}/api/extractor/extract",
            json=extractor_request,
            timeout=30
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            if data.get('data'):
                print(f"   Data keys: {list(data['data'].keys())}")
        else:
            print(f"   Error: {response.text}")
            
        # Test 2: Get results (should be processing)
        print("\n2. Testing extractor results endpoint...")
        response = requests.get(
            f"{API_BASE_URL}/api/extractor/results/{DOCUMENT_ID}",
            params={"user_id": USER_ID},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Extractor endpoint error: {e}")
    print()

def test_openapi_docs():
    """Test OpenAPI documentation endpoints"""
    print("📚 Testing OpenAPI Documentation")
    print("-" * 40)
    
    try:
        # Test OpenAPI schema
        response = requests.get(f"{API_BASE_URL}/openapi.json", timeout=10)
        print(f"OpenAPI Schema: {response.status_code}")
        
        if response.status_code == 200:
            schema = response.json()
            paths = schema.get('paths', {})
            print(f"   Available paths: {len(paths)}")
            
            # Check analyzer endpoints
            analyzer_paths = [p for p in paths if 'analyzer' in p]
            extractor_paths = [p for p in paths if 'extractor' in p]
            
            print(f"   Analyzer paths: {analyzer_paths}")
            print(f"   Extractor paths: {extractor_paths}")
            
            # Check if paths have proper schemas
            for path in analyzer_paths + extractor_paths:
                path_info = paths.get(path, {})
                for method in ['post', 'get']:
                    if method in path_info:
                        operation = path_info[method]
                        print(f"   {method.upper()} {path}:")
                        print(f"     - Summary: {operation.get('summary', 'Missing')}")
                        print(f"     - Parameters: {len(operation.get('parameters', []))}")
                        
                        if method == 'post':
                            request_body = operation.get('requestBody', {})
                            if request_body:
                                print(f"     - Request body: Yes")
                            else:
                                print(f"     - Request body: Missing")
                        
                        responses = operation.get('responses', {})
                        print(f"     - Response codes: {list(responses.keys())}")
        
    except Exception as e:
        print(f"❌ OpenAPI documentation error: {e}")
    print()

def wait_and_check_processing():
    """Wait and check if background processing completed"""
    print("⏳ Waiting for background processing...")
    print("-" * 40)
    
    max_wait = 60  # Wait max 1 minute
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        try:
            # Check analyzer results
            response = requests.get(
                f"{API_BASE_URL}/api/analyzer/results/{DOCUMENT_ID}",
                params={"user_id": USER_ID},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    print("✅ Analyzer processing completed!")
                    analyzer_data = data['data']
                    print(f"   Keys: {list(analyzer_data.keys())}")
                    break
            
            # Check extractor results
            response = requests.get(
                f"{API_BASE_URL}/api/extractor/results/{DOCUMENT_ID}",
                params={"user_id": USER_ID},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('data'):
                    print("✅ Extractor processing completed!")
                    extractor_data = data['data']
                    print(f"   Keys: {list(extractor_data.keys())}")
                    break
            
            print(f"   Still processing... ({int(time.time() - start_time)}s)")
            time.sleep(5)
            
        except Exception as e:
            print(f"   Error checking status: {e}")
            break
    
    if time.time() - start_time >= max_wait:
        print("⚠️  Processing timeout - background tasks may still be running")
    print()

def main():
    """Main test function"""
    print("🚀 Legal Clarity API - Endpoint Analysis")
    print("=" * 50)
    print(f"Base URL: {API_BASE_URL}")
    print(f"Document ID: {DOCUMENT_ID}")
    print(f"User ID: {USER_ID}")
    print()
    
    # Test all endpoints
    test_health_endpoints()
    test_analyzer_endpoint()
    test_extractor_endpoint()
    test_openapi_docs()
    
    # Wait for background processing
    wait_and_check_processing()

if __name__ == "__main__":
    main()