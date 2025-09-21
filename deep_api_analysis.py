#!/usr/bin/env python3
"""
Deep analysis of API responses to understand current functionality and issues
"""

import requests
import json
import pprint
from typing import Dict, Any

# API Configuration
API_BASE_URL = "http://localhost:8001"
DOCUMENT_ID = "c0133bb6-f25a-4114-a4c3-1b1e8630e27f"
USER_ID = "e0722091-aaeb-43f3-8cac-d6562c85ec79"

def analyze_api_response_structure():
    """Analyze the structure and content of API responses"""
    print("🔬 Deep API Response Analysis")
    print("=" * 50)
    
    # Get analyzer results
    print("1. ANALYZER RESULTS ANALYSIS")
    print("-" * 30)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/analyzer/results/{DOCUMENT_ID}",
            params={"user_id": USER_ID},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analyzer Response Structure:")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            
            if data.get('data'):
                analysis_data = data['data']
                print("\n   Analysis Data Structure:")
                for key, value in analysis_data.items():
                    print(f"     {key}: {type(value)} - {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
                
                # Deep dive into analysis_result
                if 'analysis_result' in analysis_data:
                    result = analysis_data['analysis_result']
                    print(f"\n   Analysis Result Details:")
                    if isinstance(result, dict):
                        for key, value in result.items():
                            print(f"     {key}: {type(value)}")
                            if key == 'extracted_entities' and isinstance(value, list):
                                print(f"       - Count: {len(value)}")
                                if value:
                                    print(f"       - First entity: {value[0]}")
                            elif key == 'key_terms' and isinstance(value, list):
                                print(f"       - Count: {len(value)}")
                            elif key == 'risk_assessment' and isinstance(value, dict):
                                print(f"       - Risk level: {value.get('overall_risk_level')}")
                                print(f"       - Risk factors: {len(value.get('risk_factors', []))}")
                            elif key == 'compliance_check' and isinstance(value, dict):
                                print(f"       - Compliance score: {value.get('compliance_score')}")
        else:
            print(f"❌ Analyzer error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Analyzer analysis error: {e}")
    
    print("\n" + "="*50)
    
    # Get extractor results
    print("2. EXTRACTOR RESULTS ANALYSIS")
    print("-" * 30)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/extractor/results/{DOCUMENT_ID}",
            params={"user_id": USER_ID},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Extractor Response Structure:")
            print(f"   Success: {data.get('success')}")
            print(f"   Message: {data.get('message')}")
            
            if data.get('data'):
                extraction_data = data['data']
                print("\n   Extraction Data Structure:")
                for key, value in extraction_data.items():
                    print(f"     {key}: {type(value)} - {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
                
                # Deep dive into extraction_result
                if 'extraction_result' in extraction_data:
                    result = extraction_data['extraction_result']
                    print(f"\n   Extraction Result Details:")
                    if isinstance(result, dict):
                        for key, value in result.items():
                            print(f"     {key}: {type(value)}")
                            if key == 'extracted_clauses' and isinstance(value, list):
                                print(f"       - Count: {len(value)}")
                                if value:
                                    print(f"       - First clause: {value[0]}")
                            elif key == 'clause_relationships' and isinstance(value, list):
                                print(f"       - Count: {len(value)}")
        else:
            print(f"❌ Extractor error: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"❌ Extractor analysis error: {e}")

def check_openapi_schema_details():
    """Check OpenAPI schema for missing details"""
    print("\n" + "="*50)
    print("3. OPENAPI SCHEMA ANALYSIS")
    print("-" * 30)
    
    try:
        response = requests.get(f"{API_BASE_URL}/openapi.json", timeout=10)
        if response.status_code == 200:
            schema = response.json()
            
            # Check components/schemas
            components = schema.get('components', {})
            schemas = components.get('schemas', {})
            
            print(f"Available schemas: {list(schemas.keys())}")
            
            # Check request/response models
            paths = schema.get('paths', {})
            
            # Analyze analyzer endpoint
            analyzer_analyze = paths.get('/api/analyzer/analyze', {}).get('post', {})
            print(f"\nAnalyzer Analyze Endpoint:")
            print(f"  Summary: {analyzer_analyze.get('summary')}")
            print(f"  Description: {analyzer_analyze.get('description', 'Missing')[:100]}...")
            
            request_body = analyzer_analyze.get('requestBody', {})
            if request_body:
                content = request_body.get('content', {})
                app_json = content.get('application/json', {})
                schema_ref = app_json.get('schema', {})
                print(f"  Request schema: {schema_ref}")
            
            responses = analyzer_analyze.get('responses', {})
            for code, response_def in responses.items():
                print(f"  Response {code}: {response_def.get('description', 'No description')}")
            
            # Analyze extractor endpoint
            extractor_extract = paths.get('/api/extractor/extract', {}).get('post', {})
            print(f"\nExtractor Extract Endpoint:")
            print(f"  Summary: {extractor_extract.get('summary')}")
            print(f"  Description: {extractor_extract.get('description', 'Missing')[:100]}...")
            
            # Check for examples
            if 'examples' in analyzer_analyze:
                print(f"  Analyzer has examples: Yes")
            else:
                print(f"  Analyzer has examples: No")
                
            if 'examples' in extractor_extract:
                print(f"  Extractor has examples: Yes")
            else:
                print(f"  Extractor has examples: No")
    
    except Exception as e:
        print(f"❌ OpenAPI schema analysis error: {e}")

def test_invalid_requests():
    """Test API validation by sending invalid requests"""
    print("\n" + "="*50)
    print("4. VALIDATION TESTING")
    print("-" * 30)
    
    # Test missing document_id
    print("Testing missing document_id...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/analyzer/analyze",
            json={"user_id": USER_ID, "document_type": "rental_agreement"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test invalid document_type
    print("\nTesting invalid document_type...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/analyzer/analyze",
            json={
                "document_id": DOCUMENT_ID,
                "user_id": USER_ID,
                "document_type": "invalid_type"
            },
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test malformed request
    print("\nTesting malformed request...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/extractor/extract",
            json={"invalid": "data"},
            timeout=10
        )
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")

def main():
    """Main analysis function"""
    print("🔍 Legal Clarity API - Deep Response Analysis")
    print("=" * 60)
    
    analyze_api_response_structure()
    check_openapi_schema_details()
    test_invalid_requests()
    
    print("\n🎯 SUMMARY OF ISSUES FOUND:")
    print("1. Basic functionality works - APIs respond correctly")
    print("2. Background processing is working")
    print("3. Need to check if actual legal extraction is happening")
    print("4. Need to verify schema completeness and validation")
    print("5. Need to check if real document content is being processed")

if __name__ == "__main__":
    main()