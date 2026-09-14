"""
Builds the baked `legal_corpus` Chroma collection from corpus/raw/*.json.

Chunking is structure-aware per ARCHITECTURE.md §3: each scraped section is
already one atomic chunk (a whole statutory provision), so no further
splitting happens here — splitting mid-section would break legal meaning.

Run after corpus/scripts/scrape_bare_acts.py. Writes a PersistentClient
directory at corpus/chroma_data/, which gets baked into the backend Docker
image at deploy time (see ARCHITECTURE.md §6) — never written at runtime.
"""
import json
from pathlib import Path

import chromadb
from fastembed import TextEmbedding

CORPUS_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = CORPUS_DIR / "raw"
CHROMA_DIR = CORPUS_DIR / "chroma_data"
COLLECTION_NAME = "legal_corpus"
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
EMBED_BATCH_SIZE = 64


def load_chunks() -> tuple[list[str], list[str], list[dict]]:
    ids, documents, metadatas = [], [], []
    for raw_file in sorted(RAW_DIR.glob("*.json")):
        data = json.loads(raw_file.read_text(encoding="utf-8"))
        source_name = data["source_name"]
        source_type = data["source_type"]
        slug = raw_file.stem
        for section in data["sections"]:
            chunk_id = f"{slug}_sec_{section['section']}"
            text = f"Section {section['section']} ({section['title']}): {section['text']}"
            ids.append(chunk_id)
            documents.append(text)
            metadatas.append(
                {
                    "source_type": source_type,
                    "source_name": source_name,
                    "section": f"Section {section['section']}",
                }
            )
    return ids, documents, metadatas


def main():
    ids, documents, metadatas = load_chunks()
    if not ids:
        raise SystemExit(f"No chunks found under {RAW_DIR} — run scrape_bare_acts.py first.")
    print(f"Loaded {len(ids)} section chunks from {RAW_DIR}")

    print(f"Loading embedding model {EMBEDDING_MODEL}...")
    model = TextEmbedding(EMBEDDING_MODEL)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    client.delete_collection(COLLECTION_NAME) if COLLECTION_NAME in [
        c.name for c in client.list_collections()
    ] else None
    collection = client.create_collection(
        COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )

    for start in range(0, len(ids), EMBED_BATCH_SIZE):
        batch_ids = ids[start : start + EMBED_BATCH_SIZE]
        batch_docs = documents[start : start + EMBED_BATCH_SIZE]
        batch_meta = metadatas[start : start + EMBED_BATCH_SIZE]
        embeddings = [e.tolist() for e in model.embed(batch_docs)]
        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_meta,
            embeddings=embeddings,
        )
        print(f"  indexed {start + len(batch_ids)}/{len(ids)}")

    print(f"Done. Collection '{COLLECTION_NAME}' has {collection.count()} chunks at {CHROMA_DIR}")


if __name__ == "__main__":
    main()
