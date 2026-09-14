"""
Chroma PersistentClient setup and the two-collection split (see CLAUDE.md
non-negotiable #4): `legal_corpus` is static and baked in by
corpus/scripts/build_corpus_index.py — never written to at runtime.
`user_documents` is created here on first use and is fine to lose on
redeploy since Render's free tier has no persistent disk.
"""
import chromadb
from chromadb.api.models.Collection import Collection

from backend import config

_client: chromadb.ClientAPI | None = None


def get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=config.CHROMA_PERSIST_DIR)
    return _client


def get_legal_corpus_collection() -> Collection:
    client = get_client()
    try:
        return client.get_collection(config.LEGAL_CORPUS_COLLECTION)
    except Exception as exc:
        raise RuntimeError(
            f"'{config.LEGAL_CORPUS_COLLECTION}' collection not found at "
            f"{config.CHROMA_PERSIST_DIR} — run corpus/scripts/build_corpus_index.py first."
        ) from exc


def get_user_documents_collection() -> Collection:
    client = get_client()
    return client.get_or_create_collection(
        config.USER_DOCUMENTS_COLLECTION, metadata={"hnsw:space": "cosine"}
    )


def get_collection(name: str) -> Collection:
    if name == config.LEGAL_CORPUS_COLLECTION:
        return get_legal_corpus_collection()
    if name == config.USER_DOCUMENTS_COLLECTION:
        return get_user_documents_collection()
    raise ValueError(f"Unknown collection: {name}")
