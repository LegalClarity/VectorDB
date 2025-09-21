#!/usr/bin/env python3
"""
Debug extraction response format
"""

import requests
import json

def debug_extraction():
    """Debug the extraction endpoint response"""
    
    print("🔍 Debugging extraction response format...")
    
    test_request = {
        "document_text": """
        RENTAL AGREEMENT
        
        Property Address: 123 Main Street, Suite 4B
        Tenant: John Doe
        Landlord: ABC Property Management LLC
        
        1. RENT: The monthly rent is $1,200, due on the 1st of each month.
        """,
        "document_type": "rental_agreement",
        "user_id": "debug_user",
        "document_id": "debug_doc"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/extractor/extract",
            json=test_request,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print("Raw Response:")
        print(response.text)
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                print("\nParsed JSON:")
                print(json.dumps(json_response, indent=2))
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    debug_extraction()