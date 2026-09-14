"""Follow-up Q&A endpoint (ARCHITECTURE.md §1): Chat Crew (QA Agent + Scope Guardrail)."""
from fastapi import APIRouter, HTTPException

from backend.agents.crew_chat import run_chat_crew
from backend.services import document_storage

router = APIRouter(prefix="/api/documents", tags=["chat"])


@router.post("/{doc_id}/chat")
def chat_with_document(doc_id: str, payload: dict):
    if document_storage.get_document(doc_id) is None:
        raise HTTPException(status_code=404, detail="Unknown doc_id")

    question = payload.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="'question' is required")
    history = payload.get("history", [])

    answer = run_chat_crew(doc_id, question, history)
    return answer.model_dump()
