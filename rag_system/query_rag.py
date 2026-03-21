# rag_system/query_rag.py
# Documentation search — txtai use kare

from rag_system.hybrid_search import HybridSearch

_search_instance = None


def get_search():
    global _search_instance
    if _search_instance is None:
        _search_instance = HybridSearch(index_on_start=True)
    return _search_instance


def query_docs(question: str) -> str:
    """
    Documentation search — txtai thi fast
    woo_project.docx + any future docs
    """
    search = get_search()
    result = search.search_docs(question)
    return result.get("top_context", "No documentation found")