# rag_system/hybrid_search.py
# txtai fast semantic search over documentation + source code
# LlamaIndex thi raw text kadi ne txtai ma index kare

import os
import txtai
from rag_system.document_loader import load_documentation, load_source_code

TXTAI_INDEX_PATH = "./storage/txtai_index"


class HybridSearch:
    """
    txtai-based fast semantic search over documentation + source code.

    - Uses LlamaIndex loaders to read files (docs, PDFs, code, etc.)
    - Indexes raw text chunks in txtai for fast retrieval
    - Provides direct answer retrieval (no LLM) for Mode 3
    """

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
            try:
                self.embeddings.load(TXTAI_INDEX_PATH)
                print("✅ txtai index loaded from disk")
            except Exception as e:
                print(f"⚠️ Load failed: {e}")
                if index_on_start:
                    self._build_full_index()
                    self._save_index()
        elif index_on_start:
            self._build_full_index()
            self._save_index()

    def _save_index(self):
        os.makedirs(TXTAI_INDEX_PATH, exist_ok=True)
        self.embeddings.save(TXTAI_INDEX_PATH)
        print("✅ txtai index saved to disk")

    def _build_full_index(self):
        """
        Documentation + Source code banne index kare
        EK SAATH full index banao (clean slate)
        """
        print("🔄 Building full txtai index (docs + source)...")

        all_docs = []

        # Load documentation
        doc_docs = load_documentation()
        for d in doc_docs:
            text = d.text.strip()
            if text:
                source = d.metadata.get("file_path", "documentation")
                combined = f"SOURCE: {source}\n\n{text}"
                all_docs.append(combined)

        # Load source code
        source_docs = load_source_code()
        for d in source_docs:
            text = d.text.strip()
            if text:
                source = d.metadata.get("file_path", "source_code")
                combined = f"SOURCE: {source}\n\n{text}"
                all_docs.append(combined)

        if not all_docs:
            print("⚠️ No documents found to index")
            return

        # Build fresh index
        self.embeddings.index([
            (str(i), text, None)
            for i, text in enumerate(all_docs)
        ])
        print(f"✅ Full index built: {len(all_docs)} total chunks")

    def search_docs(self, query, top_k=3):
        """
        Documentation ma fast semantic search
        Returns relevant context chunks
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

    def answer_query(self, query, top_k=3):
        """
        txtai through direct answer nikalvo
        Indexed content thi direct answer return kare
        No LLM call — pure txtai semantic retrieval

        Args:
            query: User's question
            top_k: Number of results to consider

        Returns:
            dict with 'answer' and 'sources'
        """
        if not self.embeddings:
            return {
                "answer": "txtai search unavailable",
                "sources": []
            }

        try:
            # Search relevant chunks
            results = self.embeddings.search(query, top_k)

            if not results:
                return {
                    "answer": "No relevant information found in documentation or source code.",
                    "sources": []
                }

            # Extract best matching chunks
            answers = []
            sources = []

            for r in results:
                text = r.get("text", "").strip()
                if not text:
                    continue

                # Extract source
                source_line = "unknown"
                for line in text.split("\n"):
                    if line.startswith("SOURCE:"):
                        source_line = line.replace("SOURCE:", "").strip()
                        # Remove the SOURCE line from text
                        text = text.replace(line, "").strip()
                        break

                if text:
                    answers.append(text[:600])
                    sources.append(source_line)

            if not answers:
                return {
                    "answer": "No clear answer found.",
                    "sources": []
                }

            # Combine top answers into a coherent response
            combined_answer = "\n\n".join(answers[:3])

            return {
                "answer": combined_answer,
                "sources": list(set(sources))
            }

        except Exception as e:
            return {
                "answer": f"txtai search error: {e}",
                "sources": []
            }