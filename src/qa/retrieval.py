"""Hybrid retrieval over the current passages: BM25 and Gemini embeddings, merged by reciprocal rank fusion.

Only authoritative passages are searched, so RULE-2 is applied before retrieval and a replaced passage
can never reach the model (decision 004). Every ranking breaks ties by passage ID, so the same inputs
always give the same result and a keyless replay is byte-identical (decision 040).
"""

from __future__ import annotations

import math
import re
import tomllib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from qa.dataset import ROOT, Dataset, Passage
from qa.llm import ModelCallError, ModelClient

SETTINGS_PATH = ROOT / "config" / "retrieval.toml"
# Common words that match almost every passage ("do", "the", "can") and would let BM25 rank on noise.
STOPWORDS = frozenset(
    "a an and are as at be by can do does for from how in is it its of on or the their they this to was what "
    "when where which who will with".split()
)


class RetrievalError(ModelCallError):
    """Retrieval could not run (no current passages, or unusable embeddings); `reason` becomes the item's
    visible error reason, like a failed model call.
    """


@dataclass(frozen=True)
class RetrievalSettings:
    top_k: int
    rrf_k: int
    bm25_k1: float
    bm25_b: float
    max_searches: int


def load_retrieval_settings(path: Path = SETTINGS_PATH) -> RetrievalSettings:
    return RetrievalSettings(**tomllib.loads(path.read_text()))


def tokens(text: str) -> list[str]:
    """Lower-case words and numbers minus stopwords; no stemming, so the keyword side is easy to explain."""
    return [word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in STOPWORDS]


def bm25_ranking(query: str, passages: list[Passage], k1: float, b: float) -> list[str]:
    """Passage IDs that share at least one word with the query, best first."""
    scores = bm25_scores(query, passages, k1, b)
    return sorted(scores, key=lambda pid: (-scores[pid], pid))


def bm25_scores(query: str, passages: list[Passage], k1: float, b: float) -> dict[str, float]:
    """Okapi BM25 with the non-negative IDF log(1 + (N - df + 0.5) / (df + 0.5)); only scores above 0."""
    docs = {p.id: tokens(p.text) for p in passages}
    average = sum(len(words) for words in docs.values()) / len(docs)
    frequency = Counter(word for words in docs.values() for word in set(words))
    scores = {}
    for passage_id, words in docs.items():
        counts = Counter(words)
        score = 0.0
        for word in set(tokens(query)) & set(counts):
            idf = math.log(1 + (len(docs) - frequency[word] + 0.5) / (frequency[word] + 0.5))
            norm = k1 * (1 - b + b * len(words) / average)
            score += idf * counts[word] * (k1 + 1) / (counts[word] + norm)
        if score > 0:
            scores[passage_id] = score
    return scores


def dense_ranking(query: list[float], vectors: dict[str, list[float]]) -> list[str]:
    """Every passage ID by cosine similarity to the query embedding, best first."""
    scores = {pid: _cosine(query, vector) for pid, vector in vectors.items()}
    return sorted(scores, key=lambda pid: (-scores[pid], pid))


def fuse(rankings: list[list[str]], rrf_k: int) -> dict[str, float]:
    """Reciprocal rank fusion: each list adds 1 / (rrf_k + rank). Only ranks count, never raw scores."""
    fused: dict[str, float] = {}
    for ranking in rankings:
        for rank, passage_id in enumerate(ranking, start=1):
            fused[passage_id] = fused.get(passage_id, 0.0) + 1 / (rrf_k + rank)
    return fused


def search(query: str, dataset: Dataset, client: ModelClient, settings: RetrievalSettings) -> dict:
    """The top-k current passages for `query`, with both ranks and the fused score for each.

    This is the only tool the drafting model can use, and it is read-only (decision 041).
    """
    if not query.strip():
        raise ModelCallError("invalid_model_output", "A search needs a non-empty query")
    passages = dataset.authoritative_passages()
    if not passages:
        raise RetrievalError("no_passages", "There is no current passage to search")
    documents = client.embed([p.text for p in passages], "RETRIEVAL_DOCUMENT")
    question = client.embed([query], "RETRIEVAL_QUERY")[0]
    _check_vectors([question.vector] + [e.vector for e in documents])
    keyword = bm25_ranking(query, passages, settings.bm25_k1, settings.bm25_b)
    vectors = {p.id: e.vector for p, e in zip(passages, documents, strict=True)}
    dense = dense_ranking(question.vector, vectors)
    fused = fuse([keyword, dense], settings.rrf_k)
    top = sorted(fused, key=lambda pid: (-fused[pid], pid))[: settings.top_k]
    hits = [
        {
            "passage_id": pid,
            "bm25_rank": keyword.index(pid) + 1 if pid in keyword else None,
            "dense_rank": dense.index(pid) + 1,
            "score": round(fused[pid], 6),
        }
        for pid in top
    ]
    labels = sorted({e.label for e in documents} | {question.label})
    return {
        "query": query,
        "top_k": settings.top_k,
        "hits": hits,
        "bm25_top": keyword[: settings.top_k],
        "dense_top": dense[: settings.top_k],
        "embedding_labels": labels,
    }


def hit_ids(result: dict) -> list[str]:
    return [hit["passage_id"] for hit in result["hits"]]


def _check_vectors(vectors: list[list[float]]) -> None:
    """Every vector must have the query's length, finite values and a non-zero length, or cosine is
    meaningless; a bad one is a visible error, never a silent ranking.
    """
    size = len(vectors[0])
    for vector in vectors:
        finite = all(math.isfinite(x) for x in vector)
        if len(vector) != size or not finite or not any(vector):
            raise RetrievalError("invalid_embedding", "An embedding is empty, the wrong size or not finite")


def _cosine(a: list[float], b: list[float]) -> float:
    """Cosine, not a dot product: vectors shortened to 768 values are not unit length."""
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    return dot / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))
