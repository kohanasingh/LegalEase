"""
Twilio REST API wrapper (ARCHITECTURE.md §5). Used for the async
push-result flow: webhook gives an immediate TwiML ack, then this sends
the actual result once background processing finishes.
"""
import requests
from twilio.rest import Client

from backend import config

MAX_MESSAGE_CHARS = 1500  # stay well under WhatsApp/Twilio's ~1600-char cap per message

_client: Client | None = None


def get_client() -> Client:
    global _client
    if _client is None:
        if not config.TWILIO_ACCOUNT_SID or not config.TWILIO_AUTH_TOKEN:
            raise RuntimeError("TWILIO_ACCOUNT_SID/TWILIO_AUTH_TOKEN not set — add them to .env.")
        _client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
    return _client


def _chunk_text(text: str, max_chars: int) -> list[str]:
    chunks = []
    remaining = text
    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break
        split_at = remaining.rfind("\n\n", 0, max_chars)
        if split_at == -1:
            split_at = remaining.rfind(" ", 0, max_chars)
        if split_at == -1:
            split_at = max_chars
        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
    return chunks


def send_whatsapp_message(to: str, body: str) -> None:
    """Sends body to `to` (a 'whatsapp:+...' address), splitting into multiple
    messages if it's too long for a single WhatsApp message."""
    client = get_client()
    for chunk in _chunk_text(body, MAX_MESSAGE_CHARS):
        client.messages.create(to=to, from_=config.TWILIO_WHATSAPP_NUMBER, body=chunk)


def download_media(media_url: str) -> bytes:
    """Downloads a media attachment from a Twilio webhook payload's MediaUrl.
    Twilio media URLs require the account's own auth to fetch."""
    response = requests.get(
        media_url, auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN), timeout=30
    )
    response.raise_for_status()
    return response.content
