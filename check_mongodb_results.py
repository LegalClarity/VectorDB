#!/usr/bin/env python3
"""
Check MongoDB to see what's actually being stored in the processed documents collection
"""

import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId
import pprint

# Load environment variables
load_dotenv()

def check_mongodb_processing_results():
    """Check what's in the processed documents collection"""
    print("🗄️ MongoDB Processing Results Analysis")
    print("=" * 50)
    
    try:
        # Connect to MongoDB
        mongo_uri = os.getenv('MONGO_URI')
        mongo_db = os.getenv('MONGO_DB')
        processed_collection = os.getenv('MONGO_PROCESSED_DOCS_COLLECTION')
        
        client = MongoClient(mongo_uri)
        db = client[mongo_db]
        collection = db[processed_collection]
        
        document_id = "c0133bb6-f25a-4114-a4c3-1b1e8630e27f"
        user_id = "e0722091-aaeb-43f3-8cac-d6562c85ec79"
        
        print(f"Looking for processed documents for document_id: {document_id}")
        
        # Find all processed documents for this document_id
        query = {"document_id": document_id}
        documents = list(collection.find(query))
        
        print(f"Found {len(documents)} processed document(s)")
        
        for i, doc in enumerate(documents):
            print(f"\n--- DOCUMENT {i+1} ---")
            print(f"Document ID: {doc.get('document_id')}")
            print(f"User ID: {doc.get('user_id')}")
            print(f"Status: {doc.get('status')}")
            print(f"Processing timestamp: {doc.get('processing_timestamp')}")
            
            if 'extraction_result' in doc:
                result = doc['extraction_result']
                print(f"Extraction result type: {type(result)}")
                
                if isinstance(result, dict):
                    print(f"Extraction result keys: {list(result.keys())}")
                    
                    # Check each key
                    for key, value in result.items():
                        print(f"  {key}: {type(value)}")
                        if isinstance(value, list):
                            print(f"    - Count: {len(value)}")
                            if value and key == 'extracted_entities':
                                print(f"    - First entity: {value[0]}")
                        elif isinstance(value, dict) and key == 'risk_assessment':
                            print(f"    - Risk level: {value.get('overall_risk_level')}")
                            print(f"    - Risk factors count: {len(value.get('risk_factors', []))}")
                        elif isinstance(value, dict) and key == 'compliance_check':
                            print(f"    - Compliance score: {value.get('compliance_score')}")
                        elif key == 'summary':
                            print(f"    - Summary: {str(value)[:100]}...")
                else:
                    print(f"Extraction result content: {result}")
            
            if 'error' in doc:
                print(f"ERROR: {doc['error']}")
        
        # Check if there are any other processing attempts
        print(f"\nChecking all documents in processed collection...")
        all_docs = list(collection.find().limit(5))
        print(f"Total processed documents in collection: {collection.count_documents({})}")
        
        for doc in all_docs[:3]:  # Show first 3
            print(f"  - Doc ID: {doc.get('document_id')}, Status: {doc.get('status')}, Timestamp: {doc.get('processing_timestamp')}")
    
    except Exception as e:
        print(f"❌ MongoDB analysis error: {e}")

def main():
    check_mongodb_processing_results()

if __name__ == "__main__":
    main()