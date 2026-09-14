"""
HybridRetriever — dense (Chroma) + sparse (BM25) + Reciprocal Rank Fusion.
See ARCHITECTURE.md §4 for why both: dense catches conceptual matches,
BM25 catches exact statutory references (e.g. "Section 27") that short,
specific tokens can under-rank in embedding space.

One `.retrieve()` method, exposed to CrewAI via ChromaRetrieverTool so
agents never need to know fusion is happening underneath.
"""
from backend.retrieval.bm25_index import BM25Index
from backend.retrieval.chroma_client import get_collection
from backend.retrieval.embeddings import embed_texts

RRF_K = 60


class HybridRetriever:
    def retrieve(
        self,
        query: str,
        collection_name: str,
        filters: dict | None = None,
        top_k: int = 5,
        dense_k: int = 20,
        sparse_k: int = 20,
    ) -> list[dict]:
        collection = get_collection(collection_name)

        all_chunks = collection.get(where=filters, include=["documents", "metadatas"])
        ids = all_chunks["ids"]
        if not ids:
            return []
        lookup = {
            chunk_id: {"document": doc, "metadata": meta}
            for chunk_id, doc, meta in zip(ids, all_chunks["documents"], all_chunks["metadatas"])
        }

        sparse_ranked = [
            chunk_id for chunk_id, _ in BM25Index(ids, all_chunks["documents"]).query(query, sparse_k)
        ]

        dense_results = collection.query(
            query_embeddings=embed_texts([query]),
            n_results=min(dense_k, len(ids)),
            where=filters,
        )
        dense_ranked = dense_results["ids"][0]

        scores: dict[str, float] = {}
        for rank, chunk_id in enumerate(dense_ranked, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank)
        for rank, chunk_id in enumerate(sparse_ranked, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (RRF_K + rank)

        ranked_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)[:top_k]
        return [
            {
                "id": chunk_id,
                "document": lookup[chunk_id]["document"],
                "metadata": lookup[chunk_id]["metadata"],
                "score": scores[chunk_id],
            }
            for chunk_id in ranked_ids
        ]
