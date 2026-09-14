"""
WhatsApp session mapping (ARCHITECTURE.md §5): one active document per
phone number at a time; a new upload replaces the mapping. In-memory,
same ephemeral-by-design lifecycle as the other services.

Also holds conversation history per number, since (unlike the web
frontend) WhatsApp has no client-side state to resend each turn.
"""
import threading
from typing import Any

_lock = threading.Lock()
_active_doc: dict[str, str] = {}
_history: dict[str, list[dict[str, Any]]] = {}


def set_active_doc(whatsapp_number: str, doc_id: str) -> None:
    with _lock:
        _active_doc[whatsapp_number] = doc_id
        _history[whatsapp_number] = []


def get_active_doc(whatsapp_number: str) -> str | None:
    with _lock:
        return _active_doc.get(whatsapp_number)


def get_history(whatsapp_number: str) -> list[dict[str, Any]]:
    with _lock:
        return list(_history.get(whatsapp_number, []))


def append_history(whatsapp_number: str, role: str, content: str) -> None:
    with _lock:
        _history.setdefault(whatsapp_number, []).append({"role": role, "content": content})
