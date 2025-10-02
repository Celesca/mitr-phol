# rag_tool_extended.py
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, ClassVar

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from sentence_transformers import CrossEncoder


# Load the embeddings model
embeddings = HuggingFaceEmbeddings(
    model_name="Qwen/Qwen3-Embedding-0.6B"
)

# Load the FAISS index
db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

dummy_query = "retrieve all documents"
dummy_embedding = embeddings.embed_query(dummy_query)
all_chunks = db.similarity_search_by_vector(dummy_embedding, k=len(db.index_to_docstore_id))

print(f"Loaded {len(all_chunks)} chunks from the FAISS index.")

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

    # ✅ Mark as ClassVar so Pydantic ignores them
    embeddings: ClassVar = HuggingFaceEmbeddings(
        model_name="Qwen/Qwen3-Embedding-0.6B"
    )
    vectorstore: ClassVar = FAISS.load_local(
        "faiss_index", embeddings, allow_dangerous_deserialization=True
    )
    cross_encoder: ClassVar = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    # NOTE: You must build BM25 index during preprocessing and load docs here
    bm25: ClassVar = BM25Retriever.from_documents(all_chunks)  # placeholder
    dense: ClassVar = vectorstore.as_retriever(search_kwargs={"k": 20})
    hybrid_retriever: ClassVar = EnsembleRetriever(
        retrievers=[bm25, dense], weights=[0.3, 0.7]
    )

    def _run(self, query: str, category: Optional[str] = None) -> str:
        """Perform retrieval with hybrid search, optional category filter, and re-ranking."""

        # Step 1: Hybrid retrieval (dense + sparse)
        candidates = self.hybrid_retriever.get_relevant_documents(query)

        # Step 2: Apply category filter if provided
        if category:
            candidates = [doc for doc in candidates if doc.metadata.get("category") == category]

        # Step 3: Re-rank with cross-encoder
        if candidates:
            pairs = [(query, d.page_content) for d in candidates]
            scores = self.cross_encoder.predict(pairs)
            reranked = [doc for _, doc in sorted(zip(scores, candidates), reverse=True)]
            top_docs = reranked[:5]
        else:
            top_docs = []

        # Step 4: Format results
        if not top_docs:
            return "No relevant documents found."
        results = "\n\n".join(
            [f"[{i+1}] {d.page_content[:400]}... (source: {d.metadata})" for i, d in enumerate(top_docs)]
        )
        return results
