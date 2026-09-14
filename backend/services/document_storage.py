"""
In-memory metadata store for uploaded documents (filename, upload time,
chunk count). Separate from job_queue.py's processing-status tracking —
this is durable-for-the-session document identity; status is transient
pipeline progress. Both are equally ephemeral across restarts, consistent
with user_documents being disposable (see CLAUDE.md).
"""
import threading
from datetime import datetime, timezone
from typing import Any

_lock = threading.Lock()
_documents: dict[str, dict[str, Any]] = {}


def create_document(doc_id: str, filename: str) -> None:
    with _lock:
        _documents[doc_id] = {
            "doc_id": doc_id,
            "filename": filename,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
            "chunk_count": None,
        }


def set_chunk_count(doc_id: str, chunk_count: int) -> None:
    with _lock:
        if doc_id in _documents:
            _documents[doc_id]["chunk_count"] = chunk_count


def get_document(doc_id: str) -> dict[str, Any] | None:
    with _lock:
        doc = _documents.get(doc_id)
        return dict(doc) if doc is not None else None
