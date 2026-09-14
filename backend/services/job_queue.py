"""
In-memory async processing status tracker (per BUILD_INSTRUCTIONS.md,
"in-memory or simple queue" is sufficient at this project's scale). Backs
GET /api/documents/{doc_id}/status polling. Lost on process restart, which
is fine — user_documents itself is equally ephemeral (see CLAUDE.md).
"""
import threading
from typing import Any

_lock = threading.Lock()
_jobs: dict[str, dict[str, Any]] = {}


def set_status(doc_id: str, status: str, detail: dict | None = None) -> None:
    with _lock:
        _jobs[doc_id] = {"status": status, **(detail or {})}


def get_status(doc_id: str) -> dict[str, Any] | None:
    with _lock:
        job = _jobs.get(doc_id)
        return dict(job) if job is not None else None
