"""
Stage 3 checkpoint (BUILD_INSTRUCTIONS.md): upload a PDF via the API and
confirm it's parsed, chunked, and embedded into `user_documents` correctly.
"""
import io
import time

import pymupdf
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.retrieval.chroma_client import get_user_documents_collection

CONTRACT_TEXT_PARAGRAPHS = [
    "RENTAL AGREEMENT\n\nThis agreement is made between the Landlord and the Tenant.",
    "1. Rent. The Tenant shall pay a monthly rent of Rs. 15,000 on or before the 5th of each month.",
    "2. Security Deposit. The Tenant shall pay a refundable security deposit of Rs. 30,000.",
    "3. Termination. Either party may terminate this agreement with 30 days written notice.",
]


def make_test_pdf_bytes() -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    y = 72
    for paragraph in CONTRACT_TEXT_PARAGRAPHS:
        page.insert_text((72, y), paragraph, fontsize=11)
        y += 60
    buffer = io.BytesIO()
    doc.save(buffer)
    doc.close()
    return buffer.getvalue()


@pytest.fixture
def client():
    return TestClient(app)


def test_upload_parses_chunks_and_embeds_into_user_documents(client):
    pdf_bytes = make_test_pdf_bytes()

    response = client.post(
        "/api/documents/upload",
        files={"file": ("rental_agreement.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 200
    doc_id = response.json()["doc_id"]

    status = None
    for _ in range(30):
        status = client.get(f"/api/documents/{doc_id}/status").json()
        if status["status"] in ("complete", "failed"):
            break
        time.sleep(0.5)

    assert status["status"] == "complete", status
    assert status["chunk_count"] >= 1

    collection = get_user_documents_collection()
    stored = collection.get(where={"doc_id": doc_id}, include=["documents", "metadatas"])
    assert len(stored["ids"]) == status["chunk_count"]
    assert all(m["source_type"] == "user_doc" for m in stored["metadatas"])
    assert any("Termination" in doc for doc in stored["documents"])

    collection.delete(ids=stored["ids"])


def test_upload_rejects_non_pdf(client):
    response = client.post(
        "/api/documents/upload",
        files={"file": ("notes.txt", b"just some text", "text/plain")},
    )
    assert response.status_code == 400


def test_unknown_doc_id_status_is_404(client):
    response = client.get("/api/documents/nonexistent-id/status")
    assert response.status_code == 404
