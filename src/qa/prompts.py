"""Build the two model requests: the instructions come from `prompts/*.md`, the documents travel as JSON data.

REQ-T1: passage text only ever appears inside the JSON user message, never in the instructions. Only
authoritative passages are sent (RULE-2 is applied in code before retrieval): the retrieved ones to the
drafter, all of them to the support check. Dates, versions and status are not sent, so they cannot sway
the model (decisions 002, 004 and 040).
"""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel

from qa.dataset import ROOT, Dataset, Passage, Question
from qa.llm import ModelRequest

DRAFT_PROMPT = "prompts/draft_answer.md"
SUPPORT_PROMPT = "prompts/check_support.md"


class Citation(BaseModel):
    passage_id: str
    excerpt: str


class ConflictPair(BaseModel):
    passage_ids: list[str]
    basis: str


class DraftOutput(BaseModel):
    """One step of the drafting loop: either a search_passages call or the final draft (decision 041)."""

    basis: str
    action: Literal["search_passages", "answer"]
    query: str
    status: Literal["answered", "unresolved"]
    answer: str
    citations: list[Citation]
    conflicts: list[ConflictPair]


class Contradiction(BaseModel):
    passage_id: str
    answer_claim: str
    passage_quote: str


class SupportVerdict(BaseModel):
    basis: str
    supported: bool
    unsupported_claims: list[str]
    contradicted_by: list[Contradiction]


def draft_request(
    question: Question, passages: list[Passage], searches: list[dict], searches_left: int
) -> ModelRequest:
    """Each step is a whole, self-contained request: the passages found so far, the searches already made
    and how many remain. So every step is recorded and replayed on its own.
    """
    data = {
        "question": question.text,
        "passages": [{"id": p.id, "text": p.text} for p in passages],
        "searches": searches,
        "searches_left": searches_left,
    }
    return _request("draft", DRAFT_PROMPT, data, DraftOutput)


def support_request(question_text: str, answer: str, cited_ids: list[str], dataset: Dataset) -> ModelRequest:
    """The check sees the cited passages and, apart, every other current passage, so a contradiction is found
    even when retrieval never showed it to the drafter (decision 040).
    """
    current = dataset.authoritative_passages()
    cited = [{"id": p.id, "text": p.text} for p in current if p.id in cited_ids]
    other = [{"id": p.id, "text": p.text} for p in current if p.id not in cited_ids]
    data = {"question": question_text, "answer": answer, "cited_passages": cited, "other_passages": other}
    return _request("support", SUPPORT_PROMPT, data, SupportVerdict)


def _request(call_type: str, prompt_file: str, data: dict, schema: type[BaseModel]) -> ModelRequest:
    system = (ROOT / prompt_file).read_text()
    user = json.dumps(data, ensure_ascii=False, indent=1)
    return ModelRequest(call_type, prompt_file, system, user, _inline_refs(schema.model_json_schema()))


def _inline_refs(schema: dict) -> dict:
    """Replace Pydantic's `$ref`/`$defs` with the definitions themselves: a plain schema the API accepts."""
    defs = schema.get("$defs", {})

    def resolve(node):
        if isinstance(node, dict):
            if "$ref" in node:
                return resolve(defs[node["$ref"].split("/")[-1]])
            return {k: resolve(v) for k, v in node.items() if k != "$defs"}
        if isinstance(node, list):
            return [resolve(v) for v in node]
        return node

    return resolve(schema)
