# rag_system/index_docs.py

import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from rag_system.document_loader import load_source_code, load_documentation
import chromadb

load_dotenv()

# Smaller + faster model
EMBED_MODEL = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-en-v1.5",
    embed_batch_size=10  # batch size ghatu rakho
)

CHROMA_PATH = "./storage/chroma_db"
BATCH_SIZE = 50  # 50 files at a time


def get_chroma_collection(name):
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(name)


def index_in_batches(docs, collection_name):
    """
    Documents ne batch ma index kare
    Memory overflow nahi thay
    """
    if not docs:
        print("⚠️ No documents found")
        return None

    collection = get_chroma_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store
    )

    # Splitter — large files ne chhota chunks ma tode
    splitter = SentenceSplitter(
        chunk_size=512,
        chunk_overlap=50
    )

    total = len(docs)
    print(f"📦 Total documents: {total}")
    print(f"📦 Batch size: {BATCH_SIZE}")

    # Pehli batch thi index banavo
    first_batch = docs[:BATCH_SIZE]
    index = VectorStoreIndex.from_documents(
        first_batch,
        storage_context=storage_context,
        embed_model=EMBED_MODEL,
        transformations=[splitter],
        show_progress=True
    )

    # Baki batches insert karo
    for i in range(BATCH_SIZE, total, BATCH_SIZE):
        batch = docs[i:i + BATCH_SIZE]
        print(f"🔄 Indexing batch {i//BATCH_SIZE + 1}... ({i}/{total})")

        for doc in batch:
            index.insert(doc)

    index.storage_context.persist()
    print(f"✅ Indexed: {total} documents")
    return index


def index_source_code():
    print("\n🔄 Indexing source code...")
    docs = load_source_code()
    return index_in_batches(docs, "source_code")


def index_documentation():
    print("\n🔄 Indexing documentation...")
    docs = load_documentation()
    return index_in_batches(docs, "documentation")


if __name__ == "__main__":
    import shutil

    print("🚀 Starting indexing...")

    # 1. Source code → ChromaDB (BMAD mate)
    print("\n📦 Step 1: Source code → ChromaDB (BMAD)")
    index_source_code()

    # 2. Documentation → ChromaDB (backup)
    print("\n📦 Step 2: Documentation → ChromaDB")
    index_documentation()

    # 3. Documentation → txtai (RAG fast search)
    print("\n📦 Step 3: Documentation → txtai (RAG)")
    from rag_system.hybrid_search import HybridSearch

    if os.path.exists("./storage/txtai_index"):
        shutil.rmtree("./storage/txtai_index")

    search = HybridSearch(index_on_start=True)

    print("\n✅ All indexing complete!")
    print("   Source code → ChromaDB (BMAD) ✅")
    print("   Documentation → txtai (RAG) ✅")