"""Mechanical evidence checks (REQ-A1). Code decides only facts it can check exactly (decision 035).

Whether a passage *supports* a claim is meaning, so the recorded support check decides that. The
strengthening-word list here only raises a hint for the support check and the reviewer; it never sets a
status (decision 006).
"""

from __future__ import annotations

import re

from qa.dataset import Dataset
from qa.prompts import Citation, ConflictPair, Contradiction

STRENGTHENING_WORDS = ("only", "all", "every", "always", "never", "exclusively", "solely")


def collapse(text: str) -> str:
    """Whitespace collapse is the only normalisation: no dash, case or quote folding (decision 008)."""
    return " ".join(text.split())


def is_verbatim(quote: str, text: str) -> bool:
    return bool(collapse(quote)) and collapse(quote) in collapse(text)


def citation_problem(citation: Citation, dataset: Dataset) -> str | None:
    """The first mechanical problem with one citation, as a reason code, or None when it checks out."""
    passage = dataset.passages.get(citation.passage_id)
    if passage is None:
        return "invalid_citation"
    if passage.doc_id in dataset.replaced_ids:
        return "superseded_source"
    if not is_verbatim(citation.excerpt, passage.text):
        return "invalid_excerpt"
    return None


def valid_conflict(pair: ConflictPair, dataset: Dataset) -> bool:
    """A reported conflict counts when it names two different current passages (the model judged meaning)."""
    current = dataset.current_passage_ids
    ids = set(pair.passage_ids)
    return len(ids) >= 2 and ids <= current


def valid_contradiction(item: Contradiction, answer: str, cited_ids: list[str], dataset: Dataset) -> bool:
    """Decision 009: the model decides a contradiction exists; code checks only that its quotes are real."""
    passage = dataset.passages.get(item.passage_id)
    current = dataset.current_passage_ids
    return (
        passage is not None
        and item.passage_id in current
        and item.passage_id not in cited_ids
        and is_verbatim(item.passage_quote, passage.text)
        and is_verbatim(item.answer_claim, answer)
    )


def strengthening_hints(answer: str, cited_texts: list[str]) -> list[str]:
    """Words like "only" that the answer uses but no cited passage does: a hint, never a verdict."""
    cited_words = set(re.findall(r"[a-z]+", " ".join(cited_texts).lower()))
    answer_words = set(re.findall(r"[a-z]+", answer.lower()))
    return [w for w in STRENGTHENING_WORDS if w in answer_words and w not in cited_words]
