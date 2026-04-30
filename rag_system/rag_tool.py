# rag_system/rag_tool.py
# Shared RAG Backend — BMAD + Wrapper banne use kare
# Singleton pattern — ek j instance

from rag_system.hybrid_search import HybridSearch
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb

CHROMA_PATH = "./storage/chroma_db"
EMBED_MODEL = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5",
    embed_batch_size=10
)


class RAGTool:
    """
    Ek j RAG backend — Singleton
    BMAD agent + Wrapper agent banne same instance use kare
    
    Adaptive retrieval — query ate ketlay complexity/goal according backend select kare:
      - search_source_code() — LlamaIndex + ChromaDB (source code, structural)
      - search_docs()        — txtai semantic search (docs, fast)
      - smart_search(query)  — adaptive router (auto txtai vs LlamaIndex)
      - answer_from_docs()   — txtai direct answer (Mode 3 — faster)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        print("🔧 Initializing RAG Tool...")

        # txtai — documentation fast search
        self.hybrid_search = HybridSearch(
            index_on_start=True
        )

        # LlamaIndex — source code search
        self.source_index = self._load_source_index()

        self._initialized = True
        print("✅ RAG Tool ready — shared backend")

    def _classify_query_intent(self, query: str) -> str:
        """
        Query nu nature inspect kari backend route kare:
        - 'fast_semantic' → txtai (segmentation, fast lookup, short factual)
        - 'deep_context'  → LlamaIndex (structural, multi-file, complex)
        """
        q = query.lower().strip()
        word_count = len(q.split())

        # Critical error keywords → immediate precise answer needed → txtai fast path
        critical_patterns = [
            "fatal error", "critical error", "white screen", "500 error",
            "parse error", "memory exhausted", "undefined", "not found",
            "class not found", "bootstrap error", "activation error",
        ]
        if any(pat in q for pat in critical_patterns):
            return "fast_semantic"

        # Short queries (1-3 words) → likely fast lookup
        if word_count <= 3:
            return "fast_semantic"

        # Gujarati/fast interrogatives
        fast_words = ["kyaa", "kevi", "kay", "su", "?"]
        if any(w in q for w in fast_words):
            return "fast_semantic"

        # Explicit fast/quick/segmentation keywords
        segmentation_keywords = [
            "segment", "chunk", "partition", "split",
            "fast", "quick", "immediate", "direct",
            "fix", "solution", "solve",
        ]
        if any(kw in q for kw in segmentation_keywords):
            return "fast_semantic"

        # Default: complex/structural reasoning → use both backends
        return "deep_context"

    def smart_search(self, query: str, intent: str = None) -> str:
        """
        Adaptive retrieval router — query nature according backend auto-select.
        
        Args:
            query: User query
            intent: Optional override from wrapper ("faster", "guidance", "troubleshooting")
                    If intent=="faster" → force txtai
        
        Returns:
            Combined context string (both backends if needed)
        """
        # Intent override (Mode 3 from wrapper)
        if intent == "faster":
            return self.search_docs(query)

        # Classify query automatically
        route = self._classify_query_intent(query)

        if route == "fast_semantic":
            # txtai fast path — single backend sufficient
            return self.search_docs(query)
        else:
            # deep_context — use both for completeness
            all_results = self.search_all(query)
            # Combine with clear separation
            combined = (
                f"SOURCE CODE CONTEXT:\n{all_results['source_code']}\n\n"
                f"DOCUMENTATION CONTEXT:\n{all_results['documentation']}"
            )
            return combined

    def _load_source_index(self):
        """
        ChromaDB thi source code index load kare
        """
        try:
            client = chromadb.PersistentClient(
                path=CHROMA_PATH
            )
            collection = client.get_or_create_collection(
                "source_code"
            )
            vector_store = ChromaVectorStore(
                chroma_collection=collection
            )
            index = VectorStoreIndex.from_vector_store(
                vector_store,
                embed_model=EMBED_MODEL
            )
            print("✅ RAG Tool: Source code index loaded")
            return index

        except Exception as e:
            print(f"⚠️ RAG Tool: Source index failed: {e}")
            return None

    def search_source_code(self, query: str) -> str:
        """
        LlamaIndex + ChromaDB — source code search
        File path + relevant code return kare
        BMAD agent + Wrapper agent banne call kari shake
        """
        if not self.source_index:
            return "Source code index not available"

        try:
            retriever = self.source_index.as_retriever(
                similarity_top_k=2
            )
            nodes = retriever.retrieve(query)

            contexts = []
            for node in nodes:
                file_path = node.metadata.get(
                    "file_path", "unknown"
                )
                text = node.text[:500]
                contexts.append(
                    f"FILE: {file_path}\n\n{text}"
                )

            if contexts:
                return "\n\n---\n\n".join(contexts)

            return "No relevant source code found"

        except Exception as e:
            return f"Source code search error: {e}"

    def search_docs(self, query: str) -> str:
        """
        txtai — fast semantic documentation search
        BMAD agent + Wrapper agent banne call kari shake
        """
        result = self.hybrid_search.search_docs(query)
        return result.get(
            "top_context", "No documentation found"
        )

    def search_all(self, query: str) -> dict:
        """
        Source code + Documentation — banne ek saath
        Complete context return kare
        """
        return {
            "source_code": self.search_source_code(query),
            "documentation": self.search_docs(query)
        }

    def answer_from_docs(self, query: str) -> dict:
        """
        Mode 3 — Faster response via txtai direct answer
        Returns answer + sources without LLM processing
        """
        return self.hybrid_search.answer_query(query)