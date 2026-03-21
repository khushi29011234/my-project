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
    
    search_source_code() — LlamaIndex + ChromaDB
    search_docs()        — txtai semantic search
    search_all()         — banne ek saath
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
                similarity_top_k=5
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