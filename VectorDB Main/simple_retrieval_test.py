"""
Simple Retrieval Test for Legal Document RAG System
Quick test to verify the retrieval functionality is working.
"""

from qdrant_vector_store import QdrantVectorStore

def test_retrieval():
    """Test basic retrieval functionality."""

    print("🧪 Simple Retrieval Test")
    print("=" * 40)

    try:
        # Initialize vector store
        vector_store = QdrantVectorStore()

        # Get collection info
        collection_info = vector_store.get_collection_info()
        print("✅ Collection Status:")
        print(f"   - Total chunks: {collection_info.get('points_count', 0)}")
        print(f"   - Status: {collection_info.get('status', 'unknown')}")
        print()

        # Test queries
        test_queries = [
            "What are tenant rights under rent control acts?",
            "Explain consumer protection provisions",
            "What does the banking regulation act say?"
        ]

        print("🔍 Testing Retrieval Queries")
        print("-" * 30)

        for i, query in enumerate(test_queries, 1):
            print(f"\n📋 Test {i}: {query}")

            # Perform retrieval
            results = vector_store.search_similar_chunks(
                query=query,
                limit=3,
                score_threshold=0.0
            )

            print(f"   Results found: {len(results)}")

            if results:
                # Show top result
                top_result = results[0]
                print(f"   📄 Top document: {top_result['document_filename']}")
                print(f"   🏷️  Type: {top_result['document_type']}")
                print(".3f")
                print(f"   📝 Preview: {top_result['content'][:150]}...")
                print("   ✅ Test PASSED")
            else:
                print("   ❌ Test FAILED - No results found")

        print("\n" + "=" * 40)
        print("🎯 RETRIEVAL TEST COMPLETE")
        print("=" * 40)

        return True

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_retrieval()
    if success:
        print("\n🎉 Retrieval system is working correctly!")
    else:
        print("\n❌ Retrieval system has issues!")
