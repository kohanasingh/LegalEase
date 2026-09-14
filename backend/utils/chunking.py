"""
Structure-aware + fallback chunking for uploaded documents (see
ARCHITECTURE.md §3): split on paragraph/clause boundaries where the
document has structure; fall back to fixed-size windows only for
paragraphs too large to be a sensible single chunk (badly-structured or
scanned documents tend to extract as a few huge blobs of text).
"""
import re

MAX_CHUNK_WORDS = 500
OVERLAP_WORDS = 50

_PARAGRAPH_SPLIT_RE = re.compile(r"\n\s*\n+")


def split_into_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in _PARAGRAPH_SPLIT_RE.split(text) if p.strip()]


def _fixed_window_chunks(words: list[str], max_words: int, overlap_words: int) -> list[str]:
    chunks = []
    start = 0
    while start < len(words):
        end = start + max_words
        chunks.append(" ".join(words[start:end]))
        if end >= len(words):
            break
        start = end - overlap_words
    return chunks


def chunk_document(
    text: str, max_words: int = MAX_CHUNK_WORDS, overlap_words: int = OVERLAP_WORDS
) -> list[str]:
    chunks = []
    for paragraph in split_into_paragraphs(text):
        words = paragraph.split()
        if len(words) <= max_words:
            chunks.append(paragraph)
        else:
            chunks.extend(_fixed_window_chunks(words, max_words, overlap_words))
    return chunks
