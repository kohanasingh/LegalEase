"""
Stage 2 checkpoint (BUILD_INSTRUCTIONS.md): known queries against the real
baked legal_corpus should return sensible, correctly-scoped results.
Requires corpus/chroma_data/ to already be built (Stage 1).
"""
import pytest

from backend.retrieval.hybrid_retriever import HybridRetriever

pytestmark = pytest.mark.filterwarnings("ignore")


@pytest.fixture(scope="module")
def retriever():
    return HybridRetriever()


def test_exact_section_reference_ranks_first(retriever):
    results = retriever.retrieve("Section 73", collection_name="legal_corpus", top_k=3)
    assert results
    assert results[0]["metadata"]["section"] == "Section 73"


def test_conceptual_query_returns_relevant_section(retriever):
    results = retriever.retrieve(
        "termination of an agency contract", collection_name="legal_corpus", top_k=5
    )
    sections = {r["metadata"]["section"] for r in results}
    assert "Section 201" in sections  # "Termination of agency"


def test_results_are_scoped_to_source_type_filter(retriever):
    results = retriever.retrieve(
        "consideration for a promise",
        collection_name="legal_corpus",
        filters={"source_type": "act"},
        top_k=5,
    )
    assert results
    assert all(r["metadata"]["source_type"] == "act" for r in results)


def test_unknown_collection_raises(retriever):
    with pytest.raises(ValueError):
        retriever.retrieve("anything", collection_name="not_a_real_collection")
