"""
Enhanced Background Processing Functions for Legal Document Analysis
"""

import logging
import time
import os
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Get settings from environment
MONGO_PROCESSED_DOCS_COLLECTION = os.getenv('MONGO_PROCESSED_DOCS_COLLECTION', 'processed_documents')

async def process_enhanced_document_analysis(
    document_id: str,
    gcs_path: str,
    document_type: str,
    user_id: str,
    analysis_options: Dict[str, Any]
):
    """Enhanced background task for document analysis"""
    
    global mongodb_db, document_processor
    
    try:
        logger.info(f"Starting enhanced analysis for document: {document_id}")
        
        # Perform analysis using enhanced processor
        analysis_result = await document_processor.analyze_document(
            document_id=document_id,
            gcs_path=gcs_path,
            document_type=document_type,
            user_id=user_id,
            analysis_options=analysis_options
        )
        
        # Convert to dict for MongoDB storage
        analysis_dict = analysis_result.model_dump(mode='json')
        
        # Store results in MongoDB
        doc_to_store = {
            "document_id": document_id,
            "user_id": user_id,
            "document_type": document_type,
            "analysis_result": analysis_dict,
            "processing_timestamp": time.time(),
            "status": "completed",
            "processing_type": "enhanced_analysis"
        }
        
        # Use the async MongoDB client
        collection = mongodb_db[MONGO_PROCESSED_DOCS_COLLECTION]
        await collection.replace_one(
            {"document_id": document_id, "user_id": user_id, "processing_type": "enhanced_analysis"},
            doc_to_store,
            upsert=True
        )
        
        logger.info(f"✅ Enhanced analysis completed for document: {document_id}")
        logger.info(f"   - Found {len(analysis_result.extracted_entities)} entities")
        logger.info(f"   - Risk level: {analysis_result.risk_assessment.overall_risk_level}")
        logger.info(f"   - Compliance score: {analysis_result.compliance_check.compliance_score}%")
        
    except Exception as e:
        logger.error(f"❌ Enhanced analysis failed for {document_id}: {e}")
        
        # Store error result
        error_doc = {
            "document_id": document_id,
            "user_id": user_id,
            "status": "failed",
            "error": str(e),
            "processing_timestamp": time.time(),
            "processing_type": "enhanced_analysis"
        }
        
        collection = mongodb_db[MONGO_PROCESSED_DOCS_COLLECTION]
        await collection.replace_one(
            {"document_id": document_id, "user_id": user_id, "processing_type": "enhanced_analysis"},
            error_doc,
            upsert=True
        )

async def process_enhanced_legal_extraction(
    document_id: str,
    gcs_path: str,
    document_type: str,
    user_id: str,
    extraction_options: Dict[str, Any]
):
    """Enhanced background task for legal clause extraction"""
    
    global mongodb_db, document_processor
    
    try:
        logger.info(f"Starting enhanced extraction for document: {document_id}")
        
        # Perform extraction using enhanced processor
        extraction_result = await document_processor.extract_legal_clauses(
            document_id=document_id,
            gcs_path=gcs_path,
            document_type=document_type,
            user_id=user_id,
            extraction_options=extraction_options
        )
        
        # Convert to dict for MongoDB storage
        extraction_dict = extraction_result.model_dump(mode='json')
        
        # Store results in MongoDB
        doc_to_store = {
            "document_id": document_id,
            "user_id": user_id,
            "document_type": document_type,
            "extraction_result": extraction_dict,
            "processing_timestamp": time.time(),
            "status": "completed",
            "processing_type": "enhanced_extraction"
        }
        
        # Use the async MongoDB client
        collection = mongodb_db[MONGO_PROCESSED_DOCS_COLLECTION]
        await collection.replace_one(
            {"document_id": document_id, "user_id": user_id, "processing_type": "enhanced_extraction"},
            doc_to_store,
            upsert=True
        )
        
        logger.info(f"✅ Enhanced extraction completed for document: {document_id}")
        logger.info(f"   - Found {len(extraction_result.extracted_clauses)} legal clauses")
        logger.info(f"   - Identified {len(extraction_result.parties_identified)} parties")
        logger.info(f"   - Extracted {len(extraction_result.financial_terms)} financial terms")
        logger.info(f"   - Found {len(extraction_result.important_dates)} important dates")
        
    except Exception as e:
        logger.error(f"❌ Enhanced extraction failed for {document_id}: {e}")
        
        # Store error result
        error_doc = {
            "document_id": document_id,
            "user_id": user_id,
            "status": "failed",
            "error": str(e),
            "processing_timestamp": time.time(),
            "processing_type": "enhanced_extraction"
        }
        
        collection = mongodb_db[MONGO_PROCESSED_DOCS_COLLECTION]
        await collection.replace_one(
            {"document_id": document_id, "user_id": user_id, "processing_type": "enhanced_extraction"},
            error_doc,
            upsert=True
        )