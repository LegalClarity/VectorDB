"""
Test script to send analysis request to the API
"""

import requests
import json
import time

def test_health_check():
    """Test health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        print("Health Check Response:")
        print(json.dumps(response.json(), indent=2))
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_document_analysis():
    """Test document analysis endpoint"""
    try:
        url = "http://localhost:8000/analyzer/analyze"
        payload = {
            "document_id": "790e9eeb-f70d-4794-941e-6b0c3e24226f",
            "document_type": "rental",  # Optional, will be detected from document metadata
            "user_id": "test_user"  # You may need to adjust this based on your user system
        }

        print("\nSending analysis request...")
        print(f"URL: {url}")
        print("Payload:")
        print(json.dumps(payload, indent=2))

        response = requests.post(url, json=payload)

        print(f"\nResponse Status: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                if data["data"]["status"] == "processing":
                    print("\n✅ Document analysis started successfully!")
                    print("The analysis is running in the background.")
                    print("Results will be stored in MongoDB collection: processed_documents")

                    # Wait a moment then check results
                    print("\n⏳ Waiting for analysis to complete...")
                    time.sleep(3)

                    # Check results
                    result_url = f"http://localhost:8000/analyzer/results/{payload['document_id']}?user_id={payload['user_id']}"
                    result_response = requests.get(result_url)

                    print(f"\nResults check - Status: {result_response.status_code}")
                    if result_response.status_code == 200:
                        result_data = result_response.json()
                        print("Analysis Results:")
                        print(json.dumps(result_data, indent=2))
                    else:
                        print("Analysis still in progress or failed")
                        print(result_response.text)

                elif data["data"]["status"] == "completed":
                    print("\n✅ Analysis already completed!")
                    print("Results:", json.dumps(data["data"]["analysis_result"], indent=2))
            else:
                print("❌ Request failed:", data.get("error", "Unknown error"))
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"❌ Analysis request failed: {e}")

def main():
    """Main test function"""
    print("🧪 Testing Document Analyzer API")
    print("=" * 50)

    # Test health check first
    if not test_health_check():
        print("❌ API is not running. Please start the API first.")
        return

    # Test document analysis
    test_document_analysis()

    print("\n" + "=" * 50)
    print("📊 API Test Complete")

if __name__ == "__main__":
    main()
