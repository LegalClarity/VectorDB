"""
Check Available Documents in MongoDB
"""

import asyncio
import os
import motor.motor_asyncio
from dotenv import load_dotenv
import json
from datetime import datetime

# Load environment variables
load_dotenv()

async def check_documents():
    """Check what documents are available in MongoDB"""
    print("🔍 Checking Available Documents in MongoDB")
    print("=" * 50)
    
    # Connect to MongoDB
    mongo_uri = os.getenv('MONGO_URI')
    mongo_db = os.getenv('MONGO_DB')
    mongo_docs_collection = os.getenv('MONGO_DOCS_COLLECTION')
    
    client = motor.motor_asyncio.AsyncIOMotorClient(mongo_uri)
    db = client[mongo_db]
    collection = db[mongo_docs_collection]
    
    try:
        # Get all documents
        documents = []
        cursor = collection.find({})
        async for doc in cursor:
            # Convert ObjectId to string for JSON serialization
            doc['_id'] = str(doc['_id'])
            documents.append(doc)
        
        print(f"📊 Found {len(documents)} documents:")
        print()
        
        for i, doc in enumerate(documents, 1):
            print(f"Document {i}:")
            print(f"  - ID: {doc.get('document_id', 'N/A')}")
            print(f"  - User ID: {doc.get('user_id', 'N/A')}")
            print(f"  - Filename: {doc.get('original_filename', 'N/A')}")
            print(f"  - Status: {doc.get('status', {}).get('processing_status', 'N/A')}")
            print(f"  - Upload Date: {doc.get('upload_timestamp', 'N/A')}")
            print(f"  - GCS Path: {doc.get('gcs_object_path', 'N/A')}")
            print()
        
        # Look specifically for our test document
        target_doc_id = "c0133bb6-f25a-4114-a4c3-1b1e8630e27f"
        target_doc = await collection.find_one({"document_id": target_doc_id})
        
        if target_doc:
            print(f"✅ Found our target document: {target_doc_id}")
            target_doc['_id'] = str(target_doc['_id'])
            print("📋 Target Document Details:")
            print(json.dumps(target_doc, indent=2, default=str))
        else:
            print(f"❌ Target document not found: {target_doc_id}")
            
            # Let's check if there's a similar document ID
            similar_cursor = collection.find({"document_id": {"$regex": "c0133bb6"}})
            similar_docs = []
            async for doc in similar_cursor:
                doc['_id'] = str(doc['_id'])
                similar_docs.append(doc)
            
            if similar_docs:
                print(f"🔍 Found {len(similar_docs)} similar documents:")
                for doc in similar_docs:
                    print(f"  - {doc.get('document_id')}")
        
    except Exception as e:
        print(f"❌ Error checking documents: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_documents())