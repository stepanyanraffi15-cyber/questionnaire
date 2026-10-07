"""RULE-3: mark an approved answer for review when a document it relies on changes version.

Each approval stores the version of every source document. A simple version comparison finds the change
(REQ-T2). The mark is sticky: once appended it stays, even if the version changes back, until a person
re-approves, which creates a new approval (decision 011).
"""

from __future__ import annotations

from qa.dataset import Dataset
from qa.store import append


def stale_reasons(approval: dict, dataset: Dataset) -> list[dict]:
    """One entry per source document that changed since approval: a new version, replaced, or no longer
    loaded.
    """
    reasons = []
    for source in approval["sources"]:
        doc = dataset.documents.get(source["doc_id"])
        if doc is None:
            change, current = "removed", None
        elif doc.id in dataset.replaced_ids:
            change, current = "superseded", doc.version
        elif doc.version != source["version"]:
            change, current = "version", doc.version
        else:
            continue
        reasons.append(
            {
                "doc_id": source["doc_id"],
                "approved_version": source["version"],
                "current_version": current,
                "change": change,
            }
        )
    return reasons


def stale_mark(state: dict, approval_id: str) -> dict | None:
    return next((m for m in state["stale_marks"] if m["approval_id"] == approval_id), None)


def refresh_stale_marks(state: dict, dataset: Dataset, at: str) -> None:
    """Append a mark for every approval that has just become stale. Existing marks are never removed."""
    for approval in state["approvals"]:
        if stale_mark(state, approval["id"]):
            continue
        reasons = stale_reasons(approval, dataset)
        if reasons:
            append(state, "stale_marks", {"approval_id": approval["id"], "reasons": reasons, "at": at})
