"""
Final Test of EmbeddingGemma-300M RAG System
"""

from qdrant_vector_store import QdrantVectorStore

def test_system():
    vs = QdrantVectorStore()

    queries = [
        'What are tenant rights under rent control acts?',
        'Explain consumer protection provisions',
        'What does the banking regulation act say?'
    ]

    print("🧪 Final System Test with EmbeddingGemma-300M")
    print("=" * 60)

    for query in queries:
        results = vs.search_similar_chunks(query, limit=3, score_threshold=0.0)
        print(f'Query: {query[:40]}...')
        print(f'Results: {len(results)} found')
        if results:
            print(f'Best match: {results[0]["document_filename"]} (score: {results[0]["score"]:.3f})')
        print()

    # Test collection info
    info = vs.get_collection_info()
    print("📊 Final Collection Status:")
    print(f"  - Total chunks: {info.get('points_count', 0)}")
    print(f"  - Status: {info.get('status', 'unknown')}")
    print("  - Embedding model: Google EmbeddingGemma-300M (768 dimensions)")

if __name__ == "__main__":
    test_system()
