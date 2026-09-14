"""
Stage 6 checkpoint (partial — routing logic only): verifies the webhook
dispatches correctly (welcome message, PDF-only enforcement, document vs.
chat branching, session mapping) without needing real Twilio credentials
or a live crew run. The actual "upload/chat over a real WhatsApp Sandbox"
checkpoint from BUILD_INSTRUCTIONS.md needs a human with a phone and is
covered manually, not here (see CHANGES.md).
"""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.services import whatsapp_session

FROM_NUMBER = "whatsapp:+15550001111"


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def isolate_session():
    yield
    whatsapp_session._active_doc.pop(FROM_NUMBER, None)  # noqa: SLF001
    whatsapp_session._history.pop(FROM_NUMBER, None)  # noqa: SLF001


def test_welcome_message_for_first_time_number_with_no_active_doc(client):
    response = client.post(
        "/api/whatsapp/webhook",
        data={"From": FROM_NUMBER, "Body": "hi", "NumMedia": "0"},
    )
    assert response.status_code == 200
    assert "Welcome to LegalEase" in response.text
    assert "informational only" in response.text


def test_non_pdf_media_is_rejected_without_processing(client):
    with patch("backend.api.whatsapp_routes.whatsapp_service.download_media") as mock_download:
        response = client.post(
            "/api/whatsapp/webhook",
            data={
                "From": FROM_NUMBER,
                "Body": "",
                "NumMedia": "1",
                "MediaUrl0": "https://api.twilio.com/fake.jpg",
                "MediaContentType0": "image/jpeg",
            },
        )
    assert response.status_code == 200
    assert "PDF" in response.text
    mock_download.assert_not_called()


def test_pdf_upload_kicks_off_processing_and_sets_session(client):
    with (
        patch("backend.api.whatsapp_routes.whatsapp_service.download_media", return_value=b"%PDF-fake"),
        patch("backend.api.whatsapp_routes._process_whatsapp_document") as mock_process,
    ):
        response = client.post(
            "/api/whatsapp/webhook",
            data={
                "From": FROM_NUMBER,
                "Body": "",
                "NumMedia": "1",
                "MediaUrl0": "https://api.twilio.com/fake.pdf",
                "MediaContentType0": "application/pdf",
            },
        )
    assert response.status_code == 200
    assert "informational only" in response.text  # disclaimer on first reply for a new doc
    assert "Analyzing now" in response.text
    mock_process.assert_called_once()
    assert whatsapp_session.get_active_doc(FROM_NUMBER) is not None


def test_text_with_active_doc_triggers_chat_processing(client):
    whatsapp_session.set_active_doc(FROM_NUMBER, "existing-doc-id")
    with patch("backend.api.whatsapp_routes._process_whatsapp_chat") as mock_chat:
        response = client.post(
            "/api/whatsapp/webhook",
            data={"From": FROM_NUMBER, "Body": "Can my landlord keep my deposit?", "NumMedia": "0"},
        )
    assert response.status_code == 200
    mock_chat.assert_called_once_with(FROM_NUMBER, "existing-doc-id", "Can my landlord keep my deposit?")


def test_format_analysis_and_chat_answer_helpers():
    from backend.utils.whatsapp_formatter import format_analysis, format_chat_answer

    analysis_text = format_analysis(
        {
            "summary": "This is a summary.",
            "flagged_clauses": [
                {"clause_type": "termination", "risk_level": "risky", "reasoning": "Bad clause."}
            ],
            "consult_professional_notes": ["Check local law."],
            "out_of_scope_notes": [],
            "disclaimer": "Not legal advice.",
        }
    )
    assert "This is a summary." in analysis_text
    assert "🔴" in analysis_text
    assert "Check local law." in analysis_text

    chat_text = format_chat_answer(
        {
            "answer": "Yes, that's fine.",
            "disclaimer": "Not legal advice.",
            "consult_professional_notes": [],
            "out_of_scope_notes": [],
        }
    )
    assert "Yes, that's fine." in chat_text
    assert "Not legal advice." in chat_text
