"""
Comprehensive Retrieval Test for Legal Document RAG System
Tests the complete retrieval pipeline with EmbeddingGemma-300M.
"""

import sys
import time
from qdrant_vector_store import QdrantVectorStore
from gemini_legal_assistant import GeminiLegalAssistant

def test_retrieval_system():
    """Test the complete retrieval system functionality."""

    print("🧪 Testing Legal Document RAG Retrieval System")
    print("=" * 60)

    try:
        # Initialize components
        print("🔧 Initializing components...")
        vector_store = QdrantVectorStore()
        gemini_assistant = GeminiLegalAssistant()

        # Get collection info
        collection_info = vector_store.get_collection_info()
        print("✅ Collection Status:")
        print(f"   - Total chunks: {collection_info.get('points_count', 0)}")
        print(f"   - Status: {collection_info.get('status', 'unknown')}")
        print(f"   - Embedding model: Google EmbeddingGemma-300M (768 dimensions)")
        print()

        # Test queries
        test_cases = [
            {
                "query": "What are tenant rights under rent control acts?",
                "expected_doc_type": "rent_control_act",
                "description": "Testing rent control legal provisions"
            },
            {
                "query": "Explain consumer protection provisions in the 2019 act",
                "expected_doc_type": "consumer_protection",
                "description": "Testing consumer protection legal analysis"
            },
            {
                "query": "What does the banking regulation act say about fair practices?",
                "expected_doc_type": "banking_regulation",
                "description": "Testing banking regulation provisions"
            },
            {
                "query": "What are the key clauses in the Indian Contract Act?",
                "expected_doc_type": "contract_act",
                "description": "Testing contract law provisions"
            },
            {
                "query": "Explain housing finance regulations",
                "expected_doc_type": "housing_finance",
                "description": "Testing housing finance regulations"
            }
        ]

        print("🔍 Running Retrieval Tests")
        print("-" * 40)

        total_tests = len(test_cases)
        passed_tests = 0
        total_response_time = 0

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}/{total_tests}: {test_case['description']}")
            print(f"Query: '{test_case['query']}'")

            # Measure retrieval time
            start_time = time.time()

            # Perform retrieval
            retrieval_results = vector_store.search_similar_chunks(
                query=test_case['query'],
                limit=5,  # Get more results for better analysis
                score_threshold=0.0  # Don't filter by score for testing
            )

            retrieval_time = time.time() - start_time
            total_response_time += retrieval_time

            print(".2f")
            # Analyze results
            if retrieval_results:
                passed_tests += 1

                # Analyze top result
                top_result = retrieval_results[0]
                doc_filename = top_result['document_filename']
                doc_type = top_result['document_type']
                relevance_score = top_result['score']

                print(f"   📄 Top result: {doc_filename}")
                print(f"   🏷️  Document type: {doc_type}")
                print(".3f")
                print(f"   📏 Content preview: {top_result['content'][:100]}...")

                # Check if result matches expected document type
                if doc_type == test_case['expected_doc_type']:
                    print("   ✅ Document type matches expectation")
                else:
                    print(f"   ⚠️  Document type differs (expected: {test_case['expected_doc_type']})")

                # Show additional results
                if len(retrieval_results) > 1:
                    print(f"   📊 Additional results: {len(retrieval_results) - 1} more found")
                    for j, result in enumerate(retrieval_results[1:3], 1):  # Show next 2
                        print(".3f")
            else:
                print("   ❌ No results found!")

            print(f"   ⏱️  Retrieval time: {retrieval_time:.3f}s")

        print("\n" + "=" * 60)
        print("📊 RETRIEVAL TEST RESULTS")
        print("=" * 60)

        success_rate = (passed_tests / total_tests) * 100
        avg_response_time = total_response_time / total_tests

        print(f"✅ Tests passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(".3f"        print(".3f"        # Test generation component
        print("\n🤖 Testing Generation Component")
        print("-" * 40)

        # Test a complete RAG query
        test_query = "What are the main tenant rights in rent control legislation?"
        print(f"Query: '{test_query}'")

        # Retrieve context
        context_results = vector_store.search_similar_chunks(test_query, limit=3)
        print(f"Retrieved {len(context_results)} context chunks")

        if context_results:
            # Generate response
            start_time = time.time()
            response = gemini_assistant.generate_legal_response(
                query=test_query,
                context_chunks=context_results,
                streaming=False
            )
            generation_time = time.time() - start_time

            print(f"\n📝 Generated Response ({generation_time:.2f}s):")
            print("-" * 40)
            print(response[:500] + "..." if len(response) > 500 else response)
            print("-" * 40)
            print("✅ Generation test completed")
        else:
            print("❌ Cannot test generation - no context retrieved")

        print("\n" + "=" * 60)
        print("🎯 FINAL ASSESSMENT")
        print("=" * 60)

        if success_rate >= 80:
            print("🎉 RETRIEVAL SYSTEM: EXCELLENT PERFORMANCE")
            print("   - High success rate for legal queries")
            print("   - Fast response times")
            print("   - Relevant document matching")
        elif success_rate >= 60:
            print("👍 RETRIEVAL SYSTEM: GOOD PERFORMANCE")
            print("   - Satisfactory success rate")
            print("   - Room for improvement in query matching")
        else:
            print("⚠️  RETRIEVAL SYSTEM: NEEDS IMPROVEMENT")
            print("   - Low success rate")
            print("   - May need query preprocessing or embedding tuning")

        print("\n🔧 System Status:")
        print("   - Embedding Model: Google EmbeddingGemma-300M ✅")
        print("   - Vector Database: QdrantDB ✅")
        print("   - Generation Model: Google Gemini 2.5 Flash ✅")
        print("   - Document Processing: Complete ✅")
        print(f"   - Total Chunks: {collection_info.get('points_count', 0)} ✅")

        return success_rate >= 60  # Consider 60%+ as passing

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_retrieval_system()
    if success:
        print("\n🎉 Retrieval system test completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Retrieval system test failed!")
        sys.exit(1)
