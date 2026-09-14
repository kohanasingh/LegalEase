"""
Sparse (BM25) side of hybrid retrieval — see ARCHITECTURE.md §4.

Built fresh, in-memory, per query, scoped to whatever chunk set the caller
hands it (already filtered by collection/metadata). At this project's
corpus scale (a few hundred to a few thousand chunks) that's cheap and
avoids maintaining a separate persistent sparse index that could drift out
of sync with Chroma.
"""
import re

from rank_bm25 import BM25Okapi

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class BM25Index:
    # Legal chunks vary hugely in length for structural reasons (a one-line
    # definitions section vs. a section full of worked illustrations) rather
    # than verbosity/padding — the assumption BM25's default length norm
    # (b=0.75) is tuned for. At the default, an exact section-number match
    # (e.g. querying "Section 73") lost to short, irrelevant chunks purely
    # because Section 73 itself is long; a lower b measurably fixed it
    # without hurting conceptual queries. See CHANGES.md.
    BM25_B = 0.3

    def __init__(self, ids: list[str], documents: list[str]):
        self.ids = ids
        self._bm25 = (
            BM25Okapi([tokenize(doc) for doc in documents], b=self.BM25_B) if documents else None
        )

    def query(self, query_text: str, top_k: int) -> list[tuple[str, float]]:
        """Returns [(chunk_id, bm25_score), ...] sorted descending, best first."""
        if self._bm25 is None:
            return []
        scores = self._bm25.get_scores(tokenize(query_text))
        ranked = sorted(zip(self.ids, scores), key=lambda pair: pair[1], reverse=True)
        return [pair for pair in ranked if pair[1] > 0][:top_k]
