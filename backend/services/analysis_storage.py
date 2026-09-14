"""In-memory store for completed Analysis Crew results, keyed by doc_id."""
import threading
from typing import Any

_lock = threading.Lock()
_analyses: dict[str, dict[str, Any]] = {}


def set_analysis(doc_id: str, analysis: dict[str, Any]) -> None:
    with _lock:
        _analyses[doc_id] = analysis


def get_analysis(doc_id: str) -> dict[str, Any] | None:
    with _lock:
        return _analyses.get(doc_id)
