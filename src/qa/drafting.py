"""Draft one item: model draft -> mechanical checks -> recorded support check -> status (REQ-A1, REQ-A2,
RULE-1).

The result is a suggestion record. It is never an approved answer; only a reviewer's approval is reused
(RULE-3).
"""

from __future__ import annotations

from pydantic import BaseModel, ValidationError

from qa.checks import citation_problem, strengthening_hints, valid_conflict, valid_contradiction
from qa.dataset import Dataset, Question
from qa.llm import ModelCallError, ModelClient, ModelReply, ModelRequest
from qa.prompts import DraftOutput, SupportVerdict, draft_request, support_request


def draft_item(question: Question, dataset: Dataset, client: ModelClient) -> dict:
    """Return a suggestion record. Every failure becomes a visible status and reason, never an exception."""
    suggestion = _blank()
    try:
        draft = _ask(client, draft_request(question, dataset), DraftOutput, suggestion)
    except ModelCallError as exc:
        return _finish(suggestion, "error", exc.reason, str(exc))
    suggestion["draft"] = draft.model_dump()
    conflicts = [pair for pair in draft.conflicts if valid_conflict(pair, dataset)]
    suggestion["conflicts"] = sorted({pid for pair in conflicts for pid in pair.passage_ids})
    if draft.status == "unresolved":
        if conflicts:
            suggestion["conflict_source"] = "draft"
            return _finish(suggestion, "unresolved", "conflict", "The passages give different answers")
        return _finish(suggestion, "unresolved", "undocumented", "No current passage states the answer")
    return _check_answered(question, draft, dataset, client, suggestion, bool(conflicts))


def check_support(
    question_text: str, answer: str, cited_ids: list[str], dataset: Dataset, client: ModelClient
) -> tuple[SupportVerdict, dict]:
    """Ask the recorded support check whether the cited passages support `answer` (also used by the guard)."""
    calls: dict = {"calls": []}
    verdict = _ask(client, support_request(question_text, answer, cited_ids, dataset), SupportVerdict, calls)
    return verdict, calls["calls"][0]


def _check_answered(
    question: Question, draft: DraftOutput, dataset: Dataset, client, suggestion: dict, has_conflict: bool
) -> dict:
    if not draft.answer.strip():
        return _finish(suggestion, "error", "invalid_model_output", "Status answered with an empty answer")
    if not draft.citations:
        return _finish(suggestion, "unresolved", "no_citation", "The draft cites no passage")
    for citation in draft.citations:
        problem = citation_problem(citation, dataset)
        if problem:
            return _finish(suggestion, "unresolved", problem, f"Citation {citation.passage_id}: {problem}")
    suggestion["citations"] = [_citation_record(c.passage_id, c.excerpt, dataset) for c in draft.citations]
    if has_conflict:
        suggestion["conflict_source"] = "draft"
        return _finish(suggestion, "unresolved", "conflict", "The draft reports conflicting passages")
    cited_ids = [c.passage_id for c in draft.citations]
    cited_texts = [dataset.passages[pid].text for pid in cited_ids]
    suggestion["hints"] = strengthening_hints(draft.answer, cited_texts)
    try:
        verdict, call = check_support(question.text, draft.answer, cited_ids, dataset, client)
    except ModelCallError as exc:
        return _finish(suggestion, "error", "support_check_failed", str(exc))
    suggestion["calls"].append(call)
    return _apply_verdict(suggestion, verdict, draft, cited_ids, dataset)


def _apply_verdict(
    suggestion: dict, verdict: SupportVerdict, draft: DraftOutput, cited_ids: list[str], dataset: Dataset
) -> dict:
    suggestion["support"] = verdict.model_dump()
    valid = [c for c in verdict.contradicted_by if valid_contradiction(c, draft.answer, cited_ids, dataset)]
    suggestion["contradictions_rejected"] = [
        c.model_dump() for c in verdict.contradicted_by if c not in valid
    ]
    if valid:
        suggestion["conflict_source"] = "support_check"
        suggestion["conflicts"] = sorted(set(cited_ids) | {c.passage_id for c in valid})
        return _finish(
            suggestion, "unresolved", "conflict", "The support check found a contradicting passage"
        )
    if verdict.supported and verdict.unsupported_claims:
        return _finish(suggestion, "error", "invalid_model_output", "Verdict says supported but lists claims")
    if not verdict.supported:
        claims = "; ".join(verdict.unsupported_claims) or verdict.basis
        return _finish(suggestion, "unresolved", "unsupported_claim", f"Not supported: {claims}")
    suggestion["answer"] = draft.answer
    return _finish(suggestion, "answered", None, verdict.basis)


def _ask(client: ModelClient, request: ModelRequest, schema: type[BaseModel], record: dict):
    """One model call, parsed against its schema; a reply that does not parse is invalid_model_output."""
    reply: ModelReply = client.call(request)
    record["calls"].append(
        {
            "call_type": request.call_type,
            "label": reply.label,
            "fingerprint": reply.fingerprint,
            "model": reply.model,
            "recorded_at": reply.recorded_at,
        }
    )
    try:
        return schema.model_validate_json(reply.text)
    except ValidationError as exc:
        raise ModelCallError("invalid_model_output", f"Reply does not match the schema: {exc}") from exc


def _citation_record(passage_id: str, excerpt: str, dataset: Dataset) -> dict:
    """Store the document version with the citation, so a later version change can be detected (RULE-3)."""
    doc_id = dataset.passages[passage_id].doc_id
    return {
        "passage_id": passage_id,
        "doc_id": doc_id,
        "version": dataset.documents[doc_id].version,
        "excerpt": excerpt,
    }


def _blank() -> dict:
    return {
        "status": None,
        "reason": None,
        "detail": "",
        "answer": "",
        "draft": None,
        "citations": [],
        "conflicts": [],
        "conflict_source": None,
        "hints": [],
        "support": None,
        "contradictions_rejected": [],
        "calls": [],
    }


def _finish(suggestion: dict, status: str, reason: str | None, detail: str) -> dict:
    suggestion.update(status=status, reason=reason, detail=detail)
    return suggestion
