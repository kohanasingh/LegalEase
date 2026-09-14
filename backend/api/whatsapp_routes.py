"""
WhatsApp webhook (ARCHITECTURE.md §5) — a second entry point into the same
backend, not a parallel product. Reuses document_routes.process_document
and the same crews as the web flow (CLAUDE.md non-negotiable #5); the only
new code here is Twilio-specific: media download, TwiML replies, session
mapping, and the WhatsApp text formatter.

Flow: webhook -> immediate TwiML ack (Twilio needs a fast response) ->
background processing (same job queue as web) -> push result via Twilio's
REST API as a new outbound message.
"""
import uuid

from fastapi import APIRouter, BackgroundTasks, Form
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse

from backend.agents.crew_chat import run_chat_crew
from backend.api.document_routes import process_document
from backend.services import analysis_storage, document_storage, job_queue, whatsapp_service, whatsapp_session
from backend.utils.whatsapp_formatter import format_analysis, format_chat_answer

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])

DISCLAIMER = "⚖️ LegalEase is informational only, not a substitute for professional legal advice."

WELCOME_MESSAGE = (
    f"👋 Welcome to LegalEase! Send a PDF document (rental agreement, contract, notice) "
    f"and I'll explain it in plain language.\n\n{DISCLAIMER}"
)


def _process_whatsapp_document(whatsapp_number: str, doc_id: str, file_bytes: bytes) -> None:
    process_document(doc_id, file_bytes)  # exact same pipeline as the web upload endpoint
    status = job_queue.get_status(doc_id)
    if status and status.get("status") == "complete":
        analysis = analysis_storage.get_analysis(doc_id)
        whatsapp_service.send_whatsapp_message(whatsapp_number, format_analysis(analysis))
    else:
        error = status.get("error") if status else "Something went wrong."
        whatsapp_service.send_whatsapp_message(
            whatsapp_number, f"Sorry, I couldn't process that document: {error}"
        )


def _process_whatsapp_chat(whatsapp_number: str, doc_id: str, question: str) -> None:
    history = whatsapp_session.get_history(whatsapp_number)
    answer = run_chat_crew(doc_id, question, history)  # exact same Chat Crew as the web endpoint
    whatsapp_session.append_history(whatsapp_number, "user", question)
    whatsapp_session.append_history(whatsapp_number, "assistant", answer.answer)
    whatsapp_service.send_whatsapp_message(whatsapp_number, format_chat_answer(answer.model_dump()))


@router.post("/webhook")
def whatsapp_webhook(
    background_tasks: BackgroundTasks,
    From: str = Form(...),
    Body: str = Form(""),
    NumMedia: str = Form("0"),
    MediaUrl0: str | None = Form(None),
    MediaContentType0: str | None = Form(None),
):
    twiml = MessagingResponse()
    num_media = int(NumMedia or "0")

    if num_media > 0:
        if MediaContentType0 != "application/pdf":
            twiml.message(
                "I can only read PDF documents right now — please resend it as a PDF file, "
                "not a photo."
            )
            return Response(content=str(twiml), media_type="application/xml")

        file_bytes = whatsapp_service.download_media(MediaUrl0)
        doc_id = str(uuid.uuid4())
        document_storage.create_document(doc_id, f"whatsapp:{From}")
        whatsapp_session.set_active_doc(From, doc_id)
        job_queue.set_status(doc_id, "uploaded")
        background_tasks.add_task(_process_whatsapp_document, From, doc_id, file_bytes)
        twiml.message(
            f"{DISCLAIMER}\n\nGot your document! Analyzing now — this usually takes a couple "
            f"of minutes, I'll message you here with the results."
        )
    else:
        doc_id = whatsapp_session.get_active_doc(From)
        if not doc_id:
            twiml.message(WELCOME_MESSAGE)
        elif not Body.strip():
            twiml.message("Send me a question about your document, or a new PDF to start over.")
        else:
            background_tasks.add_task(_process_whatsapp_chat, From, doc_id, Body.strip())
            twiml.message("On it — give me a moment to check your document and the law.")

    return Response(content=str(twiml), media_type="application/xml")
