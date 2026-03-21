# rag_system/hybrid_search.py
# Documentation ONLY — txtai fast semantic search
# LlamaIndex thi raw text kadi ne txtai ma index kare

import os
import txtai
from rag_system.document_loader import load_documentation

TXTAI_INDEX_PATH = "./storage/txtai_index"


class HybridSearch:

    def __init__(self, index_on_start=False):

        try:
            self.embeddings = txtai.Embeddings({
                "path": "sentence-transformers/all-MiniLM-L6-v2",
                "content": True
            })
            print("✅ txtai initialized")

        except Exception as e:
            print(f"⚠️ txtai init failed: {e}")
            self.embeddings = None
            return

        # Saved index che to load karo
        if os.path.exists(TXTAI_INDEX_PATH):
            print("📂 Loading saved txtai index...")
            self.embeddings.load(TXTAI_INDEX_PATH)
            print("✅ txtai index loaded from disk")

        elif index_on_start:
            self._build_doc_index()
            self._save_index()

    def _save_index(self):
        os.makedirs(TXTAI_INDEX_PATH, exist_ok=True)
        self.embeddings.save(TXTAI_INDEX_PATH)
        print("✅ txtai index saved to disk")

    def _build_doc_index(self):
        """
        Sirf DOCUMENTATION index kare
        LlamaIndex thi raw text kade — txtai ma store kare
        """
        print("🔄 Building documentation txtai index...")

        all_texts = []

        # LlamaIndex thi documentation load
        doc_docs = load_documentation()

        for d in doc_docs:
            text = d.text.strip()
            if text:
                # Document source sathe store karo
                source = d.metadata.get(
                    "file_path", "documentation"
                )
                combined = f"SOURCE: {source}\n\n{text}"
                all_texts.append(combined)

        if not all_texts:
            print("⚠️ No documentation found")
            return

        self.embeddings.index([
            (str(i), text, None)
            for i, text in enumerate(all_texts)
        ])
        print(f"✅ Documentation indexed: {len(all_texts)} chunks")

    def search_docs(self, query, top_k=3):
        """
        Documentation ma fast semantic search
        """
        if not self.embeddings:
            return {"top_context": "Search unavailable"}

        try:
            results = self.embeddings.search(query, top_k)
            contexts = []

            for r in results:
                text = r.get("text", "")
                if text:
                    contexts.append(text[:600])

            if contexts:
                combined = "\n\n---\n\n".join(contexts)
                return {"top_context": combined}

            return {"top_context": "No documentation found"}

        except Exception as e:
            return {"top_context": f"Search error: {e}"}