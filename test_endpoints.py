#!/usr/bin/env python3
"""
Quick test script to verify API endpoints
"""
import requests
import json

def test_endpoints():
    """Test the consolidated API endpoints"""
    base_url = "http://localhost:8001"
    
    print("🧪 Testing Legal Clarity Consolidated API")
    print("=" * 50)
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/api/documents/health", "Documents health"),
        ("GET", "/api/analyzer/health", "Analyzer health"),
        ("GET", "/api/extractor/health", "Extractor health"),
    ]
    
    for method, endpoint, description in endpoints:
        try:
            print(f"\n📍 Testing {description}: {method} {endpoint}")
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if 'status' in data:
                    print(f"   Status: {data['status']}")
                if 'service' in data:
                    print(f"   Service: {data['service']}")
                if 'message' in data:
                    print(f"   Message: {data['message']}")
                print("   ✅ Success")
            else:
                print("   ❌ Failed")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 Test completed!")
    print("\nTo see all endpoints, visit: http://localhost:8001/docs")

if __name__ == "__main__":
    test_endpoints()