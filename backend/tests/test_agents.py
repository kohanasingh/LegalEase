"""
Stage 4 checkpoint (BUILD_INSTRUCTIONS.md): run the full Analysis Crew and
Chat Crew end-to-end and confirm grounded, scoped, guardrail-annotated
output. These make real Gemini API calls (a handful of requests each,
well within gemini-3.1-flash-lite's free tier — see CHANGES.md) so they're
slower than the rest of the suite.
"""
import pytest

from backend.agents.crew_analysis import run_analysis_crew
from backend.agents.crew_chat import run_chat_crew
from backend.retrieval.chroma_client import get_user_documents_collection
from backend.retrieval.embeddings import embed_texts

SAMPLE_RENTAL_AGREEMENT = """
RENTAL AGREEMENT

This agreement is made between the Landlord and the Tenant.

1. Rent. The Tenant shall pay a monthly rent of Rs. 15,000 on or before the 5th of each month.

2. Security Deposit. The Tenant shall pay a refundable security deposit of Rs. 30,000. The
Landlord may deduct any amount from the deposit at his sole discretion without providing an
itemized account.

3. Termination. Either party may terminate this agreement with 30 days written notice. The
Tenant forfeits the entire security deposit if they terminate before completing 11 months of
tenancy.
"""


def test_analysis_crew_flags_risky_clauses_and_attaches_disclaimer():
    result = run_analysis_crew(SAMPLE_RENTAL_AGREEMENT)

    assert result.summary
    assert result.disclaimer

    flagged_by_type = {c.clause_type: c.risk_level for c in result.flagged_clauses}
    assert flagged_by_type.get("payment") in ("risky", "ambiguous")  # sole-discretion deduction
    assert flagged_by_type.get("termination") in ("risky", "ambiguous")  # full forfeiture penalty


@pytest.fixture
def seeded_user_document():
    doc_id = "test-chat-doc"
    chunks = [
        "1. Rent. The Tenant shall pay a monthly rent of Rs. 15,000 on or before the 5th of each month.",
        "3. Termination. Either party may terminate this agreement with 30 days written notice. "
        "The Tenant forfeits the entire security deposit if they terminate before completing 11 "
        "months of tenancy.",
    ]
    collection = get_user_documents_collection()
    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source_type": "user_doc", "doc_id": doc_id, "chunk_index": i} for i in range(len(chunks))]
    collection.add(ids=ids, documents=chunks, embeddings=embed_texts(chunks), metadatas=metadatas)
    yield doc_id
    collection.delete(ids=ids)


def test_chat_crew_answers_grounded_in_document_with_disclaimer(seeded_user_document):
    answer = run_chat_crew(
        seeded_user_document, "Can my landlord keep my whole security deposit if I leave early?"
    )
    assert "forfeit" in answer.answer.lower() or "11 month" in answer.answer.lower()
    assert answer.disclaimer
