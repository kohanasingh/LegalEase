"""
CrewAI tool wrapping HybridRetriever (ARCHITECTURE.md §4). Shared by the
Legal Retriever Agent (legal_corpus only) and the QA Agent (legal_corpus +
the current user_documents, tagged by source) — agents never see the
dense+BM25+RRF fusion happening underneath.
"""
from crewai.tools import tool

from backend.retrieval.hybrid_retriever import HybridRetriever

_retriever = HybridRetriever()

LEGAL_SOURCE_TYPES = ["act", "regulation", "case_law"]


@tool("ChromaRetrieverTool")
def chroma_retriever_tool(query: str, scope: str, doc_id: str = "", top_k: int = 5) -> str:
    """
    Retrieves relevant text chunks for a query, grounding an answer instead
    of relying on general knowledge.

    Args:
        query: what to search for.
        scope: "legal_corpus" to search Indian statutory law, or
            "user_document" to search the currently uploaded document.
        doc_id: required when scope="user_document" — the document's id.
        top_k: how many chunks to return.
    """
    if scope == "user_document":
        if not doc_id:
            return "Error: doc_id is required when scope='user_document'."
        results = _retriever.retrieve(
            query, collection_name="user_documents", filters={"doc_id": doc_id}, top_k=top_k
        )
        label = "your document"
    else:
        results = _retriever.retrieve(
            query,
            collection_name="legal_corpus",
            filters={"source_type": {"$in": LEGAL_SOURCE_TYPES}},
            top_k=top_k,
        )
        label = "Indian law"

    if not results:
        return f"No relevant content found in {label}."

    lines = []
    for r in results:
        locator = r["metadata"].get("section") or f"chunk {r['metadata'].get('chunk_index')}"
        lines.append(f"[{label} — {locator}] {r['document']}")
    return "\n\n".join(lines)
