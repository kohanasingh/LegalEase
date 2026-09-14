"""
Upload endpoint + status polling, per ARCHITECTURE.md §1 data flow:
POST /upload -> doc_id (async processing) -> frontend polls /status ->
GET /analysis once complete.

Pipeline: parse -> chunk -> embed -> store into `user_documents` -> run
the Analysis Crew on the full parsed text -> store its (guardrail-reviewed)
output for GET /analysis.
"""
import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile

from backend.agents.crew_analysis import run_analysis_crew
from backend.retrieval.chroma_client import get_user_documents_collection
from backend.retrieval.embeddings import embed_texts
from backend.services import analysis_storage, document_storage, job_queue
from backend.utils.chunking import chunk_document
from backend.utils.document_extraction import extract_text
from backend.utils.validators import UploadValidationError, validate_upload

router = APIRouter(prefix="/api/documents", tags=["documents"])


def process_document(doc_id: str, file_bytes: bytes, content_type: str) -> None:
    try:
        job_queue.set_status(doc_id, "parsing")
        text = extract_text(content_type, file_bytes)

        job_queue.set_status(doc_id, "chunking")
        chunks = chunk_document(text)
        if not chunks:
            raise ValueError("No extractable text found in this document (it may be a scanned image).")

        job_queue.set_status(doc_id, "embedding")
        embeddings = embed_texts(chunks)

        collection = get_user_documents_collection()
        ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {"source_type": "user_doc", "doc_id": doc_id, "chunk_index": i}
            for i in range(len(chunks))
        ]
        collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)
        document_storage.set_chunk_count(doc_id, len(chunks))

        job_queue.set_status(doc_id, "analyzing")
        analysis = run_analysis_crew(text)
        analysis_storage.set_analysis(doc_id, analysis.model_dump())

        job_queue.set_status(doc_id, "complete", {"chunk_count": len(chunks)})
    except Exception as exc:
        job_queue.set_status(doc_id, "failed", {"error": str(exc)})


@router.post("/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile):
    file_bytes = await file.read()
    try:
        validate_upload(file.filename, file.content_type, len(file_bytes))
    except UploadValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    doc_id = str(uuid.uuid4())
    document_storage.create_document(doc_id, file.filename)
    job_queue.set_status(doc_id, "uploaded")
    background_tasks.add_task(process_document, doc_id, file_bytes, file.content_type)
    return {"doc_id": doc_id}


@router.get("/{doc_id}/status")
async def get_document_status(doc_id: str):
    status = job_queue.get_status(doc_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Unknown doc_id")
    return status


@router.get("/{doc_id}/analysis")
async def get_document_analysis(doc_id: str):
    analysis = analysis_storage.get_analysis(doc_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="Analysis not available for this doc_id")
    return analysis
