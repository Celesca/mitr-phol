#!/usr/bin/env python3
"""
Test script to verify model caching performance improvements
"""
import time
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from rag_tool import RAGSearchTool, clear_model_cache, get_cache_stats

def test_caching_performance():
    """Test that caching significantly speeds up subsequent loads"""

    print("=== Model Caching Performance Test ===\n")

    # Clear any existing cache
    print("1. Clearing existing cache...")
    clear_model_cache()

    # First load (should be slow)
    print("\n2. First load (building cache)...")
    start_time = time.time()

    tool = RAGSearchTool()
    # Trigger loading by accessing a property
    _ = tool.embeddings
    _ = tool.vectorstore
    _ = tool.cross_encoder
    _ = tool.bm25

    first_load_time = time.time() - start_time
    print(".2f")

    # Check cache stats
    stats = get_cache_stats()
    print(f"Cache stats after first load: {stats}")

    # Second load (should be fast due to caching)
    print("\n3. Second load (using cache)...")
    start_time = time.time()

    # Clear in-memory cache but keep disk cache
    tool._embeddings = None
    tool._vectorstore = None
    tool._cross_encoder = None
    tool._bm25 = None

    # Trigger reloading (should use disk cache)
    _ = tool.embeddings
    _ = tool.vectorstore
    _ = tool.cross_encoder
    _ = tool.bm25

    second_load_time = time.time() - start_time
    print(".2f")

    # Calculate speedup
    if second_load_time > 0:
        speedup = first_load_time / second_load_time
        print(".1f")

        if speedup > 2:
            print("✅ Caching is working! Significant performance improvement detected.")
        else:
            print("⚠️  Caching may not be working optimally. Speedup should be > 2x.")
    else:
        print("❌ Second load was instantaneous - possible timing issue.")

    # Test actual RAG functionality
    print("\n4. Testing RAG functionality...")
    try:
        result = tool._run("อ้อยเป็นอย่างไรบ้าง")
        print(f"RAG test successful! Result length: {len(result)} characters")
        print(f"First 100 chars: {result[:100]}...")
    except Exception as e:
        print(f"❌ RAG test failed: {e}")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_caching_performance()