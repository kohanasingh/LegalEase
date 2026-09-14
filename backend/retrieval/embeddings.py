"""
Shared embedding model singleton (BAAI/bge-small-en-v1.5) via fastembed —
an ONNX-only library that never imports torch, unlike sentence-transformers
(whose own package unconditionally imports torch regardless of backend
choice — see CHANGES.md). fastembed's build of this model already returns
normalized vectors, so no explicit normalization step is needed here.
"""
from fastembed import TextEmbedding

from backend import config

_model: TextEmbedding | None = None


def get_embedding_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(config.EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    return [embedding.tolist() for embedding in get_embedding_model().embed(texts)]
