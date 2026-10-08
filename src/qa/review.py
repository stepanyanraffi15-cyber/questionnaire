"""Reviewer actions and reuse (RULE-3, REQ-A3, REQ-U2).

Only an approval is ever reused. An edit or a note is stored, but it stays a draft until a person approves
it. Reuse is decided when a request is processed: the newest approval for the exact question text is
served, with no model call, if it has no stale mark. Otherwise the item gets a fresh draft (decisions 014
and 015).
"""

from __future__ import annotations

import unicodedata

from qa.checks import strengthening_hints
from qa.dataset import ROOT, Dataset, load_dataset
from qa.drafting import check_support, draft_item
from qa.llm import ModelCallError
from qa.retrieval import hit_ids, load_retrieval_settings, search
from qa.staleness import refresh_stale_marks, stale_mark
from qa.store import append
from qa.views import item_view


class ApprovalBlocked(ValueError):
    """The approval guard refused; the message says why, so the reviewer can fix it."""


def match_key(question_text: str) -> str:
    """Exact match: same text after Unicode NFC and whitespace collapse. Case and wording must match."""
    return unicodedata.normalize("NFC", " ".join(question_text.split()))


def workspace_dataset(state: dict) -> Dataset:
    """The documents as they are now: the seed, this workspace's additions file if it has one, and the change
    files applied in this workspace.
    """
    additions = ROOT / state["additions"] if state.get("additions") else None
    changes = [ROOT / path for path in state["applied_changes"]]
    return load_dataset(change_paths=changes, additions_path=additions)


def set_change(state: dict, change_path: str, applied: bool, at: str) -> Dataset:
    """Apply or remove a change file, then mark any approval whose sources changed."""
    changes = [c for c in state["applied_changes"] if c != change_path]
    state["applied_changes"] = changes + [change_path] if applied else changes
    dataset = workspace_dataset(state)
    refresh_stale_marks(state, dataset, at)
    return dataset


def process_request(state: dict, dataset: Dataset, client, at: str) -> str:
    """Run the whole questionnaire as a new request; reuse fresh approvals, draft everything else."""
    refresh_stale_marks(state, dataset, at)
    request_id = f"R{len(state['requests']) + 1}"
    questions = [q.id for q in dataset.questions]
    append(
        state,
        "requests",
        {"id": request_id, "at": at, "changes": list(dataset.changes), "questions": questions},
    )
    for question in dataset.questions:
        item = f"{request_id}/{question.id}"
        approval = newest_approval(state, match_key(question.text))
        if approval and not stale_mark(state, approval["id"]):
            append(state, "reuses", {"item": item, "approval_id": approval["id"], "at": at})
            continue
        suggestion = draft_item(question, dataset, client)
        shown = approval["id"] if approval else None
        append(state, "suggestions", {"item": item, "at": at, "stale_approval_shown": shown, **suggestion})
    return request_id


def newest_approval(state: dict, key: str) -> dict | None:
    """Only the newest approval for a question can be served; an older one never comes back."""
    matching = [a for a in state["approvals"] if a["match_key"] == key]
    return matching[-1] if matching else None


def save_edit(state: dict, item: str, text: str, by: str, at: str) -> dict:
    if not text.strip():
        raise ValueError("An edit needs text")
    return append(state, "edits", {"item": item, "text": text, "by": by, "at": at})


def add_note(state: dict, item: str, text: str, by: str, at: str) -> dict:
    """Leave an item unresolved with a note for its owner."""
    if not text.strip():
        raise ValueError("A note needs text")
    return append(state, "notes", {"item": item, "text": text, "by": by, "at": at})


def approve(
    state: dict,
    dataset: Dataset,
    client,
    item: str,
    text: str,
    source_ids: list[str],
    approver: str,
    note: str,
    at: str,
) -> dict:
    """Approve `text` with chosen sources. Mechanical problems block; a failed support check needs a note."""
    view = item_view(state, dataset, item)
    sources = _guard_sources(view, dataset, source_ids, text)
    supported, check_detail, call = _support(view["question_text"], text, source_ids, dataset, client)
    if not supported and not note.strip():
        raise ApprovalBlocked(
            f"The support check did not confirm this text ({check_detail}). Add a note to approve."
        )
    record = {
        "id": f"A{len(state['approvals']) + 1}",
        "item": item,
        "match_key": match_key(view["question_text"]),
        "question_text": view["question_text"],
        "text": text,
        "sources": sources,
        "approver": approver,
        "note": note,
        "at": at,
        "support_basis": "supported" if supported else "override",
        "support_detail": check_detail,
        "warnings": strengthening_hints(text, [dataset.passages[pid].text for pid in source_ids]),
        "calls": [call] if call else [],
    }
    return append(state, "approvals", record)


def _guard_sources(view: dict, dataset: Dataset, source_ids: list[str], text: str) -> list[dict]:
    """Hard blocks are mechanical only (decision 016). Returns the sources with versions and excerpts."""
    suggestion = view["suggestion"] or {}
    if not text.strip():
        raise ApprovalBlocked("The answer text is empty")
    if view["status"] == "error":
        raise ApprovalBlocked(f"The item is in error ({view['reason']}); it cannot be approved")
    if suggestion.get("reason") == "conflict" and not view["approval"]:
        raise ApprovalBlocked("The passages conflict; leave the item unresolved with a note for its owner")
    if not source_ids:
        raise ApprovalBlocked("Choose at least one supporting passage")
    current = dataset.current_passage_ids
    bad = [pid for pid in source_ids if pid not in current]
    if bad:
        raise ApprovalBlocked(f"Not a current passage: {', '.join(bad)}")
    drafted = {c["passage_id"]: c["excerpt"] for c in suggestion.get("citations", [])}
    sources = []
    for pid in source_ids:
        passage = dataset.passages[pid]
        excerpt = drafted.get(pid, passage.text)
        version = dataset.documents[passage.doc_id].version
        sources.append({"passage_id": pid, "doc_id": passage.doc_id, "version": version, "excerpt": excerpt})
    return sources


def _support(question_text: str, text: str, source_ids: list[str], dataset: Dataset, client) -> tuple:
    """Run the recorded support check on the exact text being approved, against the passages retrieved for
    the question; a failure is reported, not hidden.
    """
    try:
        context = hit_ids(search(question_text, dataset, client, load_retrieval_settings()))
        verdict, call = check_support(question_text, text, source_ids, dataset, client, context)
    except ModelCallError as exc:
        return False, f"support check unavailable: {exc}", None
    return verdict.supported, verdict.basis, call
