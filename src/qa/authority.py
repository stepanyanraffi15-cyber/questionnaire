"""RULE-2: a document is replaced only through another document's explicit `supersedes` field.

A newer date, a higher version or a `status` value never gives authority (decisions 001, 002 and 034).
"""

from __future__ import annotations

from typing import Protocol


class _HasSupersedes(Protocol):
    id: str
    supersedes: str | None


def replaced_document_ids(documents: dict[str, _HasSupersedes]) -> set[str]:
    """IDs of loaded documents that some other loaded document names in its `supersedes` field."""
    return {
        doc.supersedes
        for doc in documents.values()
        if doc.supersedes and doc.supersedes in documents and doc.supersedes != doc.id
    }
