# rag_tool_extended.py
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, ClassVar
import os
import pickle
import time
from pathlib import Path

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from sentence_transformers import CrossEncoder

# Cache directory for ML models
CACHE_DIR = Path("model_cache")
CACHE_DIR.mkdir(exist_ok=True)

# Cache file paths
EMBEDDINGS_CACHE = CACHE_DIR / "embeddings.pkl"
FAISS_CACHE = CACHE_DIR / "faiss_store.pkl"
CROSS_ENCODER_CACHE = CACHE_DIR / "cross_encoder.pkl"
BM25_CACHE = CACHE_DIR / "bm25_retriever.pkl"

# Global variables for loaded models (lazy loaded)
_embeddings_model = None
_faiss_store = None
_cross_encoder = None
_bm25_retriever = None
_all_chunks = None

def get_embeddings_model():
    """Lazy load embeddings model with caching"""
    global _embeddings_model

    if _embeddings_model is not None:
        return _embeddings_model

    # Try to load from cache first
    if EMBEDDINGS_CACHE.exists():
        try:
            print("Loading cached embeddings model...")
            with open(EMBEDDINGS_CACHE, 'rb') as f:
                _embeddings_model = pickle.load(f)
            print("Embeddings model loaded from cache!")
            return _embeddings_model
        except Exception as e:
            print(f"Failed to load cached embeddings: {e}")

    # Load from scratch if cache miss
    print("Loading embeddings model from HuggingFace...")
    start_time = time.time()
    _embeddings_model = HuggingFaceEmbeddings(
        model_name="Qwen/Qwen3-Embedding-0.6B"
    )
    load_time = time.time() - start_time
    print(".2f")

    # Cache for future use
    try:
        with open(EMBEDDINGS_CACHE, 'wb') as f:
            pickle.dump(_embeddings_model, f)
        print("Embeddings model cached!")
    except Exception as e:
        print(f"Failed to cache embeddings: {e}")

    return _embeddings_model

def get_faiss_store():
    """Lazy load FAISS store with caching"""
    global _faiss_store, _all_chunks

    if _faiss_store is not None:
        return _faiss_store

    embeddings = get_embeddings_model()

    # Try to load from cache first
    if FAISS_CACHE.exists():
        try:
            print("Loading cached FAISS store...")
            with open(FAISS_CACHE, 'rb') as f:
                _faiss_store = pickle.load(f)
            print("FAISS store loaded from cache!")
            # Still need to get all chunks for BM25
            if _all_chunks is None:
                dummy_query = "retrieve all documents"
                dummy_embedding = embeddings.embed_query(dummy_query)
                _all_chunks = _faiss_store.similarity_search_by_vector(dummy_embedding, k=len(_faiss_store.index_to_docstore_id))
            return _faiss_store
        except Exception as e:
            print(f"Failed to load cached FAISS: {e}")

    # Load from scratch if cache miss
    print("Loading FAISS index from disk...")
    start_time = time.time()
    _faiss_store = FAISS.load_local("qwen_faiss_index", embeddings, allow_dangerous_deserialization=True)

    # Get all chunks for BM25
    dummy_query = "retrieve all documents"
    dummy_embedding = embeddings.embed_query(dummy_query)
    _all_chunks = _faiss_store.similarity_search_by_vector(dummy_embedding, k=len(_faiss_store.index_to_docstore_id))

    load_time = time.time() - start_time
    print(".2f")
    print(f"Loaded {len(_all_chunks)} chunks from the FAISS index.")

    # Cache for future use
    try:
        with open(FAISS_CACHE, 'wb') as f:
            pickle.dump(_faiss_store, f)
        print("FAISS store cached!")
    except Exception as e:
        print(f"Failed to cache FAISS: {e}")

    return _faiss_store

def get_cross_encoder():
    """Lazy load cross-encoder with caching"""
    global _cross_encoder

    if _cross_encoder is not None:
        return _cross_encoder

    # Try to load from cache first
    if CROSS_ENCODER_CACHE.exists():
        try:
            print("Loading cached cross-encoder...")
            with open(CROSS_ENCODER_CACHE, 'rb') as f:
                _cross_encoder = pickle.load(f)
            print("Cross-encoder loaded from cache!")
            return _cross_encoder
        except Exception as e:
            print(f"Failed to load cached cross-encoder: {e}")

    # Load from scratch if cache miss
    print("Loading cross-encoder model...")
    start_time = time.time()
    _cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    load_time = time.time() - start_time
    print(".2f")

    # Cache for future use
    try:
        with open(CROSS_ENCODER_CACHE, 'wb') as f:
            pickle.dump(_cross_encoder, f)
        print("Cross-encoder cached!")
    except Exception as e:
        print(f"Failed to cache cross-encoder: {e}")

    return _cross_encoder

def get_bm25_retriever():
    """Lazy load BM25 retriever with caching"""
    global _bm25_retriever, _all_chunks

    if _bm25_retriever is not None:
        return _bm25_retriever

    # Ensure we have chunks loaded
    if _all_chunks is None:
        get_faiss_store()  # This will populate _all_chunks

    # Try to load from cache first
    if BM25_CACHE.exists():
        try:
            print("Loading cached BM25 retriever...")
            with open(BM25_CACHE, 'rb') as f:
                _bm25_retriever = pickle.load(f)
            print("BM25 retriever loaded from cache!")
            return _bm25_retriever
        except Exception as e:
            print(f"Failed to load cached BM25: {e}")

    # Load from scratch if cache miss
    print("Building BM25 retriever...")
    start_time = time.time()
    _bm25_retriever = BM25Retriever.from_documents(_all_chunks)
    load_time = time.time() - start_time
    print(".2f")

    # Cache for future use
    try:
        with open(BM25_CACHE, 'wb') as f:
            pickle.dump(_bm25_retriever, f)
        print("BM25 retriever cached!")
    except Exception as e:
        print(f"Failed to cache BM25: {e}")

    return _bm25_retriever

# -----------------------------
# Input schema
# -----------------------------
class RAGToolInput(BaseModel):
    query: str = Field(..., description="Farmer's natural language query")
    category: Optional[str] = Field(None, description="Optional category filter (e.g., 'โรคและศัตรูพืช')")

# -----------------------------
# RAG Tool
# -----------------------------
class RAGSearchTool(BaseTool):
    name: str = "sugarcane_rag_tool"
    description: str = (
        "Retrieves relevant information from sugarcane farming PDFs. "
        "Supports dense retrieval, hybrid retrieval, category filtering, and re-ranking."
    )
    args_schema: Type[BaseModel] = RAGToolInput

    # Lazy-loaded components (initialized on first use)
    _embeddings: ClassVar = None
    _vectorstore: ClassVar = None
    _cross_encoder: ClassVar = None
    _bm25: ClassVar = None
    _dense: ClassVar = None
    _hybrid_retriever: ClassVar = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            self._embeddings = get_embeddings_model()
        return self._embeddings

    @property
    def vectorstore(self):
        if self._vectorstore is None:
            self._vectorstore = get_faiss_store()
        return self._vectorstore

    @property
    def cross_encoder(self):
        if self._cross_encoder is None:
            self._cross_encoder = get_cross_encoder()
        return self._cross_encoder

    @property
    def bm25(self):
        if self._bm25 is None:
            self._bm25 = get_bm25_retriever()
        return self._bm25

    @property
    def dense(self):
        if self._dense is None:
            self._dense = self.vectorstore.as_retriever(search_kwargs={"k": 10})  # Reduced from 20
        return self._dense

    @property
    def hybrid_retriever(self):
        if self._hybrid_retriever is None:
            self._hybrid_retriever = EnsembleRetriever(
                retrievers=[self.bm25, self.dense], weights=[0.3, 0.7]  # Adjusted weights for speed
            )
        return self._hybrid_retriever

    def _run(self, query: str, category: Optional[str] = None) -> str:
        """Perform retrieval with hybrid search, optional category filter, and re-ranking."""

        # Step 1: Hybrid retrieval (dense + sparse) - triggers lazy loading if needed
        candidates = self.hybrid_retriever.get_relevant_documents(query)

        # Step 2: Apply category filter if provided
        if category:
            candidates = [doc for doc in candidates if doc.metadata.get("category") == category]

        # Step 3: Re-rank with cross-encoder (reduced from 5 to 3)
        if candidates:
            pairs = [(query, d.page_content) for d in candidates]
            scores = self.cross_encoder.predict(pairs)
            reranked = [doc for _, doc in sorted(zip(scores, candidates), reverse=True)]
            top_docs = reranked[:4]  # Reduced from 5 to 3
        else:
            top_docs = []

        # Step 4: Format results
        if not top_docs:
            return "No relevant documents found."
        results = "\n\n".join(
            [f"[{i+1}] {d.page_content[:400]}... (source: {d.metadata})" for i, d in enumerate(top_docs)]
        )
        return results

# -----------------------------
# Cache Management Utilities
# -----------------------------
def clear_model_cache():
    """Clear all cached models - useful for forcing reload or cleanup"""
    global _embeddings_model, _faiss_store, _cross_encoder, _bm25_retriever, _all_chunks

    # Clear in-memory cache
    _embeddings_model = None
    _faiss_store = None
    _cross_encoder = None
    _bm25_retriever = None
    _all_chunks = None

    # Clear disk cache
    cache_files = [EMBEDDINGS_CACHE, FAISS_CACHE, CROSS_ENCODER_CACHE, BM25_CACHE]
    for cache_file in cache_files:
        if cache_file.exists():
            try:
                cache_file.unlink()
                print(f"Cleared cache: {cache_file}")
            except Exception as e:
                print(f"Failed to clear cache {cache_file}: {e}")

    print("All model caches cleared!")

def get_cache_stats():
    """Get statistics about cached models"""
    stats = {
        "embeddings_cached": EMBEDDINGS_CACHE.exists(),
        "faiss_cached": FAISS_CACHE.exists(),
        "cross_encoder_cached": CROSS_ENCODER_CACHE.exists(),
        "bm25_cached": BM25_CACHE.exists(),
        "cache_dir_size_mb": 0
    }

    # Calculate cache directory size
    try:
        total_size = 0
        for cache_file in CACHE_DIR.glob("*"):
            if cache_file.is_file():
                total_size += cache_file.stat().st_size
        stats["cache_dir_size_mb"] = total_size / (1024 * 1024)
    except:
        pass

    return stats
