"""Ad-hoc Stage 1 checkpoint: query chroma_data directly, no agents involved."""
import chromadb
from fastembed import TextEmbedding

client = chromadb.PersistentClient(path="corpus/chroma_data")
collection = client.get_collection("legal_corpus")
model = TextEmbedding("BAAI/bge-small-en-v1.5")

queries = [
    "termination of an agency contract",
    "what makes a contract voidable",
    "Section 73",
    "consideration for a promise",
]

for query in queries:
    embedding = [e.tolist() for e in model.embed([query])]
    results = collection.query(query_embeddings=embedding, n_results=3)
    print(f"\nQuery: {query!r}")
    for doc, meta, dist in zip(
        results["documents"][0], results["metadatas"][0], results["distances"][0]
    ):
        print(f"  [{meta['section']}] (dist={dist:.3f}) {doc[:100]}...")
