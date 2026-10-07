"""What a reviewer sees for one item, the per-request counts, and an item's revision history.

The UI and the report both use `item_view`, so the screen and the results table cannot disagree. Status
rules, first match wins (decision 020):
1. The item's newest linked approval (one it created, or one it was served) decides: approved, or
   needs_review once that approval carries a stale mark.
2. The item's processing failed: error.
3. A reviewer note newer than the suggestion keeps the item unresolved.
4. Otherwise the suggestion's status (answered or unresolved).
"""

from __future__ import annotations

from qa.dataset import Dataset
from qa.staleness import stale_mark

STATUSES = ("answered", "unresolved", "approved", "needs_review", "error")


def item_view(state: dict, dataset: Dataset, item: str) -> dict:
    request_id, question_id = item.split("/")
    question = next(q for q in dataset.questions if q.id == question_id)
    suggestion = _latest(state["suggestions"], item)
    reuse = _latest(state["reuses"], item)
    approval = _deciding_approval(state, item)
    edit, note = _latest(state["edits"], item), _latest(state["notes"], item)
    view = {
        "item": item,
        "request": request_id,
        "question_id": question_id,
        "question_text": question.text,
        "topic": question.topic,
        "owner": dataset.owner(question),
        "suggestion": suggestion,
        "reused": bool(reuse and approval and reuse["approval_id"] == approval["id"]),
        "approval": _approval_view(state, approval),
        "stale_approval_shown": suggestion.get("stale_approval_shown") if suggestion else None,
        "edited": bool(edit and (not approval or edit["seq"] > approval["seq"])),
        "edit_text": edit["text"] if edit else None,
        "note": note["text"] if note else None,
    }
    view.update(_status(view, suggestion, note))
    view.update(_evidence(view, suggestion, dataset))
    return view


def counts(state: dict, dataset: Dataset, request_id: str) -> dict:
    """Disjoint per-request counts: every item has exactly one status (REQ-A3)."""
    request = next(r for r in state["requests"] if r["id"] == request_id)
    tally = dict.fromkeys(STATUSES, 0)
    for question_id in request["questions"]:
        tally[item_view(state, dataset, f"{request_id}/{question_id}")["status"]] += 1
    return tally


def history(state: dict, item: str) -> list[dict]:
    """Every recorded event for an item in order, each with its reason or note (OPT-3)."""
    events = [_event(s, "drafted", s["answer"], _why(s)) for s in _all(state["suggestions"], item)]
    events += [_event(e, "edited", e["text"], f"by {e['by']}") for e in _all(state["edits"], item)]
    events += [_event(n, "note", n["text"], f"by {n['by']}") for n in _all(state["notes"], item)]
    events += [
        _event(r, "reused approval", "", f"approval {r['approval_id']}") for r in _all(state["reuses"], item)
    ]
    for approval in _linked_approvals(state, item):
        if approval["item"] == item:
            why = f"by {approval['approver']}: {approval['note'] or 'no note'} ({approval['support_basis']})"
            events.append(_event(approval, f"approved ({approval['id']})", approval["text"], why))
        mark = stale_mark(state, approval["id"])
        if mark:
            events.append(
                _event(mark, f"marked for review ({approval['id']})", "", reasons_text(mark["reasons"]))
            )
    return sorted(events, key=lambda e: e["seq"])


def _event(record: dict, event: str, text: str, why: str) -> dict:
    return {"seq": record["seq"], "at": record["at"], "event": event, "text": text, "why": why}


def _status(view: dict, suggestion: dict | None, note: dict | None) -> dict:
    approval = view["approval"]
    if approval:
        if approval["stale"]:
            return {
                "status": "needs_review",
                "reason": "source_changed",
                "detail": reasons_text(approval["stale_reasons"]),
            }
        return {
            "status": "approved",
            "reason": None,
            "detail": "reused approval" if view["reused"] else "approved",
        }
    if suggestion is None:
        return {"status": "error", "reason": "not_processed", "detail": "No suggestion was recorded"}
    if suggestion["status"] == "error":
        return {"status": "error", "reason": suggestion["reason"], "detail": suggestion["detail"]}
    if note and note["seq"] > suggestion["seq"]:
        reason = suggestion["reason"] if suggestion["status"] == "unresolved" else "reviewer_note"
        return {"status": "unresolved", "reason": reason, "detail": suggestion["detail"]}
    return {"status": suggestion["status"], "reason": suggestion["reason"], "detail": suggestion["detail"]}


def _evidence(view: dict, suggestion: dict | None, dataset: Dataset) -> dict:
    """The presented answer and the passages shown beside it, including replaced text (RULE-2)."""
    approval = view["approval"]
    if approval and view["status"] == "approved":
        answer, source, citations = approval["text"], "approval", approval["sources"]
    elif suggestion and view["status"] == "answered":
        answer, source, citations = suggestion["answer"], "model", suggestion["citations"]
    else:
        answer, source, citations = "", None, suggestion["citations"] if suggestion else []
    replaced = sorted(
        {
            p.id
            for c in citations
            if c["doc_id"] in dataset.documents
            for p in dataset.replaced_by(c["doc_id"])
        }
    )
    return {
        "answer": answer,
        "answer_source": source,
        "citations": citations,
        "replaced_shown": replaced,
        "conflicts_shown": suggestion["conflicts"] if suggestion else [],
        "calls": suggestion["calls"] if suggestion and not view["reused"] else [],
    }


def _approval_view(state: dict, approval: dict | None) -> dict | None:
    if approval is None:
        return None
    mark = stale_mark(state, approval["id"])
    return {**approval, "stale": mark is not None, "stale_reasons": mark["reasons"] if mark else []}


def _deciding_approval(state: dict, item: str) -> dict | None:
    """The newest approval linked to the item: one it created, or the one it was served when reused."""
    linked = _linked_approvals(state, item)
    return max(linked, key=lambda a: a["seq"]) if linked else None


def _linked_approvals(state: dict, item: str) -> list[dict]:
    served = {r["approval_id"] for r in _all(state["reuses"], item)}
    return [a for a in state["approvals"] if a["item"] == item or a["id"] in served]


def _latest(records: list[dict], item: str) -> dict | None:
    matching = _all(records, item)
    return matching[-1] if matching else None


def _all(records: list[dict], item: str) -> list[dict]:
    return [r for r in records if r["item"] == item]


def _why(suggestion: dict) -> str:
    return f"{suggestion['status']}" + (f" ({suggestion['reason']})" if suggestion["reason"] else "")


def reasons_text(reasons: list[dict]) -> str:
    parts = []
    for r in reasons:
        if r["change"] == "version":
            parts.append(
                f"{r['doc_id']}: version {r['approved_version']} at approval, {r['current_version']} now"
            )
        else:
            parts.append(f"{r['doc_id']}: {r['change']} since approval")
    return "; ".join(parts)
